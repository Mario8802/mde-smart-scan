import re
from dataclasses import dataclass

from scans.models import ScanRecord


TRACKING_LABEL = re.compile(
    r"(?:SENDUNGSNUMMER|SENDUNGS-NR\.?|BARCODE|IDENTCODE|ITEM\s*ID)\s*[:#-]?\s*"
    r"([A-Z]{0,2}[\d\s-]{8,24}[A-Z]{0,2})",
    re.IGNORECASE,
)
TRACKING_FALLBACK = re.compile(r"\b(?:[A-Z]{2})?[0-9][0-9\s-]{7,22}(?:AT)?\b")
POSTAL_CITY = re.compile(r"\b(\d{4})\s+([A-ZÄÖÜ][A-ZÄÖÜa-zäöüß .'-]{1,60})\b")
LABELED_LINE = re.compile(
    r"^(EMPFÄNGER|EMPFAENGER|RECIPIENT|NAME|ADRESSE|ANSCHRIFT|STRASSE|STRAßE|PLZ/ORT)\s*:\s*(.+)$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ExtractedShipment:
    tracking_number: str
    item_type: str
    recipient_name: str
    street: str
    postal_code: str
    city: str
    confidence: float


def _clean_tracking(value: str) -> str:
    return re.sub(r"[\s-]+", "", value).upper()


def _item_type(text: str) -> str:
    upper = text.upper()
    if re.search(r"\bRSA\b|RSa-Brief", text, re.IGNORECASE):
        return ScanRecord.ItemType.RSA
    if re.search(r"\bRSB\b|RSb-Brief", text, re.IGNORECASE):
        return ScanRecord.ItemType.RSB
    if "EINSCHREIBEN" in upper or "REGISTERED" in upper:
        return ScanRecord.ItemType.REGISTERED
    return ScanRecord.ItemType.UNKNOWN


def extract_shipment(text: str) -> ExtractedShipment:
    normalized = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    lines = normalized.splitlines()

    tracking_match = TRACKING_LABEL.search(normalized) or TRACKING_FALLBACK.search(normalized)
    tracking = _clean_tracking(tracking_match.group(1) if tracking_match and tracking_match.lastindex else tracking_match.group(0)) if tracking_match else ""

    labeled: dict[str, str] = {}
    for line in lines:
        match = LABELED_LINE.match(line)
        if match:
            labeled[match.group(1).upper()] = match.group(2).strip()

    recipient = next(
        (labeled[key] for key in ("EMPFÄNGER", "EMPFAENGER", "RECIPIENT", "NAME") if key in labeled),
        "",
    )
    street = next(
        (labeled[key] for key in ("ADRESSE", "ANSCHRIFT", "STRASSE", "STRAßE") if key in labeled),
        "",
    )
    postal_code = ""
    city = ""

    postal_match = POSTAL_CITY.search(labeled.get("PLZ/ORT", "")) or POSTAL_CITY.search(normalized)
    if postal_match:
        postal_code, city = postal_match.group(1), postal_match.group(2).strip()

        # Fallback for standard address blocks: name, street, postal code + city.
        if not recipient or not street:
            postal_index = next(
                (index for index, line in enumerate(lines) if POSTAL_CITY.search(line)), None
            )
            if postal_index is not None:
                if not street and postal_index >= 1:
                    candidate = lines[postal_index - 1]
                    if not LABELED_LINE.match(candidate):
                        street = candidate
                if not recipient and postal_index >= 2:
                    candidate = lines[postal_index - 2]
                    if not LABELED_LINE.match(candidate):
                        recipient = candidate

    item_type = _item_type(normalized)
    checks = [tracking, item_type != ScanRecord.ItemType.UNKNOWN, recipient, street, postal_code, city]
    confidence = round(sum(bool(value) for value in checks) / len(checks), 3)

    return ExtractedShipment(
        tracking_number=tracking,
        item_type=item_type,
        recipient_name=recipient,
        street=street,
        postal_code=postal_code,
        city=city,
        confidence=confidence,
    )
