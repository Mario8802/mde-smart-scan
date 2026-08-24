from decimal import Decimal

from django.core.management.base import BaseCommand

from scans.models import AuditEvent, ScanRecord


DEMO_RECORDS = [
    {
        "tracking_number": "RR12345678901AT",
        "item_type": ScanRecord.ItemType.RSA,
        "recipient_name": "Erika Mustermann",
        "street": "Musterstraße 12",
        "postal_code": "4020",
        "city": "Linz",
        "status": ScanRecord.Status.CONFIRMED,
    },
    {
        "tracking_number": "EE98765432101AT",
        "item_type": ScanRecord.ItemType.RSB,
        "recipient_name": "Max Beispiel",
        "street": "Testweg 4",
        "postal_code": "4060",
        "city": "Leonding",
        "status": ScanRecord.Status.PRINTED,
    },
    {
        "tracking_number": "CA24681357901AT",
        "item_type": ScanRecord.ItemType.REGISTERED,
        "recipient_name": "Anna Demo",
        "street": "Pilotgasse 7",
        "postal_code": "4040",
        "city": "Linz",
        "status": ScanRecord.Status.REVIEW,
    },
]


class Command(BaseCommand):
    help = "Create privacy-safe synthetic demo scans"

    def handle(self, *args, **options):
        created_count = 0
        for data in DEMO_RECORDS:
            record, created = ScanRecord.objects.get_or_create(
                tracking_number=data["tracking_number"],
                defaults={
                    **data,
                    "source": ScanRecord.Source.DEMO,
                    "confidence": Decimal("0.917"),
                    "raw_text": "Synthetischer Demo-Datensatz",
                },
            )
            if created:
                AuditEvent.objects.create(
                    scan=record, action="DEMO_SEEDED", metadata={"synthetic": True}
                )
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f"Created {created_count} demo records."))
