# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 11:59:11 2025

@author: Manoj Shenoy
"""

import numpy as np
from datetime import datetime

def nearest_expiry(expiry_list):
    today = datetime.today().date()
    expiry_dates = sorted(expiry_list)
    for e in expiry_dates:
        if e >= today:
            return e
    return expiry_dates[-1]

def get_atm_strike(spot, strike_gap):
    return int(round(spot / strike_gap) * strike_gap)
