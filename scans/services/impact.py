from dataclasses import dataclass


@dataclass(frozen=True)
class ImpactEstimate:
    seconds_saved_per_item: float
    hours_saved_per_year: float
    fte_days_saved_per_year: float


def calculate_impact(
    manual_seconds: float,
    smart_scan_seconds: float,
    items_per_day: int,
    workdays_per_year: int,
) -> ImpactEstimate:
    values = (manual_seconds, smart_scan_seconds, items_per_day, workdays_per_year)
    if any(value < 0 for value in values):
        raise ValueError("Impact inputs cannot be negative")

    seconds_saved = max(manual_seconds - smart_scan_seconds, 0)
    hours_saved = seconds_saved * items_per_day * workdays_per_year / 3600
    return ImpactEstimate(
        seconds_saved_per_item=round(seconds_saved, 1),
        hours_saved_per_year=round(hours_saved, 1),
        fte_days_saved_per_year=round(hours_saved / 8, 1),
    )
