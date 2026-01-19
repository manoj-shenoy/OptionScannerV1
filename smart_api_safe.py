# -*- coding: utf-8 -*-
"""
Created on Sat Jan  3 02:10:43 2026

@author: Manoj Shenoy
2️⃣ Stress-Test Result (What I Recommend)
✅ SAFE operating envelope

REFRESH_SECONDS = 12–15

Batch instruments

Detect throttling explicitly

Auto-reconnect session

We’ll enforce this in the runner only, not modules.

3️⃣ Add Graceful Reconnect (Production-Grade)

We’ll add three protections:

🛡️ A. Centralized API call wrapper

Detect:

Rate limit

Session expiry

Network hiccups

Retry with backoff

Re-auth if needed

🛡️ B. Heartbeat watchdog

If data stalls → reconnect

Prevent silent death

🛡️ C. Soft degradation

Skip one cycle instead of crashing

Preserve EWMA state

4️⃣ Minimal, Clean Enhancements (No New Logic)
🔹 Step 1: Add a SmartAPI Safe Wrapper

Create one small utility (this is infrastructure, not analytics):
"""
import time
from logzero import logger
from auth import obj
from SmartApi.smartExceptions import SmartAPIException

MAX_RETRIES = 3

def safe_call(fn, *args, **kwargs):
    for attempt in range(MAX_RETRIES):
        try:
            return fn(*args, **kwargs)
        except SmartAPIException as e:
            logger.warning(f"SmartAPI error: {e}")
            if "rate" in str(e).lower():
                time.sleep(2 + attempt)
            else:
                raise
        except Exception as e:
            logger.warning(f"Transient error: {e}")
            time.sleep(1 + attempt)
    return None

