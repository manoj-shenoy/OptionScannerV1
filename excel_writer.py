# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 14:13:07 2025

@author: Manoj Shenoy
"""

import xlwings as xw
from datetime import datetime

def write_df(sheet, start_cell, df):
    sheet.range(start_cell).options(index=False).value = df

def write_value(sheet, cell, value):
    sheet.range(cell).value = value

def write_timestamp(sheet, cell):
    sheet.range(cell).value = datetime.now().strftime("%H:%M:%S")
