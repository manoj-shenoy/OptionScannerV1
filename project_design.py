# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 11:57:41 2025

@author: Manoj Shenoy

✅ MODULE 1 — OPTION CHAIN ENGINE (LIVE, ANGEL SMARTAPI)
🎯 What this module does

For any underlying (Index or Stock), this module will:

✔ Identify the nearest tradable expiry
✔ Identify ATM strike dynamically
✔ Build a full option chain around ATM
✔ Fetch LTP, OI, Change in OI, Volume
✔ Fetch Greeks (Delta, Gamma, Vega)
✔ Return a clean Pandas DataFrame ready for:

EWMA flows (Module 2)

Volume/OI Scanner (Module 3)

Excel Dashboard (Module 4)

No NSE scraping. No hacks. Fully SmartAPI-native.

🧠 DESIGN PRINCIPLES
🔹 1. Instrument Master Driven

We load Angel’s instrument master once, cache it, and filter from there.

🔹 2. Expiry Detection (Automatic)

Index (NIFTY): picks nearest weekly

BankNifty / MidcapNifty / Stocks: picks nearest monthly

No hardcoded dates

🔹 3. ATM-Centric Chain

We only pull ± N strikes around ATM (configurable) to:

Save API calls

Improve speed

Stay within rate limits

📁 FILE STRUCTURE (STARTING)
options_engine/
│
├── option_chain_engine.py   <-- Module 1 (this)
├── instrument_loader.py
├── utils.py

"""

