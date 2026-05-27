# Auto-Research Loop with Self-Critique and Persistent Memory

**FINM Agentic AI - Final Project Writeup**
**Team:** Claire Kim, John Beecher, Sankalp Yadav, Zara Nip
**Date:** May 2026

---

## The Question

Does adding a self-critique loop and persistent memory to a research agent actually make its answers better on hard, open-ended macroeconomic questions? Or does the extra machinery just burn tokens and drift the answer off-topic?

We built a small, reproducible benchmark to find out - and the headline result was not what we expected going in.

## Method

Three configurations of the same agent system, scored on the same six FRED-backed macro questions:

| Mode | What it does |
|---|---|
| `no_loop` | One researcher pass. No critic, no memory. Baseline. |
| `loop_1` | Researcher → critic → at most one revision pass. No memory across runs. |
| `loop_n` | Iterative researcher/critic loop (cap 4 iterations) **with** persistent memory carried across runs. |

The researcher runs on `claude-opus-4-7`. The critic runs on `claude-sonnet-4-6` - deliberately a different model - to reduce the chance that the two agents share the same blind spots and rubber-stamp each other. The critic independently re-fetches FRED data rather than trusting numbers in the researcher's draft. Final answers are submitted via a structured tool call (`submit_research_answer`), which forces a schema rather than relying on post-hoc JSON parsing.

Memory is a JSON-backed store with TF-IDF retrieval. Each run writes `(question, claim, weaknesses, lessons, verdict)` and on subsequent runs the top-3 most similar prior attempts are injected into the researcher's prompt. No external embedding service.

## The Benchmark

Six hand-curated questions, all answerable from FRED primary data, none answerable by simple lookup:

| ID | Question | Difficulty |
|---|---|---|
| Q1 | Did the Fed achieve a soft landing in 2022–2023? | medium |
| Q2 | Was the 2022–2023 yield curve inversion more persistent than 2006–2007? | easy |
| Q3 | Did real wages grow or decline during the 2021–2022 inflation surge? | easy |
| Q4 | Did leisure & hospitality or professional services drive the post-COVID jobs recovery? | medium |
| Q5 | Did M2 acceleration lead the 2021–2022 CPI surge? | hard |
| Q6 | Did unemployment lead or lag GDP in 2008–2009? | easy |

Reference answers were constructed by the team from primary FRED series, not auto-generated. Each reference is defensible - but, per the original proposal and the professor's feedback, these are not questions with a unique canonical academic answer. We treat the benchmark as a proof-of-concept, not as a leaderboard contribution.

Evaluation is LLM-graded along three axes (factual accuracy, reasoning quality, completeness), averaged into a single 0–10 total, with the judge looking at both the agent's claim *and* the reference answer.

## Results

### Mode averages

| Mode | Avg Score | Avg Iterations |
|---|---:|---:|
| `no_loop` | **8.06** | 1.0 |
| `loop_1`  | 7.45 | 1.7 |
| `loop_n`  | 7.27 | 3.6 |

That's the headline. More iteration made the agent *worse* on average, not better. Adding the critic dropped the mean score by ~0.6 points. Adding memory on top dropped it another ~0.2.

### Question-level scores

| Question | no_loop | loop_1 | loop_n | Δ (loop_n − no_loop) |
|---|---:|---:|---:|---:|
| Q1 | 8.00 | 7.00 | **5.00** | **−3.00** |
| Q2 | 7.00 | 8.00 | 8.00 | +1.00 |
| Q3 | 9.00 | 8.00 | 9.00 | 0 |
| Q4 | 7.00 | 7.00 | 6.00 | −1.00 |
| Q5 | 8.67 | 8.67 | 8.00 | −0.67 |
| Q6 | 8.67 | 6.00 | **9.33** | **+0.67** |

Two questions are loud - Q1 and Q6 - and they tell opposite stories.

## When the loop helped: Q6 (unemployment lag in 2008–2009)

`no_loop` gave a clean, correct answer (8.67): unemployment lagged GDP by ~2 quarters, GDP troughed Q2 2009, unemployment peaked October 2009. Done.

`loop_n` (9.33) didn't entirely *contradict* this. The iterative version added the observation that U-3 stayed within 0.2 ppt of its peak through April 2010, so "1–2 quarters" is better stated as a range (1–3 quarters) than a single point. It also added PAYEMS as a second labor-market signal, noting payrolls bottomed in February 2010, separately from U-3. The critic pushed for that second signal and for methodological transparency on quarterly-vs-monthly alignment. Memory likely helped retain "check Okun's Law context" from prior recession-themed runs.

This is the case for the loop. When the baseline is good and the question rewards precision, iteration adds nuance without breaking the core claim.

## When the loop hurt: Q1 (the 2022–2023 soft landing) - required failure case

This is the case that mattered most for us to report honestly, because it's the rubric's explicit ask.

`no_loop` (8.0): "Largely achieved a soft landing - no recession, core PCE fell from ~5.6% peak to ~3% by end-2023." Direct, on-topic, slightly hedged but accurate.

`loop_1` (7.0): Same direction, but with the critic flagging that the researcher had elided H1 2022's negative GDP quarters (the "technical recession" debate). The revision pulled that nuance in. The score *fell* anyway, because the answer became less crisp on the core "did the soft landing happen" question. Defensible trade-off, debatable scoring.

`loop_n` (**5.0** - a 3-point drop from baseline): The agent fundamentally **misframed the question**. Across four iterations of critic feedback, it kept extending the evaluation horizon - first to late 2024, then to mid-2025, finally to September 2025 - and concluded with "the soft landing label fits a snapshot from mid-2024 to mid-2025 better than the late-2025 picture." All the numbers it cited are real. They're just answering a different question than the one asked. The reference answer is scoped to the 2022–2023 cycle. The agent's late-2025 reframing isn't wrong - it's irrelevant.

**Why this happened**, as best we can tell from reading the iteration trace:

- The critic, doing its job well, kept pushing the researcher to "engage with more recent data" and "address the open question about whether disinflation stalled." Each push was individually reasonable.
- Memory amplified this. Prior `loop_n` runs on related monetary-policy questions had stored lessons like "check post-cycle continuation" - useful for some questions, but here it nudged scope creep that the critic was already encouraging.
- There's no agent in the loop whose job is to **re-anchor on the original question**. The researcher accepts the critic's suggested investigations and follows them. Over four iterations, drift compounds.

In short: well-intentioned critics plus a memory of "be more thorough" lessons can cause an agent to win the conversation it's having with itself while losing the one it was hired for. We did not anticipate this when designing the system.

## Cost and Practicality

Rough per-question cost from our runs (Anthropic API, May 2026 pricing - Opus 4.7 for researcher, Sonnet 4.6 for critic):

| Mode | Approx cost per question | Typical wall time |
|---|---:|---:|
| `no_loop` | ~$0.40 | ~50 sec |
| `loop_1` (with revision) | ~$2.00 | ~3 min |
| `loop_n` (4 iterations) | ~$3–4 | ~6–10 min |

`loop_n` is roughly 8–10× the cost of `no_loop` for, on average, lower scores. Even on Q6 where it helped, you're paying ~$3 to gain ~0.7 points on a 10-point scale. The economics of iteration only work when the baseline is genuinely weak - and on these six questions, with Opus 4.7 as the researcher, the baseline was already pretty good.

This is consistent with the broader Self-Refine literature finding that iterative refinement helps less when the base model is already strong. We replicated that finding on a small macro benchmark with real tools.

## Limitations

A short, honest list:

- **n = 6.** This is a proof-of-concept benchmark, not a statistical study. One outlier question (Q1) drives most of the loop_n decline. We can't rule out that a different six questions would flip the conclusion.
- **LLM-judge subjectivity.** Scores come from a single Claude-Sonnet evaluator. The judge has its own priors about what a "good" answer looks like - and as the Q1 case shows, scope-of-question matters a lot to scoring. A different judge, or human scoring, might rate the loop_n answers differently.
- **Macro-only, FRED-only.** Six questions about one data source. We have no evidence about whether this loop helps on, say, equity research, legal questions, or anything outside macro time-series reasoning.
- **The Q3 loop_n cell is missing** because the Anthropic credit balance ran out mid-run. The run is reproducible from `scripts.run_benchmark` and the cell will fill in on the next funded run; we report what we have rather than backfill from a different vintage.
- **Memory scope.** We share memory across runs within a benchmark sweep. That's plausibly the *wrong* design choice for a benchmark - memory may help when questions are genuinely related, hurt when they aren't, and our six questions are only loosely related to each other.
- **No re-anchoring agent.** As Q1 showed, the system has no defender of the original question. That's a fixable gap, not an inherent limit, but we did not have it in this version.

## What We'd Change Next

If we ran this again with more budget and another two weeks:

- Add a "scope guard" check after each critic pass - a cheap call that asks whether the revised answer still answers the *original* question, before passing feedback to the researcher.
- Track per-iteration scores, not just the final answer, to see where in the loop the score actually peaks. Anecdotally on Q1, iteration 1 may have been the best.
- Separate "lessons" memory from "process" memory. The current store lumps both, which may be why Q1 inherited "be more thorough" pressure from unrelated runs.
- Test on a non-macro domain to see whether the no_loop > loop_n pattern is general or domain-specific.

## What the AI Tool Would Not Have Produced on Its Own

We want to be specific here because the rubric asks. A few things:

- The **question selection** is ours. Six FRED questions calibrated to require reasoning rather than recall is a design choice we made, not something an off-the-shelf agent would generate.
- The **failure case framing** (Q1 as scope drift, not factual error) is human analysis. The LLM judge described it as "shifted the goalposts" - accurate but generic. The structural diagnosis - critic feedback compounding with memory pressure, no agent owning the original question - required reading the iteration traces.
- The **decision to report a negative headline result honestly** is ours. An agent optimizing for "good demo" would have buried the loop_n decline. We're presenting it as the finding because that's what the data says.
- **Reference answer verification**. John independently re-pulled FRED series and confirmed reference numbers before they were used as ground truth. The agent's answers are scored against human-verified data, not other agent outputs.

## AI Usage Statement

Claude Code (Claude Opus 4.7) was used as the development assistant to scaffold the codebase - directory layout, tool wrappers, test harness, benchmark runner. The agent system itself runs on:

- **Researcher:** `claude-opus-4-7` via Anthropic API
- **Critic:** `claude-sonnet-4-6` via Anthropic API
- **LLM judge / evaluator:** `claude-sonnet-4-6` via Anthropic API

All benchmark reference answers and the six benchmark questions were hand-curated by the team from primary FRED data. Agent outputs were not used as reference answers; the references were verified independently against FRED before scoring.

External data: Federal Reserve Economic Data (FRED) via `fredapi`. Optional web search via Tavily (was not enabled for the reported runs).

## Reproducibility

```bash
pip install -r requirements.txt
cp .env.example .env  # fill in ANTHROPIC_API_KEY and FRED_API_KEY
python -m unittest discover -v
python -m scripts.run_benchmark --modes no_loop loop_1 loop_n --max-iterations 4
```

Artifacts land in `outputs/benchmark_runs/<run_id>/`:

- `run_config.json` - exact settings
- `raw_results.json` - every claim, critique, score, and token count
- `summary.csv` - flat table for plotting
- `summary.md` - same digest in markdown

The consolidated results table above is drawn from `outputs/benchmark_runs/consolidated/`.

## Part Distributions

- **Claire** - researcher/critic split, why a different model for the critic, structured tool-output schemas, why the critic independently re-fetches FRED data.
- **John** - benchmark construction, FRED-based reference verification, why these six questions resist simple lookup.
- **Sankalp** - reproducibility scaffolding, the `loop_1` "one revision pass" semantics, result aggregation pipeline, test coverage.
- **Zara** - proposal-to-writeup framing, the Q1 failure case, honest limitations, AI usage disclosure.

---

## References

- Self-Refine (Madaan et al., NeurIPS 2023) - iterative LLM refinement with self-feedback. [arXiv:2303.17651](https://arxiv.org/abs/2303.17651)
- Reflexion (Shinn et al., NeurIPS 2023) - verbal reinforcement via episodic memory. [arXiv:2303.11366](https://arxiv.org/abs/2303.11366)
- Macroeconomic Forecasting with LLMs - FRED-MD benchmark context. [arXiv:2407.00890](https://arxiv.org/abs/2407.00890)
