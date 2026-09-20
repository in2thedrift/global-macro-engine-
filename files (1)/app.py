"""
Global Macro Engine
--------------------
A Streamlit dashboard for tracking global macro indicators: growth, inflation,
rates/yields, and FX — sourced from free public APIs (FRED + Yahoo Finance).

Run locally:
    pip install -r requirements.txt
    streamlit run app.py
"""

from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.data_fetch import (
    filter_date_range,
    get_fred_series,
    get_fx_series,
    normalize_to_100,
    to_yoy_pct,
)
from utils.series_config import ALL_FRED_SECTIONS, FX_AND_MARKETS

st.set_page_config(page_title="Global Macro Engine", page_icon="🌍", layout="wide")

DEFAULT_START = date.today() - timedelta(days=365 * 10)
DEFAULT_END = date.today()


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
st.sidebar.title("🌍 Global Macro Engine")
section = st.sidebar.radio(
    "Section",
    ["Overview", "Growth & Labor", "Inflation", "Rates & Yields", "FX & Markets", "Compare"],
)

st.sidebar.markdown("---")
start_date = st.sidebar.date_input("Start date", DEFAULT_START)
end_date = st.sidebar.date_input("End date", DEFAULT_END)
st.sidebar.caption("Data: FRED (fredgraph.csv, no key needed) + Yahoo Finance via yfinance.")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def load_fred_indicator(cfg: dict) -> pd.DataFrame:
    df = get_fred_series(cfg["id"])
    if cfg.get("yoy"):
        df = to_yoy_pct(df)
    return df


def line_chart(df: pd.DataFrame, title: str, unit: str = "") -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["date"], y=df["value"], mode="lines", name=title))
    fig.update_layout(
        title=title,
        margin=dict(l=10, r=10, t=40, b=10),
        height=320,
        yaxis_title=unit,
        template="plotly_white",
    )
    return fig


def render_section(section_dict: dict):
    cols = st.columns(2)
    for i, (label, cfg) in enumerate(section_dict.items()):
        with cols[i % 2]:
            try:
                df = load_fred_indicator(cfg)
                df = filter_date_range(df, start_date, end_date)
                if df.empty:
                    st.warning(f"No data in range for {label}")
                    continue
                st.plotly_chart(line_chart(df, label, cfg["unit"]), use_container_width=True)
                latest = df.iloc[-1]
                st.caption(f"Latest: {latest['value']:.2f}{cfg['unit']} on {latest['date'].date()}")
            except Exception as e:  # noqa: BLE001
                st.error(f"Couldn't load {label}: {e}")


def render_fx_section():
    cols = st.columns(2)
    for i, (label, ticker) in enumerate(FX_AND_MARKETS.items()):
        with cols[i % 2]:
            try:
                df = get_fx_series(ticker, period="10y")
                df = filter_date_range(df, start_date, end_date)
                if df.empty:
                    st.warning(f"No data in range for {label}")
                    continue
                st.plotly_chart(line_chart(df, label), use_container_width=True)
                latest = df.iloc[-1]
                st.caption(f"Latest: {latest['value']:.4f} on {latest['date'].date()}")
            except Exception as e:  # noqa: BLE001
                st.error(f"Couldn't load {label}: {e}")


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
if section == "Overview":
    st.title("Global Macro Engine — Overview")
    st.write(
        "A live dashboard of growth, inflation, rates, and FX indicators. "
        "Use the sidebar to explore each category, or the **Compare** tab to "
        "overlay several series (e.g. yield spread vs. FX) on one chart."
    )
    headline_cfgs = {
        "US CPI Inflation (YoY %)": ("Inflation", "US CPI Inflation (YoY %)"),
        "US 10Y-2Y Yield Spread (Recession Signal)": ("Rates & Yields", "US 10Y-2Y Yield Spread (Recession Signal)"),
        "US Unemployment Rate": ("Growth & Labor", "US Unemployment Rate"),
    }
    cols = st.columns(len(headline_cfgs))
    for col, (label, (sec, key)) in zip(cols, headline_cfgs.items()):
        cfg = ALL_FRED_SECTIONS[sec][key]
        try:
            df = load_fred_indicator(cfg)
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            col.metric(label, f"{latest['value']:.2f}{cfg['unit']}", f"{latest['value'] - prev['value']:.2f}")
        except Exception as e:  # noqa: BLE001
            col.error(f"Error: {e}")

    st.markdown("---")
    st.subheader("USD Majors Snapshot")
    render_fx_section()

elif section in ALL_FRED_SECTIONS:
    st.title(section)
    render_section(ALL_FRED_SECTIONS[section])

elif section == "FX & Markets":
    st.title("FX & Markets")
    render_fx_section()

elif section == "Compare":
    st.title("Compare Series")
    st.write("Pick two or more series to overlay on a single, rebased (=100 at start) chart.")

    fred_options = {f"[FRED] {label}": ("fred", cfg) for sec in ALL_FRED_SECTIONS.values() for label, cfg in sec.items()}
    fx_options = {f"[FX] {label}": ("fx", ticker) for label, ticker in FX_AND_MARKETS.items()}
    all_options = {**fred_options, **fx_options}

    picks = st.multiselect(
        "Series to compare",
        list(all_options.keys()),
        default=list(all_options.keys())[:2],
    )

    if picks:
        fig = go.Figure()
        for pick in picks:
            kind, payload = all_options[pick]
            try:
                if kind == "fred":
                    df = load_fred_indicator(payload)
                else:
                    df = get_fx_series(payload, period="10y")
                df = filter_date_range(df, start_date, end_date)
                if df.empty:
                    continue
                df = normalize_to_100(df)
                fig.add_trace(go.Scatter(x=df["date"], y=df["value"], mode="lines", name=pick))
            except Exception as e:  # noqa: BLE001
                st.error(f"Couldn't load {pick}: {e}")
        fig.update_layout(
            title="Rebased Comparison (start = 100)",
            height=500,
            template="plotly_white",
            margin=dict(l=10, r=10, t=40, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select at least one series above.")
