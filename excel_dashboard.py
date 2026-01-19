# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 14:14:28 2025
@author: Manoj Shenoy

🚨 CONDITIONAL FORMATTING (ALERT LOGIC)
ALERT SUMMARY
Regime = Bullish → Green
Regime = Bearish → Red
Vol/OI Spike = YES → Yellow background
Sheet tab color changes if signal active
(Handled once, manually, in Excel — best practice)
"""

import time
import xlwings as xw

from option_chain_engine import build_option_chain
from ewma_flow_engine import EWMAFlowEngine, compute_flow_snapshot
from volume_oi_scanner import volume_oi_scan
from dashboard_config import *
from excel_writer import *

engine = EWMAFlowEngine()

wb = xw.Book("OptionsDashboard.xlsx")

summary = wb.sheets["ALERT_SUMMARY"]

while True:
    summary_rows = []

    # ---- INDICES ----
    for symbol in INDEX_UNIVERSE:
        chain, spot, atm, expiry = build_option_chain(symbol)

        snapshot = compute_flow_snapshot(chain, symbol)
        ewma = engine.update(snapshot)

        regime = classify_regime(ewma)

        vol_signals = volume_oi_scan(chain, atm)
        vol_flag = "YES" if not vol_signals.empty else "NO"

        summary_rows.append([
            symbol, "Index",
            ewma["atm_weighted_oi"],
            ewma["delta_weighted_oi"],
            regime,
            vol_flag,
            "PUT" if ewma["delta_weighted_oi"] > 0 else "CALL",
            time.strftime("%H:%M:%S")
        ])

        sheet = wb.sheets[symbol]
        write_df(sheet, "A5", vol_signals)
        write_value(sheet, "B2", regime)

    # ---- STOCKS GROUPED ----
    stock_alerts = []

    for stock in STOCK_UNIVERSE:
        chain, spot, atm, expiry = build_option_chain(stock)
        vol_signals = volume_oi_scan(chain, atm)

        if not vol_signals.empty:
            vol_signals["Underlying"] = stock
            stock_alerts.append(vol_signals)

    if stock_alerts:
        stock_df = pd.concat(stock_alerts)
        write_df(wb.sheets["STOCKS_GROUPED"], "A5", stock_df)

        summary_rows.append([
            "STOCKS", "Grouped",
            "", "",
            "Mixed",
            "YES",
            "MIXED",
            time.strftime("%H:%M:%S")
        ])

    summary_df = pd.DataFrame(summary_rows,
        columns=["Underlying","Type","EWMA_ATM","EWMA_Delta",
                 "Regime","VolOI","Direction","Time"])

    write_df(summary, "A2", summary_df)

    time.sleep(REFRESH_SECONDS)


"""
🚀 WHAT COMES NEXT (OPTIONAL BUT POWERFUL)
Module 5 (Optional)

Auto-hedge suggestions

Gamma regime filter

“Do not trade” zones

Module 6 (Later)

Streamlit Web Dashboard

Cloud deployment

Multi-user alerting

Final check before I proceed further:

Do you want audible Excel alerts (beep / popup) when:

EWMA regime flips?

Vol/OI spike appears near ATM?
"""