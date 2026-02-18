from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, Optional

from main.models import PriceRule


def _rule_applies(rule: "PriceRule", day: date) -> bool:
    if rule.kind == PriceRule.Kind.PERIOD:
        return rule.date_from <= day <= rule.date_to
    if rule.kind == PriceRule.Kind.WEEKEND:
        return day.weekday() >= 5
    if rule.kind == PriceRule.Kind.WEEKDAY:
        return day.weekday() < 5
    return False


def get_prices_for_range(
    accommodation,
    date_from: date,
    date_to: date,
) -> Dict[date, Optional[Decimal]]:
    rules = list(
        PriceRule.objects.filter(
            accommodation=accommodation,
            is_active=True,
        )
    )

    result: Dict[date, Optional[Decimal]] = {}
    day = date_from
    while day < date_to:
        best: Optional[PriceRule] = None
        for rule in rules:
            if not _rule_applies(rule, day):
                continue
            if best is None or rule.priority > best.priority:
                best = rule
        result[day] = best.price_per_night if best is not None else None
        day += timedelta(days=1)

    return result


def calculate_total_price(
    accommodation,
    check_in: date,
    check_out: date,
) -> Decimal:
    prices = get_prices_for_range(accommodation, check_in, check_out)
    total = Decimal("0.00")
    for day, price in prices.items():
        if price is None:
            raise ValueError(
                f"No active price rule found for {day} "
                f"(accommodation: {accommodation})."
            )
        total += price
    return total
