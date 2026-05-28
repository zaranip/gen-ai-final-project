# Auto-Research Loop with Self-Critique and Persistent Memory

**FINM Agentic AI - Final Project Writeup**

**Team:** Claire Kim, John Beecher, Sankalp Yadav, Zara Nip

**Date:** May 2026

---

## The Question

Does adding a self-critique loop and persistent memory make a macroeconomic
research agent's answers better on open-ended, FRED-backed questions?

We built a small benchmark to test that claim directly. The final answer is
qualified: the full `loop_n` system scored slightly higher than the single-shot
baseline, but the gain was small relative to the extra cost and latency.

## Method

Three configurations of the same agent system were scored on the same six
macroeconomic questions:

| Mode | What it does |
|---|---|
| `no_loop` | One researcher pass. No critic, no memory. |
| `loop_1` | Researcher -> critic -> at most one revision pass. No memory across runs. |
| `loop_n` | Iterative researcher/critic loop, capped at 4 iterations, with persistent memory across the benchmark run. |

The researcher uses `claude-opus-4-7`. The critic uses `claude-sonnet-4-6` so
the review step is not the exact same model re-reading its own work. The
evaluator uses `claude-haiku-4-5-20251001` against hand-curated reference
answers.

After an initial smoke run exposed scope drift on Q1, we added scope-discipline
instructions to both the researcher and critic: if a question names a time
window, the agent must answer that window first and treat later data only as a
labeled caveat.

## Reference Verification

Before the final run, we re-verified all six benchmark reference answers against
primary FRED data. The audit trail is in
`reports/reference_answer_verification.md`.

That audit corrected several benchmark references:

- Q1 now acknowledges the negative 2022 Q1 GDP quarter while preserving the
  no-NBER-recession soft-landing conclusion.
- Q2 now uses the verified 2006-2007 10Y-2Y trough of about -20 bps, not the
  earlier -50 to -70 bps estimate.
- Q3 now uses a real AHE decline of about -2.4% YoY at the June 2022 CPI peak.
- Q4 now uses current FRED vintages: about +4.8M leisure and hospitality jobs
  versus +1.9M professional and business services jobs from Apr 2020 to Apr 2021.

## Benchmark

| ID | Question | Difficulty |
|---|---|---|
| Q1 | Did the Fed achieve a soft landing in 2022-2023? | medium |
| Q2 | Was the 2022-2023 yield curve inversion more persistent than 2006-2007? | easy |
| Q3 | Did real wages grow or decline during the 2021-2022 inflation surge? | easy |
| Q4 | Did leisure and hospitality or professional services drive the post-COVID jobs recovery? | medium |
| Q5 | Did M2 acceleration lead the 2021-2022 CPI surge? | hard |
| Q6 | Did unemployment lead or lag GDP in 2008-2009? | easy |

Run used for final results:

```bash
python -m scripts.run_benchmark \
  --modes no_loop loop_1 loop_n \
  --max-iterations 4 \
  --run-id final_20260528_0340
```

## Results

### Mode averages

| Mode | Avg Score | Total Cost | Avg Iterations |
|---|---:|---:|---:|
| `no_loop` | 8.45 | $2.94 | 1.00 |
| `loop_1` | 8.22 | $6.45 | 1.67 |
| `loop_n` | **8.56** | $11.04 | 2.33 |

`loop_n` won the average score by 0.11 points over baseline, but cost about
3.8x as much. `loop_1` was worse than baseline on average, which suggests one
critic pass can add complexity without enough room to recover from a bad
revision direction.

### Question-level scores

| Question | no_loop | loop_1 | loop_n | Delta loop_n - no_loop |
|---|---:|---:|---:|---:|
| Q1 | 9.00 | 8.67 | 8.67 | -0.33 |
| Q2 | 8.67 | 8.33 | 8.67 | 0.00 |
| Q3 | 8.00 | 7.67 | 8.33 | +0.33 |
| Q4 | 8.00 | 8.00 | 8.67 | +0.67 |
| Q5 | 8.00 | 8.00 | **9.00** | +1.00 |
| Q6 | **9.00** | 8.67 | 8.00 | -1.00 |

## When The Loop Helped: Q5

Q5 asked whether M2 growth led the 2021-2022 CPI surge. The baseline answer was
good: it identified the 12-16 month lag and correctly cautioned against treating
M2 as a mechanical rule.

`loop_n` improved the answer to 9.00 by forcing cleaner definitions. It separated
three different timing claims:

- M2 YoY first jumping above roughly 10% in March 2020 to CPI YoY breaking above
  4% in April 2021: 13 months.
- M2 YoY peak in February 2021 to CPI YoY peak in June 2022: 16 months.
- M2 level peak in March 2022 to CPI YoY peak: only about 3 months.

That answer was more precise and more honest about historical reliability than
the baseline. This is the best case for iterative critique: it improved
definitions without losing the main question.

## When The Loop Hurt: Q6

Q6 is the required failure case. The baseline scored 9.00 with a concise answer:
real GDP troughed in 2009 Q2, unemployment peaked at 10.0% in October 2009, so
unemployment lagged GDP by about 1-2 quarters.

`loop_n` dropped to 8.00. It added correct but distracting nuance about downturn
timing, NBER monthly peaks versus quarterly GDP peaks, and whether unemployment
was coincident or slightly leading at recession entry. That nuance is defensible,
but it obscured the cleaner recovery-side answer the question was really asking
for. The loop did not hallucinate; it over-explained.

This is the practical failure mode we would emphasize in a defense: critique can
push an already-good answer toward methodological completeness even when the
audience needs a sharper answer.

## Cost And Practicality

The final full run cost estimate was $20.44 total:

| Mode | Total Cost | Approx Cost Per Question |
|---|---:|---:|
| `no_loop` | $2.94 | $0.49 |
| `loop_1` | $6.45 | $1.08 |
| `loop_n` | $11.04 | $1.84 |

The economics are mixed. `loop_n` produced the best average result, but the
score gain was small. It is most defensible on questions where definitions are
ambiguous and extra checking changes the answer quality, such as Q5. It is less
defensible on already-clean timing questions, such as Q6.

## Limitations

- **n = 6.** This is a proof-of-concept, not a statistical benchmark.
- **LLM judge subjectivity.** Scores come from one evaluator prompt and one model.
- **Reference sensitivity.** We found and corrected several reference values, which
  shows why the verification step matters.
- **Cost sensitivity.** Model pricing and latency change the practicality of loops.
- **Memory scope.** Memory is shared across benchmark questions; that may help for
  related macro concepts and hurt when questions are only loosely related.
- **Structured-output leakage.** Two final answers leaked XML-like field labels into
  the `claim` field. We normalized those artifacts for reporting and added a repair
  step to the benchmark runner.

## What We Would Change Next

- Add a cheap scope-guard judge after critic feedback, rather than relying only on
  prompt instructions.
- Score every iteration so we can see where answer quality peaks before later
  critiques add noise.
- Separate factual memory from process memory.
- Add a small human-grading pass for the six final answers.
- Try a second domain to test whether this pattern generalizes beyond FRED macro
  questions.

## What The AI Tool Would Not Have Produced On Its Own

- The benchmark question design: six FRED questions chosen to require reasoning,
  not recall.
- The primary-data reference audit and corrections.
- The decision to report a small, cost-qualified improvement rather than a broad
  "loops solve research" claim.
- The Q6 failure interpretation: the loop hurt by overcomplicating a clean answer,
  not by making a simple factual error.

## AI Usage Statement

Claude Code was used as a development assistant to scaffold and revise code,
tests, documentation, and report language. The research agent used Anthropic
models through the API:

- Researcher: `claude-opus-4-7`
- Critic: `claude-sonnet-4-6`
- Evaluator: `claude-haiku-4-5-20251001`

Benchmark reference answers were hand-curated and then re-verified against
primary FRED series in `reports/reference_answer_verification.md`. Agent outputs
were not used as ground-truth reference answers.

## Reproducibility

```bash
pip install -r requirements.txt
cp .env.example .env  # fill in ANTHROPIC_API_KEY and FRED_API_KEY
python -m unittest discover -v
python -m compileall src benchmark scripts tests
python -m scripts.verify_references
python -m scripts.run_benchmark --modes no_loop loop_1 loop_n --max-iterations 4
python -m scripts.build_charts
```

Final artifacts are consolidated under `outputs/benchmark_runs/consolidated/`.
