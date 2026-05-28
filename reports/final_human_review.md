# Final Human Review Checklist

Reviewer:
Date:

Use this file for the last read-through before submission. Write concrete edits
or blockers here, not in chat, so the final state is auditable.

## Read These Files

- `reports/final_report.md` - read end to end. This is the chosen primary
  submission artifact.
- `outputs/benchmark_runs/consolidated/summary.md` - check the final score table,
  Q5 improvement case, Q6 failure case, total costs, and evaluator notes.
- `reports/reference_answer_verification.md` - skim the six reference-answer
  audits and confirm the report's key numbers are supported.
- `docs/index.md` - quick parity check against the final report if GitHub Pages
  is being submitted as a public chartbook.

## Required Checks

- [ ] The headline matches the final result: `loop_n` averages 8.56 vs. 8.45 for
  `no_loop`, but costs $11.04 vs. $2.94.
- [ ] The report does not overclaim; it frames the result as a small,
  cost-qualified improvement.
- [ ] Q5 is presented as the strongest improvement case.
- [ ] Q6 is presented as the required failure case where critique overcomplicated
  a clean baseline answer, with an explicit caveat that evaluator calibration may
  have amplified the penalty.
- [ ] The six benchmark questions, reference verification, model names, costs,
  and AI usage statement are internally consistent.
- [ ] No stale language remains about missing Q3 results, old negative headline
  results, or an unfinished full benchmark.
- [ ] The final report is readable enough for submission without a notebook
  wrapper.

## Required Edits

Write any must-fix edits here with file paths and exact replacement text when
possible.

- TBD

## Submission Blockers

Write anything that should stop submission.

- TBD

## Optional Polish

Write non-blocking improvements here. Do not let these delay submission unless
the team agrees.

- TBD

## Sign-Off

- [ ] I read the final report end to end.
- [ ] I checked the benchmark summary against the report tables.
- [ ] I checked the reference audit for the key reported numbers.
- [ ] I am comfortable submitting `reports/final_report.md` as the primary
  artifact.
