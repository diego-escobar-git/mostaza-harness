# budget-retrieval-calibration

Depends on: foundation, agent-retrieval, evaluation

## Purpose

Prepare controlled phase-2 budget calibration and observable retrieval diagnostics without contaminating experiments or spending unapproved GPU quota. Phase-1 real-run acceptance remains historical and unchanged.

## Requirements

REQ-1: Diagnose timeout and failed verification using authentic retained evidence.
REQ-2: Separate matched budget calibration from a later retrieval-instruction treatment.
REQ-3: Preserve faithful metrics, resource provenance, leakage isolation and explicit GPU authorization.

## Rules and constraints

AC-1: Preserve the original E0/E1 manifests, submission files, frozen three-task cohort and phase-1 evidence byte-for-byte. New explicit configuration IDs E0-B180, E1-B180, E0-B300, E1-B300 and E1-R180 identify separate immutable manifests and deterministic archives; E0/E1 remain valid legacy selections. Calibration changes only matched budget values: B180 uses timeout_seconds=180, max_time_minutes=3, max_tool_calls=30; B300 uses 300, 5, 50; both retain max_turns=50 and verification_timeout_seconds=300. Model, sampling, cache/compaction, task order, environment, tools, verification and repair policy are equal within each pair. Original prompts remain byte-exact for budget calibration.

AC-2: Review current official primary resources and pin their source identities before configuration validation. Use one official LlmAgent and existing native tools only. Fail closed on incompatible official APIs, unavailable resource provenance or differing pair conditions. No local model download, Colima change, external retrieval service, submission to the competition or public notebook is permitted.

AC-3: Produce reproducible offline diagnosis from retained native traces/results with hashed source locators and exact event identifiers. Separate event-to-event elapsed intervals from attributable model generation or tool execution time; do not infer unobserved spans. Analyze Requests generated patch and execution/verification evidence only after generation, keeping reference solutions and hidden tests outside agent-visible inputs, prompts, notebooks payloads and submission archives.

AC-4: Record per task lexical-command attempts, similarity-tool attempts, graph-neighbor/subgraph attempts, exempt and rejected attempts, and official charged calls separately, together with sourced token usage, timeout reason, generated/effective patch status and independent verification. Similarity invocation alone does not establish vector execution: classify vector versus lexical fallback only when response/source evidence establishes the backend; otherwise backend is null with reason. Metrics declare units, numerator, denominator, source, availability and trace coverage. Missing or incomplete telemetry is never zero; step token aggregates are counted once. Shell search counts are explicitly observed command classifications, not exhaustive search/read totals.

AC-5: Additional instrumentation is host-side trace analysis without changing the official runtime: extract tool call/response intervals only when matched timestamps exist, returned graph nodes and repeated explicit read ranges only when observable, and classify unexplained/compound shell commands as unknown. True localization time, relevant-context ratio, Recall@K, full unique files, pure model wall time and repair count remain null unless separately defined complete evidence supports them. Fixture tests cover native ATIF, malformed/missing fields, fallback, truncation, rejected calls and no double counting; fixtures never count as real evaluations.

AC-6: Prepare a separate E1-R180 recovery-instruction experiment, excluded from budget calibration. Its sole change from E1-B180 is the exploration section: after unsuccessful exact lexical lookup, verify a real fully qualified symbol, use symbol-seeded search_similar_code(k=5) for semantic uncertainty and get_code_neighbors(max_neighbors=10) or bounded get_code_subgraph for structural uncertainty, stop when context suffices and avoid repeated unproductive queries. One hop is default; a second requires observed evidence. Do not force tool calls, add task-specific hints, expose post-run findings to the model, or alter implementation/verification/repair instructions. Document the exact diff and assess actual adherence from traces only when executed.

AC-7: Prepare a reproducible private offline Kaggle notebook and preflight without starting GPU. The initial quota proposal is exactly six task evaluations (E0-B180 and E1-B180 across requests_7205, fastapi_15589, rich_3061), one NVIDIA L4 x4 session, concurrency=1, no retries, at most 120 wall-clock minutes from session start including startup/loading/compiler/generation/verification/export, at most 8 GPU-device-hours, and zero paid purchases. Require explicit separate human quota authorization before any remote GPU start. Check remaining quota and enforce a session deadline/watchdog with fail-closed launch and cleanup; inability to enforce the ceiling blocks execution. Budget approval is not GPU authorization.

AC-8: A 300-second calibration batch or E1-R180 comparison is a separate six-evaluation batch, never automatically launched. Propose B300 only if B180 remains time/tool constrained before implementation/verification; retain its failures and avoid selecting on success. Propose E1-R180 versus E0-B180 only after budget calibration is analyzed and held fixed, with a new contemporaneous matched pair, not reused baseline outcomes. Each later batch needs a new explicit quota decision and its own 120-minute/8-device-hour/$0 ceiling; no implicit combined authorization or restart is allowed.

AC-9: Always complete local preparation, compiler validation, diagnosis and documentation independently of GPU permission. Readiness reports explicitly label future runs NOT_RUN with reasons until authorized; this preparation checkpoint makes no claim of phase-2 real evaluation or retrieval success. If execution is specifically authorized, retain all six records including failures/NOT_RUN, immutable native acquisition receipts, exact config/archive/model/cohort bindings and reproducible paired comparison with coverage and limitations before describing real outcomes. A denial or missing quota is reported as pending real evaluation, not silently simulated or a successful benchmark.

AC-10: Exact local gates validate all new configuration closures with the pinned official compiler, leakage boundaries, legacy artifact immutability, metrics and report recomputation, quota defaults/ceilings, and notebook payload provenance without GPU. Preserve phase-1 evidence and its original normalizer receipts; changing host code must not rewrite historical evidence or pretend a new normalizer was executed in the old notebook. Reports are declared before creation, and no significance/superiority claim is made for this exploratory cohort.

## Product decisions

PD-1 — Start with three minutes and 30 charged tools, retaining five minutes/50 as a separately authorized follow-up; these are exploratory budgets, not measured optima or competition submission limits (plan: mostaza-phase2-budget-retrieval, 2026-10-13).
PD-2 — Keep budget-only prompts immutable and prepare a distinct recovery-instruction variant; never force graph/vector calls to improve telemetry (plan: mostaza-phase2-budget-retrieval, 2026-10-13).
PD-3 — Local readiness may close as preparation with real evaluation explicitly pending when no GPU authorization exists; historical evaluation:AC-4 remains satisfied only by the historical runs, never by this checkpoint (plan: mostaza-phase2-budget-retrieval, 2026-10-13).
PD-4 — GPU authorization is per concrete six-evaluation batch and separate from plan/gate and Git closure approval (plan: mostaza-phase2-budget-retrieval, 2026-10-13).

## Interfaces and data contracts

New configuration IDs are independent of E0/E1 analytical arm labels. Extend host schemas compatibly, preserving legacy schema-1 records and commands. Coverage metadata distinguishes complete trace coverage from partial observations and unobservable backend details. Diagnostic and authorization material is host-only and never enters the submitted dependency closure. Native sources remain private/ignored, compact hash-bound summaries are committed.

## Out of scope

No model/sampling sweep, new tasks, hidden-test-driven tuning, reference solutions, alternative runtime, mandatory retrieval-call quota, public notebook, competition submission, paid service, or implicit GPU consumption.
