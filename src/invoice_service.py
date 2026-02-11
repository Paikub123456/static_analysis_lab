    def compute_total(self, inv: Invoice) -> Tuple[float, List[str]]:
        warnings: List[str] = []
        problems = self._validate(inv)
        if problems:
            raise ValueError("; ".join(problems))

        subtotal = sum(it.unit_price * it.qty for it in inv.items)
        fragile_fee = sum(5.0 * it.qty for it in inv.items if it.fragile)

        shipping = self._calculate_shipping(inv.country, subtotal)
        discount = self._calculate_discount(inv, subtotal, warnings)
        tax = self._calculate_tax(inv.country, subtotal - discount)

        total = subtotal + shipping + fragile_fee + tax - discount

        if subtotal > 10000 and inv.membership not in ("gold", "platinum"):
            warnings.append("Consider membership upgrade")

        return max(total, 0), warnings
