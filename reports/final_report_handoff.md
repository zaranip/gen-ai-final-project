# Final Report Handoff

This file is the bridge from the reproducible benchmark run to the final audience-facing writeup. It avoids inventing results before the API-backed benchmark has been run.

## Source Artifacts

After running:

```bash
python -m scripts.run_benchmark --modes no_loop loop_1 loop_n --max-iterations 4
```

use the newest folder in `outputs/benchmark_runs/`:

- `summary.md`: first-pass narrative of scores, costs, iterations, and evaluator notes.
- `summary.csv`: source table for charts.
- `raw_results.json`: source for direct answer excerpts, critique verdicts, and failure-case analysis.
- `run_config.json`: exact run settings to cite in reproduction notes.

## Recommended Final Writeup Structure

1. **Title:** Auto-Research Loop with Self-Critique and Persistent Memory.
2. **Question:** Does iterative critique plus memory improve open-ended macroeconomic research answers?
3. **Method:** Compare `no_loop`, `loop_1`, and `loop_n` on six FRED-backed benchmark questions.
4. **System:** Researcher agent gathers evidence; critic independently checks claims; memory stores prior lessons for `loop_n`.
5. **Benchmark:** List the six questions, FRED series used, and why they require reasoning rather than recall.
6. **Results:** Paste or adapt the mode summary table from `summary.md`; add one chart from `summary.csv`.
7. **Failure Case:** Use `raw_results.json` to show one question where critique or memory made the answer worse, more expensive, or less complete.
8. **Cost and Practicality:** Report total cost, average iterations, and when the added loop is worth the latency.
9. **Limitations:** LLM judge subjectivity, small benchmark size, FRED-only macro scope, and model/API sensitivity.
10. **AI Usage Statement:** Name Claude Code and any model calls used to generate, critique, evaluate, or help code the project.

## Defense Notes By Owner

- **Claire:** Explain the researcher/critic split, structured tool outputs, model separation, and independent FRED re-checks.
- **John:** Explain benchmark construction, reference-answer verification, and why the questions are not trivial lookup tasks.
- **Sankalp:** Explain reproducibility, run artifacts, test coverage, `loop_1` semantics, and result aggregation.
- **Zara:** Explain proposal-to-writeup framing, audience communication, limitations, and final submission packaging.

## Quality Gate Before Submission

Run these commands and keep the output in the team record:

```bash
python -m unittest discover -v
python -m compileall src benchmark scripts tests
python -m scripts.run_benchmark --modes no_loop loop_1 --questions Q1 --max-iterations 2
```

Then inspect `outputs/benchmark_runs/<run_id>/summary.md` before launching the full benchmark.

