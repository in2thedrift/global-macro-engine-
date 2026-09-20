# Global Macro Engine

A Streamlit dashboard for tracking global macro indicators — growth, inflation,
rates/yields, and FX — built entirely on free, no-signup data sources:

- **FRED** (`fredgraph.csv` endpoint) — no API key required
- **Yahoo Finance** (via `yfinance`) — no API key required

## Features

- **Overview** — headline metrics + USD majors snapshot
- **Growth & Labor**, **Inflation**, **Rates & Yields**, **FX & Markets** — per-category charts
- **Compare** — overlay any combination of series on one rebased (start = 100) chart
- Sidebar date range filter, 1hr data caching, graceful error handling per chart

## Project structure

```
global-macro-engine/
├── app.py                     # main Streamlit app / page router
├── utils/
│   ├── data_fetch.py          # FRED + FX data fetching & transforms
│   └── series_config.py       # indicator list — edit this to add/remove series
├── requirements.txt
├── .streamlit/config.toml     # theme
└── .gitignore
```

## Run locally

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Deploy (Streamlit Community Cloud — free)

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub.
3. Click **New app**, pick this repo/branch, set the main file to `app.py`.
4. Deploy — no secrets/API keys are required for the default setup.

## Adding or changing indicators

Edit `utils/series_config.py`:

- **FRED series**: find the series ID from the URL on [fred.stlouisfed.org](https://fred.stlouisfed.org)
  (e.g. `https://fred.stlouisfed.org/series/CPIAUCSL` → id is `CPIAUCSL`), then add a dict entry:
  ```python
  "My Label": {"id": "SERIES_ID", "yoy": False, "unit": "%"},
  ```
  Set `"yoy": True` for level/index series (like a CPI index) that should be shown as
  year-over-year % change instead of a raw level.

- **FX / market tickers**: add any valid Yahoo Finance ticker to `FX_AND_MARKETS`,
  e.g. `"Silver": "SI=F"`.

## Notes & next steps

- The FRED CSV endpoint is public but unofficial-ish; for production use, consider
  switching to the official `fredapi` package with a free API key for more reliability
  and metadata (release dates, revisions, etc.).
- Caching is set to 1 hour (`ttl=3600` in `data_fetch.py`) — tune as needed.
- To turn this into a signal-generating "engine" (e.g. regime detection, z-scores,
  or a macro-based asset allocation view), the `Compare` tab's rebased-series pattern
  is a good starting point to build on.

## License

MIT — use freely.
