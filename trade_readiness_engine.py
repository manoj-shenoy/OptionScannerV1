# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 20:44:51 2025

@author: Manoj Shenoy

📊 HOW THIS SHOWS UP IN EXCEL (Module 4 Extension)
In ALERT_SUMMARY
Underlying	  Regime	Vol/OI	TRS	  Action
NIFTY	      Bullish	YES	    82	  AGGRESSIVEI 
BANKNIFTY	 Bearish	NO	    38	  SMALL
STOCKS	      Mixed	   YES	    61	  NORMAL

Conditional Formatting
TRS > 80 → Dark Green
TRS 60–80 → Light Green
TRS < 40 → Grey / Red
"""
from datetime import datetime

class TradeReadinessEngine:
    def __init__(self):
        self.last_regime = None
        self.flip_count = 0

    def compute_trs(self, ewma_state, vol_signal, timestamp):
        score = 0

        # Structural alignment (40)
        if ewma_state["atm_weighted_oi"] > 0:
            score += 20
        if ewma_state["atm_weighted_oi"] * ewma_state["delta_weighted_oi"] > 0:
            score += 20

        # Trigger quality (30)
        if vol_signal == "VALID":
            score += 30

        # Regime stability (20)
        regime = (
            "BULL" if ewma_state["delta_weighted_oi"] > 0
            else "BEAR" if ewma_state["delta_weighted_oi"] < 0
            else "NEUTRAL"
        )

        if self.last_regime and regime != self.last_regime:
            self.flip_count += 1
            score -= min(20, self.flip_count * 5)
        else:
            self.flip_count = max(0, self.flip_count - 1)

        self.last_regime = regime

        # Time filter (10)
        h, m = timestamp.hour, timestamp.minute
        if h == 9 and m < 30:
            score -= 10
        if h >= 15:
            score -= 10

        return max(0, min(100, score))
