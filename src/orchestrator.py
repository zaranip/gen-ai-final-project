"""
Orchestrator — the main entry point for running experiments.

Supports three modes that map directly to the evaluation design in the proposal:

  no_loop  — single-shot baseline (no critic, no memory)
  loop_1   — one researcher pass + one critic pass, memory disabled across runs
  loop_n   — full system: iterative critique + persistent memory across runs

Usage:
    from src.orchestrator import run
    result = run("Did the Fed achieve a soft landing?", mode="loop_n")
    print(result["final_answer"]["claim"])
"""

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

from src.agents.critic import CriticAgent
from src.agents.researcher import ResearchAgent
from src.memory.store import MemoryStore

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

Mode = Literal["no_loop", "loop_1", "loop_n"]

# Approximate per-token cost (USD) — Anthropic pricing as of May 2026
_COST = {
    "claude-opus-4-7":   {"input": 15 / 1e6, "output": 75 / 1e6},
    "claude-sonnet-4-6": {"input":  3 / 1e6, "output": 15 / 1e6},
    "claude-haiku-4-5-20251001": {"input": 0.8 / 1e6, "output": 4 / 1e6},
}


def run(
    question: str,
    mode: Mode = "loop_n",
    max_iterations: int = 5,
    researcher_model: str = "claude-opus-4-7",
    critic_model: str = "claude-sonnet-4-6",
    memory_dir: Optional[Path] = None,
) -> dict:
    """Run the research loop. mode = "no_loop" | "loop_1" | "loop_n"."""
    t0 = time.time()
    use_memory = (mode == "loop_n")
    memory_path = Path(memory_dir) if memory_dir is not None else None
    memory = MemoryStore(memory_path) if use_memory else None
    researcher = ResearchAgent(model=researcher_model)
    critic = CriticAgent(model=critic_model)

    run_log = {
        "question": question,
        "mode": mode,
        "researcher_model": researcher_model,
        "critic_model": critic_model,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "iterations": [],
    }

    total_tokens = {"input_tokens": 0, "output_tokens": 0}
    final_answer: Optional[dict] = None
    final_critique: Optional[dict] = None
    memory_context = memory.retrieve(question) if memory else None

    if mode == "no_loop":
        log.info("[no_loop] Investigating: %s", question[:80])
        result = researcher.investigate(question)
        _add_tokens(total_tokens, result["token_usage"])
        run_log["iterations"].append({"researcher": result, "critic": None})
        final_answer = result["answer"]

    elif mode == "loop_1":
        log.info("[loop_1] Initial investigation: %s", question[:80])
        result = researcher.investigate(question)
        _add_tokens(total_tokens, result["token_usage"])

        critique = critic.critique(question, result)
        _add_tokens(total_tokens, critique["token_usage"])

        verdict = critique["critique"].get("verdict", "accept")
        log.info("  Critic verdict: %s", verdict)

        run_log["iterations"].append({
            "iteration": 1,
            "researcher": result,
            "critic": critique,
            "verdict": verdict,
        })
        final_answer = result["answer"]
        final_critique = critique["critique"]

        if verdict != "accept":
            # One revision pass keyed off the critic's specific weaknesses.
            # Final answer is the revision; no second critic pass (that's loop_n).
            weaknesses = critique["critique"].get("weaknesses", [])
            critic_feedback = "\n".join(weaknesses)

            log.info("[loop_1] Revision pass")
            revised = researcher.investigate(
                question,
                critic_feedback=critic_feedback,
            )
            _add_tokens(total_tokens, revised["token_usage"])
            run_log["iterations"].append({
                "iteration": 2,
                "researcher": revised,
                "critic": None,
                "verdict": "revision_only",
            })
            final_answer = revised["answer"]

    else:
        max_iters = max_iterations
        critic_feedback: Optional[str] = None

        for i in range(max_iters):
            log.info("[%s] Iteration %d/%d", mode, i + 1, max_iters)

            r = researcher.investigate(
                question,
                memory_context=memory_context,
                critic_feedback=critic_feedback,
            )
            _add_tokens(total_tokens, r["token_usage"])

            c = critic.critique(question, r)
            _add_tokens(total_tokens, c["token_usage"])

            verdict = c["critique"].get("verdict", "accept")
            log.info("  Critic verdict: %s", verdict)

            run_log["iterations"].append({
                "iteration": i + 1,
                "researcher": r,
                "critic": c,
                "verdict": verdict,
            })

            final_answer = r["answer"]
            final_critique = c["critique"]

            if use_memory:
                memory.save(question, final_answer, final_critique, verdict)
                memory_context = memory.retrieve(question)

            if verdict == "accept":
                log.info("  Converged at iteration %d.", i + 1)
                break

            critic_feedback = "\n".join(c["critique"].get("weaknesses", []))

    elapsed = round(time.time() - t0, 1)
    _save_log(run_log)

    return {
        "question": question,
        "mode": mode,
        "final_answer": final_answer,
        "final_critique": final_critique,
        "iterations": len(run_log["iterations"]),
        "total_tokens": total_tokens,
        "cost_estimate_usd": _estimate_cost(
            total_tokens, researcher_model, critic_model
        ),
        "elapsed_seconds": elapsed,
    }


def _add_tokens(total: dict, usage: dict) -> None:
    total["input_tokens"] += usage.get("input_tokens", 0)
    total["output_tokens"] += usage.get("output_tokens", 0)


def _estimate_cost(
    tokens: dict,
    researcher_model: str,
    critic_model: str,
) -> float:
    # Rough split: researcher uses ~60% of tokens, critic ~40%
    r_rate = _COST.get(researcher_model, {"input": 15 / 1e6, "output": 75 / 1e6})
    c_rate = _COST.get(critic_model, {"input": 3 / 1e6, "output": 15 / 1e6})
    in_t = tokens["input_tokens"]
    out_t = tokens["output_tokens"]
    cost = (
        0.6 * in_t * r_rate["input"]
        + 0.6 * out_t * r_rate["output"]
        + 0.4 * in_t * c_rate["input"]
        + 0.4 * out_t * c_rate["output"]
    )
    return round(cost, 5)


def _save_log(run_log: dict) -> None:
    fname = LOG_DIR / f"run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(fname, "w") as f:
            json.dump(run_log, f, indent=2, default=str)
        log.info("  Log saved → %s", fname)
    except OSError as exc:
        log.warning("  Could not save log: %s", exc)
