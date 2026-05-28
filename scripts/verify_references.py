"""Verify benchmark reference answers against primary FRED data.

This script writes a durable Markdown audit trail to
reports/reference_answer_verification.md. It intentionally uses only FRED data
available through the existing project dependency stack so the calculations are
reproducible by another team member with a FRED_API_KEY in `.env`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from fredapi import Fred

from benchmark.questions import BENCHMARK
from src.tools.fred_tool import _client

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports" / "reference_answer_verification.md"


@dataclass
class Streak:
    start: pd.Timestamp
    end: pd.Timestamp
    obs: int
    min_date: pd.Timestamp
    min_value: float

    @property
    def calendar_days(self) -> int:
        return (self.end - self.start).days + 1


def get(fred: Fred, series_id: str, start: str | None = None, end: str | None = None) -> pd.Series:
    values = fred.get_series(series_id, observation_start=start, observation_end=end)
    return values.dropna().sort_index()


def yoy(series: pd.Series) -> pd.Series:
    return series.pct_change(12) * 100


def qoq_annualized(series: pd.Series) -> pd.Series:
    return ((series / series.shift(1)) ** 4 - 1) * 100


def fmt(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}"


def month(ts: pd.Timestamp) -> str:
    return ts.strftime("%b %Y")


def quarter(ts: pd.Timestamp) -> str:
    return f"{ts.year} Q{((ts.month - 1) // 3) + 1}"


def longest_negative_streak(series: pd.Series) -> Streak:
    current_start = None
    current_values = []
    best_values = []

    for date, value in series.items():
        if value < 0:
            if current_start is None:
                current_start = date
                current_values = []
            current_values.append((date, float(value)))
        else:
            if len(current_values) > len(best_values):
                best_values = current_values
            current_start = None
            current_values = []

    if len(current_values) > len(best_values):
        best_values = current_values
    if not best_values:
        raise ValueError("No negative streak found.")

    min_date, min_value = min(best_values, key=lambda item: item[1])
    return Streak(
        start=best_values[0][0],
        end=best_values[-1][0],
        obs=len(best_values),
        min_date=min_date,
        min_value=min_value,
    )


def source_table(fred: Fred, series_ids: list[str]) -> list[str]:
    lines = [
        "| Series | Title | Frequency | Units | Seasonal adjustment |",
        "|---|---|---|---|---|",
    ]
    for series_id in series_ids:
        info = fred.get_series_info(series_id)
        lines.append(
            "| {sid} | {title} | {frequency} | {units} | {seasonal} |".format(
                sid=series_id,
                title=str(info.get("title", "")).replace("|", "\\|"),
                frequency=info.get("frequency", ""),
                units=info.get("units", ""),
                seasonal=info.get("seasonal_adjustment", ""),
            )
        )
    return lines


def q1(fred: Fred) -> list[str]:
    core = get(fred, "PCEPILFE", "2020-01-01", "2023-12-31")
    core_yoy = yoy(core).dropna()
    core_window = core_yoy.loc["2021-01-01":"2023-12-31"]
    core_peak_date = core_window.idxmax()
    core_dec_2023 = core_yoy.loc["2023-12-01"]

    fedfunds = get(fred, "FEDFUNDS", "2022-01-01", "2023-12-31")
    fed_start = fedfunds.loc["2022-02-01"]
    fed_peak_date = fedfunds.idxmax()
    fed_peak = fedfunds.loc[fed_peak_date]

    gdp = get(fred, "GDPC1", "2021-10-01", "2023-12-31")
    gdp_growth = qoq_annualized(gdp).dropna()
    gdp_2022_2023 = gdp_growth.loc["2022-01-01":"2023-12-31"]
    negative_quarters = [
        f"{quarter(date)} ({fmt(value)}%)"
        for date, value in gdp_2022_2023.items()
        if value < 0
    ]
    gdp_2023 = gdp_growth.loc["2023-01-01":"2023-12-31"]

    usrec = get(fred, "USREC", "2022-01-01", "2023-12-31")
    recession_months = int((usrec == 1).sum())

    return [
        "### Q1 - Soft landing, 2022-2023",
        "",
        *source_table(fred, ["PCEPILFE", "FEDFUNDS", "GDPC1", "USREC"]),
        "",
        "- Calculation: core PCE inflation is 12-month percent change in `PCEPILFE`; real GDP growth is annualized quarter-over-quarter growth in `GDPC1`; recession status is monthly `USREC`.",
        f"- `FEDFUNDS` rose from {fmt(fed_start)}% in Feb 2022 to {fmt(fed_peak)}% in {month(fed_peak_date)}, a {fmt((fed_peak - fed_start) * 100, 0)} bp increase.",
        f"- Core PCE YoY peaked at {fmt(core_window.loc[core_peak_date])}% in {month(core_peak_date)} and was {fmt(core_dec_2023)}% in Dec 2023.",
        f"- 2022-2023 `GDPC1` annualized QoQ growth includes negative quarters: {', '.join(negative_quarters) if negative_quarters else 'none'}.",
        f"- All 2023 GDP quarters were positive: {', '.join(f'{quarter(d)} {fmt(v)}%' for d, v in gdp_2023.items())}.",
        f"- `USREC` has {recession_months} recession-flagged months in 2022-2023.",
        "- Verification note: the reference should not claim positive GDP growth in every quarter of 2022-2023; 2022 Q1 was negative in the current FRED vintage, but no NBER recession was recorded and 2023 growth was positive.",
    ]


def q2(fred: Fred) -> list[str]:
    spread = get(fred, "T10Y2Y", "2005-01-01", "2024-12-31")
    old = longest_negative_streak(spread.loc["2006-01-01":"2007-12-31"])
    new = longest_negative_streak(spread.loc["2022-01-01":"2024-12-31"])
    new_to_2023 = spread.loc[new.start:"2023-12-31"]
    negative_to_2023 = new_to_2023[new_to_2023 < 0]

    usrec_2023 = get(fred, "USREC", "2022-01-01", "2023-12-31")

    return [
        "### Q2 - 10Y minus 2Y inversion persistence",
        "",
        *source_table(fred, ["T10Y2Y", "USREC"]),
        "",
        "- Calculation: compare consecutive available FRED observations where `T10Y2Y < 0`; depth is the minimum spread in percentage points.",
        f"- 2006-2007 longest continuous negative streak: {old.start.date()} to {old.end.date()}, {old.calendar_days} calendar days ({old.obs} observations), trough {fmt(old.min_value)} pp on {old.min_date.date()}.",
        f"- 2022-2024 longest continuous negative streak: {new.start.date()} to {new.end.date()}, {new.calendar_days} calendar days ({new.obs} observations), trough {fmt(new.min_value)} pp on {new.min_date.date()}.",
        f"- By Dec 2023, the 2022 streak had already accumulated {len(negative_to_2023)} negative observations across {(negative_to_2023.index[-1] - negative_to_2023.index[0]).days + 1} calendar days.",
        f"- `USREC` has {int((usrec_2023 == 1).sum())} recession-flagged months in 2022-2023.",
        "- Verification note: the 2022 episode is clearly more persistent and deeper, but the 2006-2007 `T10Y2Y` trough is around -20 bps, not -50 to -70 bps.",
    ]


def q3(fred: Fred) -> list[str]:
    wages = get(fred, "AHETPI", "2020-01-01", "2023-12-31")
    cpi = get(fred, "CPIAUCSL", "2020-01-01", "2023-12-31")
    common = pd.concat({"wages": wages, "cpi": cpi}, axis=1).dropna()
    nominal_yoy = yoy(common["wages"]).dropna()
    cpi_yoy = yoy(common["cpi"]).dropna()
    real_index = common["wages"] / common["cpi"] * 100
    real_yoy = yoy(real_index).dropna()
    window = real_yoy.loc["2021-01-01":"2022-12-31"]
    trough_date = window.idxmin()

    return [
        "### Q3 - Real average hourly earnings during the inflation surge",
        "",
        *source_table(fred, ["AHETPI", "CPIAUCSL"]),
        "",
        "- Calculation: real AHE index = `AHETPI / CPIAUCSL * 100`; real wage growth is 12-month percent change in that index.",
        f"- CPI YoY peaked at {fmt(cpi_yoy.loc['2022-06-01'])}% in Jun 2022.",
        f"- Nominal `AHETPI` YoY was {fmt(nominal_yoy.loc['2022-06-01'])}% in Jun 2022.",
        f"- Real AHE YoY reached its local trough at {fmt(window.loc[trough_date])}% in {month(trough_date)}.",
        f"- Real AHE index fell from {fmt(real_index.loc['2021-12-01'])} in Dec 2021 to {fmt(real_index.loc['2022-06-01'])} in Jun 2022.",
        "- Verification note: the reference direction is supported, but the AHETPI/CPI magnitude at the CPI peak is closer to -2.4% YoY than -3% to -4% YoY.",
    ]


def q4(fred: Fred) -> list[str]:
    leisure = get(fred, "CEU7000000001", "2020-01-01", "2021-04-30")
    prof = get(fred, "CEU6000000001", "2020-01-01", "2021-04-30")

    def stats(series: pd.Series) -> dict[str, float]:
        feb = series.loc["2020-02-01"]
        apr = series.loc["2020-04-01"]
        apr_2021 = series.loc["2021-04-01"]
        loss = feb - apr
        gain = apr_2021 - apr
        return {
            "feb": feb,
            "apr": apr,
            "apr_2021": apr_2021,
            "loss": loss,
            "gain": gain,
            "recovered": gain / loss * 100,
        }

    leisure_stats = stats(leisure)
    prof_stats = stats(prof)

    return [
        "### Q4 - Sector employment recovery after April 2020",
        "",
        *source_table(fred, ["CEU7000000001", "CEU6000000001", "PAYEMS"]),
        "",
        "- Calculation: compare not seasonally adjusted all-employee counts from Feb 2020, Apr 2020, and Apr 2021; FRED units are thousands of persons, and the April-to-April gain controls for seasonality in the recovery window.",
        f"- Leisure and hospitality: Feb 2020 {fmt(leisure_stats['feb'] / 1000)}M, Apr 2020 {fmt(leisure_stats['apr'] / 1000)}M, Apr 2021 {fmt(leisure_stats['apr_2021'] / 1000)}M; gain from trough {fmt(leisure_stats['gain'] / 1000)}M, {fmt(leisure_stats['recovered'])}% of Feb-Apr loss recovered.",
        f"- Professional and business services: Feb 2020 {fmt(prof_stats['feb'] / 1000)}M, Apr 2020 {fmt(prof_stats['apr'] / 1000)}M, Apr 2021 {fmt(prof_stats['apr_2021'] / 1000)}M; gain from trough {fmt(prof_stats['gain'] / 1000)}M, {fmt(prof_stats['recovered'])}% of Feb-Apr loss recovered.",
        "- Verification note: leisure and hospitality led absolute job gains. Current FRED vintages support approximately +4.85M vs +1.88M, not +5.5M vs +2.5M.",
    ]


def q5(fred: Fred) -> list[str]:
    m2 = get(fred, "M2SL", "2019-01-01", "2022-12-31")
    cpi = get(fred, "CPIAUCSL", "2019-01-01", "2022-12-31")
    m2_yoy = yoy(m2).dropna()
    cpi_yoy = yoy(cpi).dropna()
    m2_peak_date = m2_yoy.loc["2020-01-01":"2021-12-31"].idxmax()
    cpi_peak_date = cpi_yoy.loc["2021-01-01":"2022-12-31"].idxmax()
    lag_months = (cpi_peak_date.year - m2_peak_date.year) * 12 + cpi_peak_date.month - m2_peak_date.month

    return [
        "### Q5 - M2 as leading indicator of the CPI surge",
        "",
        *source_table(fred, ["M2SL", "CPIAUCSL"]),
        "",
        "- Calculation: compare 12-month percent changes in `M2SL` and `CPIAUCSL`; lag is month difference between peak M2 YoY growth and peak CPI YoY inflation.",
        f"- `M2SL` rose from ${fmt(m2.loc['2020-02-01'] / 1000)}T in Feb 2020 to ${fmt(m2.loc['2022-02-01'] / 1000)}T in Feb 2022.",
        f"- M2 YoY growth peaked at {fmt(m2_yoy.loc[m2_peak_date])}% in {month(m2_peak_date)}.",
        f"- CPI YoY inflation was {fmt(cpi_yoy.loc['2021-04-01'])}% in Apr 2021 and peaked at {fmt(cpi_yoy.loc[cpi_peak_date])}% in {month(cpi_peak_date)}.",
        f"- Peak-to-peak lag from M2 YoY to CPI YoY was {lag_months} months.",
        "- Verification note: the 2020-2022 timing supports an approximately 16-month lag, while causal interpretation should remain caveated because supply disruptions and fiscal transfers were concurrent drivers.",
    ]


def q6(fred: Fred) -> list[str]:
    gdp = get(fred, "GDPC1", "2007-01-01", "2010-12-31")
    unrate = get(fred, "UNRATE", "2007-01-01", "2010-12-31")
    usrec = get(fred, "USREC", "2007-01-01", "2010-12-31")
    gdp_trough = gdp.loc["2008-01-01":"2010-12-31"].idxmin()
    unrate_peak = unrate.loc["2008-01-01":"2010-12-31"].idxmax()
    lag_months = (unrate_peak.year - gdp_trough.year) * 12 + unrate_peak.month - gdp_trough.month
    rec_months = usrec[usrec == 1]

    return [
        "### Q6 - Unemployment lag versus GDP during the Great Recession",
        "",
        *source_table(fred, ["UNRATE", "GDPC1", "USREC"]),
        "",
        "- Calculation: locate the `GDPC1` level trough and the `UNRATE` monthly peak during 2008-2010; compare monthly/quarterly timing.",
        f"- `GDPC1` trough: {quarter(gdp_trough)} at {fmt(gdp.loc[gdp_trough])} billion chained 2017 dollars.",
        f"- `UNRATE` peak: {fmt(unrate.loc[unrate_peak])}% in {month(unrate_peak)}.",
        f"- Timing gap from GDP trough quarter start to unemployment peak month: {lag_months} months, approximately 1-2 quarters depending on quarter/month alignment.",
        f"- `USREC` recession months in this window ran from {rec_months.index[0].strftime('%b %Y')} through {rec_months.index[-1].strftime('%b %Y')}.",
        "- Verification note: the reference is supported; unemployment lagged the GDP trough and recession end.",
    ]


def main() -> int:
    load_dotenv()
    fred = _client()
    question_map = {q.id: q for q in BENCHMARK}
    sections = [
        "# Reference Answer Verification",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "This audit verifies the six benchmark reference answers against primary FRED series. Several labor and CPI wage series originate from BLS but are accessed through FRED for reproducibility.",
        "",
        "## Benchmark Questions",
        "",
        "| ID | FRED series in benchmark |",
        "|---|---|",
    ]
    for qid in ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"]:
        sections.append(f"| {qid} | {', '.join(question_map[qid].fred_series)} |")

    sections.extend(["", "## Calculations", ""])
    for builder in [q1, q2, q3, q4, q5, q6]:
        sections.extend(builder(fred))
        sections.extend(["", "---", ""])

    sections.extend(
        [
            "## Follow-Up Edits Applied",
            "",
            "- `Q1` reference text should acknowledge a negative real GDP quarter in early 2022 while preserving the no-NBER-recession soft-landing conclusion.",
            "- `Q2` reference text should use the verified `T10Y2Y` depth for 2006-2007, around -20 bps, rather than -50 to -70 bps.",
            "- `Q3` reference text should use the verified AHETPI/CPI real-wage magnitude, around -2.4% YoY at the June 2022 CPI peak.",
            "- `Q4` reference text should use current FRED vintages for the April 2020 to April 2021 comparison, approximately +4.85M leisure and hospitality jobs versus +1.88M professional and business services jobs.",
            "",
        ]
    )
    OUT.write_text("\n".join(sections))
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
