"""
Hand-curated benchmark questions for the auto-research loop evaluation.

Design criteria (per professor feedback):
- No canonical academic answer exists — requires genuine reasoning over data
- Answers are defensible from FRED data and publicly available information
- Sample is intentionally small (~6 questions); project is treated as proof-of-concept
- Reference answers are hand-constructed by the team from primary data sources

Scholarly grounding:
- Self-Refine (Madaan et al., NeurIPS 2023) — iterative LLM refinement framework
- Reflexion (Shinn et al., NeurIPS 2023) — verbal reinforcement via episodic memory
- "Macroeconomic Forecasting with Large Language Models" (arXiv 2407.00890) — FRED-MD benchmark
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class BenchmarkQuestion:
    id: str
    question: str
    fred_series: List[str]       # series IDs the agent should use
    reference_answer: str        # hand-curated defensible conclusion
    reference_rationale: str     # specific data points supporting the conclusion
    difficulty: str              # "easy" | "medium" | "hard"
    tags: List[str] = field(default_factory=list)


BENCHMARK: List[BenchmarkQuestion] = [

    BenchmarkQuestion(
        id="Q1",
        question=(
            "Did the Federal Reserve achieve a 'soft landing' in its 2022–2023 "
            "rate hike cycle — that is, did core PCE inflation return meaningfully "
            "toward 2% without the U.S. economy entering a recession?"
        ),
        fred_series=["PCEPILFE", "FEDFUNDS", "GDPC1", "USREC"],
        reference_answer=(
            "Yes. Core PCE fell from a peak of ~5.6% (Feb 2023) toward 2.5–3% by "
            "late 2023 while real GDP grew in every quarter of 2022–2023 and no NBER "
            "recession was declared. By conventional definition this is a soft landing, "
            "though inflation remained above the 2% target at year-end 2023."
        ),
        reference_rationale=(
            "FEDFUNDS rose from 0.08% (Feb 2022) to 5.33% (Aug 2023), a 525 bps increase. "
            "PCEPILFE peaked at ~5.6% YoY in Feb 2023 and declined to ~2.7% by Dec 2023. "
            "GDPC1 shows positive real GDP growth in all four quarters of 2023. "
            "USREC carries no recession flag for this period. The combination of falling "
            "inflation and sustained positive growth satisfies the soft-landing criterion."
        ),
        difficulty="medium",
        tags=["monetary_policy", "inflation", "recession"],
    ),

    BenchmarkQuestion(
        id="Q2",
        question=(
            "Was the U.S. yield curve inversion of 2022–2023 (10Y minus 2Y spread) "
            "more persistent than the 2006–2007 inversion that preceded the 2008 "
            "financial crisis?"
        ),
        fred_series=["T10Y2Y", "USREC"],
        reference_answer=(
            "Yes. The 2022–2023 inversion was both deeper and longer. It began in "
            "July 2022, exceeded –100 bps at its trough, and persisted for over 24 months. "
            "The 2006–2007 inversion lasted roughly 12 months and was shallower (–50 to –70 bps). "
            "Notably, the 2022–2023 inversion did not produce a declared recession through "
            "end of 2023, challenging its reliability as a leading indicator."
        ),
        reference_rationale=(
            "T10Y2Y first turned negative in July 2022 and remained inverted through at "
            "least late 2024. The prior inversion ran from approximately January 2006 to "
            "early 2007 (~12 months). Comparing negative-reading runs confirms 2022–2023 "
            "is the more persistent post-2000 inversion. USREC shows no recession flag "
            "through end of 2023 despite the prolonged inversion."
        ),
        difficulty="easy",
        tags=["yield_curve", "recession_prediction", "monetary_policy"],
    ),

    BenchmarkQuestion(
        id="Q3",
        question=(
            "Did real average hourly earnings (inflation-adjusted) grow or decline "
            "during the 2021–2022 U.S. inflation surge, and by approximately how much?"
        ),
        fred_series=["AHETPI", "CPIAUCSL"],
        reference_answer=(
            "Real average hourly earnings declined materially. Despite nominal wage "
            "growth of ~5–6% YoY, CPI inflation running at 7–9% eroded purchasing power. "
            "At the peak of inflation (June 2022), real wages were falling at approximately "
            "–3 to –4% YoY — the sharpest sustained real wage decline since the early 1980s. "
            "The decline reversed only as inflation cooled in 2023."
        ),
        reference_rationale=(
            "AHETPI (nominal avg hourly earnings) grew ~5–6% YoY through 2021–2022. "
            "CPIAUCSL peaked at 9.1% YoY in June 2022. "
            "Real wage growth ≈ 5.5% – 9.0% = –3.5% at the peak. "
            "Workers lost roughly 3–4% of real purchasing power at the height of inflation."
        ),
        difficulty="easy",
        tags=["wages", "inflation", "labor_market"],
    ),

    BenchmarkQuestion(
        id="Q4",
        question=(
            "Which sector drove U.S. employment recovery more strongly in the 12 months "
            "following the COVID-19 trough (April 2020): leisure & hospitality or "
            "professional & business services?"
        ),
        fred_series=["CEU7000000001", "CEU6000000001", "PAYEMS"],
        reference_answer=(
            "Leisure & hospitality led on absolute job gains. From the April 2020 trough "
            "to April 2021, the sector recovered approximately 5.5 million jobs vs. roughly "
            "2.5 million for professional & business services. However, professional services "
            "recovered a larger share of its own losses (~74%) than leisure & hospitality "
            "(~62%), because leisure suffered far deeper initial cuts."
        ),
        reference_rationale=(
            "CEU7000000001 fell from ~16.9M (Feb 2020) to ~8.0M (Apr 2020), losing ~8.9M. "
            "By Apr 2021 it recovered to ~13.5M (+5.5M, ~62% of losses). "
            "CEU6000000001 fell from ~22.4M to ~19.0M (–3.4M). "
            "By Apr 2021 it recovered to ~21.5M (+2.5M, ~74% of losses). "
            "Absolute gains favor leisure; proportional recovery favors professional services."
        ),
        difficulty="medium",
        tags=["labor_market", "covid", "sector_analysis"],
    ),

    BenchmarkQuestion(
        id="Q5",
        question=(
            "Was M2 money supply growth a leading indicator of the 2021–2022 inflation "
            "surge? Specifically, did the M2 acceleration in 2020 precede the CPI "
            "acceleration by a meaningful and historically consistent lag?"
        ),
        fred_series=["M2SL", "CPIAUCSL"],
        reference_answer=(
            "Yes, with approximately a 12–18 month lag. M2 grew at an unprecedented "
            "~26–27% YoY rate in early 2021 following 2020 stimulus. CPI began accelerating "
            "sharply in April 2021 and peaked in June 2022 — roughly 15 months after peak "
            "M2 growth. This is consistent with monetarist transmission lag estimates of "
            "12–24 months, though supply-side disruptions were also a concurrent driver."
        ),
        reference_rationale=(
            "M2SL grew from ~$15.4T (Feb 2020) to ~$21.7T (Feb 2022), a 41% increase. "
            "YoY M2 growth peaked at ~26.9% in February 2021. "
            "CPIAUCSL began rising sharply in April 2021 (4.2% YoY) and peaked at 9.1% "
            "in June 2022, approximately 15 months after peak M2 growth. "
            "The lag is within the historical monetarist range of 12–24 months."
        ),
        difficulty="hard",
        tags=["monetary_policy", "inflation", "money_supply", "leading_indicator"],
    ),

    BenchmarkQuestion(
        id="Q6",
        question=(
            "Did the unemployment rate lead or lag real GDP growth during the "
            "2008–2009 Great Recession, and by approximately how many quarters?"
        ),
        fred_series=["UNRATE", "GDPC1", "USREC"],
        reference_answer=(
            "Unemployment lagged GDP by approximately 1–2 quarters. Real GDP troughed "
            "in Q2 2009, but unemployment continued rising to its peak of 10.0% in "
            "October 2009 — roughly one quarter after the GDP trough. This confirms "
            "unemployment as a classic lagging indicator, consistent with Okun's Law: "
            "firms delay hiring until recovery confidence builds."
        ),
        reference_rationale=(
            "GDPC1 troughed in Q2 2009. UNRATE rose from 5.0% (Jan 2008) to 10.0% "
            "(Oct 2009), peaking ~4 months after the GDP trough. USREC marks the "
            "recession as Dec 2007–June 2009. The ~1-quarter employment lag is typical "
            "of post-WWII U.S. recessions and reflects firms' reluctance to rehire "
            "before recovery is confirmed."
        ),
        difficulty="easy",
        tags=["recession", "unemployment", "gdp", "leading_lagging_indicators"],
    ),
]
