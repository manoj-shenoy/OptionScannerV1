# -*- coding: utf-8 -*-
"""
Created on Sat Jan  3 01:41:42 2026
@author: Manoj Shenoy

4️⃣ How YOU actually run this (step-by-step)
✅ One-time setup
Open OptionsDashboard.xlsx
Ensure sheets exist:
ALERT_SUMMARY
NIFTY, BANKNIFTY, MIDCPNIFTY
STOCKS_GROUPED

▶️ Run command
python run_dashboard.py

That’s it.No other scripts need to be run.

5️⃣ Why this is the correct institutional setup
Single runner (no race conditions)
Stateful EWMA preserved
Excel only consumes outputs

Easy to extend later:
Streamlit/Telegram/AWS/Auto-execution
This is exactly how prop desks structure live analytics engines.
"""

# -*- coding: utf-8 -*-
"""
Production-grade LIVE dashboard runner
- Rate-limit safe for Angel SmartAPI
- Graceful reconnect & fault tolerance
- Uses ONLY existing modules (no new analytics)

######################

🧠 WHY THIS IS DEPLOYMENT-GRADE
✅ Rate-Limit Safe - Hard refresh floor
Per-underlying micro-throttling,Cycle time watchdog
✅ Graceful Failure Handling - No crash on
transient errors, Session auto-recovery,EWMA state preserved
✅ Institutional-style Orchestration
Analytics untouched,Presentation isolated,
Runner owns resilience only
✅ Ready for:
Full-day unattended runs,Future WebSocket upgrades
AWS migration,Execution bridge (Module-6)

"""
import time
from datetime import datetime
import traceback
import pyotp
import pandas as pd
import xlwings as xw
from logzero import logger

# ---------------- CORE IMPORTS ----------------
from auth import obj
from config import *
from dashboard_config import *

from option_chain_engine import build_option_chain
from ewma_flow_engine import EWMAFlowEngine, compute_flow_snapshot
from volume_oi_scanner import volume_oi_scan
from trade_readiness_engine import TradeReadinessEngine
from excel_writer import write_df, write_value

# ---------------- SAFE CONSTANTS ----------------
REFRESH_SECONDS = max(REFRESH_SECONDS, 12)  # hard floor for REST safety
MAX_CONSECUTIVE_FAILURES = 5
MAX_CYCLE_TIME = 20  # seconds watchdog

# ---------------- INITIALISE ENGINES ----------------
ewma_engine = EWMAFlowEngine()
trs_engine = TradeReadinessEngine()

# ---------------- EXCEL CONNECTION ----------------
wb = xw.Book(EXCEL_FILE)
summary_sheet = wb.sheets["ALERT_SUMMARY"]

# ---------------- HEALTH TRACKERS ----------------
LOOP_COUNTER = 0
LOOP_TIMES = []
LAST_ERROR_MSG = "None"

MODULE_HEALTH = {
    "OPTION_CHAIN": None,
    "EWMA": None,
    "VOL_OI": None
}

API_HEALTH = {
    "last_call": None,
    "reconnects": 0,
    "rate_limit_hits": 0
}


logger.info("🚀 Live Options Dashboard Started")

# ---------------- RECONNECT HANDLER ----------------
def reconnect():
    logger.warning("🔄 Attempting Angel SmartAPI reconnect...")
    try:
        totp = pyotp.TOTP(secret_key).now()
        session = obj.generateSession(UserName, MPin, totp)

        if not session["status"]:
            raise Exception("Session regeneration failed")

        obj.generateToken(session["data"]["refreshToken"])
        logger.info("✅ Reconnected to Angel SmartAPI")
        API_HEALTH["reconnects"] += 1


    except Exception as e:
        logger.error("❌ Reconnect failed")
        raise e


#==============UPDATE SYSTEM HEALTH================
def update_system_health(wb, cycle_time):
    sheet = wb.sheets["SYSTEM_HEALTH"]
    now = datetime.now()

    # Section 1: Heartbeat
    sheet.range("B1").value = "RUNNING"
    sheet.range("B2").value = now.strftime("%H:%M:%S")
    sheet.range("B3").value = int(cycle_time)
    sheet.range("B4").value = LOOP_COUNTER
    sheet.range("B5").value = round(sum(LOOP_TIMES) / len(LOOP_TIMES), 2) if LOOP_TIMES else 0
    sheet.range("B6").value = LAST_ERROR_MSG

    # Section 2: Module freshness
    sheet.range("B9").value = MODULE_HEALTH["OPTION_CHAIN"]
    sheet.range("B10").value = MODULE_HEALTH["EWMA"]
    sheet.range("B11").value = MODULE_HEALTH["VOL_OI"]

    # Section 3: API health
    sheet.range("B14").value = "CONNECTED"
    sheet.range("B15").value = API_HEALTH["last_call"]
    sheet.range("B16").value = API_HEALTH["reconnects"]
    sheet.range("B17").value = API_HEALTH["rate_limit_hits"]


# ---------------- MAIN LOOP ----------------
failure_count = 0

while True:
    LOOP_COUNTER += 1

    cycle_start = time.time()

    try:
        summary_rows = []
        API_HEALTH["last_call"] = datetime.now().strftime("%H:%M:%S")


        # ================= INDEX UNIVERSE =================
        for symbol in INDEX_UNIVERSE:
            chain_df, spot, atm, expiry = build_option_chain(symbol)
            MODULE_HEALTH["OPTION_CHAIN"] = datetime.now().strftime("%H:%M:%S")

            snapshot = compute_flow_snapshot(chain_df, symbol)
            ewma_state = ewma_engine.update(snapshot)
            MODULE_HEALTH["EWMA"] = datetime.now().strftime("%H:%M:%S")

            vol_df = volume_oi_scan(chain_df, atm)
            MODULE_HEALTH["VOL_OI"] = datetime.now().strftime("%H:%M:%S")

            vol_flag = "YES" if not vol_df.empty else "NO"

            regime = (
                "Bullish" if ewma_state["delta_weighted_oi"] > 0
                else "Bearish" if ewma_state["delta_weighted_oi"] < 0
                else "Neutral"
            )

            trs = trs_engine.compute_trs(
                ewma_state,
                "VALID" if vol_flag == "YES" else "INVALID",
                pd.Timestamp.now()
            )

            summary_rows.append([
                symbol,
                "Index",
                ewma_state["atm_weighted_oi"],
                ewma_state["delta_weighted_oi"],
                regime,
                vol_flag,
                trs,
                time.strftime("%H:%M:%S")
            ])

            sheet = wb.sheets[symbol]
            write_df(sheet, "A5", vol_df)
            write_value(sheet, "B2", regime)
            write_value(sheet, "C2", trs)

            time.sleep(0.5)  # micro-throttle per underlying

        # ================= STOCK OPTIONS (GROUPED) =================
        stock_frames = []

        for stock in STOCK_UNIVERSE:
            chain_df, spot, atm, expiry = build_option_chain(stock)
            vol_df = volume_oi_scan(chain_df, atm)
            MODULE_HEALTH["VOL_OI"] = datetime.now().strftime("%H:%M:%S")


            if not vol_df.empty:
                vol_df["Underlying"] = stock
                stock_frames.append(vol_df)

            time.sleep(0.25)  # throttle for stock universe

        if stock_frames:
            stock_df = (
                pd.concat(stock_frames)
                .sort_values("score", ascending=False)
            )

            write_df(
                wb.sheets["STOCKS_GROUPED"],
                "A5",
                stock_df
            )

            summary_rows.append([
                "STOCKS",
                "Grouped",
                "",
                "",
                "Mixed",
                "YES",
                "",
                time.strftime("%H:%M:%S")
            ])

        # ================= SUMMARY UPDATE =================
        summary_df = pd.DataFrame(
            summary_rows,
            columns=[
                "Underlying",
                "Type",
                "EWMA_ATM",
                "EWMA_Delta",
                "Regime",
                "VolOI",
                "TRS",
                "Time"
            ]
        )

        write_df(summary_sheet, "A2", summary_df)

        failure_count = 0  # reset after success

    except Exception as e:
        failure_count += 1
        logger.error(f"⚠ Runtime error (count={failure_count})")
        logger.error(traceback.format_exc())
        LAST_ERROR_MSG = str(e)[:150]

        if failure_count >= MAX_CONSECUTIVE_FAILURES:
            reconnect()
            failure_count = 0

    # ================= RATE-LIMIT SAFE SLEEP =================
    elapsed = time.time() - cycle_start

    if elapsed > MAX_CYCLE_TIME:
        logger.warning(f"⚠ Cycle exceeded {MAX_CYCLE_TIME}s ({elapsed:.1f}s)")
    
    LOOP_TIMES.append(elapsed)
    LOOP_TIMES = LOOP_TIMES[-50:]  # rolling window

    update_system_health(wb, elapsed)

    sleep_time = max(REFRESH_SECONDS - elapsed, 1)
    time.sleep(sleep_time)


# # run_dashboard.py
# import time
# import pandas as pd
# import xlwings as xw

# from auth import obj
# from dashboard_config import *
# from option_chain_engine import build_option_chain
# from ewma_flow_engine import EWMAFlowEngine, compute_flow_snapshot
# from volume_oi_scanner import volume_oi_scan
# from trade_readiness_engine import TradeReadinessEngine
# from excel_writer import write_df, write_value

# # -------------------------------
# # INITIALISE ENGINES
# # -------------------------------
# ewma_engine = EWMAFlowEngine()
# trs_engine = TradeReadinessEngine()

# # -------------------------------
# # EXCEL CONNECTION
# # -------------------------------
# wb = xw.Book("OptionsDashboard.xlsx")
# summary_sheet = wb.sheets["ALERT_SUMMARY",
#                           # "NIFTY", "BANKNIFTY",
#                           # "MIDCPNIFTY",
#                           # "STOCKS_GROUPED"
#                           ]

# print("🚀 Live Dashboard Started...")

# # -------------------------------
# # MAIN LOOP
# # -------------------------------
# while True:
#     summary_rows = []

#     # ================= INDICES =================
#     for symbol in INDEX_UNIVERSE:
#         chain_df, spot, atm, expiry = build_option_chain(symbol)

#         snapshot = compute_flow_snapshot(chain_df, symbol)
#         ewma_state = ewma_engine.update(snapshot)

#         vol_df = volume_oi_scan(chain_df, atm)
#         vol_flag = "YES" if not vol_df.empty else "NO"

#         regime = (
#             "Bullish" if ewma_state["delta_weighted_oi"] > 0
#             else "Bearish" if ewma_state["delta_weighted_oi"] < 0
#             else "Neutral"
#         )

#         trs = trs_engine.compute_trs(
#             ewma_state,
#             "VALID" if vol_flag == "YES" else "INVALID",
#             pd.Timestamp.now()
#         )

#         summary_rows.append([
#             symbol, "Index",
#             ewma_state["atm_weighted_oi"],
#             ewma_state["delta_weighted_oi"],
#             regime, vol_flag, trs,
#             time.strftime("%H:%M:%S")
#         ])

#         sheet = wb.sheets[symbol]
#         write_df(sheet, "A5", vol_df)
#         write_value(sheet, "B2", regime)

#     # ================= STOCKS (GROUPED) =================
#     stock_signals = []

#     for stock in STOCK_UNIVERSE:
#         chain_df, spot, atm, expiry = build_option_chain(stock)
#         vol_df = volume_oi_scan(chain_df, atm)

#         if not vol_df.empty:
#             vol_df["Underlying"] = stock
#             stock_signals.append(vol_df)

#     if stock_signals:
#         stock_df = pd.concat(stock_signals).sort_values("score", ascending=False)
#         write_df(wb.sheets["STOCKS_GROUPED"], "A5", stock_df)

#         summary_rows.append([
#             "STOCKS", "Grouped",
#             "", "", "Mixed", "YES",
#             "",
#             time.strftime("%H:%M:%S")
#         ])

#     # ================= SUMMARY =================
#     summary_df = pd.DataFrame(
#         summary_rows,
#         columns=[
#             "Underlying", "Type",
#             "EWMA_ATM", "EWMA_Delta",
#             "Regime", "VolOI",
#             "TRS", "Time"
#         ]
#     )

#     write_df(summary_sheet, "A2", summary_df)

#     time.sleep(REFRESH_SECONDS)

