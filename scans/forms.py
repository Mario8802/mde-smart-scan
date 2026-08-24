from django import forms

from .models import ScanRecord


class ScanCaptureForm(forms.Form):
    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={"accept": "image/jpeg,image/png,image/webp", "capture": "environment"}
        ),
    )
    ocr_text = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={"rows": 7, "placeholder": "Optional: bereits erkannten Text einfügen …"}
        ),
    )
    demo_mode = forms.BooleanField(required=False)

    def clean(self):
        cleaned = super().clean()
        if not any(
            [cleaned.get("image"), cleaned.get("ocr_text"), cleaned.get("demo_mode")]
        ):
            raise forms.ValidationError(
                "Bitte Foto aufnehmen, Bild auswählen oder Demo starten."
            )
        return cleaned


class ScanReviewForm(forms.ModelForm):
    class Meta:
        model = ScanRecord
        fields = (
            "tracking_number",
            "item_type",
            "recipient_name",
            "street",
            "postal_code",
            "city",
        )
        widgets = {
            "tracking_number": forms.TextInput(attrs={"inputmode": "numeric"}),
            "postal_code": forms.TextInput(attrs={"inputmode": "numeric"}),
        }

    def clean_tracking_number(self) -> str:
        value = "".join(self.cleaned_data["tracking_number"].upper().split())
        if len(value) < 8:
            raise forms.ValidationError("Die Sendungsnummer ist zu kurz.")
        return value
