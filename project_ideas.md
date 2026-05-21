# Final Project Ideas

## 1. Auto-Research Loop with Self-Critique and Memory

**Shape:** Auto-research.
**Pitch:** A general-purpose agent that takes a research question, runs experiments (code, web search, dataset queries), critiques its own results, and iterates. Persistent memory across runs lets it avoid repeating dead ends. Finance angle: point it at an alpha-discovery or macro-forecasting question.
**Data:** Any structured dataset the team picks (Kaggle, HuggingFace, public APIs). Real data, no synthetic fallback.
**Evaluation:** Compare loop-N vs. loop-1 vs. no-loop on a held-out benchmark. Show at least one iteration where self-critique made things worse.
**Extension:** Closed-loop self-improvement with durable memory, not one-shot prompting.

## 2. Skill Marketplace for Claude Code

**Shape:** Tool / platform.
**Pitch:** A lightweight registry where users publish/install Claude Code skills with semver, dependencies, and trust scores. Includes a "skill linter" that audits skill files for prompt-injection risk and unsafe shell calls. Finance angle: enables analyst teams to share internal skills safely.
**Data:** Real corpus of public skills scraped from GitHub + a hand-built seed set.
**Evaluation:** Run the linter on N real skills; measure precision/recall of unsafe-pattern detection against a hand-labeled set. Demo install/run round-trip.
**Extension:** A reusable distribution layer for skills, not just one skill.

## 3. Hook-Based Guardrails for LLM Tool Use

**Shape:** Tool / safety layer.
**Pitch:** A set of Claude Code hooks (PreToolUse, PostToolUse) that intercept dangerous tool calls — file deletes, network egress to unknown hosts, large credential reads — and require structured approval. The LLM explains the risk in plain English before the user clicks through. Finance angle: makes Claude Code safer for desks handling PII or order data.
**Data:** Realistic command corpus + real session transcripts from team members.
**Evaluation:** False-positive / false-negative rates on a labeled set of 100 commands (50 safe, 50 risky). Compare against a regex-only baseline.
**Extension:** Hook-level enforcement, not prompt-level "please be careful."

## 4. Auto-Research Agent for Literature Review

**Shape:** Auto-research.
**Pitch:** Give the agent a research question; it searches arXiv/SSRN/Semantic Scholar, builds a citation graph, identifies seminal vs. derivative papers, and produces a structured survey with claims linked to citations. Finance angle: run it on "transformer-based volatility forecasting" and use the survey as a project starting point.
**Data:** arXiv API, Semantic Scholar API, OpenAlex.
**Evaluation:** Have a domain expert (or a teammate playing one) rate coverage and citation accuracy on 3 topics vs. a human-written survey on the same topic. Include hallucinated-citation failure case.
**Extension:** Citation grounding — every claim links to a real paper, verified by API.

## 5. Skill for Structured Document Extraction with Self-Verification

**Shape:** Agent use case.
**Pitch:** A `/extract` skill that turns any PDF (contracts, filings, research notes, invoices) into a JSON schema the user specifies. Includes a self-verification pass that re-reads the source and challenges its own extractions. Finance angle: 10-K table extraction, term-sheet parsing.
**Data:** A mixed corpus — public 10-Ks, legal contracts (CUAD dataset), invoices (open invoice datasets).
**Evaluation:** F1 on field-level extraction vs. a no-verify baseline and vs. a non-LLM tool (e.g., Unstructured.io). Failure analysis on tables with merged cells.
**Extension:** Two-pass self-verification is the contribution, not extraction itself.

## 6. Hook-Driven Provenance Tracker

**Shape:** Tool.
**Pitch:** A PostToolUse hook that logs every file the model read, every web fetch, and every tool output into a content-addressed provenance graph. End of session, generate a "where did this answer come from" report. Finance angle: audit trail for any analysis a regulator might later ask about.
**Data:** Real Claude Code session transcripts from the team's own usage.
**Evaluation:** On a set of 20 multi-step tasks, can a non-author reconstruct what evidence supported each conclusion using only the provenance report? Time-to-reconstruct as the metric.
**Extension:** Provenance as a first-class artifact of agent runs, not an afterthought.

## 7. Benchmark: Long-Context LLMs on Cross-Document Reasoning

**Shape:** Benchmark.
**Pitch:** Hand-build a benchmark of ~200 questions that require synthesizing info across 3+ documents (e.g., comparing claims in paper A with results in paper B and dataset C). Score Claude 4.7 1M, Sonnet 4.6, GPT-5, Gemini 2.x. Finance angle: include a sub-track on cross-filing comparisons.
**Data:** Public papers, filings, Wikipedia; team hand-labels ground truth.
**Evaluation:** Accuracy table by model × number-of-docs. Failure taxonomy: needle-in-haystack vs. genuine synthesis vs. cross-doc contradiction.
**Extension:** New benchmark — the cross-document labels are the contribution.

## 8. Auto-Research for Prompt Optimization

**Shape:** Auto-research / meta.
**Pitch:** An agent that takes a task spec + eval set and iteratively rewrites the prompt, runs the eval, reads its own results, and proposes refinements. DSPy-adjacent but Claude-Code-native. Finance angle: tune prompts for sentiment classification on earnings calls.
**Data:** Any open eval set (MMLU subsets, FinSent, custom team-built set).
**Evaluation:** Score improvement vs. starting prompt across 3 task types. Show one task where the optimizer overfit the eval set.
**Extension:** Self-improving prompts with held-out validation, not just train-set tuning.

## 9. Skill + Hook System for Reproducible Notebook Workflows

**Shape:** Tool.
**Pitch:** A `/notebook-check` skill plus a pre-commit hook that re-runs notebook cells, diffs outputs, flags hidden state issues (cells run out of order), and writes a reproducibility report. Finance angle: every research notebook in a quant team becomes provably reproducible before merge.
**Data:** Real notebooks from public quant/data repos seeded with reproducibility bugs.
**Evaluation:** Detection rate on 50 seeded bugs (out-of-order execution, mutable state, undeclared dependencies). Compare against `nbqa` / `papermill` alone.
**Extension:** Hook-enforced reproducibility gate, not a manual checklist.

## 10. Startup Pitch: "AutoAnalyst" — Auto-Research Workspace for Knowledge Workers

**Shape:** Startup pitch + working prototype.
**Pitch:** A general-purpose auto-research product: drop in a question and a data source, the system runs a multi-step research loop with skills (search, extract, summarize, critique), hooks (cite-everything, log-everything), and memory across sessions. Finance angle: pitch the buy-side analyst as the launch customer, but the product is industry-agnostic.
**Data:** Whatever the demo question requires — real APIs, public datasets, web.
**Evaluation:** Time-trial on 3 real research tasks (one in finance, one in science, one in policy) with vs. without AutoAnalyst. Blind-rated quality + time-to-draft. Include the case where the tool confidently asserted a false fact.
**Extension:** A product surface combining skills + hooks + auto-research, not a single notebook.