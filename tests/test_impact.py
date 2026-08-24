import pytest

from scans.services.impact import calculate_impact


def test_calculates_transparent_annual_estimate():
    result = calculate_impact(42, 12, 24, 220)

    assert result.seconds_saved_per_item == 30
    assert result.hours_saved_per_year == 44
    assert result.fte_days_saved_per_year == 5.5


def test_never_reports_negative_savings():
    result = calculate_impact(10, 20, 20, 200)
    assert result.hours_saved_per_year == 0


def test_rejects_negative_inputs():
    with pytest.raises(ValueError):
        calculate_impact(-1, 10, 20, 200)
