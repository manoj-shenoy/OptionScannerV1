# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 12:17:02 2025

@author: Manoj Shenoy

🎯 What Module 2 Produces

From the live option chain (Module 1), this module computes:

1️⃣ EWMA of Net OI Change weighted by proximity to ATM
2️⃣ EWMA of Net OI Change weighted by Delta
3️⃣ A single composite flow score you can:

Display on Excel

Use as an intraday filter

Feed into option-selling logic
"""

import pandas as pd
import numpy as np
from config import EWMA_ALPHA, OPTION_STRIKE_GAP

# --------------------------------------------------
# ATM Proximity Weight
# --------------------------------------------------
def atm_weight(distance, symbol):
    gap = OPTION_STRIKE_GAP.get(symbol, 50)
    return np.exp(-distance / gap)


# --------------------------------------------------
# Compute Flow Metrics (Single Snapshot)
# --------------------------------------------------
def compute_flow_snapshot(option_chain_df, symbol):
    df = option_chain_df.copy()

    # ATM proximity weight
    df["atm_weight"] = df["distance_from_atm"].apply(
        lambda d: atm_weight(d, symbol)
    )

    # ATM-weighted OI change
    df["atm_weighted_oi"] = df["oi_change"] * df["atm_weight"]

    # Delta-weighted OI change
    df["delta_weighted_oi"] = df["oi_change"] * df["delta"]

    snapshot = {
        "net_oi_change": df["oi_change"].sum(),
        "atm_weighted_oi": df["atm_weighted_oi"].sum(),
        "delta_weighted_oi": df["delta_weighted_oi"].sum()
    }

    return snapshot


# --------------------------------------------------
# EWMA Engine (Stateful)
# --------------------------------------------------
class EWMAFlowEngine:
    def __init__(self, alpha=EWMA_ALPHA):
        self.alpha = alpha
        self.state = {
            "net_oi_change": 0.0,
            "atm_weighted_oi": 0.0,
            "delta_weighted_oi": 0.0
        }

    def update(self, snapshot):
        for key in self.state.keys():
            self.state[key] = (
                self.alpha * snapshot[key]
                + (1 - self.alpha) * self.state[key]
            )
        return self.state.copy()
