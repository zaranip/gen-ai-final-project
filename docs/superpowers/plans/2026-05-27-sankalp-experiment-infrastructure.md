# Sankalp Experiment Infrastructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the immediately actionable experiment infrastructure for the macro auto-research project.

**Architecture:** Keep Claire's agent scaffold intact and add a thin reproducibility layer around it. The orchestrator owns mode semantics, while scripts own CLI execution and persisted result artifacts.

**Tech Stack:** Python standard library, existing Anthropic/FRED dependencies, `unittest` for local tests, CSV/JSON/Markdown files for reproducible outputs.

---

### Task 1: Repository Hygiene And Team Plan

**Files:**
- Create: `.gitignore`
- Create: `outputs/.gitkeep`
- Create: `docs/team_execution_plan.md`

- [x] **Step 1: Protect local-only files**

Add ignore rules for `.env`, Python caches, virtual environments, `.worktrees/`, generated logs, generated memory JSON, and generated benchmark outputs.

- [x] **Step 2: Record team ownership**

Write `docs/team_execution_plan.md` with project scope, Claire's completed work, Sankalp-owned implementation scope, team partition, execution order, and remaining team work.

- [ ] **Step 3: Commit**

Run:

```bash
git add .gitignore outputs/.gitkeep docs/team_execution_plan.md docs/superpowers/plans/2026-05-27-sankalp-experiment-infrastructure.md
git commit -m "docs: add execution plan and repo hygiene"
```

### Task 2: `loop_1` Revision Semantics

**Files:**
- Create: `tests/test_orchestrator_modes.py`
- Modify: `src/orchestrator.py`

- [ ] **Step 1: Write failing tests**

Add tests that patch `ResearchAgent`, `CriticAgent`, and `_save_log`. The key test should assert that `loop_1` returns the revised answer after the critic returns `revise`.

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
python -m unittest tests.test_orchestrator_modes -v
```

Expected: at least one failure because current `loop_1` stops after the first critic pass.

- [ ] **Step 3: Implement the smallest orchestrator change**

Adjust `loop_1` so it performs one additional researcher pass when the critic verdict is not `accept`. Do not enable persistent memory for `loop_1`.

- [ ] **Step 4: Run tests and confirm pass**

Run:

```bash
python -m unittest tests.test_orchestrator_modes -v
```

Expected: all orchestrator mode tests pass.

- [ ] **Step 5: Commit**

Run:

```bash
git add src/orchestrator.py tests/test_orchestrator_modes.py
git commit -m "fix: run loop one revision pass"
```

### Task 3: Reproducible Benchmark Runner

**Files:**
- Create: `scripts/__init__.py`
- Create: `scripts/run_benchmark.py`
- Create: `tests/test_run_benchmark_script.py`
- Modify: `README.md`
- Create: `reports/final_report_handoff.md`

- [ ] **Step 1: Write failing tests**

Add tests for summary-row construction and Markdown summary output. These tests should not call Anthropic, FRED, or Tavily.

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
python -m unittest tests.test_run_benchmark_script -v
```

Expected: import failure because `scripts/run_benchmark.py` does not exist yet.

- [ ] **Step 3: Implement CLI and output writers**

Create a CLI that supports `--modes`, `--questions`, `--max-iterations`, `--output-dir`, and `--run-id`. It should require `ANTHROPIC_API_KEY` and `FRED_API_KEY`, then save `run_config.json`, `raw_results.json`, `summary.csv`, and `summary.md`.

- [ ] **Step 4: Run tests and confirm pass**

Run:

```bash
python -m unittest tests.test_run_benchmark_script -v
```

Expected: all benchmark script tests pass without external API calls.

- [ ] **Step 5: Update documentation**

Document the runner command, output files, and final-report handoff path in `README.md` and `reports/final_report_handoff.md`.

- [ ] **Step 6: Commit**

Run:

```bash
git add scripts tests README.md reports/final_report_handoff.md
git commit -m "feat: add reproducible benchmark runner"
```

### Task 4: Final Verification

**Files:**
- All changed files

- [ ] **Step 1: Run full local test suite**

Run:

```bash
python -m unittest discover -v
```

Expected: all tests pass.

- [ ] **Step 2: Run syntax check**

Run:

```bash
python -m compileall src benchmark scripts tests
```

Expected: command exits with status 0.

- [ ] **Step 3: Review git state**

Run:

```bash
git status --short --branch
git log --oneline -n 5
```

Expected: working tree clean after commits, with the new professional commits visible on `main`.

