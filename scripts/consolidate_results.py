"""
Consolidates logs from partial/crashed benchmark runs into a single summary.

Usage:
    python -m scripts.consolidate_results

Reads all logs/run_*.json files, matches them to benchmark questions,
scores any unscored answers, and writes a combined summary to
outputs/benchmark_runs/consolidated/.
"""

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from benchmark.evaluator import evaluate
from benchmark.questions import BENCHMARK

load_dotenv()

LOGS_DIR = Path("logs")
OUT_DIR = Path("outputs/benchmark_runs/consolidated")

# Skip the smoke test run (single Q1 loop_1 run done before the full benchmark)
SMOKE_TEST_LOG = "run_20260527_162729.json"

SUMMARY_FIELDS = [
    "question_id", "mode", "difficulty", "tags",
    "factual_accuracy", "reasoning_quality", "completeness", "total",
    "iterations", "cost_estimate_usd", "elapsed_seconds", "claim", "explanation",
]


def match_question(question_text: str):
    """Find the BenchmarkQuestion whose question text starts the same way."""
    for q in BENCHMARK:
        if q.question[:60] in question_text or question_text[:60] in q.question:
            return q
    return None


def extract_final_answer(log: dict) -> dict:
    """Pull the final researcher answer from a log's iterations."""
    iterations = log.get("iterations", [])
    if not iterations:
        return {}
    last = iterations[-1]
    researcher = last.get("researcher", {})
    return researcher.get("answer", {})


def count_iterations(log: dict) -> int:
    return len(log.get("iterations", []))


def main():
    log_files = sorted(LOGS_DIR.glob("run_*.json"))
    results = []

    for log_path in log_files:
        if log_path.name == SMOKE_TEST_LOG:
            continue

        with open(log_path) as f:
            log = json.load(f)

        question_obj = match_question(log.get("question", ""))
        if question_obj is None:
            print(f"  [skip] Could not match: {log_path.name}")
            continue

        mode = log.get("mode", "")
        answer = extract_final_answer(log)
        if not answer or not answer.get("claim"):
            print(f"  [skip] No answer in: {log_path.name}")
            continue

        print(f"  Scoring {question_obj.id} / {mode} ...")
        scores = evaluate(question_obj, answer)

        results.append({
            "question_id": question_obj.id,
            "question": question_obj.question,
            "mode": mode,
            "difficulty": question_obj.difficulty,
            "tags": question_obj.tags,
            "scores": scores,
            "final_answer": answer,
            "iterations": count_iterations(log),
            "cost_estimate_usd": "",   # not stored in raw logs
            "elapsed_seconds": "",
        })

    # ------------------------------------------------------------------ #
    # Write outputs                                                        #
    # ------------------------------------------------------------------ #
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # raw JSON
    with open(OUT_DIR / "raw_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    # CSV
    with open(OUT_DIR / "summary.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_FIELDS, lineterminator="\n")
        writer.writeheader()
        for r in results:
            s = r.get("scores", {})
            writer.writerow({
                "question_id": r["question_id"],
                "mode": r["mode"],
                "difficulty": r["difficulty"],
                "tags": ";".join(r["tags"]),
                "factual_accuracy": s.get("factual_accuracy", ""),
                "reasoning_quality": s.get("reasoning_quality", ""),
                "completeness": s.get("completeness", ""),
                "total": s.get("total", ""),
                "iterations": r["iterations"],
                "cost_estimate_usd": r["cost_estimate_usd"],
                "elapsed_seconds": r["elapsed_seconds"],
                "claim": r["final_answer"].get("claim", "")[:200],
                "explanation": s.get("explanation", ""),
            })

    # Markdown summary
    _write_markdown(results, OUT_DIR / "summary.md")
    print(f"\nDone. Results written to {OUT_DIR}/")


def _write_markdown(results: list, path: Path):
    from collections import defaultdict
    by_mode = defaultdict(list)
    for r in results:
        by_mode[r["mode"]].append(r)

    lines = [
        "# Consolidated Benchmark Results",
        "",
        "All three modes across all 6 questions.",
        "",
        "## Mode Averages",
        "",
        "| Mode | Avg Score | Avg Iterations |",
        "|---|---:|---:|",
    ]

    for mode in ["no_loop", "loop_1", "loop_n"]:
        rows = by_mode.get(mode, [])
        if not rows:
            continue
        scores = [r["scores"].get("total", 0) for r in rows if isinstance(r["scores"].get("total"), (int, float))]
        iters = [r["iterations"] for r in rows]
        avg_score = round(sum(scores) / len(scores), 2) if scores else "n/a"
        avg_iters = round(sum(iters) / len(iters), 1) if iters else "n/a"
        lines.append(f"| `{mode}` | {avg_score} | {avg_iters} |")

    lines += ["", "## Question-Level Results", "",
              "| Question | Difficulty | no_loop | loop_1 | loop_n |",
              "|---|---|---:|---:|---:|"]

    score_map = {}
    for r in results:
        score_map[(r["question_id"], r["mode"])] = r["scores"].get("total", "—")

    for q in BENCHMARK:
        no  = score_map.get((q.id, "no_loop"), "—")
        l1  = score_map.get((q.id, "loop_1"), "—")
        ln  = score_map.get((q.id, "loop_n"), "—")
        lines.append(f"| {q.id} | {q.difficulty} | {no} | {l1} | {ln} |")

    path.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
