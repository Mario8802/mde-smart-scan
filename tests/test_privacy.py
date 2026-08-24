import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from scans.services.ocr import OCRProcessingError, _prepare_image


def test_rejects_non_image_upload():
    upload = SimpleUploadedFile("document.txt", b"not-an-image", content_type="text/plain")
    with pytest.raises(OCRProcessingError):
        _prepare_image(upload)


def test_accepts_small_png(tmp_path):
    path = tmp_path / "scan.png"
    Image.new("RGB", (120, 80), "white").save(path)
    with path.open("rb") as handle:
        upload = SimpleUploadedFile("scan.png", handle.read(), content_type="image/png")
    prepared = _prepare_image(upload)
    assert prepared.mode == "L"
