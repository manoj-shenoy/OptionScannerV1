# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 12:55:30 2025
@author: Manoj Shenoy

Module 4 — EXCEL LIVE DASHBOARD
Sheet 1: Option Chain (filtered)
Sheet 2: EWMA Flows
Sheet 3: Volume/OI Alerts (highlighted)
Conditional formatting for:
Vol/OI > threshold, Delta alignment, ATM proximity

🚀 MODULE 4: LIVE EXCEL DASHBOARD (xlwings)
5–15 sec refresh
No RTD instability
Clean tables
Visual alerts (no WhatsApp yet, as decided)

✅ MODULE 4 — LIVE EXCEL ALERT DASHBOARD (xlwings)
🎯 OBJECTIVE (Restated Precisely)

You want Excel to behave like a radar + siren, not a report.

So the dashboard must:

Continuously update

Visually scream when something matters

Require zero clicking

Scale across indices + stocks

🧠 FINAL DASHBOARD DESIGN (LOCKED)
📊 Sheet Structure
1️⃣ ALERT_SUMMARY ✅ (MOST IMPORTANT)

One-glance market state

Underlying	Type	EWMA ATM Flow	EWMA Delta Flow	Regime	Vol/OI Spike	Direction	Last Update
NIFTY	Index	+82k	+41k	Bullish	YES	PUT	11:21:05
BANKNIFTY	Index	-55k	-39k	Bearish	YES	CALL	11:21:04
STOCKS	Grouped	+120k	+18k	Mixed	YES	MIXED	11:21:02

👉 This is where your eyes live.

2️⃣ Index Sheets (One per Index)

NIFTY

BANKNIFTY

MIDCPNIFTY

Each sheet contains:

EWMA metrics (top)

Volume/OI table (center)

Option chain snapshot (bottom, trimmed)

3️⃣ STOCKS_GROUPED ✅ (Your request)

Instead of 1 sheet per stock:

Symbol	Strike	Type	Vol/OI	Volume	OI	Delta	Signal
INFY	1600	PE	4.2	180k	42k	-0.32	PUT
RELIANCE	2500	CE	3.9	150k	38k	0.41	CALL

This avoids:

30+ sheets

Cognitive overload

Excel lag

🧱 TECH STACK DECISION (WHY xlwings)

We use xlwings, not RTD:

✔ RTD is unstable for frequent updates
✔ xlwings gives:

Full formatting control

Deterministic refresh

Python-side intelligence

Easy alert hooks later

This is the correct choice.

📁 MODULE 4 FILE STRUCTURE
dashboard/
│
├── excel_dashboard.py        <-- main engine
├── excel_writer.py           <-- formatting + writing
├── dashboard_config.py
│
├── option_chain_engine.py    <-- Module 1
├── ewma_flow_engine.py       <-- Module 2
├── volume_oi_scanner.py      <-- Module 3
│
├── auth.py
├── config.py

"""

