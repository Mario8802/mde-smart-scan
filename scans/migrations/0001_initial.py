# Generated manually for a reproducible prototype.
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ScanRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tracking_number", models.CharField(db_index=True, max_length=32, unique=True)),
                ("item_type", models.CharField(choices=[("RSA", "RSa-Brief"), ("RSB", "RSb-Brief"), ("REGISTERED", "Einschreiben"), ("UNKNOWN", "Unbekannt")], default="UNKNOWN", max_length=16)),
                ("recipient_name", models.CharField(blank=True, max_length=160)),
                ("street", models.CharField(blank=True, max_length=160)),
                ("postal_code", models.CharField(blank=True, max_length=4, validators=[django.core.validators.RegexValidator("^\\d{4}$", "Die PLZ muss vierstellig sein.")])),
                ("city", models.CharField(blank=True, max_length=100)),
                ("confidence", models.DecimalField(decimal_places=3, default=0, max_digits=4)),
                ("status", models.CharField(choices=[("REVIEW", "Prüfung erforderlich"), ("CONFIRMED", "Bestätigt"), ("PRINTED", "Benachrichtigung gedruckt")], db_index=True, default="REVIEW", max_length=16)),
                ("source", models.CharField(choices=[("CAMERA", "Kamera"), ("UPLOAD", "Upload"), ("TEXT", "OCR-Text"), ("DEMO", "Demo")], max_length=16)),
                ("raw_text", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("confirmed_at", models.DateTimeField(blank=True, null=True)),
                ("printed_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="AuditEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action", models.CharField(max_length=48)),
                ("actor_label", models.CharField(default="MDE Demo User", max_length=80)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("scan", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="events", to="scans.scanrecord")),
            ],
            options={"ordering": ["created_at"]},
        ),
    ]
