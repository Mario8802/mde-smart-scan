from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .forms import ScanCaptureForm, ScanReviewForm
from .models import AuditEvent, ScanRecord
from .services.extractor import extract_shipment
from .services.impact import calculate_impact
from .services.ocr import DEMO_OCR_TEXT, OCRProcessingError, extract_text


def dashboard(request):
    today = timezone.localdate()
    recent = ScanRecord.objects.all()[:8]
    today_records = ScanRecord.objects.filter(created_at__date=today)
    impact = calculate_impact(42, 12, max(today_records.count(), 24), 220)
    context = {
        "recent": recent,
        "today_count": today_records.count(),
        "review_count": ScanRecord.objects.filter(status=ScanRecord.Status.REVIEW).count(),
        "printed_count": ScanRecord.objects.filter(status=ScanRecord.Status.PRINTED).count(),
        "impact": impact,
    }
    return render(request, "scans/dashboard.html", context)


def scan_capture(request):
    if request.method == "POST":
        form = ScanCaptureForm(request.POST, request.FILES)
        if form.is_valid():
            source = ScanRecord.Source.TEXT
            engine = "provided-text"
            raw_text = form.cleaned_data.get("ocr_text", "").strip()
            try:
                if form.cleaned_data.get("demo_mode"):
                    raw_text = DEMO_OCR_TEXT
                    source = ScanRecord.Source.DEMO
                    engine = "deterministic-demo"
                elif form.cleaned_data.get("image"):
                    result = extract_text(form.cleaned_data["image"])
                    raw_text = result.text
                    engine = result.engine
                    source = ScanRecord.Source.UPLOAD

                shipment = extract_shipment(raw_text)
                tracking = shipment.tracking_number or f"REVIEW{timezone.now():%Y%m%d%H%M%S%f}"
                record = ScanRecord.objects.create(
                    tracking_number=tracking,
                    item_type=shipment.item_type,
                    recipient_name=shipment.recipient_name,
                    street=shipment.street,
                    postal_code=shipment.postal_code,
                    city=shipment.city,
                    confidence=Decimal(str(shipment.confidence)),
                    source=source,
                    raw_text=(
                        raw_text
                        if source == ScanRecord.Source.DEMO or settings.STORE_RAW_OCR
                        else ""
                    ),
                )
                AuditEvent.objects.create(
                    scan=record,
                    action="OCR_EXTRACTED",
                    metadata={"engine": engine, "confidence": shipment.confidence},
                )
                return redirect("scan-review", pk=record.pk)
            except OCRProcessingError as exc:
                form.add_error("image", str(exc))
            except IntegrityError:
                existing = ScanRecord.objects.get(tracking_number=shipment.tracking_number)
                messages.info(request, "Diese Sendung wurde bereits erfasst.")
                return redirect("scan-review", pk=existing.pk)
    else:
        form = ScanCaptureForm()
    return render(request, "scans/capture.html", {"form": form})


def scan_review(request, pk: int):
    record = get_object_or_404(ScanRecord, pk=pk)
    if request.method == "POST":
        form = ScanReviewForm(request.POST, instance=record)
        if form.is_valid():
            record = form.save(commit=False)
            record.confirm()
            record.save()
            AuditEvent.objects.create(
                scan=record,
                action="DATA_CONFIRMED",
                metadata={"fields_reviewed": list(form.fields.keys())},
            )
            messages.success(request, "Sendungsdaten bestätigt.")
            return redirect("scan-review", pk=record.pk)
    else:
        form = ScanReviewForm(instance=record)
    return render(request, "scans/review.html", {"record": record, "form": form})


@require_POST
def prepare_label(request, pk: int):
    record = get_object_or_404(ScanRecord, pk=pk)
    if record.status == ScanRecord.Status.REVIEW:
        messages.error(request, "Bitte Sendungsdaten vor dem Druck bestätigen.")
        return redirect("scan-review", pk=record.pk)
    record.mark_printed()
    record.save(update_fields=["status", "printed_at"])
    AuditEvent.objects.create(scan=record, action="LABEL_PREPARED")
    return redirect("scan-label", pk=record.pk)


def scan_label(request, pk: int):
    record = get_object_or_404(ScanRecord, pk=pk)
    return render(request, "scans/label.html", {"record": record})


@require_GET
def scans_api(request):
    records = ScanRecord.objects.all()[:50]
    return JsonResponse(
        {
            "count": len(records),
            "results": [
                {
                    "id": record.pk,
                    "tracking_number": record.tracking_number,
                    "item_type": record.item_type,
                    "recipient_name": record.recipient_name,
                    "postal_code": record.postal_code,
                    "city": record.city,
                    "confidence": float(record.confidence),
                    "status": record.status,
                    "created_at": record.created_at.isoformat(),
                }
                for record in records
            ],
        }
    )


@require_GET
def impact_api(request):
    try:
        estimate = calculate_impact(
            float(request.GET.get("manual_seconds", 42)),
            float(request.GET.get("smart_scan_seconds", 12)),
            int(request.GET.get("items_per_day", 24)),
            int(request.GET.get("workdays", 220)),
        )
    except (TypeError, ValueError):
        return JsonResponse({"error": "Invalid impact parameters"}, status=400)
    return JsonResponse(estimate.__dict__)


@require_GET
def health(request):
    return JsonResponse({"status": "ok", "service": "mde-smart-scan"})
