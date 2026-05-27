# Team Execution Plan

## Project Scope

The project is a macroeconomic auto-research loop. It compares three research configurations on real FRED-backed questions:

- `no_loop`: one researcher answer, no critic, no persistent memory.
- `loop_1`: researcher answer, critic review, and one revision pass when the critic requests changes.
- `loop_n`: iterative researcher/critic loop with persistent memory across related runs.

The defensible final claim is not that the agent always improves with more loops. The defensible claim is narrower: the team built a reproducible experiment to test when self-critique and memory improve open-ended macroeconomic research, and it reports both improvements and failures honestly.

## Work Completed Before This Plan

Claire has already built the core prototype scaffold:

- Researcher and critic agents in `src/agents/`.
- FRED and optional Tavily tools in `src/tools/`.
- TF-IDF memory store in `src/memory/store.py`.
- Main orchestration in `src/orchestrator.py`.
- Six benchmark questions and LLM-based evaluator in `benchmark/`.
- README, requirements, `.env.example`, and output folders.

Zara has already contributed the project ideas, instructions, and proposal artifacts.

## Sankalp-Owned Implementation Scope

This pass focuses on the work that can be implemented immediately without waiting on teammates:

1. Protect the repository from accidental secret, log, cache, and generated-output commits.
2. Correct the `loop_1` experiment semantics so it performs one revision pass after a critic revision request.
3. Add tests around the experiment control flow so teammates can safely change prompts and benchmark content.
4. Add a reproducible benchmark runner that saves raw JSON, summary CSV, and a Markdown results digest.
5. Add a report handoff file that turns benchmark outputs into a final audience-facing writeup without inventing results.
6. Update README instructions so another team member can run and verify the experiment.

## Team Partition

| Member | Primary Ownership | Concrete Deliverables |
|---|---|---|
| Claire | Core agent behavior | Maintain researcher/critic prompts, tool schemas, Anthropic calls, and loop behavior. Explain why the critic uses independent data checks and a different model. |
| John | Benchmark validity | Verify reference answers against FRED/BLS-style primary data, record calculations, and flag any reference answer that is too loose or misleading. |
| Sankalp | Reproducibility and experiment infrastructure | Own `.gitignore`, tests, run scripts, result aggregation, cost/iteration tables, and final quality gate. |
| Zara | Narrative and submission | Convert proposal into final writeup/static page, integrate tables and failure cases, polish README and AI usage disclosure, and coordinate submission email. |

## Execution Order

1. Commit repository hygiene and this execution plan.
2. Add failing tests for `loop_1` revision semantics.
3. Fix `src/orchestrator.py` to match the intended experiment.
4. Add failing tests for benchmark-result summarization.
5. Implement the benchmark runner and output writers.
6. Update README and report handoff instructions.
7. Run local tests and syntax checks.
8. Commit with professional, narrowly scoped commit messages.

## Remaining Work For The Team

- Run the full benchmark after API keys are available.
- Verify all six reference answers against primary FRED data.
- Identify at least one case where self-critique worsens the answer.
- Convert the generated result digest into the final audience-facing artifact.
- Prepare each member's defense talking points from their owned component.

