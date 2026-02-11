from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple


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
    coupon: Optional[str]
    items: List[LineItem]


class InvoiceService:
    def __init__(self) -> None:
        self._coupon_rate: Dict[str, float] = {
            "WELCOME10": 0.10,
            "VIP20": 0.20,
            "STUDENT5": 0.05,
        }

    # -------------------------
    # Validation
    # -------------------------
    def _validate(self, inv: Invoice) -> List[str]:
        problems: List[str] = []

        if inv is None:
            return ["Invoice is missing"]

        if not inv.invoice_id:
            problems.append("Missing invoice_id")

        if not inv.customer_id:
            problems.append("Missing customer_id")

        if not inv.items:
            problems.append("Invoice must contain items")

        for it in inv.items:
            if not it.sku:
                problems.append("Item sku is missing")
            if it.qty <= 0:
                problems.append(f"Invalid qty for {it.sku}")
            if it.unit_price < 0:
                problems.append(f"Invalid price for {it.sku}")
            if it.category not in ("book", "food", "electronics", "other"):
                problems.append(f"Unknown category for {it.sku}")

        return problems

    # -------------------------
    # Shipping
    # -------------------------
    def _calculate_shipping(self, country: str, subtotal: float) -> float:
        shipping_rules = {
            "TH": (500, 60),
            "JP": (4000, 600),
        }

        if country == "US":
            if subtotal < 100:
                return 15
            if subtotal < 300:
                return 8
            return 0

        limit, fee = shipping_rules.get(country, (200, 25))
        return fee if subtotal < limit else 0

    # -------------------------
    # Discount
    # -------------------------
    def _calculate_discount(
        self, inv: Invoice, subtotal: float, warnings: List[str]
    ) -> float:
        discount = 0.0

        membership_rates = {
            "gold": 0.03,
            "platinum": 0.05,
        }

        if inv.membership in membership_rates:
            discount += subtotal * membership_rates[inv.membership]
        elif subtotal > 3000:
            discount += 20

        if inv.coupon:
            code = inv.coupon.strip()
            if code in self._coupon_rate:
                discount += subtotal * self._coupon_rate[code]
            else:
                warnings.append("Unknown coupon")

        return discount

    # -------------------------
    # Tax
    # -------------------------
    def _calculate_tax(self, country: str, taxable_amount: float) -> float:
        tax_rates = {
            "TH": 0.07,
            "JP": 0.10,
            "US": 0.08,
        }

        rate = tax_rates.get(country, 0.05)
        return taxable_amount * rate

    # -------------------------
    # Public API
    # -------------------------
    def compute_total(self, inv: Invoice) -> Tuple[float, List[str]]:
        warnings: List[str] = []

        problems = self._validate(inv)
        if problems:
            raise ValueError("; ".join(problems))

        subtotal = 0.0
        fragile_fee = 0.0

        for it in inv.items:
            line = it.unit_price * it.qty
            subtotal += line
            if it.fragile:
                fragile_fee += 5.0 * it.qty

        shipping = self._calculate_shipping(inv.country, subtotal)
        discount = self._calculate_discount(inv, subtotal, warnings)
        tax = self._calculate_tax(inv.country, subtotal - discount)

        total = subtotal + shipping + fragile_fee + tax - discount
        total = max(total, 0)

        if subtotal > 10000 and inv.membership not in ("gold", "platinum"):
            warnings.append("Consider membership upgrade")

        return total, warnings
