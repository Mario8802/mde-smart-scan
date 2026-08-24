import pytest
from django.urls import reverse

from scans.models import AuditEvent, ScanRecord


pytestmark = pytest.mark.django_db


def test_dashboard_is_available(client):
    response = client.get(reverse("dashboard"))
    assert response.status_code == 200
    assert b"MDE Smart Scan" in response.content


def test_demo_creates_reviewable_scan(client):
    response = client.post(reverse("scan-capture"), {"demo_mode": "on"})

    record = ScanRecord.objects.get()
    assert response.status_code == 302
    assert response.url == reverse("scan-review", kwargs={"pk": record.pk})
    assert record.item_type == ScanRecord.ItemType.RSA
    assert record.recipient_name == "Erika Mustermann"
    assert AuditEvent.objects.filter(scan=record, action="OCR_EXTRACTED").exists()


def test_confirmation_and_print_workflow(client):
    record = ScanRecord.objects.create(
        tracking_number="RR12345678901AT",
        item_type=ScanRecord.ItemType.RSA,
        recipient_name="Erika Mustermann",
        street="Musterstraße 12",
        postal_code="4020",
        city="Linz",
        confidence="1.000",
        source=ScanRecord.Source.DEMO,
    )
    response = client.post(
        reverse("scan-review", kwargs={"pk": record.pk}),
        {
            "tracking_number": record.tracking_number,
            "item_type": record.item_type,
            "recipient_name": record.recipient_name,
            "street": record.street,
            "postal_code": record.postal_code,
            "city": record.city,
        },
    )
    assert response.status_code == 302
    record.refresh_from_db()
    assert record.status == ScanRecord.Status.CONFIRMED

    response = client.post(reverse("prepare-label", kwargs={"pk": record.pk}))
    assert response.status_code == 302
    record.refresh_from_db()
    assert record.status == ScanRecord.Status.PRINTED
    assert record.printed_at is not None


def test_print_requires_confirmation(client):
    record = ScanRecord.objects.create(
        tracking_number="REVIEW12345678",
        source=ScanRecord.Source.TEXT,
    )
    response = client.post(reverse("prepare-label", kwargs={"pk": record.pk}))
    record.refresh_from_db()
    assert response.url == reverse("scan-review", kwargs={"pk": record.pk})
    assert record.status == ScanRecord.Status.REVIEW


def test_health_and_api(client):
    assert client.get(reverse("health")).json()["status"] == "ok"
    response = client.get(reverse("impact-api"), {"items_per_day": 24})
    assert response.status_code == 200
    assert response.json()["hours_saved_per_year"] == 44
