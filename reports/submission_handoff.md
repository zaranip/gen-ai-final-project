# Submission Handoff Notes

Updated: 2026-05-28 UTC

## What Was Added

- Added a reproducible FRED reference-audit script:
  `scripts/verify_references.py`.
- Added the generated reference-audit report:
  `reports/reference_answer_verification.md`.
- Corrected benchmark reference answers in `benchmark/questions.py` where primary
  FRED data contradicted the old values:
  - `Q1`: acknowledges the negative 2022 Q1 GDP quarter while preserving the
    no-NBER-recession soft-landing conclusion.
  - `Q2`: corrects the 2006-2007 10Y-2Y inversion depth to about -20 bps rather
    than -50 to -70 bps.
  - `Q3`: corrects the real AHE decline to about -2.4% YoY at the June 2022 CPI
    peak.
  - `Q4`: updates employment recovery numbers to current FRED vintages, about
    +4.8M leisure and hospitality jobs vs. +1.9M professional and business
    services jobs.
- Added scope-discipline instructions to the researcher and critic prompts so
  historical benchmark questions stay anchored to the requested date window.
- Added structured-output normalization in `scripts/run_benchmark.py` for rare
  XML-like field leakage from Anthropic tool output, plus a regression test.
- Ran the clean final benchmark and regenerated publishable artifacts:
  - Run ID: `final_20260528_0340`
  - Consolidated artifacts:
    `outputs/benchmark_runs/consolidated/raw_results.json`,
    `summary.csv`, and `summary.md`
  - Charts in `docs/assets/`
- Updated `reports/final_report.md`, `docs/index.md`, `README.md`, and `TODO.md`
  to reflect the clean full run.

## Final Benchmark Result

| Mode | Avg Score | Total Cost | Avg Iterations |
|---|---:|---:|---:|
| `no_loop` | 8.45 | $2.94 | 1.00 |
| `loop_1` | 8.22 | $6.45 | 1.67 |
| `loop_n` | 8.56 | $11.04 | 2.33 |

Headline: `loop_n` edges the baseline by 0.11 points, but costs about 3.8x as
much. The best improvement case is Q5, where iterative critique sharpened the
M2/CPI lag definitions. The required failure case is Q6, where iteration added
correct but distracting nuance and scored below the concise baseline.

Total final-run cost estimate: $20.44.

## Validation Completed

```bash
python -m unittest discover -v
python -m compileall src benchmark scripts tests
python -m scripts.verify_references
python -m scripts.run_benchmark --modes no_loop loop_1 loop_n --max-iterations 4 --run-id final_20260528_0340
python -m scripts.build_charts
```

Also ran a Q1 smoke benchmark after the scope prompt fix:

- `smoke_20260528_0316`: exposed scope drift into 2024-2026.
- `smoke_20260528_0321`: post-scope-fix run looked healthy; `no_loop` scored
  8.67 and `loop_1` scored 9.00.

The interrupted `final_20260528_0325` run should not be used for reporting.

## Not 100% Yet

- GitHub Pages still needs to be enabled or confirmed for the `docs/` directory
  after the branch is pushed/merged.
- The team still needs to decide whether `reports/final_report.md` is the primary
  submission artifact or whether to add a notebook wrapper.
- Someone should do a final human read-through of the six consolidated claims and
  the final report before submission.

## Recommended Next Steps

1. After write access is granted, push:
   ```bash
   git push -u origin codex-submission-handoff
   ```
2. Open a PR or merge the branch into the submission branch.
3. Confirm the GitHub Pages URL renders `docs/index.md` and chart images.
4. Submit the repo link, report/chartbook link, and any required email materials.
