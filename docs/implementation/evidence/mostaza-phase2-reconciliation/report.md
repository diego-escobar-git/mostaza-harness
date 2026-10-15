# Phase 2 reconciliation

Reconciliation only; iteration 2 research remains pending.

Develop `60ad0cec85bb36a1e65609ca2b1a743ba087384d` and unmerged PR2 `1b86b19f7654212c1d9f95eeca84d0e2a05db16b` remain separate.

Original SDD closure covers preparation. Later CPU work is ORDINARY, with its own scoped audits. No historical allowance or PASS transfers here.

## Acceptance reconciliation

Every source locator below is immutable; locator SHA256 and full requirement text are in source-inventory.json.

### foundation:AC-1 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/foundation.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:scripts/setup.sh#L5`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase1-foundation/report.md`.

Contract: AC-1: A fresh macOS development environment installs the locked Python 3.13 tooling with uv; setup validates the interpreter and never installs GPU model weights or changes global Colima configuration. Kaggle GPU execution follows the official notebook environment separately.

Locked local setup exists; fresh installation is not replayed here.

Locked local setup exists; fresh installation is not replayed here.


Pending: Validate fresh macOS setup from locked tooling under a separate approved environment scope.

### foundation:AC-2 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/foundation.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:pyproject.toml#L11`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase1-foundation/report.md`.

Contract: AC-2: The repository has the requested source, tests, submission, experiments, scripts, results and documentation structure, Apache-2.0 license, and ignore rules excluding credentials, virtual environments, weights, datasets, archives and bulky run outputs.

Repository packaging/license structure is versioned; ignored bulk resources stay external.

Repository packaging/license structure is versioned; ignored bulk resources stay external.


Pending: Preserve this historical preparation contract during separately approved integration.

### foundation:AC-3 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/foundation.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase1-foundation/resource-review.json#L1`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase1-foundation/report.md`.

Contract: AC-3: The resource inventory records official URLs, retrieval date, notebook and wheelhouse versions, wheel SHA-256 and Python requirements; HARNESS_README, sample submission and selected task resources are reviewed from official authenticated downloads before integration. Missing resources cause an explicit prerequisite failure, never invented API behavior.

Official acquisition identities are historical pins, not current remote requirements.

Official acquisition identities are historical pins, not current remote requirements.


Pending: Preserve this historical preparation contract during separately approved integration.

### foundation:AC-4 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/foundation.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase1-foundation/report.md#L59`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase1-foundation/report.md`.

Contract: AC-4: Local unit, integration, lint, formatting, type and package-build checks execute reproducibly; simulation, compiler-only validation and actual Gemma/Kaggle evaluation are distinguishable in documentation and results.

Historical local validation is separate from native Gemma execution.

Historical local validation is separate from native Gemma execution.


Pending: Preserve this historical preparation contract during separately approved integration.

### agent-retrieval:AC-1 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/agent-retrieval.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/packaging.py#L169`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase2-budget-retrieval/report.md`.

Contract: AC-1: E0 is a single Google ADK LlmAgent derived minimally from the official starter, using gemma-4-31b-it-qat-w4a16-ct, authorized tools, no LoRA and no Graph-SDD retrieval optimization; every removal or adjustment from the official sample is documented and its source hashed.

Packaging enforces declared single-agent closure and permitted model/tools; model behavior is not replayed.

Historical preparation/receipts only; PR2 is unmerged. Fresh checkout portability and actual model adherence are unproven.


Pending: Preserve this historical preparation contract during separately approved integration.

### agent-retrieval:AC-2 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/agent-retrieval.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:tests/unit/test_retrieval_policy.py#L14`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase2-budget-retrieval/report.md`.

Contract: AC-2: E1 preserves E0 model, generation parameters, tool availability, repair policy, budgets and environment; only exploration instructions change. It prioritizes exact lexical clues, then relevant one-hop graph neighbors and symbol-seeded similarity when useful; two-hop expansion needs explicit evidence, neighbors are bounded, visited symbols are reused and unproductive searches stop.

Prompt-policy fixtures cover exploration constraints; actual adherence remains unproven.

Historical preparation/receipts only; PR2 is unmerged. Fresh checkout portability and actual model adherence are unproven.


Pending: Preserve this historical preparation contract during separately approved integration.

### agent-retrieval:AC-3 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/agent-retrieval.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:tests/unit/test_retrieval_policy.py#L14`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase2-budget-retrieval/report.md`.

Contract: AC-3: E1 applies understandable context priorities: issue/test/stack-trace evidence and exact matches first, structural proximity and similarity next, then minimum sufficient code and low context cost; no learned ranker or claim of optimal weights. Understand, Explore, Implement and Verify remain phases of one agent, with E0-equivalent implementation and repair behavior.

Static instruction contract covers context priorities; no learned ranking efficacy follows.

Historical preparation/receipts only; PR2 is unmerged. Fresh checkout portability and actual model adherence are unproven.


Pending: Preserve this historical preparation contract during separately approved integration.

### agent-retrieval:AC-4 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/agent-retrieval.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase2-startup-run/trace-observations.json#L1`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase2-budget-retrieval/report.md`.

Contract: AC-4: Both configurations use official budget enforcement, check get_status at meaningful transitions, preserve time for patching and verification, and record observed model/tool calls, time, reads, graph expansions and repairs when exposed; starting numeric limits are copied from the inspected official baseline, shared across arms and labeled provisional until measured.

Published ordinary B180 trace observations distinguish recorded attempts and charged calls.

Observed trace counters only; backend/pure model time/repair remain null when unavailable.


Pending: Review integration separately, then validate a fresh candidate under a new protocol.

### agent-retrieval:AC-5 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/agent-retrieval.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/packaging.py#L503`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase2-budget-retrieval/report.md`.

Contract: AC-5: Packaging requires an explicit E0 or E1 selection, produces a deterministic submission.zip with root agent.yaml and only its allowed dependency closure, and fails on traversal, symlinks, unknown tools/models, forbidden files or missing includes. Both archives pass current official directory/schema/compiler validation; archive creation alone never establishes official evaluation compatibility.

Deterministic explicit configuration packaging plus published compiler receipts; archive validity is not task success.

Historical preparation/receipts only; PR2 is unmerged. Fresh checkout portability and actual model adherence are unproven.


Pending: Preserve this historical preparation contract during separately approved integration.

### agent-retrieval:AC-6 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/agent-retrieval.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:tests/integration/test_retrieval_contract.py#L28`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase2-budget-retrieval/report.md`.

Contract: AC-6: Official graph/embedding fixtures and source-based contract tests verify symbol lookup, missing/ambiguous symbols, unavailable graph data and bounded retrieval behavior without external encoders or databases; prompt-policy tests are never represented as proof that a real agent followed those policies.

Official retrieval contract fixtures cover tool interfaces; fixtures are not agent executions.

Historical preparation/receipts only; PR2 is unmerged. Fresh checkout portability and actual model adherence are unproven.


Pending: Preserve this historical preparation contract during separately approved integration.

### evaluation:AC-1 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/evaluation.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:experiments/cohort.json#L8`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase2-startup-run/report.md`.

Contract: AC-1: The benchmark cohort freezes exact existing public instance_id values, base commits and resource hashes before either arm runs, selecting one Requests, one FastAPI and one Rich or HTTPX task with a documented difficulty rationale; selection does not use successful outcomes or expose reference patches/tests to the agent. If those resources are unavailable the cohort remains pending, without invented IDs.

Frozen Requests/FastAPI/Rich identifiers remain historical cohort inputs; no task reselection.

Historical preparation/receipts only; PR2 is unmerged. Fresh checkout portability and actual model adherence are unproven.


Pending: Preserve this historical preparation contract during separately approved integration.

### evaluation:AC-2 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/evaluation.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:tests/unit/test_task_isolation.py#L15`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase2-startup-run/report.md`.

Contract: AC-2: Agent-visible task inputs contain only an allowlisted issue and snapshot context; reference patch and test_patch stay exclusively in isolated post-generation verification/analysis. Tests cover leakage through serialized inputs, logs, filesystem packaging and future repository history.

Leakage fixtures and allowlist contract separate agent inputs from post-generation reference analysis.

Historical preparation/receipts only; PR2 is unmerged. Fresh checkout portability and actual model adherence are unproven.


Pending: Preserve this historical preparation contract during separately approved integration.

### evaluation:AC-3 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/evaluation.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/contracts.py#L31`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase2-startup-run/report.md`.

Contract: AC-3: Each immutable run record includes experiment/run ID, UTC timestamp, code commit plus working-tree/config/archive digest, model, harness/wheelhouse/dataset versions, exact cohort, inference parameters, budgets, environment and limitations. Per-task JSONL records distinguish PASS, FAIL, ERROR and NOT_RUN, patch presence/validity, test outcomes and sourced metrics; absent measurements are null with reasons, never zero or fabricated.

Run/result contract preserves sourced identity, outcomes and nullable metrics; unavailable fields are not zero.

Historical preparation/receipts only; PR2 is unmerged. Fresh checkout portability and actual model adherence are unproven.


Pending: Preserve this historical preparation contract during separately approved integration.

### evaluation:AC-4 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/evaluation.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase2-startup-run/evaluation-records.json#L1`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase2-startup-run/report.md`.

Contract: AC-4: At least one actual Gemma 4 execution and complete paired E0/E1 evaluation on the same frozen cohort take place in the official Kaggle environment. Both arms use the same fixed non-treatment conditions and official verification, with durable source run identifiers, trace/result and patch hashes. Missing authentication, resources or GPU leaves this criterion pending and prevents phase completion.

Six historical B180 records exist; no new C8K-L1 evaluation is implied.

Historical phase1/B180 evidence only; C8K-L1 NOT_RUN; no phase completion or significance.


Pending: Review integration separately, then validate a fresh candidate under a new protocol.

### evaluation:AC-5 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/evaluation.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase2-startup-run/comparison.json#L1`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase2-startup-run/report.md`.

Contract: AC-5: A reproducible preliminary report computes matched E1-minus-E0 metrics for localization, context efficiency and engineering outcomes; it separates unavailable/estimated metrics, failures and simulation, reports denominators and provenance, and makes no significance or superiority claim from the small exploratory sample. Recall@K and relevant-context ratio are reported only with explicit post-run ground-truth mapping and definitions.

Published descriptive paired comparison retains failures and denominators; no significance or superiority.

Historical phase1/B180 evidence only; C8K-L1 NOT_RUN; no phase completion or significance.


Pending: Review integration separately, then validate a fresh candidate under a new protocol.

### evaluation:AC-6 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/evaluation.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/runbooks/kaggle-execution.md#L1`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase2-startup-run/report.md`.

Contract: AC-6: Documentation provides exact verified setup, package, Kaggle execution, result import and report commands, obtained from the pinned official resources; it states observed baseline/hybrid outcomes, remaining blockers and next research steps. A local-only checkpoint never satisfies real compatibility or full phase completion.

Versioned operational commands document historical paths; a new checkout needs fresh validation/resources.

Historical phase1/B180 evidence only; C8K-L1 NOT_RUN; no phase completion or significance.


Pending: Review integration separately, then validate a fresh candidate under a new protocol.

### budget-retrieval-calibration:AC-1 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/budget-retrieval-calibration.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:experiments/E0-B180/manifest.json#L3`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase2-budget-retrieval/report.md`.

Contract: AC-1: Preserve the original E0/E1 manifests, submission files, frozen three-task cohort and phase-1 evidence byte-for-byte. New explicit configuration IDs E0-B180, E1-B180, E0-B300, E1-B300 and E1-R180 identify separate immutable manifests and deterministic archives; E0/E1 remain valid legacy selections. Calibration changes only matched budget values: B180 uses timeout_seconds=180, max_time_minutes=3, max_tool_calls=30; B300 uses 300, 5, 50; both retain max_turns=50 and verification_timeout_seconds=300. Model, sampling, cache/compaction, task order, environment, tools, verification and repair policy are equal within each pair. Original prompts remain byte-exact for budget calibration.

Pinned B180 manifest; B300/R180 remain separate prepared configurations and startup-v3 serving delta prevents a clean phase1 causal comparison.

B180 180s/3min/30 calls; B300 300s/5min/50; max_turns50/verify300 unchanged. startup-v3 serving differs from phase1; no causal superiority.


Pending: Review integration separately, then validate a fresh candidate under a new protocol.

### budget-retrieval-calibration:AC-2 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/budget-retrieval-calibration.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase2-budget-retrieval/resource-review.json#L43`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase2-budget-retrieval/report.md`.

Contract: AC-2: Review current official primary resources and pin their source identities before configuration validation. Use one official LlmAgent and existing native tools only. Fail closed on incompatible official APIs, unavailable resource provenance or differing pair conditions. No local model download, Colima change, external retrieval service, submission to the competition or public notebook is permitted.

Official wheel/API pins were reviewed historically; this checker hashes retained resources only.

Historical preparation/receipts only; PR2 is unmerged. Fresh checkout portability and actual model adherence are unproven.


Pending: Preserve this historical preparation contract during separately approved integration.

### budget-retrieval-calibration:AC-3 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/budget-retrieval-calibration.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/research/trace_diagnostics.py#L607`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase2-budget-retrieval/report.md`.

Contract: AC-3: Produce reproducible offline diagnosis from retained native traces/results with hashed source locators and exact event identifiers. Separate event-to-event elapsed intervals from attributable model generation or tool execution time; do not infer unobserved spans. Analyze Requests generated patch and execution/verification evidence only after generation, keeping reference solutions and hidden tests outside agent-visible inputs, prompts, notebooks payloads and submission archives.

Offline trace/patch diagnosis is post-generation and must not enter prompts or agent payloads.

Diagnosis strictly post-generation; references/tests must stay outside agent-visible inputs.


Pending: Preserve this historical preparation contract during separately approved integration.

### budget-retrieval-calibration:AC-4 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/budget-retrieval-calibration.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/research/trace_diagnostics.py#L99`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase2-budget-retrieval/report.md`.

Contract: AC-4: Record per task lexical-command attempts, similarity-tool attempts, graph-neighbor/subgraph attempts, exempt and rejected attempts, and official charged calls separately, together with sourced token usage, timeout reason, generated/effective patch status and independent verification. Similarity invocation alone does not establish vector execution: classify vector versus lexical fallback only when response/source evidence establishes the backend; otherwise backend is null with reason. Metrics declare units, numerator, denominator, source, availability and trace coverage. Missing or incomplete telemetry is never zero; step token aggregates are counted once. Shell search counts are explicitly observed command classifications, not exhaustive search/read totals.

Trace classifier separates observable attempts, responses and availability; backend remains unknown without evidence.

Recorded E0 46 events/42 charged/409334 tokens; E1 64/60/664669. Zero named graph/similarity in recorded coverage; backend null.


Pending: Review integration separately, then validate a fresh candidate under a new protocol.

### budget-retrieval-calibration:AC-5 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/budget-retrieval-calibration.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:tests/unit/test_trace_diagnostics.py#L12`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase2-budget-retrieval/report.md`.

Contract: AC-5: Additional instrumentation is host-side trace analysis without changing the official runtime: extract tool call/response intervals only when matched timestamps exist, returned graph nodes and repeated explicit read ranges only when observable, and classify unexplained/compound shell commands as unknown. True localization time, relevant-context ratio, Recall@K, full unique files, pure model wall time and repair count remain null unless separately defined complete evidence supports them. Fixture tests cover native ATIF, malformed/missing fields, fallback, truncation, rejected calls and no double counting; fixtures never count as real evaluations.

Malformed/missing/native trace fixtures validate host instrumentation, never real evaluation or complete recall.

Host trace instrumentation only; ATIF empty-call discrepancy retained. Localization, Recall@K, context ratio, pure timing/repair null without full evidence.


Pending: Review integration separately, then validate a fresh candidate under a new protocol.

### budget-retrieval-calibration:AC-6 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/budget-retrieval-calibration.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:experiments/E1-R180/manifest.json#L3`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase2-budget-retrieval/report.md`.

Contract: AC-6: Prepare a separate E1-R180 recovery-instruction experiment, excluded from budget calibration. Its sole change from E1-B180 is the exploration section: after unsuccessful exact lexical lookup, verify a real fully qualified symbol, use symbol-seeded search_similar_code(k=5) for semantic uncertainty and get_code_neighbors(max_neighbors=10) or bounded get_code_subgraph for structural uncertainty, stop when context suffices and avoid repeated unproductive queries. One hop is default; a second requires observed evidence. Do not force tool calls, add task-specific hints, expose post-run findings to the model, or alter implementation/verification/repair instructions. Document the exact diff and assess actual adherence from traces only when executed.

Separate recovery variant exists; no R180 model run or demonstrated adherence.

E1-R180 prepared but NOT_RUN; no demonstrated exploration adherence.


Pending: Preserve this historical preparation contract during separately approved integration.

### budget-retrieval-calibration:AC-7 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/budget-retrieval-calibration.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/phase2.py#L85`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase2-budget-retrieval/report.md`.

Contract: AC-7: Prepare a reproducible private offline Kaggle notebook and preflight without starting GPU. The initial quota proposal is exactly six task evaluations (E0-B180 and E1-B180 across requests_7205, fastapi_15589, rich_3061), one NVIDIA L4 x4 session, concurrency=1, no retries, at most 120 wall-clock minutes from session start including startup/loading/compiler/generation/verification/export, at most 8 GPU-device-hours, and zero paid purchases. Require explicit separate human quota authorization before any remote GPU start. Check remaining quota and enforce a session deadline/watchdog with fail-closed launch and cleanup; inability to enforce the ceiling blocks execution. Budget approval is not GPU authorization.

Historical fail-closed launch readiness and notebook preparation do not grant a new GPU session.

Historical operational closeout includes polling gap and unknown physical release; no transferable quota.


Pending: Review integration separately, then validate a fresh candidate under a new protocol.

### budget-retrieval-calibration:AC-8 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/budget-retrieval-calibration.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/phase2.py#L517`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase2-budget-retrieval/report.md`.

Contract: AC-8: A 300-second calibration batch or E1-R180 comparison is a separate six-evaluation batch, never automatically launched. Propose B300 only if B180 remains time/tool constrained before implementation/verification; retain its failures and avoid selecting on success. Propose E1-R180 versus E0-B180 only after budget calibration is analyzed and held fixed, with a new contemporaneous matched pair, not reused baseline outcomes. Each later batch needs a new explicit quota decision and its own 120-minute/8-device-hour/$0 ceiling; no implicit combined authorization or restart is allowed.

Scheduling contract separates later batches; consumed individual allocations cannot be reused.

B300/R180 NOT_RUN; each requires a new contemporaneous pair and explicit six-evaluation allocation.


Pending: Preserve this historical preparation contract during separately approved integration.

### budget-retrieval-calibration:AC-9 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/budget-retrieval-calibration.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase2-startup-run/evaluation-records.json#L1`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase2-budget-retrieval/report.md`.

Contract: AC-9: Always complete local preparation, compiler validation, diagnosis and documentation independently of GPU permission. Readiness reports explicitly label future runs NOT_RUN with reasons until authorized; this preparation checkpoint makes no claim of phase-2 real evaluation or retrieval success. If execution is specifically authorized, retain all six records including failures/NOT_RUN, immutable native acquisition receipts, exact config/archive/model/cohort bindings and reproducible paired comparison with coverage and limitations before describing real outcomes. A denial or missing quota is reported as pending real evaluation, not silently simulated or a successful benchmark.

Ordinary six-row actual B180 acquisition succeeds as acquisition, not task resolution; current candidate NOT_RUN.

Original closure six NOT_RUN; ordinary startup-v3 six real rows: each arm PASS0/FAIL2/ERROR1; new candidate NOT_RUN.


Pending: Review integration separately, then validate a fresh candidate under a new protocol.

### budget-retrieval-calibration:AC-10 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/budget-retrieval-calibration.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:scripts/check_phase2.py#L34`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-phase2-budget-retrieval/report.md`.

Contract: AC-10: Exact local gates validate all new configuration closures with the pinned official compiler, leakage boundaries, legacy artifact immutability, metrics and report recomputation, quota defaults/ceilings, and notebook payload provenance without GPU. Preserve phase-1 evidence and its original normalizer receipts; changing host code must not rewrite historical evidence or pretend a new normalizer was executed in the old notebook. Reports are declared before creation, and no significance/superiority claim is made for this exploratory cohort.

Original local validation entry point is inspected as source only; no historical gate is run or transferred.

Historical gate/audit only; no transferable PASS to this branch/candidate.


Pending: Preserve this historical preparation contract during separately approved integration.

### context-verification:AC-CV1 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/context-verification.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/context_variants.py#L83`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-context-verification/report.md`.

Contract: AC-CV1: Preserve all original submission/configuration files, historical manifests,
candidates, native outcomes and compact evidence. Context rejection, time/tool
limits, verification failure and unknown verification binding are independent
qualifications; never silently reclassify historical FAIL/ERROR as PASS.

Original variants preserved through new explicit derived manifests.

C8K/Q1/R1 preparation and CPU fixtures; context/retrieval treatment has no new model evaluation.


Pending: Run a separately approved matched context/retrieval comparison after readiness.

### context-verification:AC-CV2 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/context-verification.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/verification_origin.py#L51`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-context-verification/report.md`.

Contract: AC-CV2: Observe module identity through the official sandbox exec interface, with
interpreter, cwd/import paths, expected/resolved file hash and explicit coverage.
A sibling process is not proof of exact verifier-process execution. Unknown or
failed editable installation and unsupported exact-process receipts block new GPU
readiness. Never alter verifier PYTHONPATH, secret tests, scoring, dependency
source or official setup silently. If the official setup/receipt is inaccessible,
finish independent work and document the required protocol decision.

Module-origin observation is diagnostic; origin alone does not prove task semantics.

C8K/Q1/R1 preparation and CPU fixtures; context/retrieval treatment has no new model evaluation.


Pending: Run a separately approved matched context/retrieval comparison after readiness.

### context-verification:AC-CV3 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/context-verification.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/context_variants.py#L83`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-context-verification/report.md`.

Contract: AC-CV3: E0-C8K/E1-C8K change only max_output_tokens16384 to8192 from corresponding
B180 closures. Keep thinking_budget4096/include_thoughts=true, temperature0.2,
top_p0.95,32768 context, native cache/compaction null, serial-memory-v3, original
cohort,180s generation/30 tools/50 turns/300s verification unchanged. Model and
sampling/environment/repair conditions match within every contemporaneous pair.
Larger nominal input headroom is not guaranteed future fit. Compaction is a
separate unapproved treatment, not silently enabled.

C8K context treatment is prepared; no model evaluation tests its effect.

C8K/Q1/R1 preparation and CPU fixtures; context/retrieval treatment has no new model evaluation.


Pending: Run a separately approved matched context/retrieval comparison after readiness.

### context-verification:AC-CV4 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/context-verification.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/context_variants.py#L62`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-context-verification/report.md`.

Contract: AC-CV4: E0-C8K-Q1/E1-C8K-Q1 share identical generic Q1 additions: bounded symbol-led
reads/exact keys/returned-range validation, one duplicate then bounded alternate
read, correct workspace imports, nonzero assertion failures with negative/positive
controls and final source-diff cleanup. No task-specific hints, netrc examples,
reference solutions or hidden expectations enter prompts or archives.

Q1 generic instruction treatment is distinct from context calibration; adherence untested.

C8K/Q1/R1 preparation and CPU fixtures; context/retrieval treatment has no new model evaluation.


Pending: Run a separately approved matched context/retrieval comparison after readiness.

### context-verification:AC-CV5 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/context-verification.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/context_variants.py#L62`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-context-verification/report.md`.

Contract: AC-CV5: E1-C8K-Q1-R1 changes only E1-C8K-Q1's exploration section using the prepared
recovery policy. Name the unresolved navigation question and useful verified-symbol
query or a justified skip. No graph/vector quota; use k5,10-neighbor/one-hop pilot
bounds, and evidence before a second hop. Decisions are measured only when observed
in native text; missing decisions/backend receipts remain null with reasons.

R1 exploration-only treatment is prepared; no contemporaneous comparison executed.

C8K/Q1/R1 preparation and CPU fixtures; context/retrieval treatment has no new model evaluation.


Pending: Run a separately approved matched context/retrieval comparison after readiness.

### context-verification:AC-CV6 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/context-verification.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/context_candidate.py#L33`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-context-verification/report.md`.

Contract: AC-CV6: Prepare GPU-disabled, output-free private-intent notebooks with explicit
matched selection and source/archive hashes, retaining one official LlmAgent and
native harness/tools. Host diagnosis and outcome fixtures never enter their
payload. Bound the external read-only monitor before T0; require fresh successful
initialization, exact-version fallback without Active Events, timeout/escalation
for stalled reads and available browser stop controls. Monitoring does not prove
physical release and implements no session start/cancel action.

Disabled notebook source/payload checks establish preparation, not full Linux/model loop.

C8K/Q1/R1 preparation and CPU fixtures; context/retrieval treatment has no new model evaluation.


Pending: Run a separately approved matched context/retrieval comparison after readiness.

### context-verification:AC-CV7 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/context-verification.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-context-verification/compiler-and-fixtures.json#L1`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-context-verification/report.md`.

Contract: AC-CV7: Run the six commands of the approved exact deterministic gate. Native CPU
fixtures must exercise actual import shadowing, E0 None regression, ADK optional-key
filtering, context known/unknown bounds, bounded-read recovery and pre-T0/hung
observation behavior; compile all five closures using the pinned official compiler.
Require independent PASS with zero open findings. Local PASS does not establish
benchmark results, historical verifier origin, model adherence or GPU readiness.

Published CPU/compiler fixture receipt is historical and scoped; no native replay here.

C8K/Q1/R1 preparation and CPU fixtures; context/retrieval treatment has no new model evaluation.


Pending: Run a separately approved matched context/retrieval comparison after readiness.

### pcv01:AC-P1 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/pcv01.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/pytest_origin_receipt.py#L223`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-pcv01-access/report.md`.

Contract: AC-P1: Provide an opt-in diagnostic pytest plugin, copied only into disposable
native CPU sandbox environments as mostaza_origin_receipt.py. Its sole activation
is adding `-p mostaza_origin_receipt` to the unchanged synthetic verifier command.
No entry point, autoload registration, conftest injection, product installation,
PYTHONPATH repair, official source patch or real harness configuration change.

Opt-in diagnostic hook observes disposable pytest processes only.

Public source and local diagnostic evidence; private scorer parity remains unknown and readiness false.


Pending: Keep parity unknown until authoritative private scorer evidence is available.

### pcv01:AC-P2 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/pcv01.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/pytest_origin_receipt.py#L151`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-pcv01-access/report.md`.

Contract: AC-P2: At tryfirst pytest_runtest_call, observe ONLY already-loaded named public
product modules from sys.modules and supported module-level Python functions.
Accept no item/test arguments. Do not import/reload product, inspect test bodies,
names, arguments, fixtures or expectations; do not alter product namespaces,
imports, search paths, environment, test outcomes, exceptions or scoring.

Loaded public-module observation avoids treating an import probe as scorer equivalence.

Public source and local diagnostic evidence; private scorer parity remains unknown and readiness false.


Pending: Keep parity unknown until authoritative private scorer evidence is available.

### pcv01:AC-P3 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/pcv01.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/pytest_origin_receipt.py#L45`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-pcv01-access/report.md`.

Contract: AC-P3: Configuration is host-only, bounded and explicit: schema1, absolute receipt
outside workspace, reviewed module/symbol/expected file and at most five pinned
public files per target (at most20 targets). Exclude test/conftest paths and module
names. Bound file reads to2MiB and append only to a regular nonsymlink destination
(up to10MiB before append). Fail silently on diagnostic errors; the host marks
missing receipts unavailable with a reason. Never reinterpret missing as zero.

Bounded host-only receipt configuration remains outside agent payloads.

Public source and local diagnostic evidence; private scorer parity remains unknown and readiness false.


Pending: Keep parity unknown until authoritative private scorer evidence is available.

### pcv01:AC-P4 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/pcv01.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/pytest_origin_receipt.py#L109`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-pcv01-access/report.md`.

Contract: AC-P4: Receipts identify PID/interpreter/Python/pytest, timestamp, cwd/sys.path,
plugin hash and each requested public target's module origin/file hash, expected
binding and function code/source hashes. Nulls carry reasons. Read only reviewed
public files. Do not hash code from a replacement originating in test/fixture
files. A reexport from a different reviewed public file may have a code hash but
must not misattribute the importing module's source segment. Module binding does
not prove unchanged function semantics. No source text or code constants emitted.

Function/origin witnesses identify executed source; semantic result remains separate.

Public source and local diagnostic evidence; private scorer parity remains unknown and readiness false.


Pending: Keep parity unknown until authoritative private scorer evidence is available.

### pcv01:AC-P5 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/pcv01.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-pcv01-cpu/cpu-controls.json#L1`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-pcv01-access/report.md`.

Contract: AC-P5: Validate actual native SubprocessManager pytest processes with and without
the plugin using the same synthetic inputs, environment, options and targets.
Exercise positive/negative outcomes, installed-package shadowing, fixture function
replacement, setup error, logging failure and missing configuration, under both
pytest8.4.2 and9.1.1. Require exit/JUnit-count parity, same PID/function identity
at the call hook when supported, no dynamic product accessor/import, no fixture
expectation/name leakage and no source/test mutation. Code changed later in the
test is outside this point-in-time receipt's coverage.

Published local native controls cover this diagnostic protocol; no full Kaggle parity.

Public source and local diagnostic evidence; private scorer parity remains unknown and readiness false.


Pending: Keep parity unknown until authoritative private scorer evidence is available.

### pcv01:AC-P6 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/pcv01.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/scorer_contract.py#L206`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-pcv01-access/report.md`.

Contract: AC-P6: Review official pytest APIs and pinned harness sources. Clearly separate
public API support from organizer authorization and real scorer parity, which
remain unknown without authorized setup provenance. The native fixed command is
not changed. Test both pytest versions on local Python3.13; Python3.12 grammar
validation is not Python3.12 runtime/Kaggle validation.

Pinned public API/source review is not access to private scorer deployment.

Public source and local diagnostic evidence; private scorer parity remains unknown and readiness false.


Pending: Keep parity unknown until authoritative private scorer evidence is available.

### pcv01:AC-P7 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/pcv01.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:tests/integration/test_pcv01_cpu_contract.py#L10`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-pcv01-access/report.md`.

Contract: AC-P7: Keep plugin, raw synthetic tests/receipts and analyst diagnosis outside
all submitted closures/notebook payloads. Preserve original experiments, notebooks,
lock/dependencies and historical evidence byte-exact against eb04b1c. Preserve
blocked GPU readiness and the sibling observer's fail-closed behavior. No model,
GPU, remote sessions, competition submission, purchases or large model download.

Acceptance gate: run the six existing CPU correction commands in their recorded
order, followed by `.venv/bin/python scripts/check_pcv01.py --check` (optionally
retain raws in a NEW results directory). Tests, lint/types/build, official compiler,
historical evidence recomputation and native controls must actually pass. Record
command statuses/source hashes and obtain independent PASS with zero open findings
before commit/push/update PR2, without merge. The exact seven-command gate and
reproduction prerequisites are recorded in the new CPU evidence report. A local
PASS never unlocks GPU or proves historical Requests imports/task correctness.

Diagnostic isolation contract keeps analyst/plugin evidence outside agent inputs.

Public source and local diagnostic evidence; private scorer parity remains unknown and readiness false.


Pending: Keep parity unknown until authoritative private scorer evidence is available.

### pcv01:AC-P8 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/pcv01.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-pcv01-access/public-sources.json#L1`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-pcv01-access/report.md`.

Contract: AC-P8: Retain the individually downloaded public sandbox/setup.py and two public
Docker recipes as ignored, hash-pinned source data. Record source URL/path, bytes,
acquisition method/date and null version/reason when the UI exposes no numeric
version. Bound downloads to four allowlisted text artifacts,256KiB each/1MiB total.
A metric wrapper may be acquired only when an official public/redacted source is
actually supplied; no guessed private paths,403 bypass or credential expansion.
The earlier dataset403 does not establish public competition-file inaccessibility.

Individually acquired public sources are retained with provenance; no Discussion publication.

Public source and local diagnostic evidence; private scorer parity remains unknown and readiness false.


Pending: Keep parity unknown until authoritative private scorer evidence is available.

### pcv01:AC-P9 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/pcv01.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/scorer_contract.py#L406`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-pcv01-access/report.md`.

Contract: AC-P9: Implement an offline static contract checker. Verify original native wheel
and installed config/bootstrap/verifier/subprocess bytes; review AST facts without
importing/executing downloaded setup, building/running images or invoking a grader.
Separate native subprocess early returns from Docker install/setup operations,
public workspace_paths.pth generation from observed effective import order, and
host/agent/verifier runtime identities. Mutable Python image tags and unpinned
pytest requirements must not become concrete image/patch/pytest runtime versions.
No native source, real verifier command/environment/config or plugin activation.

Static source contract checker compares public/native artifacts; unavailable private implementation remains unknown.

Public source and local diagnostic evidence; private scorer parity remains unknown and readiness false.


Pending: Keep parity unknown until authoritative private scorer evidence is available.

### pcv01:AC-P10 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/specs/pcv01.md`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/scorer_contract.py#L280`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-pcv01-access/report.md`.

Contract: AC-P10: Keep public_setup_acquired/source_hash_verified/development_backend_reviewed
separate from scorer_backend_attested/scorer_source_equivalence_attested,
organizer_diagnostic_permission/supported_observation_route,
actual_scorer_runtime_parity and gpu_readiness. Absent or unverified organizer
metadata yields nulls/reasons, never approval or denial. The current A/B checker
rejects attempts to promote claims or authorize publication; no verified response
pipeline is included. Public source access and CPU PASS preserve blocked GPU
readiness. No message, support request, Discussion post or automatic reply polling.

The source-access gate extends the preceding seven commands with
`.venv/bin/python scripts/check_pcv01_scorer_contract.py --check`. Its exact order,
20min serial local-command ceiling,1GiB additional artifact cap and audit/closure
requirements are in the approved source-access proposal. Synthetic controls are
CPU diagnostics, not actual scorer execution. Historical setup-inaccessibility
claims are superseded only for the acquired participant-facing public files;
private scorer provenance and historical Requests import identity stay unknown.

Public-source review does not promote private scorer parity or real readiness.

Public source and local diagnostic evidence; private scorer parity remains unknown and readiness false.


Pending: Keep parity unknown until authoritative private scorer evidence is available.

### verify-task-cpu:proposal-paragraph-004 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-004`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/cpu-results.json#/results`.

Contract: Exercise the complete pinned swegemma 0.2.11 verify_task path using the actual
SubprocessManager on CPU. Establish that our local diagnostic protocol credits
only passing, required tests against the intended workspace product, and diagnose
Requests using the retained agent-generated patches. Keep the native result,
import qualification and semantic test results separate.

Eight synthetic controls satisfy their intended observations; R00/R01/R02 all reach five nodes but bind installed Requests 2.34.2: origin fails and four behavioral checks pass. Intended workspace patch semantics remain unvalidated.

Actual macOS ARM/Python3.13.15/pytest9.1.1 diagnostic coverage only; raw JUnit is removed by native cleanup and not replaced by test-body telemetry.


Pending: Preserve native/semantic/binding distinctions; separately validate future production/scorer portability.

### verify-task-cpu:proposal-paragraph-005 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-005`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/cpu-results.json#/results`.

Contract: This establishes local development-backend behavior. It does not establish
historical Kaggle imports, private scorer equivalence, benchmark task resolution,
future GPU-environment binding, P-CV-01 activation permission or hybrid retrieval
success. No organizer reply or Discussion publication is needed for this bounded
local experiment. These CPU results cannot clear real-evaluation readiness.

Published readiness stays false and scorer parity null; scoped CPU milestone does not claim a real evaluation or full notebook loop.

Historical source review and diagnostic success do not establish private scorer or hybrid efficacy.


Pending: Keep real evaluation blocked until separately approved readiness evidence.

### verify-task-cpu:proposal-paragraph-008 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-008`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/verify_task_cpu.py`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/report.md`.

Contract: prerequisites.json pins the cached wheel, installed native sources, actual Requests
archive and two B180 agent_patch inputs. The archive has 193 members, 39,052,005
unpacked bytes and two links. Before native extraction, validate member paths,
link targets and types against an owned disposable extraction root; reject escapes,
devices and excess size. Do not rewrite the official archive to remove links.

Bounded archive/input validation and actual native fixture path exist; frozen native inputs and own-test isolation are preserved. No import repair is made in V.

Static immutable implementation evidence plus historical receipts; no execution/import of historical product code here.


Pending: Separately approve integration before transferring this implementation to develop.

### verify-task-cpu:proposal-paragraph-009 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-009`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/verify_task_cpu.py`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/report.md`.

Contract: Requests archive SHA256 is
42dc3d360f842a5c7a66d0008ac05447fcd807dc33ee8cc18d2f2d4876283106,
37,402,474 bytes. The older cohort SHA starts 4a293476 and is not the downloaded
archive identity. Existing B180 acquisition evidence already records this archive
and base-tree correspondence: exported HEAD 443f0b73558781b7dac0e304ad268a30ee35aaeb,
tree 683d44befe0d3519469011c35e46f332eebbc010, original base
1b40fdd004bfc8ba5301bcf8a6908264e9b6b877. Recheck the tree locally before testing;
never alter the cohort or pretend the compressed files have equal hashes.

Bounded archive/input validation and actual native fixture path exist; frozen native inputs and own-test isolation are preserved. No import repair is made in V.

Static immutable implementation evidence plus historical receipts; no execution/import of historical product code here.


Pending: Separately approve integration before transferring this implementation to develop.

### verify-task-cpu:proposal-paragraph-010 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-010`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/cpu-results.json#/results`.

Contract: The official local interpreter is Python 3.13.15, pytest 9.1.1, swegemma 0.2.11,
adk-submission 0.2.13. Requests 2.34.2 is installed in its site-packages, so a competing
installed distribution is plausible; metadata alone does not prove its selection.
Record effective interpreter, dependencies, platform and pytest per process.
Historical Kaggle host Python 3.12.13 / pytest 8.4.2 differ. Existing isolated
P-CV-01 pytest-version controls remain evidence only for their own protocol; this
new matrix does not claim full verify_task equivalence on those historical versions.
No dependency upgrade, extra interpreter, image, VM or network download is included.

Eight synthetic controls satisfy their intended observations; R00/R01/R02 all reach five nodes but bind installed Requests 2.34.2: origin fails and four behavioral checks pass. Intended workspace patch semantics remain unvalidated.

Actual macOS ARM/Python3.13.15/pytest9.1.1 diagnostic coverage only; raw JUnit is removed by native cleanup and not replaced by test-body telemetry.


Pending: Preserve native/semantic/binding distinctions; separately validate future production/scorer portability.

### verify-task-cpu:proposal-paragraph-012 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-012`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/verify_task_cpu.py`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/report.md`.

Contract: After approval, add docs/specs/verify-task-cpu.md with the contract below and an
append-only clarification in the Kaggle runbook. Do not reopen the closed SDD plan.
Proposed implementation boundaries:

Bounded archive/input validation and actual native fixture path exist; frozen native inputs and own-test isolation are preserved. No import repair is made in V.

Static immutable implementation evidence plus historical receipts; no execution/import of historical product code here.


Pending: Separately approve integration before transferring this implementation to develop.

### verify-task-cpu:proposal-paragraph-013 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-013`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/verify_task_cpu.py`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/report.md`.

Contract: - scripts/verify_task_cpu_fixtures.py: disposable fixture/Task construction and
  direct native calls, independent test sources, raw CPU evidence collection.
- src/mostaza/evaluation/verify_task_cpu.py: bounded inputs, receipt validation,
  result classification and immutable-input checks; no alternate verifier.
- scripts/check_verify_task_cpu.py: exact --check entry point below. It executes
  the 11-case matrix, validates its evidence and writes a compact result summary.
- tests/unit/test_verify_task_cpu.py and tests/integration/test_verify_task_cpu_contract.py:
  meaningful receipt, classification, source-integrity and scope checks. They do
  not repeat the entire matrix; the dedicated gate command runs it once.
- docs/implementation/evidence/mostaza-verify-task-cpu/: approval, report, compact
  inventories, command receipts and independent audit. Large/raw outputs remain
  ignored under results/verify-task-cpu/<run-id>/ with hashes and retention paths.

Bounded archive/input validation and actual native fixture path exist; frozen native inputs and own-test isolation are preserved. No import repair is made in V.

Static immutable implementation evidence plus historical receipts; no execution/import of historical product code here.


Pending: Separately approve integration before transferring this implementation to develop.

### verify-task-cpu:proposal-paragraph-014 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-014`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/verify_task_cpu.py`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/report.md`.

Contract: No edits to experiments, manifests, original evidence, notebooks, native installed
files, wheel, setup, scorer, locks or agent prompts. Keep the existing
binding_readiness helper and its real-evaluation block intact. A new CPU-only
assessment must not reinterpret its editable-install requirement or unknown fields.

Bounded archive/input validation and actual native fixture path exist; frozen native inputs and own-test isolation are preserved. No import repair is made in V.

Static immutable implementation evidence plus historical receipts; no execution/import of historical product code here.


Pending: Separately approve integration before transferring this implementation to develop.

### verify-task-cpu:proposal-paragraph-016 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-016`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/verify_task_cpu.py`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/report.md`.

Contract: 1. Fail closed on missing/changed pins, unavailable dependencies, unsafe archive,
   wrong Requests tree, missing agent patches or insufficient local resource budget.
   Use existing local caches; do not fetch replacements silently.
2. Build small owned fixture archives and actual 40-hex baseline Git commits. Create
   fresh Task objects explicitly: patch="", our own test_patch and required nodes.
   Avoid the native special-case repo test/mock_repo + base_commit 123456. Do not
   hydrate an original Task or read its solution/hidden-test fields. Historical
   result JSON is allowlisted to agent_patch and its provenance.
3. Call the imported, unmodified native verify_task with an actual SubprocessManager,
   sandbox="subprocess", default inherited-site-packages behavior, fast_path=True,
   concurrency one, verification timeout 30 seconds and command timeout 30 seconds.
   Set config.wheels_dir to an owned empty directory to prevent automatic bulk
   wheelhouse discovery/copying; inherited cached packages remain unchanged.
   No subclass, monkeypatch, fake manager or substituted helper. Pass a real monotonic
   start_time so returned durations are meaningful. No model server or agent runner.
4. Native code must perform extraction, bootstrap, baseline, protected-path handling,
   patch application, test reset/application, its fixed pytest command, JUnit
   validation and cleanup. Native subprocess setup intentionally skips editable
   installation/dependency setup. Do not compensate with pip install, a path shim,
   .pth injection, altered PYTHONPATH, conftest repair, plugin loading or changed
   command. Our own diagnostic test_patch is the only new pytest test content.
5. Ordinary diagnostic test bodies capture import witnesses in their actual pytest
   process, before behavioral assertions. Store them atomically in the run's owned
   host evidence directory outside the sandbox that native finally removes. Capture
   TaskResult/stdout through normal returned data; do not intercept native execution.
   Preserve collection/setup errors and missing-witness reasons. A receipt must be
   independently validated, not trusted simply because its JSON claims a match.
6. Check manager state and owned sandbox directories after each native cleanup.
   The local watchdog may terminate only this run's child process group, with a
   cleanup attempt and explicit incomplete status. Never touch Kaggle sessions.

Bounded archive/input validation and actual native fixture path exist; frozen native inputs and own-test isolation are preserved. No import repair is made in V.

Static immutable implementation evidence plus historical receipts; no execution/import of historical product code here.


Pending: Separately approve integration before transferring this implementation to develop.

### verify-task-cpu:proposal-paragraph-018 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-018`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/cpu-results.json#/results`.

Contract: Each fixture has an independent diagnostic test_patch and explicit required test
nodes. A negative expected result is a successful control only when its intended
failure condition is evidenced; unrelated setup/import failure does not qualify.

Eight synthetic controls satisfy their intended observations; R00/R01/R02 all reach five nodes but bind installed Requests 2.34.2: origin fails and four behavioral checks pass. Intended workspace patch semantics remain unvalidated.

Actual macOS ARM/Python3.13.15/pytest9.1.1 diagnostic coverage only; raw JUnit is removed by native cleanup and not replaced by test-body telemetry.


Pending: Preserve native/semantic/binding distinctions; separately validate future production/scorer portability.

### verify-task-cpu:proposal-paragraph-019:V01 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-019`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/cpu-results.json#/results/0`.

Contract: | V01 | Small flat product, faulty baseline, no agent patch | Native resolved=false; genuine required assertion fails; witness binds to intended baseline workspace file. |

Expected control/observation reached; native outcome retained separately from binding.

Owned diagnostic nodes only, not hidden tests or task scores.

Observed: {"coverage_reason": null, "id": "V01", "native_error_message": null, "native_resolved": false, "node_outcomes": {"test_required": "assertion_failed"}, "test_exit_code": 1, "workspace_binding": true}
Pending: Preserve this scoped diagnostic; no rerun allowance transfers.

### verify-task-cpu:proposal-paragraph-019:V02 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-019`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/cpu-results.json#/results/1`.

Contract: | V02 | Same product/tests, generic correct agent patch | Native resolved=true, exit 0, required tests pass under native JUnit checks; patched workspace and function identities match. |

Expected control/observation reached; native outcome retained separately from binding.

Owned diagnostic nodes only, not hidden tests or task scores.

Observed: {"coverage_reason": null, "id": "V02", "native_error_message": null, "native_resolved": true, "node_outcomes": {"test_required": "passed"}, "test_exit_code": 0, "workspace_binding": true}
Pending: Preserve this scoped diagnostic; no rerun allowance transfers.

### verify-task-cpu:proposal-paragraph-019:V03 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-019`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/cpu-results.json#/results/2`.

Contract: | V03 | Same product/tests, deliberately incorrect agent patch | Native resolved=false because required behavior assertion fails; patched workspace binding verified. |

Expected control/observation reached; native outcome retained separately from binding.

Owned diagnostic nodes only, not hidden tests or task scores.

Observed: {"coverage_reason": null, "id": "V03", "native_error_message": null, "native_resolved": false, "node_outcomes": {"test_required": "assertion_failed"}, "test_exit_code": 1, "workspace_binding": true}
Pending: Preserve this scoped diagnostic; no rerun allowance transfers.

### verify-task-cpu:proposal-paragraph-019:V04 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-019`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/cpu-results.json#/results/3`.

Contract: | V04 | Owned src-layout fixture with a root-level competing module; correct patch only to src product | Real pytest witness identifies the competing module; mandatory origin assertion fails even if its behavior would pass. Native resolved=false; CPU diagnostic never credits intended-patch success. No path/environment repair. |

Expected control/observation reached; native outcome retained separately from binding.

Owned diagnostic nodes only, not hidden tests or task scores.

Observed: {"coverage_reason": null, "id": "V04", "native_error_message": null, "native_resolved": false, "node_outcomes": {"test_required": "assertion_failed"}, "test_exit_code": 1, "workspace_binding": false}
Pending: Preserve this scoped diagnostic; no rerun allowance transfers.

### verify-task-cpu:proposal-paragraph-019:V05 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-019`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/cpu-results.json#/results/4`.

Contract: | V05 | Required fixture test skipped | Native resolved=false; required node is skipped, not counted as passed. |

Expected control/observation reached; native outcome retained separately from binding.

Owned diagnostic nodes only, not hidden tests or task scores.

Observed: {"coverage_reason": "Intentional skip/no-collection control", "id": "V05", "native_error_message": "No passing tests recorded in JUnit XML (total=1, passed=0, skipped=1)", "native_resolved": false, "node_outcomes": {}, "test_exit_code": 0, "workspace_binding": null}
Pending: Preserve this scoped diagnostic; no rerun allowance transfers.

### verify-task-cpu:proposal-paragraph-019:V06 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-019`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/cpu-results.json#/results/5`.

Contract: | V06 | Owned test file contains no collected tests and names a required node | Native resolved=false; no required passing tests. The missing-test-spec early return must not substitute for this invocation. |

Expected control/observation reached; native outcome retained separately from binding.

Owned diagnostic nodes only, not hidden tests or task scores.

Observed: {"coverage_reason": "Intentional skip/no-collection control", "id": "V06", "native_error_message": null, "native_resolved": false, "node_outcomes": {}, "test_exit_code": 5, "workspace_binding": null}
Pending: Preserve this scoped diagnostic; no rerun allowance transfers.

### verify-task-cpu:proposal-paragraph-019:V07 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-019`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/cpu-results.json#/results/6`.

Contract: | V07 | Owned required test exits its own pytest process with os._exit(0) before JUnit is finalized | Native resolved=false despite child exit 0; missing/incomplete JUnit cannot be credited. This destructive-to-own-child control is synthetic only. |

Expected control/observation reached; native outcome retained separately from binding.

Owned diagnostic nodes only, not hidden tests or task scores.

Observed: {"coverage_reason": null, "id": "V07", "native_error_message": "Missing JUnit XML report (possible premature os._exit(0))", "native_resolved": false, "node_outcomes": {"test_required": "premature_exit"}, "test_exit_code": 0, "workspace_binding": true}
Pending: Preserve this scoped diagnostic; no rerun allowance transfers.

### verify-task-cpu:proposal-paragraph-019:V08 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-019`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/cpu-results.json#/results/7`.

Contract: | V08 | Faulty flat baseline; agent patch attempts to alter protected diagnostic tests instead of product | Native protected-path handling prevents a false PASS; final independent required behavior test fails. |

Expected control/observation reached; native outcome retained separately from binding.

Owned diagnostic nodes only, not hidden tests or task scores.

Observed: {"coverage_reason": null, "id": "V08", "native_error_message": null, "native_resolved": false, "node_outcomes": {"test_required": "assertion_failed"}, "test_exit_code": 1, "workspace_binding": true}
Pending: Preserve this scoped diagnostic; no rerun allowance transfers.

### verify-task-cpu:proposal-paragraph-019:R00 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-019`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/cpu-results.json#/results/8`.

Contract: | R00 | Official Requests snapshot, no agent patch | Actual complete-module import witness and five diagnostic test-node results; native outcome retained, not prescribed as benchmark truth. |

Expected control/observation reached; native outcome retained separately from binding.

Owned diagnostic nodes only, not hidden tests or task scores.

Observed: {"coverage_reason": null, "id": "R00", "native_error_message": null, "native_resolved": false, "node_outcomes": {"test_empty_default": "passed", "test_empty_machine": "passed", "test_missing": "passed", "test_origin_binding": "assertion_failed", "test_valid": "passed"}, "test_exit_code": 1, "workspace_binding": false}
Pending: Preserve this scoped diagnostic; no rerun allowance transfers.

### verify-task-cpu:proposal-paragraph-019:R01 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-019`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/cpu-results.json#/results/9`.

Contract: | R01 | Identical Requests snapshot/tests with exact retained E0-B180 agent_patch | Same receipts plus before/after expected source hash and patch identity; preserve whatever native outcome occurs. |

Expected control/observation reached; native outcome retained separately from binding.

Owned diagnostic nodes only, not hidden tests or task scores.

Observed: {"coverage_reason": null, "id": "R01", "native_error_message": null, "native_resolved": false, "node_outcomes": {"test_empty_default": "passed", "test_empty_machine": "passed", "test_missing": "passed", "test_origin_binding": "assertion_failed", "test_valid": "passed"}, "test_exit_code": 1, "workspace_binding": false}
Pending: Preserve this scoped diagnostic; no rerun allowance transfers.

### verify-task-cpu:proposal-paragraph-019:R02 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-019`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/cpu-results.json#/results/10`.

Contract: | R02 | Identical Requests snapshot/tests with exact retained E1-B180 agent_patch | Same receipts and comparison; do not require or manufacture an E1 PASS. |

Expected control/observation reached; native outcome retained separately from binding.

Owned diagnostic nodes only, not hidden tests or task scores.

Observed: {"coverage_reason": null, "id": "R02", "native_error_message": null, "native_resolved": false, "node_outcomes": {"test_empty_default": "passed", "test_empty_machine": "passed", "test_missing": "passed", "test_origin_binding": "assertion_failed", "test_valid": "passed"}, "test_exit_code": 1, "workspace_binding": false}
Pending: Preserve this scoped diagnostic; no rerun allowance transfers.

### verify-task-cpu:proposal-paragraph-020 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-020`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/verify_task_cpu.py`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/report.md`.

Contract: Requests tests live in a new dedicated diagnostic test file outside the existing
tests/conftest.py hierarchy. Pytest receives that file through native Task.test_files
selection. Preserve existing snapshot files and native generated root config.
Import the complete requests.utils module normally; do not compile a function AST,
load the source by explicit filename or change search paths.

Bounded archive/input validation and actual native fixture path exist; frozen native inputs and own-test isolation are preserved. No import repair is made in V.

Static immutable implementation evidence plus historical receipts; no execution/import of historical product code here.


Pending: Separately approve integration before transferring this implementation to develop.

### verify-task-cpu:proposal-paragraph-021 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-021`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/cpu-results.json#/results`.

Contract: Use four independently authored behavioral tests derived from the public issue:
empty matching machine credentials, empty default credentials, missing matching
entry, and valid non-empty credentials. Use temporary local netrc files selected through Requests' supported NETRC
environment variable inside each owned test body, restoring it afterwards.
The native command/bootstrap environment is unchanged; NETRC is fixture input,
not an import-path repair. Use assertion-based expectations and no network. Add a
fifth mandatory origin test for workspace binding. These are our diagnostics,
not the original task tests, an official score or a reference solution. Keep their
content and forensic outcomes out of agent prompts, submissions and experiment
packaging. Do not add a new corrected Requests patch in this scope.

Eight synthetic controls satisfy their intended observations; R00/R01/R02 all reach five nodes but bind installed Requests 2.34.2: origin fails and four behavioral checks pass. Intended workspace patch semantics remain unvalidated.

Actual macOS ARM/Python3.13.15/pytest9.1.1 diagnostic coverage only; raw JUnit is removed by native cleanup and not replaced by test-body telemetry.


Pending: Preserve native/semantic/binding distinctions; separately validate future production/scorer portability.

### verify-task-cpu:proposal-paragraph-022 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-022`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/cpu-results.json#/results`.

Contract: All three Requests cases use the same snapshot, interpreter, environment, five
tests, dependency state, timeout and verification command. Only agent_patch differs.
If imports select installed Requests, record its actual location/version/hash and
per-test semantic outputs, mark binding MISMATCH, and retain native failure due to
the origin assertion. Do not relabel that as evidence that the intended patch's
semantics failed. If collection prevents execution, the witness remains null with
a reason; classify the Requests stage BLOCKED rather than passing the gate silently.

Eight synthetic controls satisfy their intended observations; R00/R01/R02 all reach five nodes but bind installed Requests 2.34.2: origin fails and four behavioral checks pass. Intended workspace patch semantics remain unvalidated.

Actual macOS ARM/Python3.13.15/pytest9.1.1 diagnostic coverage only; raw JUnit is removed by native cleanup and not replaced by test-body telemetry.


Pending: Preserve native/semantic/binding distinctions; separately validate future production/scorer portability.

### verify-task-cpu:proposal-paragraph-024 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-024`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/cpu-results.json#/results`.

Contract: Per case retain inputs/hashes, native result/resolved/exit/error/stdout, wall-clock
seconds, expected required nodes, observed per-node statuses and witness presence.
The witness is inside our own diagnostic test, not the general P-CV-01 plugin or a
receipt for the historical hidden tests. Coverage is exactly
actual_pytest_owned_diagnostic_test_cpu. Required passing-node coverage is validated
using native results and diagnostic evidence, without replacing native JUnit logic.
Own test bodies record node start and assertion outcome before returning or
re-raising; these are labeled test-body observations, not complete hook/teardown
telemetry. Native TaskResult and its JUnit validation remain the final resolution
authority. Native JUnit bytes are not returned and are deleted at cleanup: record
raw_junit=null with that reason rather than inventing or intercepting a report.

Eight synthetic controls satisfy their intended observations; R00/R01/R02 all reach five nodes but bind installed Requests 2.34.2: origin fails and four behavioral checks pass. Intended workspace patch semantics remain unvalidated.

Actual macOS ARM/Python3.13.15/pytest9.1.1 diagnostic coverage only; raw JUnit is removed by native cleanup and not replaced by test-body telemetry.


Pending: Preserve native/semantic/binding distinctions; separately validate future production/scorer portability.

### verify-task-cpu:proposal-paragraph-025 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-025`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/cpu-results.json#/results`.

Contract: The deliberate no-execution controls V05/V06 may have no test-body witness:
require the intended skip/no-collection evidence and explicit null reason instead.
V07 records its witness before exiting. All behavior/import controls and all three
Requests cases require valid witnesses.

Eight synthetic controls satisfy their intended observations; R00/R01/R02 all reach five nodes but bind installed Requests 2.34.2: origin fails and four behavioral checks pass. Intended workspace patch semantics remain unvalidated.

Actual macOS ARM/Python3.13.15/pytest9.1.1 diagnostic coverage only; raw JUnit is removed by native cleanup and not replaced by test-body telemetry.


Pending: Preserve native/semantic/binding distinctions; separately validate future production/scorer portability.

### verify-task-cpu:proposal-paragraph-026 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-026`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/cpu-results.json#/results`.

Contract: Record PID/parent PID, sys.executable, Python/pytest, cwd and ordered sys.path;
loaded module __file__/resolved path/file SHA256; function __module__,
__code__.co_filename, source/code fingerprint with algorithm/version, and expected
workspace relative path and effective patched file/function fingerprints. Validate
loaded module and function together. Unknown runtime-generated/unavailable data
stays null with a reason, never zero. Fingerprints are comparable only with their
recorded algorithm/runtime. Hashing the file alone does not prove loaded code identity.

Eight synthetic controls satisfy their intended observations; R00/R01/R02 all reach five nodes but bind installed Requests 2.34.2: origin fails and four behavioral checks pass. Intended workspace patch semantics remain unvalidated.

Actual macOS ARM/Python3.13.15/pytest9.1.1 diagnostic coverage only; raw JUnit is removed by native cleanup and not replaced by test-body telemetry.


Pending: Preserve native/semantic/binding distinctions; separately validate future production/scorer portability.

### verify-task-cpu:proposal-paragraph-027 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-027`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/gate-attempts.json#/attempts`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/audit.json`.

Contract: Each of R00/R01/R02 must reach all five required test nodes (pass/fail observations),
produce a valid in-process import receipt and either establish intended binding or
expose a concrete mismatch. Unexpected import/collection/setup failure blocks this
milestone and is reported, never fixed by modifying the verifier/environment.
A binding mismatch is an allowed diagnosis, not readiness: it yields
CPU_E2E_CONTROLS_PASS_REQUESTS_BINDING_MISMATCH if all eight controls pass and all
three Requests receipts are complete. Intended binding yields
CPU_E2E_CONTROLS_PASS_REQUESTS_OBSERVED, with behavior outcomes reported separately.
Neither label claims all Requests tests passed. Missing required/invalid receipts, unrelated
control failures, changed pins, incomplete cleanup or exhausted budget fail the gate.

Final corrected full gate and independent scoped audit passed; prior failures remain failed and each added attempt is separately sourced.

Consumed historical CPU allowances; zero authorization for another native run or for this checkout.


Pending: Use a fresh approved scope/budget before any future execution.

### verify-task-cpu:proposal-paragraph-028 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-028`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/cpu-results.json#/results`.

Contract: All eight synthetic expectations must hold. R00/R01/R02 native resolved=false may
be expected diagnostic evidence; it never becomes an official resolved-task count.
Keep public_setup_acquired/source review separate from private scorer attestation.
All prior unknown scorer fields stay null with reasons, gpu_readiness stays false,
and existing blocked readiness cannot be promoted. No CPU PASS can authorize GPU.

Published readiness stays false and scorer parity null; scoped CPU milestone does not claim a real evaluation or full notebook loop.

Historical source review and diagnostic success do not establish private scorer or hybrid efficacy.


Pending: Keep real evaluation blocked until separately approved readiness evidence.

### verify-task-cpu:proposal-paragraph-030 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-030`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/gate-attempts.json#/attempts`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/audit.json`.

Contract: Run from the worktree above, sequentially; require exit 0 for every command:

Final corrected full gate and independent scoped audit passed; prior failures remain failed and each added attempt is separately sourced.

Consumed historical CPU allowances; zero authorization for another native run or for this checkout.


Pending: Use a fresh approved scope/budget before any future execution.

### verify-task-cpu:proposal-paragraph-032 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-032`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/gate-attempts.json#/attempts`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/audit.json`.

Contract: The ninth command is proposed, not yet implemented or executed. It performs the
11 invocations once and verifies classifications, provenance, cleanup and immutable
inputs. It must also reject acceptance based on a synthetic/mock bypass, a changed
native source, missing actual pytest evidence, a forged binding claim, or an
unsupported readiness promotion. Unit tests exercise receipt/classifier negative
cases with owned data; they are not extra claims of native execution.

Final corrected full gate and independent scoped audit passed; prior failures remain failed and each added attempt is separately sourced.

Consumed historical CPU allowances; zero authorization for another native run or for this checkout.


Pending: Use a fresh approved scope/budget before any future execution.

### verify-task-cpu:proposal-paragraph-033 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-033`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/gate-attempts.json#/attempts`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/audit.json`.

Contract: Existing eight commands preserve prior checks, historical evidence recomputation,
compiler validation and local P-CV-01 controls. Record versions, exact commands,
exit codes, durations and log hashes. A passing old gate does not substitute for
the new ninth command. No silent retries or conditional omissions of Requests.
After meaningful corrections rerun the affected checks and the full final gate;
if a scope/contract change is needed, return it for approval instead.

Final corrected full gate and independent scoped audit passed; prior failures remain failed and each added attempt is separately sourced.

Consumed historical CPU allowances; zero authorization for another native run or for this checkout.


Pending: Use a fresh approved scope/budget before any future execution.

### verify-task-cpu:proposal-paragraph-035 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-035`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/gate-attempts.json#/attempts`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/audit.json`.

Contract: CPU only; zero GPU hours, Kaggle sessions/mutations, model calls, purchases,
submissions, Discussion/posts/messages, network downloads or verifier changes.
Eleven invocations per matrix execution, serial; 30 seconds native pytest timeout,
30 seconds per native setup command, 90 seconds outer wall ceiling per case and
20 minutes total wall ceiling per full gate attempt. A watchdog must enforce the
outer limits and retain timeout evidence; command timeouts alone are insufficient.
At most two full gate attempts (initial and corrections); if more are needed,
report the blocker and seek a revised budget. No automatic retries of cases.

Final corrected full gate and independent scoped audit passed; prior failures remain failed and each added attempt is separately sourced.

Consumed historical CPU allowances; zero authorization for another native run or for this checkout.


Pending: Use a fresh approved scope/budget before any future execution.

### verify-task-cpu:proposal-paragraph-036 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-036`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/gate-attempts.json#/attempts/2`.

Contract: At most 1 GiB additional temporary plus retained local artifacts at any time;
preflight and check between cases, retain compact logs, clean only owned temporary
sandboxes. No bulk copying of wheelhouses/site-packages. If space/time/dependencies
prevent execution, report BLOCKED with the exact missing prerequisite, not success.

Corrected final gate reports complete scoped cleanup and bounded wall time; original interrupted/cap failures remain in the history.

Polled limits are not an instantaneous physical peak. V/R peak bytes and process CPU time were not retained; N peak is sampled 556434407 bytes.


Pending: Retain null reasons and bounded supervision requirements in future protocols.

### verify-task-cpu:proposal-paragraph-037 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md#paragraph-037`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/gate-attempts.json#/attempts`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/audit.json`.

Contract: Approval covers the specification delta, bounded implementation, nine-command gate,
independent audit and corrections, then commit/push/update existing PR2 toward
develop after audit PASS with zero findings. No merge. Audit inspects the complete
relevant diff, native integrity, actual CPU results, leakage boundaries and exact
gate evidence. Preserve the pre-existing dirty closed-plan file without staging it.
This proposal itself requests no new Kaggle authorization. A future real batch,
any import/setup repair or real-verifier instrumentation requires a separate plan.

Final corrected full gate and independent scoped audit passed; prior failures remain failed and each added attempt is separately sourced.

Consumed historical CPU allowances; zero authorization for another native run or for this checkout.


Pending: Use a fresh approved scope/budget before any future execution.

### requests-import-cpu:proposal-paragraph-004 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-004`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/cpu-results.json#/results`.

Contract: Correct and measure Requests imports inside the actual native CPU pytest process,
so diagnostics exercise the snapshot's patched product. Preserve native verification
source, command, protection rules, JUnit decisions and cleanup. Separate import
correction from whether the retained agent patches satisfy our own behavior tests.

Generic faulty/correct/wrong controls discriminate. All U stages reproduce installed-code mismatch; all B stages bind patched workspace. Bound baseline fails empty-machine/default; E0 missing-match raises TypeError; E1 passes all five OWN checks.

Actual macOS ARM/Python3.13.15/pytest9.1.1 diagnostic coverage only; raw JUnit is removed by native cleanup and not replaced by test-body telemetry.


Pending: Preserve native/semantic/binding distinctions; separately validate future production/scorer portability.

### requests-import-cpu:proposal-paragraph-008 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-008`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/cpu-results.json#/results`.

Contract: These source facts establish API availability. They do not establish that the
proposed alias works, is supported by the private scorer or may be used in a real
competition run. CPU validation is the next test, not an already proven repair.

Published readiness stays false and scorer parity null; scoped CPU milestone does not claim a real evaluation or full notebook loop.

Historical source review and diagnostic success do not establish private scorer or hybrid efficacy.


Pending: Keep real evaluation blocked until separately approved readiness evidence.

### requests-import-cpu:proposal-paragraph-010 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-010`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/requests_import_cpu.py`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/report.md`.

Contract: Use the unchanged acquired Requests archive plus a separately identified, hashed
layout delta through the native patch_path argument. The complete delta is one
new relative symbolic link at workspace root:

Host-only validator enforces the one-link 120000 delta requests -> src/requests, separate original/derived trees, canonical module/function binding and exact U/B pair matching.

Static immutable implementation evidence plus historical receipts; no execution/import of historical product code here.


Pending: Separately approve integration before transferring this implementation to develop.

### requests-import-cpu:proposal-paragraph-012 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-012`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/requests_import_cpu.py`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/report.md`.

Contract: Use Git symlink mode 120000. No Requests source bytes, tests, configuration,
packaging metadata or existing links are edited by the layout delta. The target
must be an existing in-workspace package directory with __init__.py. The root alias
must not exist, be tracked or be ignored before application. Refuse conflicts,
absolute/escaping/circular targets, extra paths, renames or other file modes.
Generate and verify the delta in owned scratch data; retain its exact patch bytes,
SHA256 and path/mode/target manifest. Do not accept arbitrary user-supplied patches
as layout deltas or fall back to another import trick.

Host-only validator enforces the one-link 120000 delta requests -> src/requests, separate original/derived trees, canonical module/function binding and exact U/B pair matching.

Static immutable implementation evidence plus historical receipts; no execution/import of historical product code here.


Pending: Separately approve integration before transferring this implementation to develop.

### requests-import-cpu:proposal-paragraph-013 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-013`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/requests_import_cpu.py`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/report.md`.

Contract: The archive remains byte-identical. Its original exported Git tree remains pinned
and checked BEFORE overlay application. The source layout before native bootstrap is
an explicitly derived input: its delta adds this link, so its complete tree must
not be labeled identical to the original tree. Native bootstrap later generates
its normal pytest/config files as well; distinguish those native additions from
the layout delta, which must touch only the declared link. Record original archive/tree,
layout-delta hash, derived layout and retained agent_patch hash separately.
The native eval_baseline may include the added alias; document this fact.

Host-only validator enforces the one-link 120000 delta requests -> src/requests, separate original/derived trees, canonical module/function binding and exact U/B pair matching.

Static immutable implementation evidence plus historical receipts; no execution/import of historical product code here.


Pending: Separately approve integration before transferring this implementation to develop.

### requests-import-cpu:proposal-paragraph-014 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-014`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/requests_import_cpu.py`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/report.md`.

Contract: This changes CPU workspace layout, not the native verification command or source.
It is NOT the unchanged-input V-CPU-01 protocol, and must use new case/run IDs.
Do not alter that protocol's strict raw-path assertions to make its old cases pass.
Do not modify its evidence/readiness or silently enable this route in experiments,
runner.py, notebooks, agent contexts, Kaggle inputs or submissions.

Host-only validator enforces the one-link 120000 delta requests -> src/requests, separate original/derived trees, canonical module/function binding and exact U/B pair matching.

Static immutable implementation evidence plus historical receipts; no execution/import of historical product code here.


Pending: Separately approve integration before transferring this implementation to develop.

### requests-import-cpu:proposal-paragraph-015 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-015`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/cpu-results.json#/results`.

Contract: No pip/editable install, dependency change, .pth, sitecustomize, conftest repair,
PYTHONPATH change, sys.path injection, custom loader, module reload, verifier/sandbox interception wrapper,
subclass/name spoof or monkeypatch. Keep the real SubprocessManager with inherited
site-packages and the exact native pytest/JUnit behavior. No Docker/Colima changes,
image/VM creation or new services. If native behavior rejects/removes the valid
link, record BLOCKED; propose a different route for approval instead of improvising.

Generic faulty/correct/wrong controls discriminate. All U stages reproduce installed-code mismatch; all B stages bind patched workspace. Bound baseline fails empty-machine/default; E0 missing-match raises TypeError; E1 passes all five OWN checks.

Actual macOS ARM/Python3.13.15/pytest9.1.1 diagnostic coverage only; raw JUnit is removed by native cleanup and not replaced by test-body telemetry.


Pending: Preserve native/semantic/binding distinctions; separately validate future production/scorer portability.

### requests-import-cpu:proposal-paragraph-017 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-017`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/requests_import_cpu.py`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/report.md`.

Contract: Add docs/specs/requests-import-cpu.md for this contract and append a clearly scoped
section to docs/runbooks/kaggle-execution.md. Preserve all earlier sections and the
V-CPU-01 specification, code, tests and evidence pinned in prerequisites.json.
The old no-further-execution statement is a historical authorization checkpoint;
new approval would cover the eleven regression invocations explicitly listed here.
It would not reopen any previous GPU authorization.

Host-only validator enforces the one-link 120000 delta requests -> src/requests, separate original/derived trees, canonical module/function binding and exact U/B pair matching.

Static immutable implementation evidence plus historical receipts; no execution/import of historical product code here.


Pending: Separately approve integration before transferring this implementation to develop.

### requests-import-cpu:proposal-paragraph-018 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-018`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/requests_import_cpu.py`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/report.md`.

Contract: 1. Implement host-only src/mostaza/evaluation/requests_import_cpu.py: allowlisted
   layout validation, input/provenance pins, canonical binding validation and CPU
   result classification. Add scripts/requests_import_cpu_fixtures.py for direct
   native invocation and independently authored diagnostic tests.
2. Add scripts/check_requests_import_cpu.py --check for the nine new cases below.
   Reuse the frozen V-CPU-01 watchdog/disk-meter primitives rather than rewriting
   them. Keep the new classifier separate; do not weaken the old raw-path rule.
3. Add tests/unit/test_requests_import_cpu.py and
   tests/integration/test_requests_import_cpu_contract.py. Focused tests cover
   delta conflicts/escapes/mode/extra paths, immutable-input protection, alias
   versus canonical provenance, code replacement despite a matching source file,
   stale/duplicate receipts, exact pair matching and failure classification.
   Do not make unit/integration tests rerun a full native matrix implicitly.
4. Add scripts/run_requests_import_cpu_gate.py --check --attempt 1 (or 2 only under
   the corrective-attempt rules below). It runs the ten exact commands below,
   records exits/log hashes and enforces a single 1200s deadline across ALL commands.
   Monitor owned descendant groups, including native detached sessions; terminate
   only owned groups and attempt cleanup on timeout. Create the attempt directory
   exclusively so a prior run cannot be overwritten. No automatic case/command retry.
5. Run the approved gate, produce compact evidence under this directory and ignored
   raw artifacts under results/requests-import-cpu/<attempt-id>/, obtain independent
   audit/corrections, then approved commit/push/update PR2 toward develop, no merge.

Host-only validator enforces the one-link 120000 delta requests -> src/requests, separate original/derived trees, canonical module/function binding and exact U/B pair matching.

Static immutable implementation evidence plus historical receipts; no execution/import of historical product code here.


Pending: Separately approve integration before transferring this implementation to develop.

### requests-import-cpu:proposal-paragraph-019 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-019`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/requests_import_cpu.py`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/report.md`.

Contract: Do not change old files merely to make their frozen checks accept the new route.
Freeze the current runbook as an append-only prefix. Freeze original experiments,
notebooks, manifests/locks, native wheel/install files and historical evidence.
No fresh source/data/model downloads; use the existing pinned resources.

Host-only validator enforces the one-link 120000 delta requests -> src/requests, separate original/derived trees, canonical module/function binding and exact U/B pair matching.

Static immutable implementation evidence plus historical receipts; no execution/import of historical product code here.


Pending: Separately approve integration before transferring this implementation to develop.

### requests-import-cpu:proposal-paragraph-021 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-021`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/cpu-results.json#/results`.

Contract: Use ordinary owned Git baselines and explicit own required test nodes; no reserved
mock bypass and no original Task.patch/test_patch. A test failure is a valid
negative control only when it reaches the intended assertion with proven binding.
Unrelated setup/collection/dependency failures are BLOCKED, never successful controls.

Generic faulty/correct/wrong controls discriminate. All U stages reproduce installed-code mismatch; all B stages bind patched workspace. Bound baseline fails empty-machine/default; E0 missing-match raises TypeError; E1 passes all five OWN checks.

Actual macOS ARM/Python3.13.15/pytest9.1.1 diagnostic coverage only; raw JUnit is removed by native cleanup and not replaced by test-body telemetry.


Pending: Preserve native/semantic/binding distinctions; separately validate future production/scorer portability.

### requests-import-cpu:proposal-paragraph-022:L01 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-022`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/cpu-results.json#/results/0`.

Contract: | L01 | Owned generic src package, valid root alias, faulty baseline | Origin/function binding true; required behavior fails; native resolved=false. |

Expected control/observation reached; native outcome retained separately from binding.

Owned diagnostic nodes only, not hidden tests or task scores.

Observed: {"binding": true, "id": "L01", "native_resolved": false, "node_outcomes": {"test_required": "assertion_failed"}, "test_exit_code": 1}
Pending: Preserve this scoped diagnostic; no rerun allowance transfers.

### requests-import-cpu:proposal-paragraph-022:L02 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-022`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/cpu-results.json#/results/1`.

Contract: | L02 | Same package/tests/alias with a generic correct patch | Binding true; native resolved=true, exit 0, required passing nodes validated natively. |

Expected control/observation reached; native outcome retained separately from binding.

Owned diagnostic nodes only, not hidden tests or task scores.

Observed: {"binding": true, "id": "L02", "native_resolved": true, "node_outcomes": {"test_required": "passed"}, "test_exit_code": 0}
Pending: Preserve this scoped diagnostic; no rerun allowance transfers.

### requests-import-cpu:proposal-paragraph-022:L03 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-022`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/cpu-results.json#/results/2`.

Contract: | L03 | Same package/tests/alias with a deliberately wrong patch | Binding true; required behavior fails; native resolved=false. |

Expected control/observation reached; native outcome retained separately from binding.

Owned diagnostic nodes only, not hidden tests or task scores.

Observed: {"binding": true, "id": "L03", "native_resolved": false, "node_outcomes": {"test_required": "assertion_failed"}, "test_exit_code": 1}
Pending: Preserve this scoped diagnostic; no rerun allowance transfers.

### requests-import-cpu:proposal-paragraph-022:R00-U — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-022`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/cpu-results.json#/results/3`.

Contract: | R00-U | Requests baseline, no layout delta | Five own nodes reached; installed-code binding mismatch measured and origin rejected. |

Expected control/observation reached; native outcome retained separately from binding.

Owned diagnostic nodes only, not hidden tests or task scores.

Observed: {"binding": false, "id": "R00-U", "native_resolved": false, "node_outcomes": {"test_empty_default": "passed", "test_empty_machine": "passed", "test_missing": "passed", "test_origin_binding": "assertion_failed", "test_valid": "passed"}, "test_exit_code": 1}
Pending: Preserve this scoped diagnostic; no rerun allowance transfers.

### requests-import-cpu:proposal-paragraph-022:R00-B — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-022`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/cpu-results.json#/results/4`.

Contract: | R00-B | Same baseline plus layout delta | Five nodes reached; parent requests and requests.utils bind canonically to workspace/src/requests; origin passes. |

Expected control/observation reached; native outcome retained separately from binding.

Owned diagnostic nodes only, not hidden tests or task scores.

Observed: {"binding": true, "id": "R00-B", "native_resolved": false, "node_outcomes": {"test_empty_default": "assertion_failed", "test_empty_machine": "assertion_failed", "test_missing": "passed", "test_origin_binding": "passed", "test_valid": "passed"}, "test_exit_code": 1}
Pending: Preserve this scoped diagnostic; no rerun allowance transfers.

### requests-import-cpu:proposal-paragraph-022:R01-U — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-022`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/cpu-results.json#/results/5`.

Contract: | R01-U | Retained E0-B180 agent_patch, no layout delta | Same unbound control with that exact agent patch. |

Expected control/observation reached; native outcome retained separately from binding.

Owned diagnostic nodes only, not hidden tests or task scores.

Observed: {"binding": false, "id": "R01-U", "native_resolved": false, "node_outcomes": {"test_empty_default": "passed", "test_empty_machine": "passed", "test_missing": "passed", "test_origin_binding": "assertion_failed", "test_valid": "passed"}, "test_exit_code": 1}
Pending: Preserve this scoped diagnostic; no rerun allowance transfers.

### requests-import-cpu:proposal-paragraph-022:R01-B — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-022`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/cpu-results.json#/results/6`.

Contract: | R01-B | Same E0 agent_patch plus layout delta | Verified binding to the actual E0-patched utils file/function, origin passes. |

Expected control/observation reached; native outcome retained separately from binding.

Owned diagnostic nodes only, not hidden tests or task scores.

Observed: {"binding": true, "id": "R01-B", "native_resolved": false, "node_outcomes": {"test_empty_default": "passed", "test_empty_machine": "passed", "test_missing": "exception", "test_origin_binding": "passed", "test_valid": "passed"}, "test_exit_code": 1}
Pending: Preserve this scoped diagnostic; no rerun allowance transfers.

### requests-import-cpu:proposal-paragraph-022:R02-U — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-022`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/cpu-results.json#/results/7`.

Contract: | R02-U | Retained E1-B180 agent_patch, no layout delta | Same unbound control with that exact agent patch. |

Expected control/observation reached; native outcome retained separately from binding.

Owned diagnostic nodes only, not hidden tests or task scores.

Observed: {"binding": false, "id": "R02-U", "native_resolved": false, "node_outcomes": {"test_empty_default": "passed", "test_empty_machine": "passed", "test_missing": "passed", "test_origin_binding": "assertion_failed", "test_valid": "passed"}, "test_exit_code": 1}
Pending: Preserve this scoped diagnostic; no rerun allowance transfers.

### requests-import-cpu:proposal-paragraph-022:R02-B — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-022`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/cpu-results.json#/results/8`.

Contract: | R02-B | Same E1 agent_patch plus layout delta | Verified binding to the actual E1-patched utils file/function, origin passes. |

Expected control/observation reached; native outcome retained separately from binding.

Owned diagnostic nodes only, not hidden tests or task scores.

Observed: {"binding": true, "id": "R02-B", "native_resolved": true, "node_outcomes": {"test_empty_default": "passed", "test_empty_machine": "passed", "test_missing": "passed", "test_origin_binding": "passed", "test_valid": "passed"}, "test_exit_code": 0}
Pending: Preserve this scoped diagnostic; no rerun allowance transfers.

### requests-import-cpu:proposal-paragraph-023 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-023`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/cpu-results.json#/results`.

Contract: Each U/B pair has the same pinned archive, agent_patch, interpreter, dependencies,
manager, sampling-not-applicable status, limits, own test_patch bytes, five required
nodes and native verification command. Only patch_path (absent versus the manifest-
controlled layout delta) differs. Native instance IDs and generated sandbox/PID/
JUnit paths naturally differ and are recorded, not experimental knobs.

Generic faulty/correct/wrong controls discriminate. All U stages reproduce installed-code mismatch; all B stages bind patched workspace. Bound baseline fails empty-machine/default; E0 missing-match raises TypeError; E1 passes all five OWN checks.

Actual macOS ARM/Python3.13.15/pytest9.1.1 diagnostic coverage only; raw JUnit is removed by native cleanup and not replaced by test-body telemetry.


Pending: Preserve native/semantic/binding distinctions; separately validate future production/scorer portability.

### requests-import-cpu:proposal-paragraph-024 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-024`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/cpu-results.json#/results`.

Contract: The same generated test_patch bytes must be used in BOTH stages of each Requests
pair. To avoid embedding stage-specific receipt paths into tests, use one owned
host receipt destination per pair, outside native cleanup. Require it absent before
each invocation, atomically publish the test-body events, archive/move it to the
stage evidence after return, then require it absent again. Fail on stale data.
Bind stage to returned TaskResult.task_id, observed process and host invocation
record, not an event's self-reported stage. Never reuse a prior stage's witness.

Generic faulty/correct/wrong controls discriminate. All U stages reproduce installed-code mismatch; all B stages bind patched workspace. Bound baseline fails empty-machine/default; E0 missing-match raises TypeError; E1 passes all five OWN checks.

Actual macOS ARM/Python3.13.15/pytest9.1.1 diagnostic coverage only; raw JUnit is removed by native cleanup and not replaced by test-body telemetry.


Pending: Preserve native/semantic/binding distinctions; separately validate future production/scorer portability.

### requests-import-cpu:proposal-paragraph-025 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-025`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/cpu-results.json#/results`.

Contract: The four behavioral tests remain the independently authored V-CPU-01 cases:
empty matching machine credentials, empty default credentials, missing match and
valid credentials. Select temporary local netrc files through NETRC inside each
owned test body, restore it afterwards, and perform no network access. A fifth
origin assertion checks the parent package, utils module and loaded target function.
Keep diagnostics and forensic outcomes outside all agent/submission payloads.
Do not introduce a newly corrected Requests patch or any reference solution.

Generic faulty/correct/wrong controls discriminate. All U stages reproduce installed-code mismatch; all B stages bind patched workspace. Bound baseline fails empty-machine/default; E0 missing-match raises TypeError; E1 passes all five OWN checks.

Actual macOS ARM/Python3.13.15/pytest9.1.1 diagnostic coverage only; raw JUnit is removed by native cleanup and not replaced by test-body telemetry.


Pending: Preserve native/semantic/binding distinctions; separately validate future production/scorer portability.

### requests-import-cpu:proposal-paragraph-026 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-026`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/cpu-results.json#/results`.

Contract: The new protocol permits a declared alias, so __file__/co_filename spelling can
include workspace/requests while the canonical target is workspace/src/requests.
Record BOTH raw and resolved paths inside pytest while the alias still exists;
after cleanup a host Path.resolve alone cannot reconstruct a removed symlink.
Require the exact manifest alias/target, canonical in-workspace paths, actual file
hashes and expected loaded-code fingerprint for each retained patch. Independently
validate raw path spelling against the declared mapping; a forged resolved-path
claim, arbitrary outside alias or matching file with different loaded code fails.

Generic faulty/correct/wrong controls discriminate. All U stages reproduce installed-code mismatch; all B stages bind patched workspace. Bound baseline fails empty-machine/default; E0 missing-match raises TypeError; E1 passes all five OWN checks.

Actual macOS ARM/Python3.13.15/pytest9.1.1 diagnostic coverage only; raw JUnit is removed by native cleanup and not replaced by test-body telemetry.


Pending: Preserve native/semantic/binding distinctions; separately validate future production/scorer portability.

### requests-import-cpu:proposal-paragraph-027 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-027`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/cpu-results.json#/results`.

Contract: Require parent requests.__file__ and requests.utils.__file__ to select the expected
workspace package and utils files. Record the loaded function's __module__, raw and
canonical co_filename, fingerprint/algorithm, PID/parent PID, executable, Python/
pytest, cwd and ordered sys.path. Record imported Requests' public version separately
from installed distribution metadata; they need not agree. Coverage is exactly
these reviewed modules/function inside own diagnostic test bodies, not every
Requests submodule, every pytest phase or all dependencies. No such broader claim.

Generic faulty/correct/wrong controls discriminate. All U stages reproduce installed-code mismatch; all B stages bind patched workspace. Bound baseline fails empty-machine/default; E0 missing-match raises TypeError; E1 passes all five OWN checks.

Actual macOS ARM/Python3.13.15/pytest9.1.1 diagnostic coverage only; raw JUnit is removed by native cleanup and not replaced by test-body telemetry.


Pending: Preserve native/semantic/binding distinctions; separately validate future production/scorer portability.

### requests-import-cpu:proposal-paragraph-029 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-029`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/gate-attempts.json#/attempts`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/audit.json`.

Contract: All ten gate commands must exit 0 and independent audit must return PASS with zero
findings. All three generic control expectations must hold. All six Requests stages
must execute all five own nodes, return valid in-process witnesses, use the exact
paired test_patch and reach the intended native assertions. Every U stage must
reproduce the installed-code mismatch; every B stage must prove actual patched
workspace binding and pass the origin test. If the control no longer reproduces,
stop for environmental diagnosis, not automatic baseline relabeling.

Final corrected full gate and independent scoped audit passed; prior failures remain failed and each added attempt is separately sourced.

Consumed historical CPU allowances; zero authorization for another native run or for this checkout.


Pending: Use a fresh approved scope/budget before any future execution.

### requests-import-cpu:proposal-paragraph-030 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-030`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/cpu-results.json#/results`.

Contract: Behavioral results for baseline/E0/E1 are separate observations. Do not require or
manufacture an E1 PASS to accept a correctly demonstrated import remedy. Preserve
native resolved/exit/error_message and each behavioral outcome. Bound behavioral
failures can be meaningful results with correct imports; report them exactly.
Unexpected setup/import/collection failure, skipped required observation or missing
receipt blocks this milestone. The generic correct/wrong controls prove that the
protocol can distinguish real patch effects with verified binding.

Generic faulty/correct/wrong controls discriminate. All U stages reproduce installed-code mismatch; all B stages bind patched workspace. Bound baseline fails empty-machine/default; E0 missing-match raises TypeError; E1 passes all five OWN checks.

Actual macOS ARM/Python3.13.15/pytest9.1.1 diagnostic coverage only; raw JUnit is removed by native cleanup and not replaced by test-body telemetry.


Pending: Preserve native/semantic/binding distinctions; separately validate future production/scorer portability.

### requests-import-cpu:proposal-paragraph-031 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-031`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/cpu-results.json#/results`.

Contract: The successful milestone label is CPU_REQUESTS_IMPORT_BINDING_VALIDATED only if
those structural/control requirements pass. It is never a Kaggle task-score label.
Use null plus reasons for absent coverage, raw JUnit (removed by native cleanup),
CPU process time, unrecorded peak space and private-scorer parity. Retain numeric
units and measurement scope. Track started/native-results-present/assessed counts
separately, wall seconds, native errors, cleanup, delta and source hashes. Native
TaskResult usage defaults are not independently measured inference/billing metrics.

Generic faulty/correct/wrong controls discriminate. All U stages reproduce installed-code mismatch; all B stages bind patched workspace. Bound baseline fails empty-machine/default; E0 missing-match raises TypeError; E1 passes all five OWN checks.

Actual macOS ARM/Python3.13.15/pytest9.1.1 diagnostic coverage only; raw JUnit is removed by native cleanup and not replaced by test-body telemetry.


Pending: Preserve native/semantic/binding distinctions; separately validate future production/scorer portability.

### requests-import-cpu:proposal-paragraph-032 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-032`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/cpu-results.json#/results`.

Contract: Keep ready_for_gpu=false and existing binding_readiness unchanged. No promotion of
historical verifier origins, private scorer equality, organizer permission or
hybrid retrieval efficacy. CPU success would demonstrate this explicit layout
variant only; its applicability to a future real Kaggle environment is a separate
decision with its own provenance, comparability and execution authorization.

Published readiness stays false and scorer parity null; scoped CPU milestone does not claim a real evaluation or full notebook loop.

Historical source review and diagnostic success do not establish private scorer or hybrid efficacy.


Pending: Keep real evaluation blocked until separately approved readiness evidence.

### requests-import-cpu:proposal-paragraph-034 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-034`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/gate-attempts.json#/attempts`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/audit.json`.

Contract: From the phase2 worktree above, the new gate runner executes these ten commands
in this order. All are mandatory; command 9 preserves the old eleven-case matrix.
Command 10 executes exactly the nine NEW cases. No baseline is borrowed from an old
run and neither matrix may be rerun implicitly by tests/auditor.

Final corrected full gate and independent scoped audit passed; prior failures remain failed and each added attempt is separately sourced.

Consumed historical CPU allowances; zero authorization for another native run or for this checkout.


Pending: Use a fresh approved scope/budget before any future execution.

### requests-import-cpu:proposal-paragraph-038 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-038`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/gate-attempts.json#/attempts/1`.

Contract: The new checker and runner do not exist yet and have not been executed. The runner
must own the whole-gate deadline and track/stop detached native child groups;
per-case timeouts alone do not enforce a whole-gate budget. Capture source/input
inventories before execution, exact argv, versions, command exits/times/log hashes,
result/receipt inventories and immutable-input checks after cleanup. Do not change
source during a gate. A later source correction requires affected focused checks
and a complete final gate; evidence-only reporting must not rewrite raw results.

Corrected final gate reports complete scoped cleanup and bounded wall time; original interrupted/cap failures remain in the history.

Polled limits are not an instantaneous physical peak. V/R peak bytes and process CPU time were not retained; N peak is sampled 556434407 bytes.


Pending: Retain null reasons and bounded supervision requirements in future protocols.

### requests-import-cpu:proposal-paragraph-040 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-040`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/gate-attempts.json#/attempts`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/audit.json`.

Contract: CPU only. Per complete gate attempt: 20 native verify_task invocations maximum,
serial (11 old regression + 9 new), 30s native command/verification timeout, 90s
per-case ceiling, 1200s TOTAL wall deadline for all ten commands. Some old checks
also spawn their existing pytest/fixture processes; those are included in the
1200s wall budget, not counted as extra verify_task calls or model evaluations.

Final corrected full gate and independent scoped audit passed; prior failures remain failed and each added attempt is separately sourced.

Consumed historical CPU allowances; zero authorization for another native run or for this checkout.


Pending: Use a fresh approved scope/budget before any future execution.

### requests-import-cpu:proposal-paragraph-041 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-041`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/gate-attempts.json#/attempts`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/audit.json`.

Contract: At most TWO full gate attempts: one initial and one only after a demonstrated
failure/audit finding, a concrete repair and focused non-native regression checks.
This is a corrective attempt, not a silent replay. No automatic case/command retry.
Max 40 native invocations and 40 min gate wall time across both. Auditor uses raw
records/source and focused non-native checks; no extra native matrix. If another
full run is needed, report the exact blocker and seek a new budget before running.

Final corrected full gate and independent scoped audit passed; prior failures remain failed and each added attempt is separately sourced.

Consumed historical CPU allowances; zero authorization for another native run or for this checkout.


Pending: Use a fresh approved scope/budget before any future execution.

### requests-import-cpu:proposal-paragraph-042 — partial

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-042`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/gate-attempts.json#/attempts/1`.

Contract: At most 1 GiB additional owned temporary/retained artifacts at any time, checked
before launch and during execution across both new outputs and newly generated
V-CPU-01 regression outputs. Record the sampled peak if implemented, otherwise null
with a reason; do not claim a physical instantaneous peak from polling alone.
Retain prior evidence; cleanup only this run's owned temporary trees. No bulk copy
of wheelhouses/site-packages or download/install/upgrade. Missing cached inputs,
resource ceiling, cleanup failure or pin drift are BLOCKED outcomes.

Corrected final gate reports complete scoped cleanup and bounded wall time; original interrupted/cap failures remain in the history.

Polled limits are not an instantaneous physical peak. V/R peak bytes and process CPU time were not retained; N peak is sampled 556434407 bytes.


Pending: Retain null reasons and bounded supervision requirements in future protocols.

### requests-import-cpu:proposal-paragraph-043 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md#paragraph-043`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/gate-attempts.json#/attempts`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/audit.json`.

Contract: Approval would cover the specification delta, narrowly scoped CPU implementation,
exact ten-command gate/runner, those budgets, independent audit/corrections and
commit/push/update existing PR2 toward develop after final gate/audit PASS. No merge.
This authorizes no GPU/model call, Kaggle session/API/browser mutation, submission,
Discussion/message/notebook publication, real-verifier activation or production input change.
No worktree migration/new SDD state and no change to the previous worktree.

Final corrected full gate and independent scoped audit passed; prior failures remain failed and each added attempt is separately sourced.

Consumed historical CPU allowances; zero authorization for another native run or for this checkout.


Pending: Use a fresh approved scope/budget before any future execution.

### notebook-import-cpu:proposal-paragraph-004 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-004`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/cpu-results.json#/rows`.

Contract: Integrate the R-IMPORT-CPU-01 layout remedy into a NEW, GPU-disabled notebook
candidate and prove that its actual host preparation selects the same native
reconstruction inputs for agent setup and verification. Test relocatability in
CPU and explicitly delimit platform coverage.

Six separate setup and six verification witnesses bind the same resolved inputs; baseline fails two empty-credential checks, E0 missing-match raises TypeError, E1 passes five OWN nodes. Setup observes baseline; verification observes retained patch.

Actual macOS ARM/Python3.13.15/pytest9.1.1 diagnostic coverage only; raw JUnit is removed by native cleanup and not replaced by test-body telemetry.


Pending: Preserve native/semantic/binding distinctions; separately validate future production/scorer portability.

### notebook-import-cpu:proposal-paragraph-008 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-008`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/cpu-results.json#/rows`.

Contract: Available CPU environment: macOS/ARM, Python3.13.15, pytest9.1.1 in the existing
official environment. Python3.12.8 also exists at the absolute path used below.
Historical Kaggle was Linux/Python3.12.13/pytest8.4.2. Colima reports stopped;
Docker image availability could not be read through its socket. Do not start
Colima/Docker, pull/build an image, provision a VM or infer Linux compatibility.

Six separate setup and six verification witnesses bind the same resolved inputs; baseline fails two empty-credential checks, E0 missing-match raises TypeError, E1 passes five OWN nodes. Setup observes baseline; verification observes retained patch.

Actual macOS ARM/Python3.13.15/pytest9.1.1 diagnostic coverage only; raw JUnit is removed by native cleanup and not replaced by test-body telemetry.


Pending: Preserve native/semantic/binding distinctions; separately validate future production/scorer portability.

### notebook-import-cpu:proposal-paragraph-010 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-010`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/notebook_import.py`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/report.md`.

Contract: After approval add docs/specs/notebook-import-cpu.md and append a scoped section
to docs/runbooks/kaggle-execution.md. Preserve the current runbook as a byte-exact
prefix and all previously tracked files except that append, as pinned by
prerequisites.json. New files may be added. Do not rewrite historical notebooks,
experiment manifests, runner.py, CPU protocols/results or the closed SDD plan.

Host adapter creates disabled notebook/derived envelope via official base-plus-delta resolver; parent C8K closures stay byte-identical and actual-input provenance is distinct from parent binding.

Static immutable implementation evidence plus historical receipts; no execution/import of historical product code here.


Pending: Separately approve integration before transferring this implementation to develop.

### notebook-import-cpu:proposal-paragraph-011 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-011`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/notebook_import.py`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/report.md`.

Contract: 1. Candidate identity and unchanged comparison:
   - Create notebooks/mostaza-notebook-import-cpu.ipynb, candidate
     N-IMPORT-CPU-01, layout profile requests-layout-v1.
   - Derive from the pinned mostaza-context-verification.ipynb; keep its E0-C8K /
     E1-C8K pair, model revision, sampling, prompts, tools, one LlmAgent, budget,
     serving profile, task cohort, verification and repair policy byte-equivalent.
     Do not activate Q1/R1 or change retrieval instructions in this milestone.
   - Use distinct host experiment identities E0-C8K-L1 / E1-C8K-L1, each explicitly
     referencing the unchanged corresponding C8K submission closure and its hash.
     The layout is COMMON to both arms. No new agent payload behavior.
   - GPU/network metadata remain false; no executed outputs. Keep the fail-closed
     launch guard before bootstrap, dependency installation, model discovery or
     CUDA inspection. CPU validation must not remove or satisfy that guard.
     GPU authorization remains null, real evaluations NOT_RUN, ready_for_gpu=false.

Host adapter creates disabled notebook/derived envelope via official base-plus-delta resolver; parent C8K closures stay byte-identical and actual-input provenance is distinct from parent binding.

Static immutable implementation evidence plus historical receipts; no execution/import of historical product code here.


Pending: Separately approve integration before transferring this implementation to develop.

### notebook-import-cpu:proposal-paragraph-012 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-012`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/notebook_import.py`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/report.md`.

Contract: 2. Small host-only adapter and native data route:
   - Add src/mostaza/evaluation/notebook_import.py, a candidate builder and bounded
     preparation/check scripts. The production host module must not import CPU
     diagnostics, retained patches or fixture modules.
   - Use the exact Requests layout patch already validated: one Git mode120000
     relative symlink, requests -> src/requests. No product-source changes.
   - Prepare a fresh owned reconstruction view from pinned original snapshots.
     Requests is the unchanged original archive in the native base position plus
     its allowlisted patch in the native per-instance position. Derive the base
     filename through the official helper, never a guessed spelling. Copy only
     selected archives; no bulk wheelhouse or model copy.
   - FastAPI and Rich keep their unchanged standalone archives, no import repair.
     Validate the effective native resolver tuple for ALL THREE tasks. Reject a
     fallback, alternative candidate, duplicate/extra patch, path escape, stale
     view, changed base hash, conflicting/ignored alias or unsupported link mode.
     Do not fall back to another import technique.
   - Check each original archive/tree against existing acquisition/history pins
     before overlay. For Requests independently prove the derived layout differs
     only by the declared symlink. Record original and derived identities
     separately; generated native bootstrap files are a separate phase.
   - Configure the actual EvalConfig.snapshots_dir to the derived view, shared by
     the official evaluator's agent and verification phases. Do not inject
     patch_path directly into verify_task while leaving agent setup uncorrected.

Host adapter creates disabled notebook/derived envelope via official base-plus-delta resolver; parent C8K closures stay byte-identical and actual-input provenance is distinct from parent binding.

Static immutable implementation evidence plus historical receipts; no execution/import of historical product code here.


Pending: Separately approve integration before transferring this implementation to develop.

### notebook-import-cpu:proposal-paragraph-013 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-013`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/notebook_import.py`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/report.md`.

Contract: 3. Honest actual-input provenance without weakening the old guard:
   - Leave runner.validate_bindings and its standalone checks byte-identical.
   - Introduce a strictly validated, versioned HOST envelope
     mostaza.notebook-layout-evaluation/v1 with parent_binding and actual_execution.
     The parent binding describes only the unchanged source view, not the actual
     derived execution. Do not emit a legacy manifest falsely claiming that the
     original snapshot digest is the digest executed after the overlay.
   - Run the old validator on an explicitly constructed parent view. Then prove
     field-by-field that the actual config differs ONLY in snapshots_dir; validate
     that actual view against the complete derived component inventory. All other
     model/archive/budget/task/wheelhouse constraints still apply to actual config.
     No fake server starts or GPU readiness claim in CPU contract tests.
   - Bind actual task IDs/repos, source archive/history, role/path/size/SHA256 for
     effective/base/delta, layout hash, original and derived tree receipts, native
     source hashes and host payload/closure hashes. Verify immediately before
     evaluator construction and each task dispatch; refuse drift. Keep input view
     immutable during serial dispatch.
   - Export the envelope and reference its hash from host raw-result metadata.
     Preserve native TaskResult fields. Old comparison ingestion must not silently
     treat this new envelope as a historical real-run manifest. Any future
     normalizer extension needs explicit schema handling.
   - CPU tests must reject changes to actual budgets/model/tasks/closure, a claimed
     parent-as-actual digest, and an overridden resolver tuple. Validating a parent
     config alone is insufficient for acceptance.

Host adapter creates disabled notebook/derived envelope via official base-plus-delta resolver; parent C8K closures stay byte-identical and actual-input provenance is distinct from parent binding.

Static immutable implementation evidence plus historical receipts; no execution/import of historical product code here.


Pending: Separately approve integration before transferring this implementation to develop.

### notebook-import-cpu:proposal-paragraph-014 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-014`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/notebook_import.py`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/report.md`.

Contract: 4. Packaging, isolation and safe CPU extraction:
   - Positive-allowlist notebook host payload, deterministic generation and hashes.
     Agent ZIPs remain exactly the approved C8K closures. The layout module and
     delta are HOST inputs; diagnostic tests, behavioral expectations, retained
     E0/E1 patches/results, reference patches and hidden tests must never enter
     agent archives, prompts or the notebook's production payload.
   - Real-run tasks still use the native hydration/verification route, unmodified;
     no reference/test content is copied into visible task data.
   - Factor the notebook's pure layout preparation through the same host function
     called by offline CPU tests. Do not execute the complete notebook, bypass its
     guard, import a model server or synthesize a launch authorization for tests.
     Static/contract tests of execution wiring must be labeled as such.
   - No PYTHONPATH/sys.path/.pth/sitecustomize/conftest repair, dependency install,
     custom loader, native monkeypatch, manager subclass/name spoof or verifier
     wrapper. Normal host payload import bootstrapping is not a product import fix.

Host adapter creates disabled notebook/derived envelope via official base-plus-delta resolver; parent C8K closures stay byte-identical and actual-input provenance is distinct from parent binding.

Static immutable implementation evidence plus historical receipts; no execution/import of historical product code here.


Pending: Separately approve integration before transferring this implementation to develop.

### notebook-import-cpu:proposal-paragraph-016 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-016`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/notebook_import.py`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/report.md`.

Contract: A. Add the new specification, minimal host adapter, derived-input envelope and
   immutable-input checks. No edits to native sources or frozen runner.
B. Generate the fresh blocked notebook and new host experiment manifests. Verify
   that native Evaluator construction/dispatch and secret handling remain intact.
C. Add tests for guards, provenance, delta rejection, three-task resolution,
   closure isolation, relocation and cleanup; implement the bounded new CPU matrix.
D. Run the exact full gate below. Produce compact evidence and ignored raw
   records; obtain an independent audit of the complete relevant diff and raw
   evidence. Correct findings within the approved limits; never weaken the gate.
E. Only after gate PASS and independent audit PASS with zero findings: commit,
   push and update existing PR2 toward develop; no merge. Preserve the dirty plan.

Host adapter creates disabled notebook/derived envelope via official base-plus-delta resolver; parent C8K closures stay byte-identical and actual-input provenance is distinct from parent binding.

Static immutable implementation evidence plus historical receipts; no execution/import of historical product code here.


Pending: Separately approve integration before transferring this implementation to develop.

### notebook-import-cpu:proposal-paragraph-018 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-018`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/cpu-results.json#/rows`.

Contract: Run each row serially from a fresh relocated root outside the repository, with
spaces and Unicode in its path and a different launch cwd. Materialize the
notebook's allowlisted host payload there and use its actual layout-preparation
function. Do not rely on the developer checkout being importable. Original inputs
are hash-checked and treated as read-only. A distinct invocation/receipt binds every
setup and verification sandbox; no receipt borrowed from historical runs.

Six separate setup and six verification witnesses bind the same resolved inputs; baseline fails two empty-credential checks, E0 missing-match raises TypeError, E1 passes five OWN nodes. Setup observes baseline; verification observes retained patch.

Actual macOS ARM/Python3.13.15/pytest9.1.1 diagnostic coverage only; raw JUnit is removed by native cleanup and not replaced by test-body telemetry.


Pending: Preserve native/semantic/binding distinctions; separately validate future production/scorer portability.

### notebook-import-cpu:proposal-paragraph-019:N-L01 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-019`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/cpu-results.json#/rows/0`.

Contract: | N-L01 | Owned faulty src package + generic alias | Setup binds source; native verification reaches intended behavior failure, resolved=false. |

Expected control/observation reached; native outcome retained separately from binding.

Owned diagnostic nodes only, not hidden tests or task scores.

Observed: {"binding": true, "id": "N-L01", "native_resolved": false, "node_outcomes": {"test_required": "assertion_failed"}, "setup_binding": true, "test_exit_code": 1}
Pending: Preserve this scoped diagnostic; no rerun allowance transfers.

### notebook-import-cpu:proposal-paragraph-019:N-L02 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-019`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/cpu-results.json#/rows/1`.

Contract: | N-L02 | Same with own generic correct patch | Setup binds baseline source; verification binds patched source and resolved=true. |

Expected control/observation reached; native outcome retained separately from binding.

Owned diagnostic nodes only, not hidden tests or task scores.

Observed: {"binding": true, "id": "N-L02", "native_resolved": true, "node_outcomes": {"test_required": "passed"}, "setup_binding": true, "test_exit_code": 0}
Pending: Preserve this scoped diagnostic; no rerun allowance transfers.

### notebook-import-cpu:proposal-paragraph-019:N-L03 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-019`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/cpu-results.json#/rows/2`.

Contract: | N-L03 | Same with own generic incorrect patch | Setup binds baseline source; verification binds wrong patched source and intended behavior fails. |

Expected control/observation reached; native outcome retained separately from binding.

Owned diagnostic nodes only, not hidden tests or task scores.

Observed: {"binding": true, "id": "N-L03", "native_resolved": false, "node_outcomes": {"test_required": "assertion_failed"}, "setup_binding": true, "test_exit_code": 1}
Pending: Preserve this scoped diagnostic; no rerun allowance transfers.

### notebook-import-cpu:proposal-paragraph-019:N-R00 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-019`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/cpu-results.json#/rows/3`.

Contract: | N-R00 | Pinned Requests baseline + Requests alias | Setup and verification bind canonical snapshot source; five own diagnostic nodes reached. |

Expected control/observation reached; native outcome retained separately from binding.

Owned diagnostic nodes only, not hidden tests or task scores.

Observed: {"binding": true, "id": "N-R00", "native_resolved": false, "node_outcomes": {"test_empty_default": "assertion_failed", "test_empty_machine": "assertion_failed", "test_missing": "passed", "test_origin_binding": "passed", "test_valid": "passed"}, "setup_binding": true, "test_exit_code": 1}
Pending: Preserve this scoped diagnostic; no rerun allowance transfers.

### notebook-import-cpu:proposal-paragraph-019:N-R01 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-019`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/cpu-results.json#/rows/4`.

Contract: | N-R01 | Same plus exact retained E0 agent_patch | Setup binds baseline; verification binds the actual E0-patched source; all five own nodes reached. |

Expected control/observation reached; native outcome retained separately from binding.

Owned diagnostic nodes only, not hidden tests or task scores.

Observed: {"binding": true, "id": "N-R01", "native_resolved": false, "node_outcomes": {"test_empty_default": "passed", "test_empty_machine": "passed", "test_missing": "exception", "test_origin_binding": "passed", "test_valid": "passed"}, "setup_binding": true, "test_exit_code": 1}
Pending: Preserve this scoped diagnostic; no rerun allowance transfers.

### notebook-import-cpu:proposal-paragraph-019:N-R02 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-019`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/cpu-results.json#/rows/5`.

Contract: | N-R02 | Same plus exact retained E1 agent_patch | Setup binds baseline; verification binds the actual E1-patched source; all five own nodes reached. |

Expected control/observation reached; native outcome retained separately from binding.

Owned diagnostic nodes only, not hidden tests or task scores.

Observed: {"binding": true, "id": "N-R02", "native_resolved": true, "node_outcomes": {"test_empty_default": "passed", "test_empty_machine": "passed", "test_missing": "passed", "test_origin_binding": "passed", "test_valid": "passed"}, "setup_binding": true, "test_exit_code": 0}
Pending: Preserve this scoped diagnostic; no rerun allowance transfers.

### notebook-import-cpu:proposal-paragraph-020 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-020`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/cpu-results.json#/rows`.

Contract: A setup probe uses the REAL SubprocessManager and unmodified native setup functions
in the reviewed agent pre-model sequence: wheels, extraction, Git exclude,
editable/dependency setup (native subprocess skips these), workspace config and
baseline. Execute an owned, read-only import witness after that sequence. This is
a reconstruction/setup probe, NOT an execution of run_agent_in_sandbox,
Evaluator.evaluate_task, a model or an agent loop. Pin/review the official agent
prefix and statically verify evaluator forwarding separately. Do not intercept
the native loop or monkeypatch it to claim an end-to-end agent execution.

Six separate setup and six verification witnesses bind the same resolved inputs; baseline fails two empty-credential checks, E0 missing-match raises TypeError, E1 passes five OWN nodes. Setup observes baseline; verification observes retained patch.

Actual macOS ARM/Python3.13.15/pytest9.1.1 diagnostic coverage only; raw JUnit is removed by native cleanup and not replaced by test-body telemetry.


Pending: Preserve native/semantic/binding distinctions; separately validate future production/scorer portability.

### notebook-import-cpu:proposal-paragraph-021 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-021`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/cpu-results.json#/rows`.

Contract: Then call unmodified native verify_task using the EXACT resolver input tuple from
that notebook view and a fresh real manager sandbox. For Requests retain the five
owned R-IMPORT diagnostic nodes and unchanged agent_patch bytes; do not use original
Task.patch/test_patch. Setup observes baseline; verification observes baseline or
the respective retained patch. Record raw/canonical paths, alias target, module/file
hash, loaded function fingerprint, PID, executable, Python/pytest and native results.
Require actual source binding in BOTH phases; compare structural receipts to the
pinned originals. Show alias is in the native baseline and does not leak into
agent_patch. No new Requests solution is authored.

Six separate setup and six verification witnesses bind the same resolved inputs; baseline fails two empty-credential checks, E0 missing-match raises TypeError, E1 passes five OWN nodes. Setup observes baseline; verification observes retained patch.

Actual macOS ARM/Python3.13.15/pytest9.1.1 diagnostic coverage only; raw JUnit is removed by native cleanup and not replaced by test-body telemetry.


Pending: Preserve native/semantic/binding distinctions; separately validate future production/scorer portability.

### notebook-import-cpu:proposal-paragraph-022 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-022`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/cpu-results.json#/rows`.

Contract: Do not require a particular retained E0/E1 behavioral PASS. Unexpected setup,
collection, unrelated import error, absent node or stale witness is BLOCKED, not a
successful negative control. Generic correct/wrong controls must discriminate.
FastAPI/Rich get full native resolver/provenance and byte-identity checks, but no
new native sandbox/verifier run here; do not claim their imports are fixed.

Six separate setup and six verification witnesses bind the same resolved inputs; baseline fails two empty-credential checks, E0 missing-match raises TypeError, E1 passes five OWN nodes. Setup observes baseline; verification observes retained patch.

Actual macOS ARM/Python3.13.15/pytest9.1.1 diagnostic coverage only; raw JUnit is removed by native cleanup and not replaced by test-body telemetry.


Pending: Preserve native/semantic/binding distinctions; separately validate future production/scorer portability.

### notebook-import-cpu:proposal-paragraph-023 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-023`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:src/mostaza/evaluation/notebook_import.py`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/report.md`.

Contract: Production preparation accepts only the pinned three-task cohort and the Requests
alias. Generic src-package controls are explicitly CPU fixture inputs, never
accepted as production tasks or included in production payload data. Test fixture
support must not broaden the production allowlist.

Host adapter creates disabled notebook/derived envelope via official base-plus-delta resolver; parent C8K closures stay byte-identical and actual-input provenance is distinct from parent binding.

Static immutable implementation evidence plus historical receipts; no execution/import of historical product code here.


Pending: Separately approve integration before transferring this implementation to develop.

### notebook-import-cpu:proposal-paragraph-025 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-025`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/cpu-results.json#/python312_transport`.

Contract: Use the EXISTING Python3.12.8 executable, no new environment/dependencies. The
isolated checker uses only stdlib plus installed Git. Reconstruct one generic
source fixture and the real Requests baseline through the same retained,
versioned layout artifact contract in fresh relocated roots. Verify manifest
hashes, Git patch/symlink mode/target, in-root canonical paths and unchanged
Requests product-file hashes. Import the generic dependency-free package from
an ordinary workspace-root Python process; record the actual interpreter.

Two Python3.12.8 stdlib transport probes assessed; generic package import only.

Requests import/native verify_task in Python3.12 and Linux remain NOT_TESTED; no dependencies were installed.


Pending: Separately approve actual Linux/native Python3.12 Requests validation.

### notebook-import-cpu:proposal-paragraph-026 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-026`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/cpu-results.json#/python312_transport`.

Contract: This proves transport/layout behavior under another interpreter. It does NOT
import Requests in3.12, run native verify_task in3.12, or establish Linux/Kaggle
dependency compatibility. Do not expose Python3.13 site-packages to3.12, install
missing dependencies, copy compiled extensions or report a skipped probe as PASS.
AST/compile checks for Python3.12 syntax cover all new notebook cells and payload
sources. No Docker/Colima execution is authorized.

Two Python3.12.8 stdlib transport probes assessed; generic package import only.

Requests import/native verify_task in Python3.12 and Linux remain NOT_TESTED; no dependencies were installed.


Pending: Separately approve actual Linux/native Python3.12 Requests validation.

### notebook-import-cpu:proposal-paragraph-028 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-028`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/gate-attempts.json#/attempts`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/audit.json`.

Contract: All commands run from the worktree, serially and once per attempt. Commands1–10
are unchanged regression checks; command9 runs eleven legacy native verifications,
command10 runs nine R-IMPORT native verifications. Command11 runs exactly the six
NEW native verifications plus six setup probes. Command12 runs exactly two
stdlib-only3.12 probes and no native verifier.

Final corrected full gate and independent scoped audit passed; prior failures remain failed and each added attempt is separately sourced.

Consumed historical CPU allowances; zero authorization for another native run or for this checkout.


Pending: Use a fresh approved scope/budget before any future execution.

### notebook-import-cpu:proposal-paragraph-033 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-033`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/gate-attempts.json#/attempts`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/audit.json`.

Contract: Only a justified corrective attempt2 is permitted; same twelve commands with
gate-1 replaced by gate-2 in commands11–12. Attempt directories must be created
exclusively. Preserve every earlier raw run. Record exact argv, current source and
input inventories, command exits/wall times/log hashes and all started/completed/
assessed counts. No implicit native calls in unit/integration tests or audit.

Final corrected full gate and independent scoped audit passed; prior failures remain failed and each added attempt is separately sourced.

Consumed historical CPU allowances; zero authorization for another native run or for this checkout.


Pending: Use a fresh approved scope/budget before any future execution.

### notebook-import-cpu:proposal-paragraph-034 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-034`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/gate-attempts.json#/attempts/5`.

Contract: The outer runner owns the deadline and detached native child groups, not just its
controller. Extend the proven owned-output discovery/cleanup pattern in NEW code
for these worker paths. Remove only this attempt's temporary input views, fixtures
and sandboxes, never retained results or symlink targets outside owned scratch.
For interrupted controllers perform scoped cleanup explicitly; Python finally
alone is insufficient after termination. Cleanup failure blocks PASS.
No source mutation during the gate; a source repair requires the corrected full
gate before closure. Auditor may run focused non-native tests, not extra matrices.

Corrected final gate reports complete scoped cleanup and bounded wall time; original interrupted/cap failures remain in the history.

Polled limits are not an instantaneous physical peak. V/R peak bytes and process CPU time were not retained; N peak is sampled 556434407 bytes.


Pending: Retain null reasons and bounded supervision requirements in future protocols.

### notebook-import-cpu:proposal-paragraph-036 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-036`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/gate-attempts.json#/attempts`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/audit.json`.

Contract: All twelve commands must exit0; immutable checks before/after and cleanup pass;
all six new rows, setup witnesses, paired actual inputs, generic controls and both
3.12 probes meet the contract; independent audit returns PASS with zero findings.
Payload isolation, fail-closed execution guard and actual-vs-parent provenance are
mandatory acceptance criteria. Local import success alone is insufficient.

Final corrected full gate and independent scoped audit passed; prior failures remain failed and each added attempt is separately sourced.

Consumed historical CPU allowances; zero authorization for another native run or for this checkout.


Pending: Use a fresh approved scope/budget before any future execution.

### notebook-import-cpu:proposal-paragraph-037 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-037`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/gate-attempts.json#/attempts`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/audit.json`.

Contract: Budget per complete gate: max26 verify_task calls (11+9+6), six setup probes and
two stdlib portability probes; all serial. Native verification/commands30s,
each new row90s, each3.12 probe90s; one1200s outer wall deadline for ALL commands,
including regressions, build/fixtures, export and cleanup. Reserve30s for cleanup:
terminate owned work by1170s and finish cleanup/receipts by1200s. Start no new
90s case/probe with less than120s left. If cleanup cannot finish within the total
deadline, report BLOCKED and the outstanding owned paths/processes; do not declare
PASS. No automatic command/case retry.

Final corrected full gate and independent scoped audit passed; prior failures remain failed and each added attempt is separately sourced.

Consumed historical CPU allowances; zero authorization for another native run or for this checkout.


Pending: Use a fresh approved scope/budget before any future execution.

### notebook-import-cpu:proposal-paragraph-038 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-038`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/gate-attempts.json#/attempts`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/audit.json`.

Contract: Maximum TWO full gate attempts: initial plus one actual failure/audit repair
documented with focused non-native checks. Total ceilings:52 native verifications,
12 setup probes,4 stdlib portability probes,40min gate wall time. Any additional
native call or gate attempt requires a new authorization. Other existing CPU
fixtures/subprocesses are included in wall/artifact ceilings and are not model
evaluations. Do not run native matrices outside this runner, including for audit.

Final corrected full gate and independent scoped audit passed; prior failures remain failed and each added attempt is separately sourced.

Consumed historical CPU allowances; zero authorization for another native run or for this checkout.


Pending: Use a fresh approved scope/budget before any future execution.

### notebook-import-cpu:proposal-paragraph-039 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-039`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/gate-attempts.json#/attempts/5`.

Contract: At most1GiB additional owned temporary/retained files at any time across all fresh
gate outputs and legacy regression outputs; require sufficient free disk, poll
usage and record sampled peak(bytes), not a guaranteed physical peak. Stream/copy
only the selected archives; original resources are not counted as newly created
but copies are. No download/install/upgrade, model access, service or image/VM
creation. Cap/deadline/pin drift/missing input means BLOCKED, no improvised fallback.

Corrected final gate reports complete scoped cleanup and bounded wall time; original interrupted/cap failures remain in the history.

Polled limits are not an instantaneous physical peak. V/R peak bytes and process CPU time were not retained; N peak is sampled 556434407 bytes.


Pending: Retain null reasons and bounded supervision requirements in future protocols.

### notebook-import-cpu:proposal-paragraph-040 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-040`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/cpu-results.json#/rows`.

Contract: Report notebook integration, native macOS/3.13 binding and3.12 layout checks as
separate dimensions. Label success CPU_NOTEBOOK_LAYOUT_INTEGRATION_VALIDATED,
with linux_runtime_portability=NOT_TESTED, private_scorer_parity=null(reason),
gpu_readiness=false and real_evaluations=NOT_RUN. This label does not certify a
full notebook run, Kaggle task score or recovery strategy. An actual Linux3.12
CPU run, and later a real Kaggle run, remain separate pending decisions.
Absence of telemetry is null with coverage/reason, never zero.

Published readiness stays false and scorer parity null; scoped CPU milestone does not claim a real evaluation or full notebook loop.

Historical source review and diagnostic success do not establish private scorer or hybrid efficacy.


Pending: Keep real evaluation blocked until separately approved readiness evidence.

### notebook-import-cpu:proposal-paragraph-042 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-042`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/gate-attempts.json#/attempts`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/audit.json`.

Contract: Approval would cover the described specification delta, CPU-only implementation,
exact gate and NEW bounded budget, independent audit/corrections, commit/push and
update of PR2 toward develop after PASS. It would NOT authorize merge, GPU/model
calls, Kaggle API/browser/session mutations, notebook publication, submissions,
Discussion/outreach, a Linux service start or changes to the real verifier.

Final corrected full gate and independent scoped audit passed; prior failures remain failed and each added attempt is separately sourced.

Consumed historical CPU allowances; zero authorization for another native run or for this checkout.


Pending: Use a fresh approved scope/budget before any future execution.

### notebook-import-cpu:proposal-paragraph-043 — supported

Source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/plan-for-approval.md#paragraph-043`.

Evidence: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/gate-attempts.json#/attempts`, `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/audit.json`.

Contract: Deliver: fresh blocked notebook, explicit derived-input manifests, reproducible
commands, CPU/setup/portability receipts, raw inventory, audit and limitations,
runbook append and updated PR2. Preserve all historical evidence.

Final corrected full gate and independent scoped audit passed; prior failures remain failed and each added attempt is separately sourced.

Consumed historical CPU allowances; zero authorization for another native run or for this checkout.


Pending: Use a fresh approved scope/budget before any future execution.

## CPU milestone receipts

### verify-task-cpu

{"audit": {"findings": 0, "source": "1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/audit.json", "verdict": "PASS"}, "authorization_receipts": ["1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/approval.json", "1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/additional-attempt-approval.json"], "consumed_attempts": 3, "count_scope": "Standalone V attempts only; later R/N regressions counted in those gates", "cumulative_native_diagnostics": 23, "final_command_count": 9, "final_gate_wall_seconds": 98.86652154200056, "future_native_allowance": 0, "history": [{"attempt": 1, "passed": false, "wall_seconds": 96.19507687499936}, {"attempt": 2, "passed": false, "wall_seconds": 81.09148191699933}, {"attempt": 3, "passed": true, "wall_seconds": 98.86652154200056}], "history_assessed": [6, 4, 11], "history_native_results": [7, 5, 11], "initial_allowed_attempts": 2, "protocol_status": "CPU_E2E_CONTROLS_PASS_REQUESTS_BINDING_MISMATCH", "published_final_tests": {"integration": 45, "unit": 306}, "separate_additional_attempts": 1, "test_count_source": "1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/report.md", "workflow_kind": "ORDINARY"}

### requests-import-cpu

{"audit": {"findings": 0, "source": "1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/audit.json", "verdict": "PASS"}, "authorization_receipts": ["1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/approval.json", "1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/corrective-attempt.json"], "consumed_attempts": 2, "cumulative_native_diagnostics": 40, "final_command_count": 10, "final_gate_wall_seconds": 176.90367750000223, "future_native_allowance": 0, "history": [{"attempt": 1, "passed": true, "wall_seconds": 142.78773570900012}, {"attempt": 2, "passed": true, "wall_seconds": 176.90367750000223}], "initial_allowed_attempts": 2, "new_native_per_gate": 9, "protocol_status": "CPU_REQUESTS_IMPORT_BINDING_VALIDATED", "published_final_tests": {"integration": 49, "unit": 328}, "regression_native_per_gate": 11, "separate_additional_attempts": 0, "test_count_source": "1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/report.md", "workflow_kind": "ORDINARY"}

### notebook-import-cpu

{"audit": {"findings": 0, "source": "1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/audit.json", "verdict": "PASS"}, "authorization_receipts": ["1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/approval.json", "1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/additional-gate-approval.json", "1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/resource-gate-approval.json", "1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/source-filter-gate-approval.json", "1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/supervision-gate-approval.json"], "consumed_attempts": 6, "cumulative_gate_wall_seconds": 1003.3448512079922, "cumulative_native_diagnostics": 114, "cumulative_native_results": 113, "cumulative_setup": 14, "cumulative_stdlib": 2, "final_command_count": 12, "final_counts": {"legacy_native": [{"assessed": 9, "assessed_reason": null, "completed": 9, "native_start_lower_bound": 9, "raw_path": "/Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness/results/requests-import-cpu/matrix-ff29faa0-373a-4c6f-8e44-aa79a818dd19", "started": 9, "started_reason": null, "worker_starts": 9, "worker_starts_reason": null}, {"assessed": 11, "assessed_reason": null, "completed": 11, "native_start_lower_bound": 11, "raw_path": "/Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness/results/verify-task-cpu/bfad524f-f9e0-4176-974c-e8b8b27798b7", "started": 11, "started_reason": null, "worker_starts": 11, "worker_starts_reason": null}], "native_total": {"assessed": 26, "assessed_reason": null, "completed": 26, "started": 26, "started_reason": null}, "new_native": {"assessed": 6, "completed": 6, "started": 6}, "setup": {"assessed": 6, "completed": 6, "started": 6}, "stdlib": {"assessed": 2, "completed": 2, "started": 2}}, "final_gate_wall_seconds": 211.39025270799903, "future_native_allowance": 0, "history": [{"attempt": 1, "failure": "PermissionError: [Errno 1] Operation not permitted", "native_results": 19, "native_started": 20, "passed": false, "setup_started": 0, "stdlib_started": 0, "wall_seconds": 253.49931737500083}, {"attempt": 2, "failure": "ValueError: Gate command failed: .tools/official/bin/python scripts/check_notebook_import_cpu.py --check --output results/notebook-import-cpu/gate-2/matrix", "native_results": 21, "native_started": 21, "passed": false, "setup_started": 1, "stdlib_started": 0, "wall_seconds": 171.20347295899774}, {"attempt": 3, "failure": "ValueError: Whole CPU gate artifact ceiling", "native_results": 0, "native_started": 0, "passed": false, "setup_started": 0, "stdlib_started": 0, "wall_seconds": 6.929505082996911}, {"attempt": 4, "failure": "ValueError: Gate command failed: .tools/official/bin/python scripts/check_notebook_import_cpu.py --check --output results/notebook-import-cpu/gate-4/matrix", "native_results": 23, "native_started": 23, "passed": false, "setup_started": 3, "stdlib_started": 0, "wall_seconds": 144.3997087500029}, {"attempt": 5, "failure": "TimeoutExpired: Command '['ps', '-ww', '-axo', 'pid=,ppid=,pgid=,command=']' timed out after 2 seconds", "native_results": 24, "native_started": 24, "passed": false, "setup_started": 4, "stdlib_started": 0, "wall_seconds": 215.92259433299478}, {"attempt": 6, "failure": null, "native_results": 26, "native_started": 26, "passed": true, "setup_started": 6, "stdlib_started": 2, "wall_seconds": 211.39025270799903}], "initial_allowed_attempts": 2, "protocol_status": "CPU_GATE_PASS", "published_final_tests": {"integration": 119, "unit": 378}, "sampled_peak_bytes": 556434407, "separate_additional_attempts": 4, "test_count_source": "1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/report.md", "workflow_kind": "ORDINARY"}

## Current retained-input integrity

Counts are inventory references, including historical checkpoints; unique files/bytes hashed are separately deduplicated. MATCH means SHA256 and size where declared, never native execution.

- `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/checkpoints/before-additional-gate/raw-inventory.json`: {"MATCH": 276}; 1647767 declared bytes; 0 hash-only entries.
- `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/checkpoints/before-resource-gate/raw-inventory.json`: {"MATCH": 280}; 1654295 declared bytes; 0 hash-only entries.
- `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/checkpoints/before-source-filter-gate/raw-inventory.json`: {"MATCH": 450}; 2663525 declared bytes; 0 hash-only entries.
- `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/checkpoints/before-supervision-gate/raw-inventory.json`: {"MATCH": 628}; 3683590 declared bytes; 0 hash-only entries.
- `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-notebook-import-cpu/raw-inventory.json`: {"MATCH": 848}; 5071316 declared bytes; 0 hash-only entries.
- `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-pcv01-access/raw-inventory.json`: {"MATCH": 16}; 157102 declared bytes; 0 hash-only entries.
- `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-pcv01-cpu/raw-inventory.json`: {"MATCH": 158}; 206192 declared bytes; 0 hash-only entries.
- `docs/implementation/evidence/mostaza-phase1-foundation/official-validation.json::results/kaggle-v2-358139443/private-run-evidence/99c637be-d945-4dd7-85d8-4042cfcc2bad/source-inventory.json`: {"MATCH": 32}; 0 declared bytes; 32 hash-only entries.
- `docs/implementation/evidence/mostaza-phase2-observed-run/acquisition.json::results/kaggle-phase2-observed-6526b0decc91474cb1bd3335d77d06a0/download-inventory.json`: {"MATCH": 34}; 504399 declared bytes; 0 hash-only entries.
- `docs/implementation/evidence/mostaza-phase2-startup-run/acquisition.json::results/kaggle-phase2-startup-v3-ea1534a86873409b870b3b04d04e347f/download-inventory.json`: {"MATCH": 56}; 1061978 declared bytes; 0 hash-only entries.
- `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-requests-import-cpu/raw-inventory.json`: {"MATCH": 262}; 1693554 declared bytes; 0 hash-only entries.
- `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/checkpoints/before-additional-attempt/raw-inventory.json`: {"MATCH": 91}; 442274 declared bytes; 0 hash-only entries.
- `1b86b19f7654212c1d9f95eeca84d0e2a05db16b:docs/implementation/evidence/mostaza-verify-task-cpu/raw-inventory.json`: {"MATCH": 163}; 852381 declared bytes; 0 hash-only entries.

Other published structured path/hash pins: {"EXCLUDED_UNPUBLISHED_CONTINUITY": 4, "MATCH": 622, "MISMATCH": 35, "NOT_RETAINED_TEMPORARY_INPUT_VIEW": 30}.

Hash traversal: {"byte_unit": "bytes", "bytes_hashed": 945617781, "inventory_references": 3951, "max_bytes": 4294967296, "max_entries": 10000, "unique_readable_files": 2006}.

Missing/mismatched/incomplete/unresolved pins have exact reasons in the JSON. Missing evidence limits reproducibility and never supports verification. Old unpublished continuity is excluded.

## Pending roadmap

- integration: prerequisite: Separate user decision on still-unmerged PR2. Exit evidence: Reviewed integration strategy and synchronized develop in a fresh worktree. Authorization: Separate integration approval; no merge/cherry-pick/import here.
- portable-cpu: prerequisite: Integrated source and declared clean-worktree resources. Exit evidence: Linux/native Python3.12 actual Requests imports, setup/verify_task, raw/canonical/function witnesses, negative controls and cleanup. Authorization: New exact gate and finite wall/storage/native allowance; six historical N allowances spent.
- private-scorer: prerequisite: Accessible authoritative contract evidence. Exit evidence: Source-backed private/public scorer comparison; otherwise parity null and readiness false. Authorization: Separate external access decision; no Discussion authority.
- matched-kaggle: prerequisite: Readiness review, frozen three tasks and matched model/sampling/environment/verification/repair. Exit evidence: Fresh contemporaneous E0/E1 six records including failures, native receipts and paired denominators. Authorization: Separate per-batch GPU quota and enforced termination; no B300/R180 automatic batch or reused baseline.
- hybrid-research: prerequisite: Fixed calibration and observed retrieval backend evidence. Exit evidence: Treatment adherence, sourced graph/similarity/backend measurements and all inconclusive outcomes. Authorization: New research protocol; no significance/superiority claim from small cohort.

## Limits

- Source hashes and retained input integrity are current read-only observations, not native replay or semantic proof.
- Historical assertions belong to their pinned reports; no transferred PASS or current official API claim.
- Unknown backend/pure time/repair/localization/Recall@K/context ratio stay null unless separately evidenced.
- All native/GPU evaluation allowances here are zero; report does not authorize any pending roadmap action.

Independent reconciliation PR targets develop on sdd/mostaza-phase2-reconciliation after this deliverable's own gate/audit. PR2 is historical evidence; future implementation requires a separately approved integration strategy and fresh validation.
