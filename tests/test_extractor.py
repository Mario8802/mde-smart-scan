from scans.models import ScanRecord
from scans.services.extractor import extract_shipment


def test_extracts_labeled_rsa_fields():
    result = extract_shipment(
        """RSa-Brief
        Sendungsnummer: RR 1234 5678 901 AT
        Empfänger: Erika Mustermann
        Adresse: Musterstraße 12
        PLZ/Ort: 4020 Linz
        """
    )

    assert result.tracking_number == "RR12345678901AT"
    assert result.item_type == ScanRecord.ItemType.RSA
    assert result.recipient_name == "Erika Mustermann"
    assert result.street == "Musterstraße 12"
    assert result.postal_code == "4020"
    assert result.city == "Linz"
    assert result.confidence == 1.0


def test_extracts_standard_address_block():
    result = extract_shipment(
        """EINSCHREIBEN
        Sendungs-Nr: EE 9876 5432 101 AT
        Max Beispiel
        Testweg 4
        4060 Leonding
        """
    )

    assert result.item_type == ScanRecord.ItemType.REGISTERED
    assert result.recipient_name == "Max Beispiel"
    assert result.street == "Testweg 4"
    assert result.city == "Leonding"


def test_returns_partial_result_for_unclear_text():
    result = extract_shipment("RSb Brief\nUnleserlicher Rest")

    assert result.item_type == ScanRecord.ItemType.RSB
    assert result.tracking_number == ""
    assert 0 < result.confidence < 0.5
