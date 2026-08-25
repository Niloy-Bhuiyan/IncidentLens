"""Adapter contract for the Stripe-like payment gateway."""

SUPPORTED_CURRENCIES = {"USD", "EUR", "GBP", "BDT"}


def create_charge(amount_minor: int, currency: str, trace_id: str) -> dict:
    if currency not in SUPPORTED_CURRENCIES:
        raise ValueError(
            f"invalid_currency_format currency={currency} trace_id={trace_id}"
        )
    return {"status": "accepted", "amount_minor": amount_minor, "currency": currency}

