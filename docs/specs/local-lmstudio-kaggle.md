# local-lmstudio-kaggle

Depends on: foundation, agent-retrieval

## Purpose

Provide the minimal local LM Studio to Kaggle delivery loop using the existing official harness.

## Requirements

REQ-1: Run the editable submission with the requested existing local Gemma model.
REQ-2: Package the same source for manual Kaggle delivery.
REQ-3: Preserve official evaluation and distinguish integration success from agent effectiveness.

## Rules and constraints

AC-1: The local run uses the existing LM Studio OpenAI-compatible server at configurable MOSTAZA_API_BASE (observed configuration http://127.0.0.1:1234/v1), verifies the configured model against its model catalog, and selects google/gemma-4-12b for the requested /gemma-4-12b; absent server/model/authentication is an explicit prerequisite failure with no silent substitution or model download.

AC-2: Local authentication is optional configuration (MOSTAZA_API_KEY); remove the Ollama-specific key and defaults. Do not print credentials or persist them in delivery artifacts. If the official OpenAI adapter requires a nonempty key for an unauthenticated server, document a neutral non-secret adapter placeholder only for that case; authenticated servers require the actual locally supplied secret.

AC-3: The documented setup/run/pack entrypoints reuse existing installed official packages and task data when configured; every parent and compiler import resolves mostaza from this worktree even when using the source checkout interpreter. Do not edit official packages, verifier, scorer, prompts, submission files, or machine compute configuration.

AC-4: Exactly one requests_7205 evaluation for this unchanged implementation candidate uses official swegemma, subprocess sandbox and concurrency 1. Preserve timeout_seconds=60, max_tool_calls=10, max_time_minutes=1, max_turns=50 and the official verification_timeout_seconds=300 default. Native trace evidence must show a model-produced tool call and its matching official tool response. Task timeout or unresolved FAIL may satisfy connectivity/tool acceptance; missing evidence, connection/auth/model failures, setup/verification infrastructure errors and outer gate timeout fail validation. No automatic whole-task retries or budget increases. For the already executed candidate 34ac6f3f863fabded3a2d07aca5669aee53920b4e8f1902f0c6d171cc4ff4d52, the corrected gate reuses its frozen native result/trace/log without new inference; bind HEAD, source-input inventory, and evidence hashes as specified in the plan. The official ATIF same-step tool observation is matched using extra.tool_name and a successful response, with timestamp ordering. Input/evidence drift fails closed and requires a new user decision before any additional run.

AC-5: Both local run and pack consume collect_submission(submission/) and its existing allowlisted include closure. The competition model in agent.yaml remains unchanged. The official directory/schema/compiler accepts the staged delivery; the ZIP contains exactly the collected agent bytes and excludes local configuration, credentials, task data, solutions, results and development tools.

AC-6: The generated notebook executes locally to reproduce the ZIP byte-for-byte and on Kaggle writes /kaggle/working/submission.zip; it loads no model, enables no GPU, and makes no network calls. Document editing submission/, LM Studio configuration, one-task execution, ZIP/notebook generation and the manual Kaggle continuation without claiming Kaggle acceptance or score.

## Product decisions

PD-1 — Local development selects the submission directly; historical explicit E0/E1 experiment packaging remains unchanged (plan: 2026-10-17-lmstudio-local-kaggle, 2026-10-17).
PD-2 — Start only the existing LM Studio server on configured loopback port after approval; use the already loaded google/gemma-4-12b model and unchanged compute configuration (plan: 2026-10-17-lmstudio-local-kaggle, 2026-10-17).

## Interfaces and data contracts

Commands: bash scripts/setup_local.sh; bash scripts/harness.sh run --task requests_7205; bash scripts/harness.sh pack. Local configuration: MOSTAZA_API_BASE, MOSTAZA_MODEL, optional MOSTAZA_API_KEY, MOSTAZA_DATA_DIR, and MOSTAZA_PYTHON for reuse of an existing interpreter. Configuration remains outside submission/. Native official task_results.jsonl and ATIF traces establish local evidence.

## Out of scope

Kaggle sessions/publication/submissions/quota, GPU Kaggle runs, model downloads, Colima, prompt improvement, historical matrices/scorer research, extra instrumentation/test suites/product paths, and the aborted CPU worktree.
