"""
Quick sanity check — run one question through loop_1 to confirm the pipeline works.
Swap in any question from benchmark/questions.py to test different ones.
"""

import json
from src.orchestrator import run

result = run(
    "Did real wages grow or decline during the 2021-2022 inflation surge?",
    mode="loop_1",  # use loop_n for full system, no_loop for baseline
)

print("\n--- FINAL ANSWER ---")
print(json.dumps(result["final_answer"], indent=2))
print(f"\nMode: {result['mode']} | Iterations: {result['iterations']} | Cost: ${result['cost_estimate_usd']}")
