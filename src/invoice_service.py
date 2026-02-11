    def _calculate_shipping(self, country: str, subtotal: float) -> float:
        shipping_rules = {
            "TH": (500, 60),
            "JP": (4000, 600),
            "US": None
        }

        if country == "US":
            if subtotal < 100:
                return 15
            if subtotal < 300:
                return 8
            return 0

        threshold = shipping_rules.get(country, (200, 25))
        limit, fee = threshold
        return fee if subtotal < limit else 0


    def _calculate_discount(self, inv: Invoice, subtotal: float, warnings: List[str]) -> float:
        discount = 0.0

        membership_rates = {
            "gold": 0.03,
            "platinum": 0.05
        }

        if inv.membership in membership_rates:
            discount += subtotal * membership_rates[inv.membership]
        elif subtotal > 3000:
            discount += 20

        if inv.coupon:
            code = inv.coupon.strip()
            rate = self._coupon_rate.get(code)
            if rate:
                discount += subtotal * rate
            else:
                warnings.append("Unknown coupon")

        return discount


    def _calculate_tax(self, country: str, taxable_amount: float) -> float:
        tax_rates = {
            "TH": 0.07,
            "JP": 0.10,
            "US": 0.08
        }

        rate = tax_rates.get(country, 0.05)
        return taxable_amount * rate
