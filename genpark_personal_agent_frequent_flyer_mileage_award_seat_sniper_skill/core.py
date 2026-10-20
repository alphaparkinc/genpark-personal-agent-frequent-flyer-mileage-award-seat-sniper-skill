# -*- coding: utf-8 -*-
"""Frequent Flyer Mileage Award Seat Value & Sniper for GenPark Personal Agent."""
import json
from typing import Dict, Any

class FrequentFlyerAwardSeatSniper:
    """Award flight valuation, Cents-Per-Point (CPP) arbiter, and credit card transfer routing."""

    @staticmethod
    def evaluate_award_redemption_value(airline_program: str, cash_ticket_price_usd: float, required_points: int, taxes_and_surcharges_usd: float, cabin_class: str = "business") -> Dict[str, Any]:
        """Compute net redemption value in Cents Per Point (CPP): (Cash - Taxes) / Points * 100."""
        net_cash_saved = cash_ticket_price_usd - taxes_and_surcharges_usd
        if required_points <= 0 or net_cash_saved <= 0:
            cpp = 0.0
        else:
            cpp = round((net_cash_saved / float(required_points)) * 100.0, 2)

        # Baseline point valuations
        is_great_deal = cpp >= (3.5 if cabin_class in ["business", "first"] else 1.8)

        return {
            "airline_program": airline_program,
            "cabin_class": cabin_class,
            "cents_per_point_cpp": cpp,
            "net_cash_savings_usd": round(net_cash_saved, 2),
            "redemption_verdict": "OUTSTANDING_SWEETSPOT" if cpp >= 4.0 else ("EXCELLENT_VALUE" if is_great_deal else ("AVERAGE" if cpp >= 1.3 else "POOR_USE_CASH")),
            "points_efficiency_commentary": f"Redeeming at {cpp}¢/pt yields high leverage over cash." if is_great_deal else f"CPP of {cpp}¢ is below optimal threshold. Consider cash booking."
        }

    @staticmethod
    def find_optimal_credit_card_transfer_partner(target_airline: str, needed_airline_miles: int, available_bank_points: Dict[str, int] = None) -> Dict[str, Any]:
        """Identify which bank currency transfers 1:1 or with promotional bonuses."""
        transfer_matrix = {
            "virgin_atlantic": {"partner": "Amex / Chase / Citi", "bonus_pct": 30},
            "air_france_klm": {"partner": "Bilt / Chase / Amex", "bonus_pct": 20},
            "singapore_krisflyer": {"partner": "All 4 Major Banks", "bonus_pct": 0},
            "british_airways_avios": {"partner": "Chase / Amex", "bonus_pct": 0},
            "united_mileageplus": {"partner": "Chase UR", "bonus_pct": 0}
        }
        
        info = transfer_matrix.get(target_airline.lower(), {"partner": "Chase / Amex", "bonus_pct": 0})
        bonus = info["bonus_pct"]
        discount_factor = 1.0 + (bonus / 100.0)
        bank_points_required = int(needed_airline_miles / discount_factor)

        return {
            "target_airline": target_airline,
            "needed_miles": needed_airline_miles,
            "active_transfer_bonus_pct": bonus,
            "discounted_bank_points_required": bank_points_required,
            "points_saved_via_bonus": needed_airline_miles - bank_points_required,
            "recommended_transfer_source": info["partner"],
            "booking_advisory": "Transfer points only after verifying award space is held or currently live."
        }
