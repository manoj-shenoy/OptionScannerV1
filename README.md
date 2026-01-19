# OptionScannerV1
Scans for opportunities in the Indian Stock Options as well as Index options space

1️⃣ How the system is designed to run (mentally)

Think of this as one continuously running engine, not 10 scripts.

The TRUE dependency chain is:
auth.py + config.py
        ↓
instrument_loader.py
        ↓
option_chain_engine.py   ← Module 1 (data source)
        ↓
ewma_flow_engine.py      ← Module 2
volume_oi_scanner.py    ← Module 3
trade_readiness_engine.py ← Module 5
        ↓
excel_writer.py + excel_dashboard.py ← Module 4


⚠️ Important

You should NOT run individual modules manually.

live_running.py (or a cleaned-up version of it) is the only script you run.

2️⃣ What each module already does (quick confirmation)
✅ Module 1 – option_chain_engine.py

Builds live option chain using Angel SmartAPI

Pulls:

LTP

OI + OI change

Volume

Greeks

Distance from ATM

Outputs:

chain_df, spot, atm, expiry


This is the single source of truth.

✅ Module 2 – ewma_flow_engine.py

Computes:

Net OI

ATM-weighted OI

Delta-weighted OI

Maintains stateful EWMA

Exposes:

engine.update(snapshot)


Perfect for live use.

✅ Module 3 – volume_oi_scanner.py

Scans option chain snapshot

Uses absolute Vol/OI thresholds

Works for:

Indices

Stocks

Returns ranked signals

Correctly isolated.

✅ Module 5 – trade_readiness_engine.py

Converts structure + trigger into TRS (0–100)

Penalizes:

Regime flips

Late-day trading

No overlap with other modules

Well designed.

✅ Module 4 – Excel (excel_dashboard.py, excel_writer.py)

Pure presentation layer

No analytics (this is good)

Updates:

Individual index sheets

STOCKS_GROUPED

ALERT_SUMMARY

Exactly how institutional dashboards work.

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
