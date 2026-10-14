# evaluation

Depends on: foundation, agent-retrieval

## Purpose

Produce honest paired experimental evidence while preventing reference-answer leakage.

## Requirements

REQ-1: Compare E0 and E1 on identical real public tasks under matched conditions.
REQ-2: Separate agent-visible data from reference solutions and verification tests.
REQ-3: Preserve traceable measurements and report uncertainty and missing data explicitly.

## Rules and constraints

AC-1: The benchmark cohort freezes exact existing public instance_id values, base commits and resource hashes before either arm runs, selecting one Requests, one FastAPI and one Rich or HTTPX task with a documented difficulty rationale; selection does not use successful outcomes or expose reference patches/tests to the agent. If those resources are unavailable the cohort remains pending, without invented IDs.

AC-2: Agent-visible task inputs contain only an allowlisted issue and snapshot context; reference patch and test_patch stay exclusively in isolated post-generation verification/analysis. Tests cover leakage through serialized inputs, logs, filesystem packaging and future repository history.

AC-3: Each immutable run record includes experiment/run ID, UTC timestamp, code commit plus working-tree/config/archive digest, model, harness/wheelhouse/dataset versions, exact cohort, inference parameters, budgets, environment and limitations. Per-task JSONL records distinguish PASS, FAIL, ERROR and NOT_RUN, patch presence/validity, test outcomes and sourced metrics; absent measurements are null with reasons, never zero or fabricated.

AC-4: At least one actual Gemma 4 execution and complete paired E0/E1 evaluation on the same frozen cohort take place in the official Kaggle environment. Both arms use the same fixed non-treatment conditions and official verification, with durable source run identifiers, trace/result and patch hashes. Missing authentication, resources or GPU leaves this criterion pending and prevents phase completion.

AC-5: A reproducible preliminary report computes matched E1-minus-E0 metrics for localization, context efficiency and engineering outcomes; it separates unavailable/estimated metrics, failures and simulation, reports denominators and provenance, and makes no significance or superiority claim from the small exploratory sample. Recall@K and relevant-context ratio are reported only with explicit post-run ground-truth mapping and definitions.

AC-6: Documentation provides exact verified setup, package, Kaggle execution, result import and report commands, obtained from the pinned official resources; it states observed baseline/hybrid outcomes, remaining blockers and next research steps. A local-only checkpoint never satisfies real compatibility or full phase completion.

## Product decisions

PD-1 — Select the three-task cohort before observed outcomes, recording rationale and exact IDs only after official dataset inspection (plan: mostaza-phase1-foundation, 2026-10-13).
PD-2 — Preserve pending real evaluation as an incomplete acceptance criterion; no synthetic run or local compiler test substitutes for it (plan: mostaza-phase1-foundation, 2026-10-13).
PD-3 — Treat results as exploratory and descriptive; null metrics need reasons, and paired differences require comparable measurements (plan: mostaza-phase1-foundation, 2026-10-13).

## Interfaces and data contracts

A run manifest references immutable task records and selected configuration. Task records identify experiment, instance, run kind (real_kaggle or synthetic_test), patch verification, elapsed seconds and metric value/unit/source/availability. Aggregation rejects duplicate task/arm keys, mixed cohorts/configurations and mismatched units. Report symbols/files/reads/searches/localization seconds, tokens/code volume/graph expansions/repeated context/relevance when measurable, and patch validity/tests/resolution/total seconds/repairs. Character counts are not tokens. Raw traces remain outside Git; retain compact reports and content-addressed references sufficient to reproduce calculations.

## Out of scope

Fine-tuning, reinforcement learning, specialized multiagents, external embedding/vector/graph services, public APIs, dashboards, deployment and exhaustive hyperparameter tuning are outside Phase 1. No model downloads on the Mac.
