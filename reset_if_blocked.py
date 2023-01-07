
from machine import WDT

class ResetIfBlocked:
    wdt = WDT(timeout=8000)  # enable it with a timeout of 2s
    wdt.feed()