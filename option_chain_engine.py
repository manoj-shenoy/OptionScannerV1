# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 11:59:55 2025

@author: Manoj Shenoy

✅ OUTPUT (EXACTLY WHAT YOU’LL GET)

A clean DataFrame like:

strike	type	ltp	oi	oi_change	volume	delta	gamma	vega	dist_ATM

This feeds directly into:

➡ Module 2: EWMA OI Flow
➡ Module 3: Volume/OI Scanner
➡ Module 4: Excel Dashboard

"""

import pandas as pd
from datetime import datetime
from SmartApi import SmartConnect

from auth import obj
from config import *
from instrument_loader import load_instrument_master
from utils import nearest_expiry, get_atm_strike

# --------------------------------------------------
# Fetch Spot Price
# --------------------------------------------------
def get_spot_price(symbol):
    if symbol == "NIFTY":
        exchange = "NSE"
        tradingsymbol = "NIFTY 50"
        token = "99926000"
    else:
        raise NotImplementedError("Add stock/index mapping")

    ltp = obj.ltpData(exchange, tradingsymbol, token)
    return float(ltp["data"]["ltp"])


# --------------------------------------------------
# Get Option Instruments
# --------------------------------------------------
def get_option_instruments(symbol):
    inst = load_instrument_master()

    df = inst[
        (inst["name"] == symbol) &
        (inst["instrumenttype"] == "OPTIDX" if symbol == "NIFTY" else inst["instrumenttype"] == "OPTSTK")
    ].copy()

    df["expiry"] = pd.to_datetime(df["expiry"]).dt.date
    return df


# --------------------------------------------------
# Build Option Chain
# --------------------------------------------------
def build_option_chain(symbol):
    spot = get_spot_price(symbol)
    strike_gap = OPTION_STRIKE_GAP.get(symbol, 50)

    atm = get_atm_strike(spot, strike_gap)

    options_df = get_option_instruments(symbol)

    expiry = nearest_expiry(options_df["expiry"].unique())
    options_df = options_df[options_df["expiry"] == expiry]

    strikes = range(
        atm - STRIKES_AROUND_ATM * strike_gap,
        atm + STRIKES_AROUND_ATM * strike_gap + strike_gap,
        strike_gap
    )

    options_df = options_df[options_df["strike"].isin(strikes)]

    rows = []

    for _, row in options_df.iterrows():
        md = obj.marketData(
            exchange="NFO",
            symboltoken=row["token"],
            mode="FULL"
        )

        greeks = obj.optionGreeks(
            exchange="NFO",
            tradingsymbol=row["symbol"]
        )

        rows.append({
            "symbol": symbol,
            "expiry": expiry,
            "strike": row["strike"],
            "option_type": row["symbol"][-2:],
            "ltp": md["data"]["ltp"],
            "oi": md["data"]["oi"],
            "oi_change": md["data"]["oiChange"],
            "volume": md["data"]["volume"],
            "delta": greeks["data"]["delta"],
            "gamma": greeks["data"]["gamma"],
            "vega": greeks["data"]["vega"],
            "distance_from_atm": abs(row["strike"] - atm)
        })

    chain_df = pd.DataFrame(rows)
    return chain_df, spot, atm, expiry
