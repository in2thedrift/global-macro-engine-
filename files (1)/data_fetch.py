"""
data_fetch.py
--------------
Helpers for pulling macro data into the app.

FRED data is pulled via the public "fredgraph.csv" endpoint, which does NOT
require an API key or account. If you later want more series/metadata you
can switch to the official `fredapi` package + a free FRED API key.

FX / rates data is pulled via yfinance (also free, no key required).
"""

from __future__ import annotations

import pandas as pd
import streamlit as st
import yfinance as yf

FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"


@st.cache_data(ttl=3600, show_spinner=False)
def get_fred_series(series_id: str) -> pd.DataFrame:
    """
    Fetch a single FRED series as a tidy DataFrame with columns [date, value].
    No API key required.
    """
    url = f"{FRED_CSV_URL}?id={series_id}"
    try:
        df = pd.read_csv(url)
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"Could not fetch FRED series '{series_id}': {e}") from e

    if df.shape[1] != 2:
        raise RuntimeError(f"Unexpected FRED response shape for '{series_id}'")

    df.columns = ["date", "value"]
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["date", "value"]).reset_index(drop=True)
    return df


def to_yoy_pct(df: pd.DataFrame, periods_per_year: int = 12) -> pd.DataFrame:
    """Convert a level series (e.g. CPI index) to a year-over-year % change series."""
    out = df.copy()
    out["value"] = out["value"].pct_change(periods_per_year) * 100
    return out.dropna(subset=["value"]).reset_index(drop=True)


@st.cache_data(ttl=3600, show_spinner=False)
def get_fx_series(ticker: str, period: str = "5y") -> pd.DataFrame:
    """
    Fetch daily close prices for an FX pair / index from Yahoo Finance.
    Example tickers: 'EURUSD=X', 'JPY=X', 'DX-Y.NYB'
    """
    try:
        data = yf.Ticker(ticker).history(period=period)
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"Could not fetch FX series '{ticker}': {e}") from e

    if data.empty:
        raise RuntimeError(f"No data returned for ticker '{ticker}'")

    data = data.reset_index()[["Date", "Close"]]
    data.columns = ["date", "value"]
    data["date"] = pd.to_datetime(data["date"]).dt.tz_localize(None)
    return data


def filter_date_range(df: pd.DataFrame, start, end) -> pd.DataFrame:
    """Filter a tidy [date, value] DataFrame to a date range (inclusive)."""
    mask = (df["date"] >= pd.Timestamp(start)) & (df["date"] <= pd.Timestamp(end))
    return df.loc[mask].reset_index(drop=True)


def normalize_to_100(df: pd.DataFrame) -> pd.DataFrame:
    """Rebase a series so its first value in the frame equals 100 (for overlay comparisons)."""
    out = df.copy()
    base = out["value"].iloc[0]
    if base:
        out["value"] = out["value"] / base * 100
    return out
