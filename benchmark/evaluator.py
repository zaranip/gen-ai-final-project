"""
LLM-based evaluator for open-ended research answers.

Because benchmark questions have no single canonical answer, a human-rubric
prompt scored by Claude Haiku grades each agent output on three dimensions
against the hand-curated reference answer.

Dimensions (0–10 each):
  factual_accuracy  — are specific data points, directions, and magnitudes correct?
  reasoning_quality — is causal logic sound? are alternatives considered?
  completeness      — does the answer address all key aspects of the question?

Usage:
    from benchmark.evaluator import evaluate
    from benchmark.questions import BENCHMARK

    q = BENCHMARK[0]
    scores = evaluate(q, agent_answer_dict)
"""

import json

import anthropic
from dotenv import load_dotenv

load_dotenv()

EVAL_SYSTEM = """You are an expert macroeconomic research evaluator. \
Score an AI agent's answer against a reference answer on three dimensions.

Scoring rubric (0–10 per dimension):
  10 — perfect; matches or exceeds reference in precision and depth
  7–9 — good; minor omissions or slight imprecision in numbers
  4–6 — partial; correct direction but missing key evidence or quantification
  1–3 — poor; major factual errors or fundamentally wrong reasoning
  0   — completely wrong or no relevant content

Be strict about numbers: an answer that gets direction right but magnitude wrong
should score no higher than 6 on factual_accuracy.

Return valid JSON only — no prose, no markdown fences."""

EVAL_PROMPT = """\
Question: {question}

Agent Answer:
  Claim:      {claim}
  Confidence: {confidence}
  Evidence:   {evidence_summary}
  Rationale:  {rationale}

Reference Answer: {reference_answer}
Reference Rationale: {reference_rationale}

Score this answer. Return JSON matching exactly:
{{
  "factual_accuracy":  <int 0-10>,
  "reasoning_quality": <int 0-10>,
  "completeness":      <int 0-10>,
  "total":             <float, average of three>,
  "explanation":       "<2–3 sentences explaining the scores>"
}}"""


def evaluate(question_obj, agent_answer: dict) -> dict:
    """
    Score an agent answer against a BenchmarkQuestion's reference.

    Args:
        question_obj:  A BenchmarkQuestion instance from benchmark/questions.py.
        agent_answer:  The "answer" sub-dict from ResearchAgent.investigate().

    Returns:
        {
          "factual_accuracy": int,
          "reasoning_quality": int,
          "completeness": int,
          "total": float,
          "explanation": str
        }
    On parse failure returns {"error": str, "raw": str}.
    """
    client = anthropic.Anthropic()

    prompt = EVAL_PROMPT.format(
        question=question_obj.question,
        claim=agent_answer.get("claim", ""),
        confidence=agent_answer.get("confidence", ""),
        evidence_summary=agent_answer.get("evidence_summary", ""),
        rationale=agent_answer.get("rationale", "")[:800],  # keep prompt manageable
        reference_answer=question_obj.reference_answer,
        reference_rationale=question_obj.reference_rationale,
    )

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=EVAL_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()

    # Strip accidental markdown fences
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1].lstrip("json").strip() if len(parts) > 1 else raw

    try:
        scores = json.loads(raw)
        # Recompute total in case the model rounded oddly
        dims = ["factual_accuracy", "reasoning_quality", "completeness"]
        if all(k in scores for k in dims):
            scores["total"] = round(sum(scores[k] for k in dims) / 3, 2)
        return scores
    except json.JSONDecodeError:
        return {"error": "Failed to parse evaluator output", "raw": raw}


def run_benchmark(mode: str = "loop_n", **orchestrator_kwargs) -> list:
    """
    Convenience function: run every benchmark question through the orchestrator
    and evaluate each result.

    Args:
        mode:                Passed to orchestrator.run().
        orchestrator_kwargs: Extra kwargs forwarded to orchestrator.run().

    Returns:
        List of dicts: [{question_id, mode, scores, final_answer, cost, iterations}, ...]
    """
    from benchmark.questions import BENCHMARK
    from src.orchestrator import run

    results = []
    for q in BENCHMARK:
        print(f"\n{'='*60}\n[{q.id}] {q.question[:70]}...")
        result = run(q.question, mode=mode, **orchestrator_kwargs)
        scores = evaluate(q, result["final_answer"])
        results.append({
            "question_id": q.id,
            "question": q.question,
            "difficulty": q.difficulty,
            "tags": q.tags,
            "mode": mode,
            "scores": scores,
            "final_answer": result["final_answer"],
            "iterations": result["iterations"],
            "cost_estimate_usd": result["cost_estimate_usd"],
            "elapsed_seconds": result["elapsed_seconds"],
        })
        print(f"  Score: {scores.get('total', 'N/A')}/10  |  Cost: ${result['cost_estimate_usd']}")

    return results
