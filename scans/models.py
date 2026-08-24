from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


class ScanRecord(models.Model):
    class ItemType(models.TextChoices):
        RSA = "RSA", "RSa-Brief"
        RSB = "RSB", "RSb-Brief"
        REGISTERED = "REGISTERED", "Einschreiben"
        UNKNOWN = "UNKNOWN", "Unbekannt"

    class Status(models.TextChoices):
        REVIEW = "REVIEW", "Prüfung erforderlich"
        CONFIRMED = "CONFIRMED", "Bestätigt"
        PRINTED = "PRINTED", "Benachrichtigung gedruckt"

    class Source(models.TextChoices):
        CAMERA = "CAMERA", "Kamera"
        UPLOAD = "UPLOAD", "Upload"
        TEXT = "TEXT", "OCR-Text"
        DEMO = "DEMO", "Demo"

    tracking_number = models.CharField(max_length=32, unique=True, db_index=True)
    item_type = models.CharField(
        max_length=16, choices=ItemType.choices, default=ItemType.UNKNOWN
    )
    recipient_name = models.CharField(max_length=160, blank=True)
    street = models.CharField(max_length=160, blank=True)
    postal_code = models.CharField(
        max_length=4,
        blank=True,
        validators=[RegexValidator(r"^\d{4}$", "Die PLZ muss vierstellig sein.")],
    )
    city = models.CharField(max_length=100, blank=True)
    confidence = models.DecimalField(max_digits=4, decimal_places=3, default=0)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.REVIEW, db_index=True
    )
    source = models.CharField(max_length=16, choices=Source.choices)
    raw_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    printed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.get_item_type_display()} · {self.tracking_number}"

    @property
    def address(self) -> str:
        return ", ".join(
            part
            for part in [self.street, f"{self.postal_code} {self.city}".strip()]
            if part
        )

    @property
    def confidence_percent(self) -> int:
        return round(float(self.confidence) * 100)

    def confirm(self) -> None:
        self.status = self.Status.CONFIRMED
        self.confirmed_at = timezone.now()

    def mark_printed(self) -> None:
        self.status = self.Status.PRINTED
        self.printed_at = timezone.now()


class AuditEvent(models.Model):
    scan = models.ForeignKey(ScanRecord, on_delete=models.CASCADE, related_name="events")
    action = models.CharField(max_length=48)
    actor_label = models.CharField(max_length=80, default="MDE Demo User")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.scan.tracking_number}: {self.action}"
