# Final Project Instructions

## Overview

The final project is your opportunity to apply the tools and concepts from this course to a real problem in finance. You will either:

1. **Conduct original research** related to generative or agentic AI in finance, or
2. **Build a tool** — a generative or agentic AI application that is useful in finance.

This is not a traditional research paper. Think of your deliverable as something closer to a **blog post**, a **tool demo**, or a **startup pitch with a working prototype**. The goal is to showcase something concrete and practical — a new benchmark, a model comparison, a useful tool, or a compelling product idea backed by a working demo.

## Groups

Students must work in groups of **4**. You can start finding your group now.

## What You Turn In

Submit a single group GitHub repository (or zip) containing:

- A primary notebook or report file with the core work.
- An audience-facing writeup — a published blog, GitHub Pages site, static HTML, or equivalent. A reader should be able to scan your results without setting up an environment.
- A `README.md` with reproduction instructions.
- `requirements.txt`, `environment.yml`, or clear package notes.
- Supporting code, prompts, schemas, or scripts as needed.
- An AI usage statement: what tools you used, where they helped, and how you checked their outputs.

Keep secrets and API keys out of the submission.

### How to Submit

**Due date:** Wednesday, May 27, 2026 at 11:59 PM (Chicago time).

Email **Mark, Jeremy, and Viren (TA, viren.desai@aprio.com)** with one of the following:

- A link to your group GitHub repository, or
- A link to your published static site (GitHub Pages, blog, etc.), or
- A zip of the project attached to the email.

**All members of the group must be on the email.** A single submission per group is fine, but every team member needs to be cc'd so we have a record of who is on the team.

## Defense

Final projects will be defended in a short oral exam with the instructors. There are no slides. The interviewer drives from your submitted artifact. Each team member should be prepared to:

- Walk through the parts of the project they personally owned.
- Explain their design decisions — why this data, this method, this evaluation approach.
- Discuss what worked, what didn't, and what they would do differently.
- Name what the team produced that an AI tool would not have produced on its own.

### Scheduling Your Defense

Defenses will be held **May 28–31, 2026**. The teaching team will share a self-serve scheduling link closer to the date — students sign up directly for an available appointment time. Details will be announced later; no action is needed until that link goes out.

Students will also present to other student groups in **bilateral meetings**, which groups will schedule among themselves.

## Optional Proposal

Before diving into full execution, any team can submit a short proposal to get early feedback. Submitting a proposal earns participation credit (see the rubric below). Just send a short note (one page or less) covering:

- What you're building or investigating.
- What data or APIs you plan to use.
- How you plan to show it works (or doesn't).
- Any scope risks — what gets cut if time runs short?

Email the proposal to **Mark, Jeremy, and Viren (TA, viren.desai@aprio.com)**, with all group members cc'd. The teaching team will respond with feedback within a few days. If you don't submit a proposal, that's fine — just make sure your final submission meets the rubric below.

## Rubric

100 points total.

| Component | Points | Level | What We're Looking For |
|---|---:|---|---|
| Ambition and scope | 15 | Group | The project is substantial, goes beyond what was done in homework or lecture, and tackles a real finance problem. A project that repackages a class exercise will score poorly here. |
| Working artifact | 20 | Group | The thing works. A reviewer can run the notebook, use the tool, or view the demo. Results are reproducible from the submitted repo. |
| Evaluation and evidence | 15 | Group | The team showed that their approach works (or honestly showed where it doesn't). What counts as evidence depends on the project shape — see below. |
| Writeup and communication | 10 | Group | A clear, audience-facing writeup that a reader can follow without cloning the repo. Good structure, honest conclusions. |
| Defense | 30 | Group + Individual | Each team member can explain their contribution and defend the project's design decisions in a live oral exam. |
| Debrief | 5 | Individual | A short individual survey submitted after the defense. |
| Proposal | 5 | Group | Participation credit for submitting an optional early proposal. Teams that skip the proposal can still earn full marks on the other components. |

### What Counts as "Evaluation and Evidence"

You will be graded on the evaluation and evidence you provide for your proposed methodology or pitch. What that looks like is up to you, and it should be tailored to the kind of project you're doing — a forecasting study calls for different evidence than a startup pitch or a benchmark. The point is that you make a serious, honest case that your approach does what you claim it does.

To give a sense of what we have in mind, here are examples of the kind of evidence we'd find compelling for a few of the project shapes described in [Potential Project Ideas](./potential_final_projects.md). These are illustrative, not prescriptive — your project may call for something different.

- *Auto-research / forecasting*: Compare results before and after the AI-driven improvement loop. Report metrics on a held-out set. Include at least one case where the automated changes didn't help or made things worse.
- *Startup pitch*: Demo the working prototype. Show that the core functionality is feasible — not just a mockup. Explain what would need to be true for this to work at scale.
- *Benchmarks*: Run the evaluation across multiple models. Report results in a clear table or visualization. Discuss where models succeed and fail, and whether the benchmark itself has blind spots.
- *Agent use cases*: Show the agent running on real examples. Compare its output to what a human (or a simpler tool) would produce. Include at least one failure case — where the agent broke, hallucinated, or needed human intervention.
- *Web app*: Demo the app working with real data. Show the AI component adding value over a non-AI version of the same workflow. Discuss limitations and failure modes.

Whatever shape your project takes: if the AI component doesn't help, say so. A project that honestly concludes "the simple approach was better for this task" is more valuable than one that oversells a marginal improvement.

## Rules

### No Duplication

The final project must add materially new work beyond the homework assignments, lecture notebooks, and course examples. Earlier work can be a starting point, but not a resubmission.

If your project builds on HW1 (sentiment), course RAG examples, or any other module material, you must add at least one substantial extension: new data, a different method, a new downstream use, a different evaluation design, or a deeper analysis not present in the earlier work. Name the extension explicitly in your writeup.

### Real Data

Every project uses real data, real documents, or a real workflow. No notebook may silently switch to synthetic or fallback data when a file is missing or an API is down. If your data source is unavailable at grading time, your notebook should raise a clear error — not quietly generate fake data.

### AI Usage Disclosure

Disclose all AI use, including coding assistants, in your AI usage statement. State what tools produced, where they helped, and how you checked their outputs. This is not a penalty — it's part of the project discipline. Do not present AI-generated features or analyses as original source truth.

### Paid Services

Paid services are allowed. Document the provider, model or dataset, and approximate cost. If you expect to spend more than $50 per team, get instructor approval first.
