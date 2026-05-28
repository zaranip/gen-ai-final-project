---
layout: default
title: Auto-Research Loop Chartbook
---

# Auto-Research Loop with Self-Critique and Persistent Memory

**FINM Agentic AI - Final Project Writeup**

**Team:** Claire Kim, John Beecher, Sankalp Yadav, Zara Nip

**Date:** May 2026

[Repository on GitHub](https://github.com/zaranip/gen-ai-final-project) · [Raw report](https://github.com/zaranip/gen-ai-final-project/blob/main/reports/final_report.md) · [Consolidated CSV](https://github.com/zaranip/gen-ai-final-project/blob/main/outputs/benchmark_runs/consolidated/summary.csv)

---

## The Question

This project evaluates whether augmenting a macroeconomic research agent with a self-critique loop and a persistent memory measurably improves its answers to open-ended, FRED-backed questions.

We constructed a small benchmark to test this directly. We find that the full `loop_n` configuration achieved a marginally higher mean score than the single-shot baseline, but the improvement is negligible relative to its additional cost and latency.

## Method

Three configurations of the same agent system were evaluated on an identical set of six macroeconomic questions:

| Mode | What it does |
|---|---|
| `no_loop` | One researcher pass. No critic and no memory. |
| `loop_1` | Researcher -> critic -> at most one revision pass. No memory across runs. |
| `loop_n` | Iterative researcher/critic loop, capped at 4 iterations, with persistent memory across the benchmark run. |

The researcher uses `claude-opus-4-7`. The critic uses a distinct model, `claude-sonnet-4-6`, so that the review step does not reduce to a single model re-evaluating its own output and converging on agreement. Scoring is performed by `claude-haiku-4-5-20251001` against hand-curated reference answers.

An initial smoke run revealed scope drift on Q1. In response, we added scope-discipline instructions to both the researcher and critic prompts: when a question specifies a time window, the agent must answer that window first and treat subsequent data only as an explicitly labeled caveat, rather than as grounds to redefine the question.

## Reference Verification

Prior to the final run, all six reference answers were re-verified against primary FRED data. The complete audit trail is recorded in [`reports/reference_answer_verification.md`](https://github.com/zaranip/gen-ai-final-project/blob/main/reports/reference_answer_verification.md).

The audit corrected several references:

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

![Average benchmark score by mode](assets/mode_averages.png)

`loop_n` achieved the highest mean score, exceeding the baseline by 0.11 points at approximately 3.8x the cost. Notably, `loop_1` scored below the baseline. We attribute this to a single critic pass introducing additional complexity without providing sufficient subsequent iterations to recover from a poorly directed revision.

### Question-level scores

| Question | no_loop | loop_1 | loop_n | Delta loop_n - no_loop |
|---|---:|---:|---:|---:|
| Q1 | 9.00 | 8.67 | 8.67 | -0.33 |
| Q2 | 8.67 | 8.33 | 8.67 | 0.00 |
| Q3 | 8.00 | 7.67 | 8.33 | +0.33 |
| Q4 | 8.00 | 8.00 | 8.67 | +0.67 |
| Q5 | 8.00 | 8.00 | **9.00** | +1.00 |
| Q6 | **9.00** | 8.67 | 8.00 | -1.00 |

![Score per question by mode](assets/per_question.png)

## When The Loop Helped: Q5

Q5 asked whether M2 growth led the 2021-2022 CPI surge. The baseline answer was already strong: it identified the 12-16 month lag and appropriately cautioned against interpreting M2 as a mechanical predictor.

`loop_n` improved the score to 9.00 by enforcing definitional precision, separating three distinct timing claims that the baseline had conflated:

- M2 YoY first jumping above roughly 10% in March 2020 to CPI YoY breaking above
  4% in April 2021: 13 months.
- M2 YoY peak in February 2021 to CPI YoY peak in June 2022: 16 months.
- M2 level peak in March 2022 to CPI YoY peak: only about 3 months.

The result is both more precise and more candid about the limited historical reliability of the relationship, tightening the definitions without diverging from the original question. This is the strongest case for iterative critique in this project.

## When The Loop Hurt: Q6

Q6 is the required failure case. The baseline scored 9.00 with a concise answer: real GDP troughed in 2009 Q2 and unemployment peaked at 10.0% in October 2009, indicating that unemployment lagged GDP by approximately 1-2 quarters.

`loop_n` reduced the score to 8.00 without introducing any factual error. It added correct but extraneous nuance regarding downturn timing, NBER monthly peaks versus quarterly GDP peaks, and whether unemployment was coincident or marginally leading at the onset of the recession. Each point is individually defensible, but collectively they obscured the concise recovery-side answer the question required. The outcome is over-explanation rather than inaccuracy.

We conclude that iterative critique can drive an already-adequate answer toward methodological completeness even when the question calls for concision.

There is also an evaluator consideration. The `loop_n` Q6 answer addressed the main question and cited accurate data, yet the Haiku judge appeared to reward close adherence to the concise reference framing and to penalize the additional nuance. Although our rubric permits a score of 10 to exceed the reference in depth, in practice the judge sometimes treated differences in emphasis as clarity or completeness deficiencies. We therefore interpret Q6 in two ways simultaneously: as an agent-design failure mode and as a caution regarding evaluator design. A single-model LLM judge can be unduly sensitive to reference wording, specific benchmark figures, and answer length.

## Cost And Practicality

The final full run cost an estimated $20.44 in total:

| Mode | Total Cost | Approx Cost Per Question |
|---|---:|---:|
| `no_loop` | $2.94 | $0.49 |
| `loop_1` | $6.45 | $1.08 |
| `loop_n` | $11.04 | $1.84 |

![Iterations vs score scatter](assets/iters_vs_score.png)

The cost-benefit tradeoff is unfavorable in aggregate. `loop_n` produced the highest mean score, but the improvement was small and the cost was substantial. The configuration is most justifiable on questions with ambiguous definitions, where an additional round of verification materially improves answer quality, as in Q5. On questions with an already-precise answer, such as the timing question in Q6, it is considerably harder to justify.

## Limitations

The principal limitations:

- **n = 6.** This is a proof-of-concept, not a statistically powered benchmark.
- **LLM judge subjectivity.** Scores derive from a single evaluator prompt and a
  single Haiku model. The Q6 result indicates that the judge sometimes penalizes
  valid nuance or alternative emphasis that does not mirror the reference answer's
  exact framing. The reported averages are therefore directionally useful but not a
  definitive human-quality ranking.
- **Reference sensitivity.** We identified and corrected several reference values,
  which demonstrates the necessity of the verification step.
- **Cost sensitivity.** Model pricing and latency materially affect the
  practicality of the looped configurations.
- **Memory scope.** Memory is shared across benchmark questions, which may benefit
  related macroeconomic concepts and degrade performance when questions are only
  loosely related.
- **Structured-output leakage.** Two final answers leaked XML-like field labels into
  the `claim` field. These artifacts were normalized for reporting, and a repair
  step was added to the benchmark runner.

## What We Would Change Next

- Add a low-cost scope-guard judge after critic feedback, rather than relying on
  prompt instructions alone.
- Score every iteration to identify where answer quality peaks before later
  critiques introduce noise.
- Separate factual memory from process memory.
- Replace the single Haiku judge with an evaluator ensemble spanning multiple
  models and/or rubric variants, summarized via a median or trimmed mean together
  with score variance.
- Calibrate the evaluator prompt against direct human feedback, including examples
  in which valid above-reference nuance is rewarded and examples in which
  additional detail is penalized only when it changes the question or obscures the
  answer.
- Add a human-grading pass over the six final answers and compare it against the
  LLM ensemble.
- Extend the evaluation to a second domain to assess whether these findings
  generalize beyond FRED macroeconomic questions.

## What The AI Tool Would Not Have Produced On Its Own

- The benchmark design: six FRED questions selected to require reasoning rather
  than recall.
- The primary-data reference audit and the resulting corrections.
- The decision to report a small, cost-qualified improvement rather than a broad
  claim that iterative loops resolve research tasks.
- The interpretation of Q6: the loop degraded the answer by overcomplicating a
  concise result, not by committing a factual error.

## AI Usage Statement

Claude Code served as a development assistant, scaffolding and revising code, tests, documentation, and report language. The research agent ran on Anthropic models through the API:

- Researcher: `claude-opus-4-7`
- Critic: `claude-sonnet-4-6`
- Evaluator: `claude-haiku-4-5-20251001`

Benchmark reference answers were hand-curated and subsequently re-verified against primary FRED series in [`reports/reference_answer_verification.md`](https://github.com/zaranip/gen-ai-final-project/blob/main/reports/reference_answer_verification.md). Agent outputs were not used as ground-truth reference answers.

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

## References

- Self-Refine (Madaan et al., NeurIPS 2023) - iterative LLM refinement with self-feedback. [arXiv:2303.17651](https://arxiv.org/abs/2303.17651)
- Reflexion (Shinn et al., NeurIPS 2023) - verbal reinforcement via episodic memory. [arXiv:2303.11366](https://arxiv.org/abs/2303.11366)
- Macroeconomic Forecasting with LLMs - FRED-MD benchmark context. [arXiv:2407.00890](https://arxiv.org/abs/2407.00890)
