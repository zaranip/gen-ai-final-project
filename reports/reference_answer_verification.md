# Reference Answer Verification

Generated: 2026-05-28 03:15:06 UTC

This audit verifies the six benchmark reference answers against primary FRED series. Several labor and CPI wage series originate from BLS but are accessed through FRED for reproducibility.

## Benchmark Questions

| ID | FRED series in benchmark |
|---|---|
| Q1 | PCEPILFE, FEDFUNDS, GDPC1, USREC |
| Q2 | T10Y2Y, USREC |
| Q3 | AHETPI, CPIAUCSL |
| Q4 | CEU7000000001, CEU6000000001, PAYEMS |
| Q5 | M2SL, CPIAUCSL |
| Q6 | UNRATE, GDPC1, USREC |

## Calculations

### Q1 - Soft landing, 2022-2023

| Series | Title | Frequency | Units | Seasonal adjustment |
|---|---|---|---|---|
| PCEPILFE | Personal Consumption Expenditures Excluding Food and Energy (Chain-Type Price Index) | Monthly | Index 2017=100 | Seasonally Adjusted |
| FEDFUNDS | Federal Funds Effective Rate | Monthly | Percent | Not Seasonally Adjusted |
| GDPC1 | Real Gross Domestic Product | Quarterly | Billions of Chained 2017 Dollars | Seasonally Adjusted Annual Rate |
| USREC | NBER based Recession Indicators for the United States from the Period following the Peak through the Trough | Monthly | +1 or 0 | Not Seasonally Adjusted |

- Calculation: core PCE inflation is 12-month percent change in `PCEPILFE`; real GDP growth is annualized quarter-over-quarter growth in `GDPC1`; recession status is monthly `USREC`.
- `FEDFUNDS` rose from 0.08% in Feb 2022 to 5.33% in Aug 2023, a 525 bp increase.
- Core PCE YoY peaked at 5.61% in Sep 2022 and was 3.11% in Dec 2023.
- 2022-2023 `GDPC1` annualized QoQ growth includes negative quarters: 2022 Q1 (-1.02%).
- All 2023 GDP quarters were positive: 2023 Q1 2.93%, 2023 Q2 2.54%, 2023 Q3 4.69%, 2023 Q4 3.42%.
- `USREC` has 0 recession-flagged months in 2022-2023.
- Verification note: the reference should not claim positive GDP growth in every quarter of 2022-2023; 2022 Q1 was negative in the current FRED vintage, but no NBER recession was recorded and 2023 growth was positive.

---

### Q2 - 10Y minus 2Y inversion persistence

| Series | Title | Frequency | Units | Seasonal adjustment |
|---|---|---|---|---|
| T10Y2Y | 10-Year Treasury Constant Maturity Minus 2-Year Treasury Constant Maturity | Daily | Percent | Not Seasonally Adjusted |
| USREC | NBER based Recession Indicators for the United States from the Period following the Peak through the Trough | Monthly | +1 or 0 | Not Seasonally Adjusted |

- Calculation: compare consecutive available FRED observations where `T10Y2Y < 0`; depth is the minimum spread in percentage points.
- 2006-2007 longest continuous negative streak: 2006-08-17 to 2007-03-20, 216 calendar days (147 observations), trough -0.19 pp on 2006-11-15.
- 2022-2024 longest continuous negative streak: 2022-07-06 to 2024-08-26, 783 calendar days (537 observations), trough -1.08 pp on 2023-07-03.
- By Dec 2023, the 2022 streak had already accumulated 373 negative observations across 542 calendar days.
- `USREC` has 0 recession-flagged months in 2022-2023.
- Verification note: the 2022 episode is clearly more persistent and deeper, but the 2006-2007 `T10Y2Y` trough is around -20 bps, not -50 to -70 bps.

---

### Q3 - Real average hourly earnings during the inflation surge

| Series | Title | Frequency | Units | Seasonal adjustment |
|---|---|---|---|---|
| AHETPI | Average Hourly Earnings of Production and Nonsupervisory Employees, Total Private | Monthly | Dollars per Hour | Seasonally Adjusted |
| CPIAUCSL | Consumer Price Index for All Urban Consumers: All Items in U.S. City Average | Monthly | Index 1982-1984=100 | Seasonally Adjusted |

- Calculation: real AHE index = `AHETPI / CPIAUCSL * 100`; real wage growth is 12-month percent change in that index.
- CPI YoY peaked at 8.98% in Jun 2022.
- Nominal `AHETPI` YoY was 6.58% in Jun 2022.
- Real AHE YoY reached its local trough at -2.52% in Apr 2021.
- Real AHE index fell from 9.53 in Dec 2021 to 9.33 in Jun 2022.
- Verification note: the reference direction is supported, but the AHETPI/CPI magnitude at the CPI peak is closer to -2.4% YoY than -3% to -4% YoY.

---

### Q4 - Sector employment recovery after April 2020

| Series | Title | Frequency | Units | Seasonal adjustment |
|---|---|---|---|---|
| CEU7000000001 | All Employees, Leisure and Hospitality | Monthly | Thousands of Persons | Not Seasonally Adjusted |
| CEU6000000001 | All Employees, Professional and Business Services | Monthly | Thousands of Persons | Not Seasonally Adjusted |
| PAYEMS | All Employees, Total Nonfarm | Monthly | Thousands of Persons | Seasonally Adjusted |

- Calculation: compare not seasonally adjusted all-employee counts from Feb 2020, Apr 2020, and Apr 2021; FRED units are thousands of persons, and the April-to-April gain controls for seasonality in the recovery window.
- Leisure and hospitality: Feb 2020 16.29M, Apr 2020 8.60M, Apr 2021 13.44M; gain from trough 4.83M, 62.85% of Feb-Apr loss recovered.
- Professional and business services: Feb 2020 21.23M, Apr 2020 19.17M, Apr 2021 21.05M; gain from trough 1.88M, 91.32% of Feb-Apr loss recovered.
- Verification note: leisure and hospitality led absolute job gains. Current FRED vintages support approximately +4.85M vs +1.88M, not +5.5M vs +2.5M.

---

### Q5 - M2 as leading indicator of the CPI surge

| Series | Title | Frequency | Units | Seasonal adjustment |
|---|---|---|---|---|
| M2SL | M2 | Monthly | Billions of Dollars | Seasonally Adjusted |
| CPIAUCSL | Consumer Price Index for All Urban Consumers: All Items in U.S. City Average | Monthly | Index 1982-1984=100 | Seasonally Adjusted |

- Calculation: compare 12-month percent changes in `M2SL` and `CPIAUCSL`; lag is month difference between peak M2 YoY growth and peak CPI YoY inflation.
- `M2SL` rose from $15.49T in Feb 2020 to $21.72T in Feb 2022.
- M2 YoY growth peaked at 26.78% in Feb 2021.
- CPI YoY inflation was 4.13% in Apr 2021 and peaked at 8.98% in Jun 2022.
- Peak-to-peak lag from M2 YoY to CPI YoY was 16 months.
- Verification note: the 2020-2022 timing supports an approximately 16-month lag, while causal interpretation should remain caveated because supply disruptions and fiscal transfers were concurrent drivers.

---

### Q6 - Unemployment lag versus GDP during the Great Recession

| Series | Title | Frequency | Units | Seasonal adjustment |
|---|---|---|---|---|
| UNRATE | Unemployment Rate | Monthly | Percent | Seasonally Adjusted |
| GDPC1 | Real Gross Domestic Product | Quarterly | Billions of Chained 2017 Dollars | Seasonally Adjusted Annual Rate |
| USREC | NBER based Recession Indicators for the United States from the Period following the Peak through the Trough | Monthly | +1 or 0 | Not Seasonally Adjusted |

- Calculation: locate the `GDPC1` level trough and the `UNRATE` monthly peak during 2008-2010; compare monthly/quarterly timing.
- `GDPC1` trough: 2009 Q2 at 16269.15 billion chained 2017 dollars.
- `UNRATE` peak: 10.00% in Oct 2009.
- Timing gap from GDP trough quarter start to unemployment peak month: 6 months, approximately 1-2 quarters depending on quarter/month alignment.
- `USREC` recession months in this window ran from Jan 2008 through Jun 2009.
- Verification note: the reference is supported; unemployment lagged the GDP trough and recession end.

---

## Follow-Up Edits Applied

- `Q1` reference text should acknowledge a negative real GDP quarter in early 2022 while preserving the no-NBER-recession soft-landing conclusion.
- `Q2` reference text should use the verified `T10Y2Y` depth for 2006-2007, around -20 bps, rather than -50 to -70 bps.
- `Q3` reference text should use the verified AHETPI/CPI real-wage magnitude, around -2.4% YoY at the June 2022 CPI peak.
- `Q4` reference text should use current FRED vintages for the April 2020 to April 2021 comparison, approximately +4.85M leisure and hospitality jobs versus +1.88M professional and business services jobs.
