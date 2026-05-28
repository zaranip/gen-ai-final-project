"""
Run the macro auto-research benchmark and persist reproducible artifacts.

The helper functions in this file are intentionally pure where possible so the
summary outputs can be tested without calling Anthropic, FRED, or Tavily.
"""

import argparse
import csv
import json
import os
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

from dotenv import load_dotenv

SUMMARY_FIELDS = [
    "question_id",
    "mode",
    "difficulty",
    "tags",
    "factual_accuracy",
    "reasoning_quality",
    "completeness",
    "total",
    "iterations",
    "cost_estimate_usd",
    "elapsed_seconds",
    "claim",
    "explanation",
]


def build_summary_rows(results: Iterable[dict]) -> list[dict]:
    """Flatten nested benchmark result records into CSV-friendly rows."""
    rows = []
    for item in results:
        scores = item.get("scores") or {}
        answer = normalize_answer(item.get("final_answer") or {})
        rows.append(
            {
                "question_id": item.get("question_id", ""),
                "mode": item.get("mode", ""),
                "difficulty": item.get("difficulty", ""),
                "tags": ";".join(item.get("tags", [])),
                "factual_accuracy": scores.get("factual_accuracy", ""),
                "reasoning_quality": scores.get("reasoning_quality", ""),
                "completeness": scores.get("completeness", ""),
                "total": scores.get("total", ""),
                "iterations": item.get("iterations", ""),
                "cost_estimate_usd": item.get("cost_estimate_usd", ""),
                "elapsed_seconds": item.get("elapsed_seconds", ""),
                "claim": answer.get("claim", ""),
                "explanation": scores.get("explanation", ""),
            }
        )
    return rows


def normalize_answer(answer: dict) -> dict:
    """Repair occasional XML-like field leakage in structured tool output."""
    out = dict(answer)
    claim = str(out.get("claim", "") or "")
    if "</claim>" not in claim:
        return out

    out["claim"] = _clean_text(claim.split("</claim>", 1)[0])
    for field in ["evidence_summary", "rationale", "confidence"]:
        if not out.get(field):
            extracted = _extract_embedded_field(claim, field)
            if extracted:
                out[field] = extracted
    if not out.get("open_questions"):
        extracted = _extract_embedded_field(claim, "open_questions")
        if extracted:
            out["open_questions"] = [extracted]
    return out


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(payload, f, indent=2, default=str)


def write_summary_csv(path: Path, rows: Sequence[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in SUMMARY_FIELDS})


def write_markdown_summary(path: Path, rows: Sequence[dict], config: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Benchmark Run Summary",
        "",
        f"- Run ID: `{config['run_id']}`",
        f"- Modes: `{', '.join(config['modes'])}`",
        f"- Questions: `{', '.join(config['question_ids'])}`",
        f"- Max iterations for `loop_n`: `{config['max_iterations']}`",
        "",
        "## Mode Summary",
        "",
        "| Mode | Avg Score | Total Cost USD | Avg Iterations |",
        "|---|---:|---:|---:|",
    ]

    for mode, mode_rows in _rows_by_mode(rows).items():
        avg_score = _mean(_numeric(row.get("total")) for row in mode_rows)
        total_cost = sum(_numeric(row.get("cost_estimate_usd")) for row in mode_rows)
        avg_iterations = _mean(_numeric(row.get("iterations")) for row in mode_rows)
        lines.append(
            f"| {mode} | {avg_score:.2f} | {total_cost:.2f} | {avg_iterations:.2f} |"
        )

    lines.extend(
        [
            "",
            "## Question-Level Results",
            "",
            "| Question | Mode | Score | Iterations | Cost USD | Claim |",
            "|---|---|---:|---:|---:|---|",
        ]
    )
    for row in rows:
        lines.append(
            "| {question_id} | {mode} | {total:.2f} | {iterations:.0f} | "
            "{cost:.2f} | {claim} |".format(
                question_id=row.get("question_id", ""),
                mode=row.get("mode", ""),
                total=_numeric(row.get("total")),
                iterations=_numeric(row.get("iterations")),
                cost=_numeric(row.get("cost_estimate_usd")),
                claim=_escape_table_text(str(row.get("claim", ""))),
            )
        )

    lines.extend(["", "## Evaluator Notes", ""])
    for row in rows:
        explanation = str(row.get("explanation", "")).strip()
        if explanation:
            lines.append(
                "- `{question_id}` `{mode}`: {explanation}".format(
                    question_id=row.get("question_id", ""),
                    mode=row.get("mode", ""),
                    explanation=explanation,
                )
            )

    lines.append("")
    path.write_text("\n".join(lines))


def run_experiment(
    modes: Sequence[str],
    question_ids: Sequence[str] | None,
    max_iterations: int,
    output_dir: Path,
    run_id: str,
) -> Path:
    """Run selected benchmark questions across selected modes and write artifacts."""
    validate_environment()

    from benchmark.evaluator import evaluate
    from benchmark.questions import BENCHMARK
    from src.orchestrator import run

    selected_questions = select_questions(BENCHMARK, question_ids)
    selected_ids = [q.id for q in selected_questions]
    run_dir = output_dir / run_id
    config = {
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "modes": list(modes),
        "question_ids": selected_ids,
        "max_iterations": max_iterations,
    }
    write_json(run_dir / "run_config.json", config)

    results = []
    for mode in modes:
        mode_memory_dir = run_dir / "memory_store" / mode if mode == "loop_n" else None
        for question in selected_questions:
            result = run(
                question.question,
                mode=mode,
                max_iterations=max_iterations,
                memory_dir=mode_memory_dir,
            )
            scores = evaluate(question, result["final_answer"])
            final_answer = normalize_answer(result["final_answer"])
            results.append(
                {
                    "question_id": question.id,
                    "question": question.question,
                    "difficulty": question.difficulty,
                    "tags": question.tags,
                    "mode": mode,
                    "scores": scores,
                    "final_answer": final_answer,
                    "final_critique": result["final_critique"],
                    "iterations": result["iterations"],
                    "cost_estimate_usd": result["cost_estimate_usd"],
                    "elapsed_seconds": result["elapsed_seconds"],
                }
            )

    rows = build_summary_rows(results)
    write_json(run_dir / "raw_results.json", results)
    write_summary_csv(run_dir / "summary.csv", rows)
    write_markdown_summary(run_dir / "summary.md", rows, config)
    return run_dir


def select_questions(benchmark, question_ids: Sequence[str] | None):
    if not question_ids:
        return list(benchmark)

    wanted = {qid.upper() for qid in question_ids}
    selected = [question for question in benchmark if question.id.upper() in wanted]
    found = {question.id.upper() for question in selected}
    missing = sorted(wanted - found)
    if missing:
        raise SystemExit(f"Unknown benchmark question id(s): {', '.join(missing)}")
    return selected


def validate_environment() -> None:
    load_dotenv()
    required = ["ANTHROPIC_API_KEY", "FRED_API_KEY"]
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        joined = ", ".join(missing)
        raise SystemExit(
            f"Missing required environment variable(s): {joined}. "
            "Copy .env.example to .env and fill in the keys before running."
        )


def parse_args(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser(
        description="Run the macro auto-research benchmark and save artifacts."
    )
    parser.add_argument(
        "--modes",
        nargs="+",
        default=["no_loop", "loop_1", "loop_n"],
        choices=["no_loop", "loop_1", "loop_n"],
        help="Experiment modes to run.",
    )
    parser.add_argument(
        "--questions",
        nargs="+",
        default=None,
        help="Optional benchmark question IDs, for example Q1 Q3.",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=4,
        help="Maximum researcher/critic iterations for loop_n.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/benchmark_runs"),
        help="Directory where run artifacts will be written.",
    )
    parser.add_argument(
        "--run-id",
        default=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"),
        help="Stable identifier for this run.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    run_dir = run_experiment(
        modes=args.modes,
        question_ids=args.questions,
        max_iterations=args.max_iterations,
        output_dir=args.output_dir,
        run_id=args.run_id,
    )
    print(f"Benchmark artifacts written to {run_dir}")
    return 0


def _rows_by_mode(rows: Sequence[dict]) -> dict[str, list[dict]]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[row.get("mode", "")].append(row)
    return dict(grouped)


def _numeric(value) -> float:
    if value in ("", None):
        return 0.0
    return float(value)


def _mean(values: Iterable[float]) -> float:
    values = list(values)
    if not values:
        return 0.0
    return sum(values) / len(values)


def _escape_table_text(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _extract_embedded_field(text: str, field: str) -> str:
    patterns = [
        rf"<{field}>(.*?)</{field}>",
        rf'<parameter name="{field}">(.*?)</{field}>',
        rf'<parameter name="{field}">(.*?)</parameter>',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.DOTALL)
        if match:
            return _clean_text(match.group(1))
    return ""


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


if __name__ == "__main__":
    raise SystemExit(main())
