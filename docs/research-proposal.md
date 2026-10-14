# Research proposal

## Question and hypothesis

Can adaptive lexical, vector and structural retrieval improve the localization
and resolution of software engineering issues while reducing exploration cost?
The hypothesis is provisional; Mostaza does not claim superiority before paired
real execution provides evidence.

## Initial comparison

E0 uses the verified official baseline. E1 alters exploration through the
Graph-SDD protocol and hybrid retrieval instructions. Both use
`gemma-4-31b-it-qat-w4a16-ct`, the same sampling, global budget, repair behavior
and single-agent architecture. No new embedding service or model is trained.

Preselect three public tasks from Requests, FastAPI, and Rich or HTTPX based on
availability and documented selection rationale before inspecting outcomes.
Freeze exact instance IDs and resource hashes. Run both arms on the same cohort
through the official Kaggle harness. Reference solutions belong exclusively to
post-generation verification, never agent-visible task context.

## Measurements and limitations

Retain PASS/FAIL, duration, tool calls, token counts when supplied, exploration
operations, patch existence/validity and execution errors, with native run/trace
provenance. Preserve unavailable measurements explicitly. Compute paired raw
metric differences, denominators and missingness rather than replacing missing
values with zero or claiming statistical significance from this small pilot.

Local fixtures establish record and tooling contracts. Compiler acceptance
establishes configuration validity. Neither substitutes for actual Gemma runs.
Issue failures are experimental outcomes; inaccessible official resources or
execution evidence are prerequisites that must be reported honestly. A preliminary
report should explain outcomes, costs, threats to validity and the next measurable
improvement. Fine-tuning, specialized multiagents, external retrieval databases
and exhaustive parameter optimization are outside this phase.
