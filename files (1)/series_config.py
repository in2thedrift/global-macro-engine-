"""
series_config.py
-----------------
Single place to add/remove the indicators tracked by the dashboard.

To add a new FRED series:
  1. Find its series ID at https://fred.stlouisfed.org (search, then look at the URL).
  2. Add an entry below with a human-readable label, the series id, a unit label,
     and whether it needs a YoY % transform (True for index/level series like CPI).

To add a new FX/market ticker, use any valid Yahoo Finance ticker symbol.
"""

GROWTH_AND_LABOR = {
    "US Real GDP Growth (QoQ, SAAR %)": {"id": "A191RL1Q225SBEA", "yoy": False, "unit": "%"},
    "US Unemployment Rate": {"id": "UNRATE", "yoy": False, "unit": "%"},
    "US Nonfarm Payrolls (level, thousands)": {"id": "PAYEMS", "yoy": False, "unit": "K jobs"},
    "US Retail Sales (YoY %)": {"id": "RSAFS", "yoy": True, "unit": "%"},
}

INFLATION = {
    "US CPI Inflation (YoY %)": {"id": "CPIAUCSL", "yoy": True, "unit": "%"},
    "US Core PCE Inflation (YoY %)": {"id": "PCEPILFE", "yoy": True, "unit": "%"},
    "Eurozone HICP Inflation (Index)": {"id": "CP0000EZ19M086NEST", "yoy": True, "unit": "%"},
    "US Producer Price Index (YoY %)": {"id": "PPIACO", "yoy": True, "unit": "%"},
}

RATES_AND_YIELDS = {
    "Fed Funds Rate": {"id": "FEDFUNDS", "yoy": False, "unit": "%"},
    "US 2Y Treasury Yield": {"id": "DGS2", "yoy": False, "unit": "%"},
    "US 10Y Treasury Yield": {"id": "DGS10", "yoy": False, "unit": "%"},
    "US 10Y-2Y Yield Spread (Recession Signal)": {"id": "T10Y2Y", "yoy": False, "unit": "%"},
    "US 30Y Treasury Yield": {"id": "DGS30", "yoy": False, "unit": "%"},
}

FX_AND_MARKETS = {
    "EUR/USD": "EURUSD=X",
    "USD/JPY": "JPY=X",
    "GBP/USD": "GBPUSD=X",
    "USD/CNY": "CNY=X",
    "US Dollar Index (DXY)": "DX-Y.NYB",
    "Gold (USD/oz)": "GC=F",
    "WTI Crude Oil": "CL=F",
}

ALL_FRED_SECTIONS = {
    "Growth & Labor": GROWTH_AND_LABOR,
    "Inflation": INFLATION,
    "Rates & Yields": RATES_AND_YIELDS,
}
