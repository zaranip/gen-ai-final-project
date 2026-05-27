# Auto-Research Loop with Self-Critique and Persistent Memory

Final project — FINM Agentic AI, University of Chicago, Spring 2026.

## What This Is

A macroeconomic research agent that investigates open-ended questions using real FRED data,
critiques its own answers with a separate adversarial agent, and stores lessons across
runs so it doesn't repeat dead ends.

Three configurations are compared head-to-head on a 6-question hand-curated benchmark:

| Mode | Description |
|---|---|
| `no_loop` | Single-shot baseline — one researcher call, no critic, no memory |
| `loop_1` | Researcher → critic → one revision pass |
| `loop_n` | Full system — iterative critique + persistent memory across runs |

**Scholarly grounding**
- Self-Refine (Madaan et al., NeurIPS 2023) — iterative LLM refinement with self-feedback ([arXiv:2303.17651](https://arxiv.org/abs/2303.17651))
- Reflexion (Shinn et al., NeurIPS 2023) — verbal reinforcement via episodic memory ([arXiv:2303.11366](https://arxiv.org/abs/2303.11366))
- Macroeconomic Forecasting with LLMs ([arXiv:2407.00890](https://arxiv.org/abs/2407.00890)) — FRED-MD benchmark context

---

## Setup

### 1. Clone and install

```bash
git clone <repo-url>
cd gen-ai-final-project
pip install -r requirements.txt
```

### 2. Set API keys

```bash
cp .env.example .env
# Fill in your keys:
#   ANTHROPIC_API_KEY  — required
#   FRED_API_KEY       — required (free at https://fred.stlouisfed.org/docs/api/api_key.html)
#   TAVILY_API_KEY     — optional (enables web search; free tier at tavily.com)
```

### 3. Run a quick test

```python
from src.orchestrator import run

result = run(
    "Did the Fed achieve a soft landing in 2022-2023?",
    mode="loop_1",          # start here — cheaper than loop_n
)
print(result["final_answer"]["claim"])
print(f"Cost: ${result['cost_estimate_usd']}  |  Iterations: {result['iterations']}")
```

---

## Project Structure

```
src/
  orchestrator.py          main entry point — call run() here
  agents/
    researcher.py          generates evidence-grounded answers via FRED tools
    critic.py              adversarial reviewer; uses different model to cut echo-chamber risk
  memory/
    store.py               JSON-backed memory with TF-IDF retrieval
  tools/
    fred_tool.py           FRED API wrapper (fetch_series, get_series_info)
    search_tool.py         web search via Tavily (stub if key not set)

benchmark/
  questions.py             6 hand-curated macro questions with reference answers
  evaluator.py             LLM-based scorer + run_benchmark() convenience function

logs/                      per-run JSON logs (auto-created)
memory_store/              persistent memory JSON (auto-created)
```

---

## Running Local Verification

Run the unit tests before changing agent logic or experiment runners:

```bash
python -m unittest discover -v
python -m compileall src benchmark scripts tests
```

These tests do not call Anthropic, FRED, or Tavily.

---

## Running the Full Benchmark

Use the reproducible runner so raw outputs and summaries are saved together:

```bash
python -m scripts.run_benchmark \
  --modes no_loop loop_1 loop_n \
  --max-iterations 4
```

For a cheaper smoke run, run one question first:

```bash
python -m scripts.run_benchmark \
  --modes no_loop loop_1 \
  --questions Q1 \
  --max-iterations 2
```

Each run writes a timestamped folder under `outputs/benchmark_runs/`:

| File | Purpose |
|---|---|
| `run_config.json` | Modes, question IDs, run ID, and iteration cap |
| `raw_results.json` | Full final answers, critiques, scores, costs, and timing |
| `summary.csv` | Flat table for charts and final report tables |
| `summary.md` | Human-readable digest for the audience-facing writeup |

---

## Cost Notes

- `loop_n` with 4 iterations on all 6 questions costs roughly **$3–8** depending on
  model usage. Start with `loop_1` or a single question to calibrate.
- Cost estimates are logged in each result dict (`cost_estimate_usd`).
- Paid services used: Anthropic API, FRED API (free), Tavily (optional).

---

## Key Design Decisions

**Why different models for researcher and critic?**
Using the same model for both risks echo-chamber agreement — both agents share
the same training biases. Critic defaults to `claude-sonnet-4-6` while the researcher
uses `claude-opus-4-7`.

**Why TF-IDF for memory retrieval instead of embeddings?**
No external embedding API dependency. For ~50 stored memories the quality is
adequate. Swap `MemoryStore` retrieval for dense embeddings if the store grows large.

**Why `submit_research_answer` as a tool call?**
Forces structured output without post-hoc JSON parsing. The schema is enforced
by the Anthropic SDK tool definition.

---

## What the Defense Will Cover

Per the assignment rubric, each team member should be ready to explain:
- Which component they personally built
- Why this data, this method, this evaluation design
- At least one case where self-critique made the answer *worse* (required by rubric)
- What an AI tool would not have produced on its own

Current ownership plan is tracked in `docs/team_execution_plan.md`.
The final-report handoff structure is in `reports/final_report_handoff.md`.

---

## AI Usage Statement

Claude Code (claude-sonnet-4-6) was used to scaffold this codebase. The benchmark
questions and reference answers were hand-curated from primary FRED data by the team.
All agent outputs were verified against actual FRED data before being accepted as
reference answers. Model outputs were not used as primary evidence.
