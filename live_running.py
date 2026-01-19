# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 12:26:40 2025

@author: Manoj Shenoy

🧠 HOW TO INTERPRET THIS (VERY IMPORTANT)
📈 Bullish Structure
ATM-weighted OI ↑,Delta-weighted OI ↑ → Put writing / Call covering near ATM

📉 Bearish Structure
ATM-weighted OI ↑, Delta-weighted OI ↓ → Call writing / Put buying near ATM

⚠️ Choppy / Dangerous
net OI ↑,  ATM-weighted flat → Far OTM junk, no real conviction

🔌 HOW THIS FEEDS NEXT MODULES
Module 3 (Volume/OI Scanner)
Only alert strikes aligned with EWMA direction

Module 4 (Excel Dashboard)
One row showing:
EWMA ATM Flow
EWMA Delta Flow
Regime Label (Bull / Bear / Neutral)

Live Trading Use:
Short gamma only when flows stabilize
Avoid selling when EWMA flips sign intraday

🚀 NEXT: MODULE 3

Module 3 will build:

Volume/OI Scanner (Index + Stock options)
Unusual activity detection
Signal ranking
Excel alerts (highlight / conditional formatting)

"""

from option_chain_engine import build_option_chain
from ewma_flow_engine import EWMAFlowEngine, compute_flow_snapshot

engine = EWMAFlowEngine()

chain_df, spot, atm, expiry = build_option_chain("NIFTY")

snapshot = compute_flow_snapshot(chain_df, "NIFTY")
ewma_state = engine.update(snapshot)

print(ewma_state)

# SAMPLE OUTPUT

# {
#  'net_oi_change': 152000,
#  'atm_weighted_oi': 84250,
#  'delta_weighted_oi': -41230
# }

# LIVE USAGE MODULE 3 : VOLUME/OI SCANNER

from option_chain_engine import build_option_chain
from volume_oi_scanner import volume_oi_scan

chain_df, spot, atm, expiry = build_option_chain("NIFTY")

signals = volume_oi_scan(chain_df, atm)

print(signals)

#EXAMPLE OUTPUT
  # strike  type  vol/oi  volume   delta   score
  # 22650   CE    4.8     185000   0.42    9200
  # 22500   PE    3.6     140000  -0.38    7100

"""
🧠 HOW TO READ THESE SIGNALS FROM VOL/OI SCANNER (IMPORTANT)
🚀 Bullish Pressure
High Vol/OI on PUTS near ATM
Positive EWMA Delta Flow (Module 2)
→ Put writing / upside magnet

🔥 Bearish Pressure
High Vol/OI on CALLS near ATM
Negative EWMA Delta Flow
→ Call writing / downside pressure

⚠️ Trap / Reversal Risk
High Vol/OI far OTM
EWMA ATM Flow flat
→ Noise / punt / retail flow

🔗 INTEGRATION WITH MODULE 2 (CRITICAL)
In live trading, you never act on Module 3 alone.
Rule of thumb:

Volume/OI Signal	EWMA Flow	Action
Call spike	Bearish	Valid
Call spike	Bullish	Ignore
Put spike	Bullish	Valid
Put spike	Bearish	Ignore

This prevents:
False breakouts
Random weekly option noise

"""