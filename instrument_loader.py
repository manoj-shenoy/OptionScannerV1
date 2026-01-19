# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 11:58:38 2025

@author: Manoj Shenoy
"""

import pandas as pd
import requests
from functools import lru_cache

ANGEL_INSTRUMENT_URL = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"

@lru_cache(maxsize=1)
def load_instrument_master():
    print("Loading Angel Instrument Master...")
    data = requests.get(ANGEL_INSTRUMENT_URL).json()
    df = pd.DataFrame(data)
    return df
