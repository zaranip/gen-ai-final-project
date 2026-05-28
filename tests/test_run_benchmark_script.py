import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.run_benchmark import (
    build_summary_rows,
    normalize_answer,
    write_json,
    write_markdown_summary,
    write_summary_csv,
)


class BenchmarkRunnerOutputTests(unittest.TestCase):
    def sample_results(self):
        return [
            {
                "question_id": "Q1",
                "question": "Did the Fed achieve a soft landing?",
                "difficulty": "medium",
                "tags": ["inflation", "recession"],
                "mode": "no_loop",
                "scores": {
                    "factual_accuracy": 6,
                    "reasoning_quality": 7,
                    "completeness": 5,
                    "total": 6.0,
                    "explanation": "Correct direction, thin evidence.",
                },
                "final_answer": {"claim": "Mostly yes."},
                "iterations": 1,
                "cost_estimate_usd": 0.11,
                "elapsed_seconds": 12.3,
            },
            {
                "question_id": "Q1",
                "question": "Did the Fed achieve a soft landing?",
                "difficulty": "medium",
                "tags": ["inflation", "recession"],
                "mode": "loop_1",
                "scores": {
                    "factual_accuracy": 8,
                    "reasoning_quality": 8,
                    "completeness": 7,
                    "total": 7.67,
                    "explanation": "Revision added the missing GDP evidence.",
                },
                "final_answer": {"claim": "Yes, with caveats."},
                "iterations": 2,
                "cost_estimate_usd": 0.19,
                "elapsed_seconds": 24.5,
            },
        ]

    def test_build_summary_rows_flattens_nested_result_records(self):
        rows = build_summary_rows(self.sample_results())

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["question_id"], "Q1")
        self.assertEqual(rows[0]["mode"], "no_loop")
        self.assertEqual(rows[0]["tags"], "inflation;recession")
        self.assertEqual(rows[0]["total"], 6.0)
        self.assertEqual(rows[1]["claim"], "Yes, with caveats.")

    def test_normalize_answer_repairs_embedded_tool_fields(self):
        answer = normalize_answer(
            {
                "claim": (
                    "M2 growth led CPI.</claim>\n"
                    '<parameter name="evidence_summary">M2 peaked first.</parameter>\n'
                    "<rationale>The lead depends on onset definitions.</rationale>"
                )
            }
        )

        self.assertEqual(answer["claim"], "M2 growth led CPI.")
        self.assertEqual(answer["evidence_summary"], "M2 peaked first.")
        self.assertEqual(
            answer["rationale"], "The lead depends on onset definitions."
        )

    def test_writers_create_json_csv_and_markdown_artifacts(self):
        rows = build_summary_rows(self.sample_results())
        config = {
            "run_id": "unit-test-run",
            "modes": ["no_loop", "loop_1"],
            "question_ids": ["Q1"],
            "max_iterations": 4,
        }

        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            write_json(out_dir / "raw_results.json", self.sample_results())
            write_summary_csv(out_dir / "summary.csv", rows)
            write_markdown_summary(out_dir / "summary.md", rows, config)

            raw = json.loads((out_dir / "raw_results.json").read_text())
            self.assertEqual(raw[1]["mode"], "loop_1")

            with open(out_dir / "summary.csv", newline="") as f:
                csv_rows = list(csv.DictReader(f))
            self.assertEqual(csv_rows[0]["question_id"], "Q1")
            self.assertEqual(csv_rows[1]["total"], "7.67")

            markdown = (out_dir / "summary.md").read_text()
            self.assertIn("# Benchmark Run Summary", markdown)
            self.assertIn("| loop_1 | 7.67 | 0.19 | 2.00 |", markdown)
            self.assertIn("Revision added the missing GDP evidence.", markdown)


if __name__ == "__main__":
    unittest.main()
