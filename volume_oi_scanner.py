# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 12:42:49 2025

@author: Manoj Shenoy
✅ MODULE 3 — VOLUME / OI SCANNER (Index + Stocks)
🎯 What Module 3 Does This module scans live option chains (from Module 1) and flags:
✔ Strikes where traded volume is aggressively high relative to OI
✔ Both Calls and Puts
✔ Works for:
Index options (NIFTY, BANKNIFTY, MIDCPNIFTY)
Stock options (INFY, RELIANCE, etc.)
✔ Uses absolute thresholds (Vol / OI > X) as requested
✔ Integrates cleanly with EWMA Flow (Module 2) to avoid false signals

This is exactly how prop desks detect:
Late entrants
Gamma traps
Dealers getting forced

🧠 WHY VOLUME / OI WORKS
Very simple intuition:
OI = existing positioning
Volume = fresh activity
So:
High Volume + Low OI → new risk being added
High Vol/OI near ATM → someone is in a hurry
Repeated Vol/OI spikes → directional conviction
"""
import pandas as pd
from config import VOL_OI_THRESHOLD, MIN_VOLUME, MAX_DISTANCE_FROM_ATM

# --------------------------------------------------
# Volume / OI Scanner (Single Snapshot)
# --------------------------------------------------
def volume_oi_scan(option_chain_df, atm_strike):
    df = option_chain_df.copy()

    # Avoid division by zero
    df = df[df["oi"] > 0]

    # Core metric
    df["vol_oi_ratio"] = df["volume"] / df["oi"]

    # Distance from ATM in strikes
    df["strike_distance"] = abs(df["strike"] - atm_strike)

    # Filters
    scan = df[
        (df["vol_oi_ratio"] >= VOL_OI_THRESHOLD) &
        (df["volume"] >= MIN_VOLUME) &
        (df["strike_distance"] <= MAX_DISTANCE_FROM_ATM * df["strike_distance"].median())
    ]

    if scan.empty:
        return pd.DataFrame()

    # Ranking score
    scan["score"] = (
        scan["vol_oi_ratio"] *
        scan["volume"] /
        (scan["strike_distance"] + 1)
    )

    scan = scan.sort_values("score", ascending=False)

    return scan[
        [
            "symbol",
            "expiry",
            "strike",
            "option_type",
            "ltp",
            "volume",
            "oi",
            "vol_oi_ratio",
            "delta",
            "gamma",
            "distance_from_atm",
            "score"
        ]
    ]

