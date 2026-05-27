# Group To-Do

Delete sections as they're done. Each task is meant for one person.

---

## 1 — Run the Full Benchmark
**Owner:** ___

- [ ] Set `ANTHROPIC_API_KEY` and `FRED_API_KEY` in `.env`
- [ ] Run `python run.py` first to confirm the pipeline works on one question
- [ ] Run all three modes across all 6 benchmark questions:
  ```python
  from benchmark.evaluator import run_benchmark
  no_loop = run_benchmark(mode="no_loop")
  loop_1  = run_benchmark(mode="loop_1")
  loop_n  = run_benchmark(mode="loop_n", max_iterations=4)
  ```
- [ ] Save raw results to `results/` as JSON

---

## 2 — Results Table + Failure Case
**Owner:** ___  
*Depends on: Task 1*

- [ ] Build a comparison table: no_loop vs loop_1 vs loop_n scores per question
- [ ] Calculate average score per mode across all 6 questions
- [ ] Find at least one case where self-critique made the answer **worse** — document it clearly
- [ ] Note iteration counts and cost per mode

---

## 3 — Primary Notebook
**Owner:** ___  
*Depends on: Tasks 1 + 2*

- [ ] Create `notebook.ipynb` that walks through the experiment end to end
- [ ] Sections: motivation → system design → results table → failure case → conclusions
- [ ] Should be runnable top-to-bottom (the defense will be driven from this)
- [ ] Include at least one full example: researcher output → critic feedback → revised answer

---

## 4 — Audience-Facing Writeup (GitHub Pages)
**Owner:** ___  
*Can start in parallel with Tasks 1–3*

- [ ] Enable GitHub Pages on the repo (Settings → Pages → main branch → `/docs`)
- [ ] Create `docs/index.md` with: what we built, why, results table, honest conclusions
- [ ] No setup required to read it — results should be visible as static content
- [ ] Include the failure case section (required by rubric)

---

## 5 — Polish README + AI Statement
**Owner:** ___  
*Do last*

- [ ] Add actual reproduction steps once notebook is finalized
- [ ] Fill in the AI usage statement with real specifics
- [ ] Add actual cost numbers from the benchmark runs
- [ ] Double-check all group members are on the submission email
