"""
FRED API wrapper. Requires FRED_API_KEY in environment.
Free key: https://fred.stlouisfed.org/docs/api/api_key.html

Useful series IDs:
  CPIAUCSL   — CPI All Urban Consumers (monthly)
  PCEPILFE   — Core PCE Price Index (monthly, Fed's preferred inflation gauge)
  FEDFUNDS   — Federal Funds Effective Rate (monthly)
  GDPC1      — Real GDP, Chained 2017 Dollars (quarterly)
  UNRATE     — Unemployment Rate (monthly)
  PAYEMS     — Total Nonfarm Payroll Employment (monthly)
  T10Y2Y     — 10Y minus 2Y Treasury spread (daily)
  M2SL       — M2 Money Supply (monthly)
  AHETPI     — Avg Hourly Earnings, Total Private (monthly)
  USREC      — NBER Recession Indicator (monthly, 1=recession)
  CEU7000000001 — Leisure & Hospitality Employment (monthly)
  CEU6000000001 — Professional & Business Services Employment (monthly)
"""

import os
from typing import Optional

import pandas as pd
from dotenv import load_dotenv
from fredapi import Fred

load_dotenv()


def _client() -> Fred:
    key = os.getenv("FRED_API_KEY")
    if not key:
        raise RuntimeError(
            "FRED_API_KEY is not set. Add it to your .env file. "
            "Free key at https://fred.stlouisfed.org/docs/api/api_key.html"
        )
    return Fred(api_key=key)


def fetch_series(
    series_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> dict:
    """
    Fetch a FRED time series.

    Returns:
        {
          "series_id": str,
          "data": [{"date": "YYYY-MM-DD", "value": float}, ...],
          "count": int,
          "latest": {"date": str, "value": float}   # convenience
        }
    On error returns {"error": str, "series_id": str}.
    """
    try:
        fred = _client()
        raw = fred.get_series(
            series_id,
            observation_start=start_date,
            observation_end=end_date,
        )
        records = [
            {"date": str(idx.date()), "value": round(float(v), 6)}
            for idx, v in raw.items()
            if not pd.isna(v)
        ]
        return {
            "series_id": series_id,
            "data": records,
            "count": len(records),
            "latest": records[-1] if records else None,
        }
    except Exception as exc:
        return {"error": str(exc), "series_id": series_id}


def get_series_info(series_id: str) -> dict:
    """
    Fetch metadata for a FRED series (title, frequency, units).

    Returns dict on success, {"error": str} on failure.
    """
    try:
        fred = _client()
        info = fred.get_series_info(series_id)
        return {
            "id": series_id,
            "title": info.get("title", ""),
            "frequency": info.get("frequency", ""),
            "units": info.get("units", ""),
            "seasonal_adjustment": info.get("seasonal_adjustment", ""),
            "notes": (info.get("notes") or "")[:400],
        }
    except Exception as exc:
        return {"error": str(exc), "series_id": series_id}
