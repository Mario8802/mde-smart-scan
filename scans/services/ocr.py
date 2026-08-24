from dataclasses import dataclass
from io import BytesIO

from django.conf import settings
from PIL import Image, ImageEnhance, ImageOps, UnidentifiedImageError


MAX_IMAGE_BYTES = 8 * 1024 * 1024
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}

DEMO_OCR_TEXT = """RSa-Brief
Sendungsnummer: RR 1234 5678 901 AT
Empfänger: Erika Mustermann
Adresse: Musterstraße 12
PLZ/Ort: 4020 Linz
"""


class OCRProcessingError(ValueError):
    pass


@dataclass(frozen=True)
class OCRResult:
    text: str
    engine: str


def _prepare_image(uploaded_file) -> Image.Image:
    if uploaded_file.size > MAX_IMAGE_BYTES:
        raise OCRProcessingError("Das Bild ist größer als 8 MB.")
    try:
        image = Image.open(uploaded_file)
        image.verify()
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
    except (UnidentifiedImageError, OSError) as exc:
        raise OCRProcessingError("Ungültige oder beschädigte Bilddatei.") from exc

    if image.format not in ALLOWED_FORMATS:
        raise OCRProcessingError("Unterstützt werden JPEG, PNG und WebP.")

    image = ImageOps.exif_transpose(image).convert("L")
    image.thumbnail((1800, 1800))
    image = ImageOps.autocontrast(image)
    return ImageEnhance.Sharpness(image).enhance(1.5)


def extract_text(uploaded_file) -> OCRResult:
    image = _prepare_image(uploaded_file)
    try:
        import pytesseract

        try:
            text = pytesseract.image_to_string(
                image,
                lang=settings.OCR_LANGUAGES,
                config="--psm 6",
                timeout=settings.OCR_TIMEOUT_SECONDS,
            )
        except pytesseract.TesseractError:
            text = pytesseract.image_to_string(
                image,
                lang="eng",
                config="--psm 6",
                timeout=settings.OCR_TIMEOUT_SECONDS,
            )
    except (ImportError, RuntimeError, OSError) as exc:
        raise OCRProcessingError(
            "OCR ist lokal nicht verfügbar. Bitte Demo-Modus verwenden."
        ) from exc

    if not text.strip():
        raise OCRProcessingError(
            "Kein Text erkannt. Bitte näher fotografieren und erneut versuchen."
        )
    return OCRResult(text=text.strip(), engine="tesseract-5")
