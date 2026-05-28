# Group To-Do

Project objective: build and defend a reproducible macroeconomic research-agent
benchmark that compares `no_loop`, `loop_1`, and `loop_n` on six FRED-backed
questions, then explain when self-critique and persistent memory help or hurt.

Delete sections or checks as they become true.

---

## Current State

- [x] Core researcher/critic/memory scaffold exists in `src/`.
- [x] FRED and optional Tavily tool wrappers exist in `src/tools/`.
- [x] Six benchmark questions and reference answers exist in `benchmark/questions.py`.
- [x] LLM evaluator exists in `benchmark/evaluator.py`.
- [x] `loop_1` now performs one critic-triggered revision pass.
- [x] Local tests cover loop semantics and benchmark summary writers.
- [x] Reproducible benchmark runner writes `run_config.json`, `raw_results.json`,
  `summary.csv`, and `summary.md` under `outputs/benchmark_runs/<run_id>/`.
- [x] Draft final report, GitHub Pages writeup, charts, and consolidated outputs exist.
- [x] Reference answers have an auditable FRED verification report in
  `reports/reference_answer_verification.md`.
- [x] Researcher and critic prompts now include scope-discipline instructions to
  reduce historical-window drift.
- [x] Post-scope-fix Q1 smoke run completed locally as `smoke_20260528_0321`.

---

## 1 - Reference Answer Verification
**Owner:** John

This is the main evidence-quality gate. Do this before treating benchmark scores
as final.

- [x] Verify all six benchmark reference answers against primary FRED/BLS-style data.
- [x] For each question, record the exact series IDs, date windows, transformations,
  calculations, and source notes used to support the reference answer.
- [x] Save the verification record in a durable artifact:
  `reports/reference_answer_verification.md`.
- [x] Update loose or misleading reference answer text in `benchmark/questions.py`.
- [x] Re-run local tests after benchmark text changes:
  ```bash
  python -m unittest discover -v
  python -m compileall src benchmark scripts tests
  ```

---

## 2 - Clean Benchmark Run
**Owner:** ___

Wait until `ANTHROPIC_API_KEY` and `FRED_API_KEY` are ready in `.env`.

- [x] Run the smoke benchmark first:
  ```bash
  python -m scripts.run_benchmark \
    --modes no_loop loop_1 \
    --questions Q1 \
    --max-iterations 2 \
    --run-id smoke_20260528_0321
  ```
- [x] Inspect `outputs/benchmark_runs/<run_id>/summary.md` for obvious failures,
  malformed claims, missing scores, bad costs, or scope drift.
- [ ] If the smoke output is sound, run the full final benchmark:
  ```bash
  python -m scripts.run_benchmark \
    --modes no_loop loop_1 loop_n \
    --max-iterations 4
  ```
- [ ] Use the newest full-run `outputs/benchmark_runs/<run_id>/` as the final source
  of truth for scores, costs, iterations, answer excerpts, and failure cases.
- [ ] Ignore the interrupted `final_20260528_0325` attempt for final reporting; it
  was intentionally stopped before writing complete benchmark artifacts.
- [ ] Do not rely on the current `outputs/benchmark_runs/consolidated/` directory as
  final until it is reconciled or replaced; it appears to be assembled from partial
  logs and is missing `Q3`/`loop_n` in `summary.md`.

---

## 3 - Results And Report Reconciliation
**Owner:** ___
**Depends on:** Tasks 1 and 2

- [ ] Replace or regenerate the consolidated results from the clean full run.
- [ ] Rebuild charts from the final `summary.csv`.
- [ ] Reconcile the current inconsistency: `reports/final_report.md` says the `Q3`
  `loop_n` cell is missing, while `docs/index.md` presents a filled `Q3` `loop_n`
  score.
- [ ] Update `reports/final_report.md` with the final mode averages, per-question
  scores, costs, run ID, and limitations.
- [ ] Update `docs/index.md` and chart images so the audience-facing page matches
  the final report and benchmark artifacts.
- [ ] Confirm the required failure case is supported by `raw_results.json`, not just
  by the summary table.

---

## 4 - Submission Packaging
**Owner:** Zara / ___

- [ ] Decide whether `reports/final_report.md` satisfies the "primary notebook or
  report file" requirement, or create `notebook.ipynb` if the team wants a notebook
  defense artifact.
- [ ] Ensure GitHub Pages is enabled for the `docs/` directory and the public link
  resolves.
- [ ] Update README reproduction steps if the final workflow changes.
- [ ] Fill in actual benchmark cost numbers from the clean run.
- [ ] Finalize the AI usage statement with the actual tools/models used in the
  final run and writeup.
- [ ] Double-check all group members are on the submission email.

---

## Nice To Add If Time

- [ ] Add a cheap "scope guard" after critic feedback to check whether the next
  revision still answers the original question.
- [ ] Track and score every iteration, not just the final answer, to identify where
  the loop peaks before it drifts.
- [ ] Split persistent memory into factual lessons vs. process lessons so generic
  "be more thorough" memories do not create scope creep.
- [ ] Add a small human-grading pass for the six final answers to sanity-check the
  LLM judge.
- [ ] Add CI for `python -m unittest discover -v` and `python -m compileall src benchmark scripts tests`.
- [ ] Try a non-macro or non-FRED mini-benchmark to see whether the negative
  `loop_n` result generalizes.
