from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class LineItem:
    sku: str
    category: str
    unit_price: float
    qty: int
    fragile: bool = False


@dataclass
class Invoice:
    invoice_id: str
    customer_id: str
    country: str
    membership: str
    coupon: str | None
    items: List[LineItem]


class InvoiceService:

    def compute_total(self, invoice: Invoice) -> Tuple[float, List[str]]:
        if not invoice.invoice_id or not invoice.customer_id:
            raise ValueError("Invalid invoice")

        if not invoice.items:
            raise ValueError("Invoice must contain items")

        subtotal = 0
        warnings = []

        for item in invoice.items:
            if item.qty <= 0:
                raise ValueError("Invalid quantity")
            subtotal += item.unit_price * item.qty

        tax_rate = self._get_tax(invoice.country)
        subtotal *= (1 + tax_rate)

        subtotal = self._apply_membership(subtotal, invoice.membership)
        subtotal, coupon_warning = self._apply_coupon(subtotal, invoice.coupon)

        if coupon_warning:
            warnings.append(coupon_warning)

        if subtotal > 10000:
            warnings.append("Consider membership upgrade")

        return round(subtotal, 2), warnings

    def _get_tax(self, country: str) -> float:
        return {
            "TH": 0.07,
            "JP": 0.10,
            "US": 0.08
        }.get(country, 0.05)

    def _apply_membership(self, subtotal: float, membership: str) -> float:
        discounts = {
            "gold": 0.10,
            "platinum": 0.20
        }
        return subtotal * (1 - discounts.get(membership, 0))

    def _apply_coupon(self, subtotal: float, coupon: str | None):
        if coupon == "WELCOME10":
            return subtotal * 0.9, None
        elif coupon is None:
            return subtotal, None
        else:
            return subtotal, "Unknown coupon"
