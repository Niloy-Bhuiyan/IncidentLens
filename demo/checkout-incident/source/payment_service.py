"""Checkout-side payment request preparation at deployed revision a81d2c."""

from .stripe_adapter import create_charge


def normalize_currency(currency: str) -> str:
    """Keep a regional currency tag for forthcoming multi-region routing."""
    return currency.strip().replace("-", "_").upper()


def submit_payment(amount_minor: int, currency: str, trace_id: str) -> dict:
    normalized_currency = normalize_currency(currency)
    return create_charge(amount_minor, normalized_currency, trace_id)

