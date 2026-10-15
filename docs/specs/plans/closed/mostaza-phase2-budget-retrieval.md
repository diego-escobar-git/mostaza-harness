# mostaza-phase2-budget-retrieval

## Original requirement

Iteración 2 de Mostaza Harness: calibración de presupuestos e instrumentación de recuperación híbrida.

Trabaja sobre el repositorio mostaza-harness:
- Ruta local: /Users/diego/Documents/Desarrollo/Mostaza Dev/PyCharm Projects/Mostaza-Harness
- Remoto: git@github.com:diego-escobar-git/mostaza-harness.git
- PR de la primera iteración: https://github.com/diego-escobar-git/mostaza-harness/pull/1
- Commit: e3b57574a9f9ca1aca80039ec401637e0306198d
- Worktree anterior: /Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness

Sigue AGENTS.md y el flujo SDD completo. Inspecciona primero el estado de Git y del PR. No asumas que está integrado en develop. Si develop aún no contiene la primera iteración, explica esa dependencia y solicita la decisión necesaria antes de implementar. No hagas merge automáticamente ni modifiques el worktree anterior. Crea el nuevo worktree mediante el runtime SDD.

CONTEXTO VERIFICADO
La primera iteración implementó:
- E0: baseline derivado del ejemplo oficial, con un único LlmAgent.
- E1: el mismo agente con instrucciones de exploración híbrida adaptativa.
- Configuraciones declarativas, empaquetado explícito y herramientas locales de evaluación.
- Registro de resultados, comparación reproducible y verificación de procedencia.
- 92 pruebas unitarias y 29 de integración aprobadas.
- Gate completo aprobado y auditoría independiente PASS sin hallazgos.
Se realizaron seis evaluaciones REALES en Kaggle con gemma-4-31b-it-qat-w4a16-ct, NVIDIA L4 x4, harness oficial y las mismas tres tareas para E0 y E1: requests_7205, fastapi_15589, rich_3061.
Resultados por configuración: PASS 0; FAIL 1 (Requests con parche aplicable y verificación fallida); ERROR 2 (FastAPI y Rich sin parche ni verificación). Las seis ejecuciones alcanzaron el timeout de sesión de un minuto. Requests: 205 pruebas aprobadas, 13 omitidas y 1 fallida. Tokens totales: E0 223770; E1 146555. Intentos de herramientas: E0 29; E1 22. Llamadas cobradas por el harness: E0 27; E1 21. E1 no realizó ninguna llamada vectorial ni de grafos. E0 realizó una llamada vectorial; ninguna configuración utilizó grafos. Estos resultados NO demuestran eficacia de Hybrid Graph-Vector Retrieval ni superioridad de E1.

FUENTES
Lee las especificaciones y estos archivos de la primera iteración:
- docs/architecture.md
- docs/experiments.md
- docs/kaggle-setup.md
- experiments/cohort.json
- experiments/E0-baseline/manifest.json
- experiments/E1-hybrid-retrieval/manifest.json
- docs/implementation/evidence/mostaza-phase1-foundation/report.md
- Los demás archivos compactos de evidencia de esa carpeta.
Los paquetes nativos, trazas y notebook ejecutado se conservaron fuera de Git bajo /Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/results/kaggle-v2-358139443/.
Notebook privado: https://www.kaggle.com/code/diegofescobar/mostaza-e0-e1-phase-1-paired-benchmark
Utiliza las evidencias anteriores en modo de lectura. Si faltan recursos, documenta qué falta y no sustituyas resultados reales por datos simulados.

OBJETIVO
Preparar una segunda comparación real que permita observar implementación, verificación y uso efectivo de las herramientas de recuperación, con presupuestos justificados por la evidencia anterior.

INVESTIGACIÓN Y PLANIFICACIÓN
1. Analiza las trazas para determinar qué consumió el tiempo y por qué no se completaron las soluciones.
2. Investiga el fallo de Requests para análisis posterior. No incorpores la solución de referencia ni las pruebas ocultas a los prompts o al contexto del agente.
3. Revisa las restricciones y APIs oficiales actuales antes de modificar configuraciones.
4. Propón una calibración pequeña de presupuestos basada en los tiempos y límites observados. Mantén el mismo presupuesto dentro de cada comparación E0/E1.
5. Identifica las métricas que pueden obtenerse fielmente de las trazas oficiales y las que requieren instrumentación adicional.
6. Define en las especificaciones criterios de aceptación, condiciones comparables, límites de gasto y gate exacto. Presenta la delta de especificaciones y el plan para aprobación.

IMPLEMENTACIÓN ESPERADA TRAS LA APROBACIÓN
- Conservar los resultados y configuraciones originales como evidencia inmutable.
- Añadir nuevos identificadores y manifiestos para los experimentos.
- Separar la calibración de presupuesto de cualquier cambio posterior en las instrucciones de recuperación.
- Mantener iguales modelo, sampling, entorno, tareas, verificación y estrategia de reparación dentro de cada par.
- Mantener un único LlmAgent y el harness oficial.
- No añadir servicios externos, otro modelo, bases vectoriales, fine-tuning ni infraestructura innecesaria.
- Aprovechar search_similar_code con símbolos existentes y las herramientas nativas de grafos.
- Registrar llamadas léxicas, vectoriales y de grafos, intentos frente a llamadas cobradas, tokens, timeout, parches y verificación.
- Definir unidades y cobertura de las métricas; conservar null con razones cuando no puedan medirse.
- No interpretar ausencia de telemetría como cero.
- Si se modifica E1, documentar exactamente el cambio y comprobar en las trazas si el agente empleó la estrategia.

EVALUACIÓN Y SEGURIDAD EXPERIMENTAL
- Mantener inicialmente el mismo cohort de tres tareas.
- No orientar al agente con información obtenida de soluciones de referencia o resultados esperados.
- No forzar llamadas vectoriales o de grafos únicamente para mejorar una métrica: deben aportar evidencia relevante.
- Distinguir pruebas locales, validación del compilador y evaluaciones reales.
- No afirmar significancia estadística ni mejora de la hipótesis con este cohort.
- No descargar modelos grandes localmente ni cambiar Colima.
- No enviar submissions al concurso ni publicar notebooks.
La autorización de GPU de la primera sesión se limitaba a las seis evaluaciones ya realizadas. Antes de iniciar nuevas ejecuciones de Kaggle, prepara el notebook y un plan concreto con número de ejecuciones, presupuestos, GPU y límites de gasto, y solicita autorización específica para consumir cuota. Completa mientras tanto todo el trabajo independiente.

CIERRE
Después de aprobar el plan, continúa con implementación, gate, auditoría y correcciones. Publica el PR hacia develop conforme a la autorización que se otorgue en esa aprobación, sin merge automático.
Entrega: diagnóstico respaldado por las trazas; cambios implementados y verificados; configuraciones y comandos reproducibles; resultados reales y comparación con sus limitaciones si se autorizaron las ejecuciones; bloqueos concretos y tareas pendientes; PR y evidencia de cierre SDD.
No declares éxito de recuperación híbrida si no hay uso observado y resultados que lo sustenten. Una conclusión negativa o inconclusa también es un resultado válido.

## Subsequent explicit user decision
Autorizo el merge del PR #1 en develop. Después sincroniza develop local e inicia la iteración 2 con el runtime SDD. No modifiques el worktree anterior y presenta la delta de especificaciones y el plan para aprobación.

## Verified prerequisite resolution
PR #1 merged at head e3b57574a9f9ca1aca80039ec401637e0306198d, merge commit 60ad0cec85bb36a1e65609ca2b1a743ba087384d. Local and origin/develop synchronized to that merge commit. Source checkout remains on main. Prior worktree not modified; it already has a modification of docs/specs/plans/closed/mostaza-phase1-foundation.md. Treat all prior evidence as read-only.

## Applicable user-provided global policy
Explicit SDD workflow only. Parent is Orchestrator; native Planner, user plan/gate approval, Implementer, deterministic gate, independent Auditor, correction cycles, Versioner. Read scoped contracts under /Users/diego/.codex/workflow. Filesystem is durable memory; this plan is sole workflow state. Specifications under docs/specs excluding plans are Planner-owned; Implementers never edit normative specs. Use returned project_path for all roles. Initial approval includes push/PR to develop. Only Versioner performs final Git writes; never force-push, amend, discard changes or rebase published history. Ordinary engineering: English source, simple readable code, existing patterns, no unnecessary dependencies or unrelated refactoring; changed behavior tests, relevant tests, lint, typecheck and build where available; claim checks only if actually run. Ask only material decisions not safely inferable. Only Orchestrator declares complete after plan, implementation, gate, zero-finding independent PASS and authorized Git closure. Global policy details provided by user remain applicable; use shared and role contracts for execution mechanics.

## Planning diagnosis and official research

Read-only baseline: `/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness/results/kaggle-v2-358139443/private-run-evidence/99c637be-d945-4dd7-85d8-4042cfcc2bad`; each arm's `results/traces/trace_<task>.json` and `official-result-0001.json` were inspected offline. Do not modify that worktree. The merged repository contains the five compact phase-1 artifacts; source ZIP/notebook/native bundle remain ignored. Before checks, copy needed original ignored resources/results into this worktree without altering source bytes or using escaping symlinks, verify the recorded inventories, and prepare new local environments with existing setup instructions. These are implementation prerequisites, not evidence that validation already passed.

Trace findings (seconds measured from native event elapsed_s; intervals are not pure model or tool wall time): E0 FastAPI 10 recorded attempts, last 37.635; Requests 7, last 53.904; Rich 12, last 56.821. E1 FastAPI 8, last 54.874; Requests 6, last 50.969; Rich 8, last 57.129. Largest adjacent agent-event gaps respectively 7.962, 32.628, 27.137 and 27.000, 35.765, 32.744. Requests write_file occurred at 52.689 E0 / 49.011 E1 after long intervals; final command observations at 54.183 / 51.249 left little of the 60-second session. FastAPI repeatedly read params/dependencies; E0 included malformed start_line argument. Rich repeated unsuccessful exact lexical queries; E0 made one similarity attempt; E1 made none. No graph tool or submit_patch appears. Agent-event timestamps and matched observations allow bounded response latency, but do not isolate token generation, scheduling and model-server latency. Timing attribution remains unknown where spans do not exist.

Requests diagnosis: effective generated patch changed only the new reproduction script (repro.py / reproduce_issue.py), not src/requests product files. Both scripts caught a failing assertion, printed the failure, and exited zero; thus a successful shell exit did not establish correction. The official verifier still reported 205 passed, 13 skipped, 1 failed. Patch application success and native SUCCESS are not resolution. This is a failure to progress beyond reproduction before timeout, not evidence that a product fix was implemented incorrectly. Only generated artifacts and returned observations were inspected; no reference patch or hidden-test content was used. Do not copy these task-specific findings into any agent instructions or notebook generation context.

Calibration rationale: all six reached the session limit, with >27-second late intervals in five runs and only Requests reaching a reproduction script. Three minutes adds headroom for implementation and verification while 30 charged tools avoids immediately replacing time starvation with the observed ten-call cap. Five minutes/50 is a small bounded second candidate, not an automatic retry. Keep max_turns=50 and sampling unchanged so only the budget tuple changes. This is not an optimum estimate; three tasks with prior observed outcomes support descriptive calibration only.

Current official research (2026-10-13 local / 2026-10-14 UTC): browsed official starter, wheelhouse and competition overview; web-rendered pages exposed no text, so verified official JSON APIs directly with an approved network request. `https://www.kaggle.com/api/v1/kernels/pull/ryanholbrook/getting-started-gemma-4-developer-agent` returned starter version 3, offline L4 configuration and model revision 2 mounts; response SHA256 238d1d45d9a98652d954310cd5b48d68baca54006174e28eb5104ca0af359aa6 (volatile response metadata is not a new notebook revision). `https://www.kaggle.com/api/v1/datasets/list?search=gemma-4-developer-agent-wheelhouse` reported metric wheelhouse version 31, updated 2026-10-12T19:51:31.09Z. The official version-31 swegemma-0.2.11 wheel was downloaded in memory, 119670 bytes, SHA256 9ad876581f3acde8ec3c369858f0834e2b9f41a3cffce3ca42f09cb090aea9d3, matching the retained pin. Primary source in that wheel: config.py exposes EvalConfig timeout_seconds, max_time_minutes, max_tool_calls, max_turns, verification_timeout_seconds; budget.py separates EvaluationBudget from HarnessLimits (300-second verification). Native graph tools use existing symbol lookup, bounded neighbors and response truncation; similarity invocation may fall back lexically. These are verified local experimental API capabilities, not a claim of permitted competition submission-budget changes. No official limit or local default is silently upgraded.

## Specification changes

Files: docs/specs/budget-retrieval-calibration.md (new normative spec) and docs/specs/README.md (one-line index addition). Existing foundation, agent-retrieval and evaluation ACs remain unchanged. Added acceptance text follows verbatim; modified/removed/restored IDs: none. Product decisions PD-1 through PD-4 choose bounded budget-only calibration, independent recovery treatment, truthful preparation closure and separate per-batch quota authorization.

budget-retrieval-calibration:AC-1: Preserve the original E0/E1 manifests, submission files, frozen three-task cohort and phase-1 evidence byte-for-byte. New explicit configuration IDs E0-B180, E1-B180, E0-B300, E1-B300 and E1-R180 identify separate immutable manifests and deterministic archives; E0/E1 remain valid legacy selections. Calibration changes only matched budget values: B180 uses timeout_seconds=180, max_time_minutes=3, max_tool_calls=30; B300 uses 300, 5, 50; both retain max_turns=50 and verification_timeout_seconds=300. Model, sampling, cache/compaction, task order, environment, tools, verification and repair policy are equal within each pair. Original prompts remain byte-exact for budget calibration.

budget-retrieval-calibration:AC-2: Review current official primary resources and pin their source identities before configuration validation. Use one official LlmAgent and existing native tools only. Fail closed on incompatible official APIs, unavailable resource provenance or differing pair conditions. No local model download, Colima change, external retrieval service, submission to the competition or public notebook is permitted.

budget-retrieval-calibration:AC-3: Produce reproducible offline diagnosis from retained native traces/results with hashed source locators and exact event identifiers. Separate event-to-event elapsed intervals from attributable model generation or tool execution time; do not infer unobserved spans. Analyze Requests generated patch and execution/verification evidence only after generation, keeping reference solutions and hidden tests outside agent-visible inputs, prompts, notebooks payloads and submission archives.

budget-retrieval-calibration:AC-4: Record per task lexical-command attempts, similarity-tool attempts, graph-neighbor/subgraph attempts, exempt and rejected attempts, and official charged calls separately, together with sourced token usage, timeout reason, generated/effective patch status and independent verification. Similarity invocation alone does not establish vector execution: classify vector versus lexical fallback only when response/source evidence establishes the backend; otherwise backend is null with reason. Metrics declare units, numerator, denominator, source, availability and trace coverage. Missing or incomplete telemetry is never zero; step token aggregates are counted once. Shell search counts are explicitly observed command classifications, not exhaustive search/read totals.

budget-retrieval-calibration:AC-5: Additional instrumentation is host-side trace analysis without changing the official runtime: extract tool call/response intervals only when matched timestamps exist, returned graph nodes and repeated explicit read ranges only when observable, and classify unexplained/compound shell commands as unknown. True localization time, relevant-context ratio, Recall@K, full unique files, pure model wall time and repair count remain null unless separately defined complete evidence supports them. Fixture tests cover native ATIF, malformed/missing fields, fallback, truncation, rejected calls and no double counting; fixtures never count as real evaluations.

budget-retrieval-calibration:AC-6: Prepare a separate E1-R180 recovery-instruction experiment, excluded from budget calibration. Its sole change from E1-B180 is the exploration section: after unsuccessful exact lexical lookup, verify a real fully qualified symbol, use symbol-seeded search_similar_code(k=5) for semantic uncertainty and get_code_neighbors(max_neighbors=10) or bounded get_code_subgraph for structural uncertainty, stop when context suffices and avoid repeated unproductive queries. One hop is default; a second requires observed evidence. Do not force tool calls, add task-specific hints, expose post-run findings to the model, or alter implementation/verification/repair instructions. Document the exact diff and assess actual adherence from traces only when executed.

budget-retrieval-calibration:AC-7: Prepare a reproducible private offline Kaggle notebook and preflight without starting GPU. The initial quota proposal is exactly six task evaluations (E0-B180 and E1-B180 across requests_7205, fastapi_15589, rich_3061), one NVIDIA L4 x4 session, concurrency=1, no retries, at most 120 wall-clock minutes from session start including startup/loading/compiler/generation/verification/export, at most 8 GPU-device-hours, and zero paid purchases. Require explicit separate human quota authorization before any remote GPU start. Check remaining quota and enforce a session deadline/watchdog with fail-closed launch and cleanup; inability to enforce the ceiling blocks execution. Budget approval is not GPU authorization.

budget-retrieval-calibration:AC-8: A 300-second calibration batch or E1-R180 comparison is a separate six-evaluation batch, never automatically launched. Propose B300 only if B180 remains time/tool constrained before implementation/verification; retain its failures and avoid selecting on success. Propose E1-R180 versus E0-B180 only after budget calibration is analyzed and held fixed, with a new contemporaneous matched pair, not reused baseline outcomes. Each later batch needs a new explicit quota decision and its own 120-minute/8-device-hour/$0 ceiling; no implicit combined authorization or restart is allowed.

budget-retrieval-calibration:AC-9: Always complete local preparation, compiler validation, diagnosis and documentation independently of GPU permission. Readiness reports explicitly label future runs NOT_RUN with reasons until authorized; this preparation checkpoint makes no claim of phase-2 real evaluation or retrieval success. If execution is specifically authorized, retain all six records including failures/NOT_RUN, immutable native acquisition receipts, exact config/archive/model/cohort bindings and reproducible paired comparison with coverage and limitations before describing real outcomes. A denial or missing quota is reported as pending real evaluation, not silently simulated or a successful benchmark.

budget-retrieval-calibration:AC-10: Exact local gates validate all new configuration closures with the pinned official compiler, leakage boundaries, legacy artifact immutability, metrics and report recomputation, quota defaults/ceilings, and notebook payload provenance without GPU. Preserve phase-1 evidence and its original normalizer receipts; changing host code must not rewrite historical evidence or pretend a new normalizer was executed in the old notebook. Reports are declared before creation, and no significance/superiority claim is made for this exploratory cohort.

## Implementation stages

### Stage 1 [stage-1] HIGH

HIGH for backward-compatible result/provenance and leakage boundaries; interacting native ATIF parser, normalized records and immutable report checker. trace-metrics implements sourced coverage and diagnostic extraction, with null reasons and rejection/fallback tests. legacy-provenance preserves old schema and exact historical reports; retain original archived normalizer for historical replay or provide verified compatibility replay without rewriting receipts. New findings appear only in new evidence. Run new focused fixtures and legacy replay before checkpointing.

Items: trace-metrics, legacy-provenance. Depends: none. Satisfies: budget-retrieval-calibration:AC-3, budget-retrieval-calibration:AC-4, budget-retrieval-calibration:AC-5, budget-retrieval-calibration:AC-10.

Exact owned paths:
- src/mostaza/evaluation/runner.py
- src/mostaza/evaluation/contracts.py
- src/mostaza/research/metrics.py
- src/mostaza/research/report.py
- src/mostaza/research/trace_diagnostics.py
- scripts/check_evidence.py
- tests/unit/test_metrics.py
- tests/unit/test_results.py
- tests/unit/test_trace_diagnostics.py
- tests/integration/test_pipeline.py

### Stage 2 [stage-2] MEDIUM

MEDIUM for interactions among configuration registry, manifest conditions, deterministic packaging and official compiler. variant-packaging adds five explicit selections and arm/config separation, leaving existing submission/agent.yaml, eval_config.yaml and baseline/hybrid prompts untouched; generate per-selection budget overlays in temporary packaging trees. recovery-policy adds only the separate exploration prompt and verifies exact allowed diff and native APIs. Record actual compiler validation and official hashes; ready does not mean inference.

Items: variant-packaging, recovery-policy. Depends: stage-1. Satisfies: budget-retrieval-calibration:AC-1, budget-retrieval-calibration:AC-2, budget-retrieval-calibration:AC-6, budget-retrieval-calibration:AC-10.

Exact owned paths:
- src/mostaza/packaging.py
- scripts/check_official.py
- experiments/E0-B180/manifest.json
- experiments/E1-B180/manifest.json
- experiments/E0-B300/manifest.json
- experiments/E1-B300/manifest.json
- experiments/E1-R180/manifest.json
- submission/prompts/hybrid-recovery.md
- tests/unit/test_packaging.py
- tests/unit/test_retrieval_policy.py
- tests/integration/test_official_contract.py
- tests/integration/test_retrieval_contract.py

### Stage 3 [stage-3] HIGH

HIGH for quota enforcement, offline execution isolation and proof of notebook/source provenance. notebook-preflight constructs a clean notebook payload from explicit host modules, cohort and approved prompts, excludes diagnostics/verification secrets, leaves GPU start disabled by default, enforces finite batch/session limits and cleanup. readiness-evidence writes deterministic reports and exact operator commands. Complete and verify local preparation before asking for quota. Record NOT_RUN and pending real evaluation when authorization is absent. A later authorized run uses the same scoped files and declared reports; if product/source/evidence changes after a gate, rerun gate and independent audit. External authorization is consumed only by Orchestrator; never self-authorize.

Items: notebook-preflight, readiness-evidence. Depends: stage-1, stage-2. Satisfies: budget-retrieval-calibration:AC-7, budget-retrieval-calibration:AC-8, budget-retrieval-calibration:AC-9, budget-retrieval-calibration:AC-10.

Exact owned paths:
- src/mostaza/evaluation/phase2.py
- scripts/prepare_phase2.py
- scripts/check_phase2.py
- notebooks/mostaza-phase2-budget-retrieval.ipynb
- tests/unit/test_phase2.py
- tests/integration/test_phase2.py
- docs/architecture.md
- docs/experiments.md
- docs/kaggle-setup.md
- README.md

## Exact gate and prerequisites

All commands run in the resolved project root, with project-local uv on PATH, existing setup completed, compiler dependencies isolated, and authenticated phase-1 resources copied and hash-checked read-only. No check launches Kaggle, downloads weights, modifies product files or updates snapshots. Existing validate.sh performs ruff format --check ., ruff check ., strict mypy src scripts, unit and integration pytest with no cacheprovider, package build in a temporary copy, authentic E0/E1 compiler validation and original evidence replay. Do not weaken that script or skip unavailable official dependencies. Its historical check must keep passing without altering original artifacts. No project CI/migration/model catalog command exists to add. New check_phase2.py is an implementation deliverable, not an already-existing validation result: it must compare/recompute declared evidence without writing it, compile all five new closures in temporary directories, verify selected payloads/no secrets, and reject invalid/incomplete source provenance. It accepts truthful local readiness with NOT_RUN; if real outputs are declared it independently verifies full native acquisition and pair conditions.

- repository-validation: `["bash", "scripts/validate.sh"]`; timeout 1200 seconds; foundation:AC-4; existing required formatting/lint/type/unit/integration/temp-build/compiler and authentic phase-1 evidence validation, unchanged command.
- phase2-readiness: `["uv", "run", "--frozen", "--no-sync", "python", "scripts/check_phase2.py", "--check", "--cohort", "experiments/cohort.json", "--evidence-dir", "docs/implementation/evidence/mostaza-phase2-budget-retrieval"]`; timeout 600 seconds; budget-retrieval-calibration:AC-1 through AC-10; nonmutating compiler, exact variant/prompt/provenance/leakage/budget/evidence/notebook readiness and conditional real evidence validation.
- Runtime additionally executes `git diff --check HEAD -- <exact stage paths>` for every stage and spec-frozen integrity checks.

## Declared evidence

- `docs/implementation/evidence/mostaza-phase2-budget-retrieval/trace-diagnosis.json` — stage-1: Source-hashed post-run trace diagnosis, Requests patch-only findings and metric coverage.
- `docs/implementation/evidence/mostaza-phase2-budget-retrieval/resource-review.json` — stage-2: Current official source review and immutable input receipts.
- `docs/implementation/evidence/mostaza-phase2-budget-retrieval/official-validation.json` — stage-2: Actual compiler receipts for all five configurations without inference.
- `docs/implementation/evidence/mostaza-phase2-budget-retrieval/readiness.json` — stage-3: Local preflight, prepared notebook/config hashes and explicit NOT_RUN or authorized acquisition evidence.
- `docs/implementation/evidence/mostaza-phase2-budget-retrieval/comparison.json` — stage-3: Deterministic observed historical diagnosis and separately identified phase-2 records/coverage, never simulated real results.
- `docs/implementation/evidence/mostaza-phase2-budget-retrieval/report.md` — stage-3: Reproducible limitations, readiness, quota proposal and real outcomes only if authorized.

These outputs are evidence, not another workflow state. Keep counters, approvals, decisions and stage checkpoints solely in this plan. Evidence output bytes are checked and frozen by gate/audit; never regenerate after PASS. Raw model outputs, patches and private verification stay ignored with content-addressed receipts. No old artifact is overwritten.

## Quota decision and closure

Prepare the concrete notebook and a six-evaluation B180 plan before requesting GPU permission. Proposed first batch: one private offline NVIDIA L4 x4 session, serial paired task execution, generation upper bound 18 minutes and verification upper bound 30 minutes, within a total 120-minute session ceiling including cold start and export (8 GPU-device-hours; no monetary purchase). No retries. The controller must stop scheduling with insufficient remaining worst-case per-task allowance and terminate resources at deadline, including failure paths. If the platform cannot enforce or expose a reliable session-start deadline, do not start; request a revised concrete limit. Quota accounting may use different platform units; record both measured wall-clock and GPU-device-hours and never equate native cost_usd=0 with free/unlimited quota. B300 generation/verification bounds would be 30+30 minutes; independent later six-run B180 recovery pair 18+30; neither is currently authorized.

Initial approval covers the specification delta, exact gate, local implementation, independent audit/corrections and Versioner commit/push/PR to develop without merge. It excludes remote GPU startup, competition submissions, notebook publication, spending and changes to the old worktree. After local preparation, Orchestrator asks for the separate concrete quota authorization. If none is given, local deliverables may close with real evaluation expressly pending; never claim phase-2 benchmark completion. If granted before closure, retain actual outcomes and regenerate/revalidate declared evidence before audit.

<!-- SDD-CONTINUITY:START -->

```sdd-execution
{
  "version": 3,
  "id": "mostaza-phase2-budget-retrieval",
  "project": "/Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness",
  "plan_path": "/Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness/docs/specs/plans/open/mostaza-phase2-budget-retrieval.md",
  "branch": "sdd/mostaza-phase2-budget-retrieval",
  "head": "60ad0cec85bb36a1e65609ca2b1a743ba087384d",
  "definition": {
    "scope": "Implement docs/specs/budget-retrieval-calibration.md AC-1 through AC-10; preserve all phase-1 artifacts; prepare local phase-2 readiness and separately gated optional real evaluation.",
    "stages": [
      {
        "id": "stage-1",
        "level": "HIGH",
        "paths": [
          "src/mostaza/evaluation/runner.py",
          "src/mostaza/evaluation/contracts.py",
          "src/mostaza/research/metrics.py",
          "src/mostaza/research/report.py",
          "src/mostaza/research/trace_diagnostics.py",
          "scripts/check_evidence.py",
          "tests/unit/test_metrics.py",
          "tests/unit/test_results.py",
          "tests/unit/test_trace_diagnostics.py",
          "tests/integration/test_pipeline.py"
        ],
        "depends": [],
        "items": [
          "trace-metrics",
          "legacy-provenance"
        ],
        "satisfies": [
          "budget-retrieval-calibration:AC-3",
          "budget-retrieval-calibration:AC-4",
          "budget-retrieval-calibration:AC-5",
          "budget-retrieval-calibration:AC-10"
        ]
      },
      {
        "id": "stage-2",
        "level": "MEDIUM",
        "paths": [
          "src/mostaza/packaging.py",
          "scripts/check_official.py",
          "experiments/E0-B180/manifest.json",
          "experiments/E1-B180/manifest.json",
          "experiments/E0-B300/manifest.json",
          "experiments/E1-B300/manifest.json",
          "experiments/E1-R180/manifest.json",
          "submission/prompts/hybrid-recovery.md",
          "tests/unit/test_packaging.py",
          "tests/unit/test_retrieval_policy.py",
          "tests/integration/test_official_contract.py",
          "tests/integration/test_retrieval_contract.py"
        ],
        "depends": [
          "stage-1"
        ],
        "items": [
          "variant-packaging",
          "recovery-policy"
        ],
        "satisfies": [
          "budget-retrieval-calibration:AC-1",
          "budget-retrieval-calibration:AC-2",
          "budget-retrieval-calibration:AC-6",
          "budget-retrieval-calibration:AC-10"
        ]
      },
      {
        "id": "stage-3",
        "level": "HIGH",
        "paths": [
          "src/mostaza/evaluation/phase2.py",
          "scripts/prepare_phase2.py",
          "scripts/check_phase2.py",
          "notebooks/mostaza-phase2-budget-retrieval.ipynb",
          "tests/unit/test_phase2.py",
          "tests/integration/test_phase2.py",
          "docs/architecture.md",
          "docs/experiments.md",
          "docs/kaggle-setup.md",
          "README.md"
        ],
        "depends": [
          "stage-1",
          "stage-2"
        ],
        "items": [
          "notebook-preflight",
          "readiness-evidence"
        ],
        "satisfies": [
          "budget-retrieval-calibration:AC-7",
          "budget-retrieval-calibration:AC-8",
          "budget-retrieval-calibration:AC-9",
          "budget-retrieval-calibration:AC-10"
        ]
      }
    ],
    "checks": [
      {
        "id": "repository-validation",
        "stage": "stage-3",
        "argv": [
          "bash",
          "scripts/validate.sh"
        ],
        "timeout": 1200,
        "basis": "foundation:AC-4; existing required formatting/lint/type/unit/integration/temp-build/compiler and authentic phase-1 evidence validation, unchanged command"
      },
      {
        "id": "phase2-readiness",
        "stage": "stage-3",
        "argv": [
          "uv",
          "run",
          "--frozen",
          "--no-sync",
          "python",
          "scripts/check_phase2.py",
          "--check",
          "--cohort",
          "experiments/cohort.json",
          "--evidence-dir",
          "docs/implementation/evidence/mostaza-phase2-budget-retrieval"
        ],
        "timeout": 600,
        "basis": "budget-retrieval-calibration:AC-1 through AC-10; nonmutating compiler, exact variant/prompt/provenance/leakage/budget/evidence/notebook readiness and conditional real evidence validation"
      }
    ],
    "evidence": [
      {
        "path": "docs/implementation/evidence/mostaza-phase2-budget-retrieval/trace-diagnosis.json",
        "stage": "stage-1",
        "purpose": "Source-hashed post-run trace diagnosis, Requests patch-only findings and metric coverage"
      },
      {
        "path": "docs/implementation/evidence/mostaza-phase2-budget-retrieval/resource-review.json",
        "stage": "stage-2",
        "purpose": "Current official source review and immutable input receipts"
      },
      {
        "path": "docs/implementation/evidence/mostaza-phase2-budget-retrieval/official-validation.json",
        "stage": "stage-2",
        "purpose": "Actual compiler receipts for all five configurations without inference"
      },
      {
        "path": "docs/implementation/evidence/mostaza-phase2-budget-retrieval/readiness.json",
        "stage": "stage-3",
        "purpose": "Local preflight, prepared notebook/config hashes and explicit NOT_RUN or authorized acquisition evidence"
      },
      {
        "path": "docs/implementation/evidence/mostaza-phase2-budget-retrieval/comparison.json",
        "stage": "stage-3",
        "purpose": "Deterministic observed historical diagnosis and separately identified phase-2 records/coverage, never simulated real results"
      },
      {
        "path": "docs/implementation/evidence/mostaza-phase2-budget-retrieval/report.md",
        "stage": "stage-3",
        "purpose": "Reproducible limitations, readiness, quota proposal and real outcomes only if authorized"
      }
    ],
    "spec_changes": {
      "files": [
        "docs/specs/budget-retrieval-calibration.md",
        "docs/specs/README.md"
      ],
      "added": [
        "budget-retrieval-calibration:AC-1",
        "budget-retrieval-calibration:AC-2",
        "budget-retrieval-calibration:AC-3",
        "budget-retrieval-calibration:AC-4",
        "budget-retrieval-calibration:AC-5",
        "budget-retrieval-calibration:AC-6",
        "budget-retrieval-calibration:AC-7",
        "budget-retrieval-calibration:AC-8",
        "budget-retrieval-calibration:AC-9",
        "budget-retrieval-calibration:AC-10"
      ],
      "modified": [],
      "removed": [],
      "restores": [],
      "justification": null
    }
  },
  "baseline": {},
  "approval": {
    "digest": "0d02aac9cf5ce3c98f4c2d52501bbcb153801e587135b6ed715e964f48cd1291",
    "gate_digest": "cb65f19e3b3cfa8e70f024bee55c9e20ad83d45c0f2e3e6d8f95be8ef0635f47",
    "evidence": "User explicitly approved delta, plan, exact gate, implementation, independent audit/corrections, commit/push and PR to develop without merge; GPU execution is not authorized and must be requested after notebook preparation.",
    "publish": {
      "remote": "origin",
      "base": "develop"
    }
  },
  "approvals": [
    {
      "digest": "0d02aac9cf5ce3c98f4c2d52501bbcb153801e587135b6ed715e964f48cd1291",
      "gate_digest": "cb65f19e3b3cfa8e70f024bee55c9e20ad83d45c0f2e3e6d8f95be8ef0635f47",
      "evidence": "User explicitly approved delta, plan, exact gate, implementation, independent audit/corrections, commit/push and PR to develop without merge; GPU execution is not authorized and must be requested after notebook preparation.",
      "publish": {
        "remote": "origin",
        "base": "develop"
      }
    }
  ],
  "normative_digest": "aceab86f0a881e35fea7029dcaad01736f7e2d53a91860fd664c687870d8c152",
  "normative_material_digest": "0af9872a8b7d3bc3880249157892785d58bb84b71032f87f4886f7ae7f72e25d",
  "planner_pending": false,
  "dispatches": [
    {
      "id": 1,
      "role": "planner",
      "stage": null,
      "status": "DONE",
      "review": null
    },
    {
      "id": 2,
      "role": "implementer-high",
      "stage": "stage-1",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 3,
      "role": "implementer-medium",
      "stage": "stage-2",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 4,
      "role": "implementer-high",
      "stage": "stage-3",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 5,
      "role": "auditor",
      "stage": null,
      "status": "DONE",
      "review": null
    },
    {
      "id": 6,
      "role": "planner",
      "stage": null,
      "status": "DONE",
      "review": null
    },
    {
      "id": 7,
      "role": "implementer-high",
      "stage": "stage-1",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 8,
      "role": "implementer-high",
      "stage": "stage-3",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 9,
      "role": "auditor",
      "stage": null,
      "status": "DONE",
      "review": null
    },
    {
      "id": 10,
      "role": "versioner",
      "stage": null,
      "status": "INTERRUPTED",
      "review": null
    },
    {
      "id": 11,
      "role": "versioner",
      "stage": null,
      "status": "DONE",
      "review": null
    }
  ],
  "legacy_dispatches": 0,
  "audits": [
    {
      "round": 1,
      "verdict": "FIX_REQUIRED",
      "candidate": {
        "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
        "value": "2068747d79b9c524f2bb606b1b97caf89326ae6d9d8b5b2e8dba33af2c86d6ff"
      },
      "approval_digest": "0d02aac9cf5ce3c98f4c2d52501bbcb153801e587135b6ed715e964f48cd1291",
      "dispatch": 5,
      "acceptance": [
        {
          "id": "budget-retrieval-calibration:AC-1",
          "status": "SATISFIED",
          "evidence": "Original tracked artifacts unchanged; five matched budget variants and deterministic official compiler-validated archives; prompts byte-exact."
        },
        {
          "id": "budget-retrieval-calibration:AC-2",
          "status": "SATISFIED",
          "evidence": "Official pins/source hashes reviewed; independently recompiled all five one-LlmAgent native-tool closures."
        },
        {
          "id": "budget-retrieval-calibration:AC-3",
          "status": "SATISFIED",
          "evidence": "Six authentic diagnoses reproduce from hashed native sources/events; Requests host-only; timing attribution unavailable."
        },
        {
          "id": "budget-retrieval-calibration:AC-4",
          "status": "UNMET",
          "evidence": "AUD-001 reproduces measured zero with absent successful-read telemetry; other counters/backend/token handling reviewed."
        },
        {
          "id": "budget-retrieval-calibration:AC-5",
          "status": "SATISFIED",
          "evidence": "Host-only matched timestamps/native ranges; unobservable metrics null; reviewed malformed/fallback/truncation/rejection/token fixtures. Aggregate defect tracked AC-4."
        },
        {
          "id": "budget-retrieval-calibration:AC-6",
          "status": "SATISFIED",
          "evidence": "Recovery exploration-only exact bounded diff separated from calibration; no adherence claimed."
        },
        {
          "id": "budget-retrieval-calibration:AC-7",
          "status": "SATISFIED",
          "evidence": "Private offline notebook disabled and exact six-run limits; manual flags cannot bypass unverified platform allocation enforcement."
        },
        {
          "id": "budget-retrieval-calibration:AC-8",
          "status": "SATISFIED",
          "evidence": "Schedule only B180; subsequent budgets/recovery require separate decisions and fresh pairs."
        },
        {
          "id": "budget-retrieval-calibration:AC-9",
          "status": "SATISFIED",
          "evidence": "Local/compiler preparation complete; all six outcomes NOT_RUN with nulls/reasons and pending real evaluation."
        },
        {
          "id": "budget-retrieval-calibration:AC-10",
          "status": "SATISFIED",
          "evidence": "Exact readiness check independently passed; full diff/evidence/legacy/notebook provenance reviewed; before/after fingerprint matches."
        }
      ]
    },
    {
      "round": 2,
      "verdict": "PASS",
      "candidate": {
        "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
        "value": "3233342bc07e167ffd079a9e7dce91e8852072404859906e71e666b4db463074"
      },
      "approval_digest": "0d02aac9cf5ce3c98f4c2d52501bbcb153801e587135b6ed715e964f48cd1291",
      "dispatch": 9,
      "files": {
        "README.md": [
          "file",
          420,
          "6fb7e729a6cb2aceddd4ee2eef420c8439adb9fad016b6f0ffacba451fc61358"
        ],
        "docs/architecture.md": [
          "file",
          420,
          "62935a9775c2fce4a93e11e96bbcdf130dfe3b0653cd920e3b706567bf561d89"
        ],
        "docs/experiments.md": [
          "file",
          420,
          "0960153f0c1d3fb577bf7027cad49cbdaf6d4ec49cc495a34eefa96e0aeeea8e"
        ],
        "docs/implementation/evidence/mostaza-phase2-budget-retrieval/comparison.json": [
          "file",
          420,
          "78d1ffcd28ba312095d19c1329db92273ec0fd46e3a286384d11161703c0c327"
        ],
        "docs/implementation/evidence/mostaza-phase2-budget-retrieval/official-validation.json": [
          "file",
          420,
          "44d2580ed9a9c76d5ea7539423d6c85ebcfdcc06c16929ae9c095212b9c2eed0"
        ],
        "docs/implementation/evidence/mostaza-phase2-budget-retrieval/readiness.json": [
          "file",
          420,
          "fda3d9b9a2c08dc973ba64a7ebac62cb45a9927e616f3528bdac3214bdf5935d"
        ],
        "docs/implementation/evidence/mostaza-phase2-budget-retrieval/report.md": [
          "file",
          420,
          "51f43590a496ae011aec55fa30beee18e42d18724c97454329fb1e485415f4f9"
        ],
        "docs/implementation/evidence/mostaza-phase2-budget-retrieval/resource-review.json": [
          "file",
          420,
          "2beea775006a5bfcfda58839801c0b4d477f76f945e39a8bf2f69cecf4273797"
        ],
        "docs/implementation/evidence/mostaza-phase2-budget-retrieval/trace-diagnosis.json": [
          "file",
          420,
          "b38d4a5d5eeeae6411c5c5604afa46f214e7efac05c13aec5e6a2d1f47c91f70"
        ],
        "docs/kaggle-setup.md": [
          "file",
          420,
          "3e473b617acefb6025e8c7348092d2bb04e23b66303816198ce76234a111cd9e"
        ],
        "docs/specs/README.md": [
          "file",
          420,
          "4a1a3d8016358ae1ce28e88189a2270e389d21fef9164cae26a1b3b3028dec8a"
        ],
        "docs/specs/budget-retrieval-calibration.md": [
          "file",
          420,
          "b1e8eddef48a6bc770899ce6bd61c4f29fa81bf1024f9c637609d1b53a28c0c6"
        ],
        "experiments/E0-B180/manifest.json": [
          "file",
          420,
          "400fa15b41cbe497d0c758b48cf10602a0563ea6bc60382266869a0c0e0bed88"
        ],
        "experiments/E0-B300/manifest.json": [
          "file",
          420,
          "fad16d4d5e21df8aae052a55522d4b7fa230dfcea639aee1fa18170a708ac3b8"
        ],
        "experiments/E1-B180/manifest.json": [
          "file",
          420,
          "58409d7a173dfcc1f6892fbc95f0d94c5ea55d3a7513935b7040d3e7c08fa464"
        ],
        "experiments/E1-B300/manifest.json": [
          "file",
          420,
          "2bad3f9ae84eb411d247542a4712ecbbef6206d5be564404d9b56d9a5e20ef9f"
        ],
        "experiments/E1-R180/manifest.json": [
          "file",
          420,
          "8204b9f04e4bc0f78c05271168a68cb500664abb539a2b06210821e0daab5b59"
        ],
        "notebooks/mostaza-phase2-budget-retrieval.ipynb": [
          "file",
          420,
          "02d410a2cec6d833426eed6cd8fcfee43d8b16c8e537592e92a87ec32cc0c4c2"
        ],
        "scripts/check_official.py": [
          "file",
          420,
          "9a391ff31b750f3067685ec523149332cb7c32747748a65e2bee1c831397e9db"
        ],
        "scripts/check_phase2.py": [
          "file",
          420,
          "3e4b35ad19e6f88a54879ff44136a08e6e5fb49441d93ced9fef70ca260e0cee"
        ],
        "scripts/prepare_phase2.py": [
          "file",
          420,
          "0c30e2e1eeddd70d609f4cfc63073b79d18004e43746dbbeddbbd5061fd5f240"
        ],
        "src/mostaza/evaluation/phase2.py": [
          "file",
          420,
          "efd71b1c73a07a267b6a4a2f42ef5f8dcec4c2e9651c8a71879619265aeb8c7b"
        ],
        "src/mostaza/packaging.py": [
          "file",
          420,
          "b1944c8e7dd66036cfc9679f0dca66386c2c30a5e2066cf2d559680b90ec029f"
        ],
        "src/mostaza/research/trace_diagnostics.py": [
          "file",
          420,
          "af9834e18f1cfacb5a2bf3705994e31ec61cde829d864bfdb811186733e0686d"
        ],
        "submission/prompts/hybrid-recovery.md": [
          "file",
          420,
          "dc303ac516a09bbff118253f9bb90542d02cba0e6055af37754fb53a59b6fae5"
        ],
        "tests/integration/test_official_contract.py": [
          "file",
          420,
          "7eeb0a0a4c9e65ed2790969bfe09f907014a67aa1c14221321e686fd2522c818"
        ],
        "tests/integration/test_phase2.py": [
          "file",
          420,
          "57f08b3f08bd74a8050afcf479c3ae712231c111fc92e79691502c221c52cd86"
        ],
        "tests/integration/test_pipeline.py": [
          "file",
          420,
          "1e8c856e8249b536a184c9b8aba98c0b2c2f838460ef6c7d713f6ce9a0af861a"
        ],
        "tests/unit/test_packaging.py": [
          "file",
          420,
          "5f81133208564d52b3ac995b241812d6551bca2a36fcda74e740c23b31f59972"
        ],
        "tests/unit/test_phase2.py": [
          "file",
          420,
          "edb1432e40392f62d2cd84399dd1d22f37ec429ef84504b67bfda050c34cc127"
        ],
        "tests/unit/test_retrieval_policy.py": [
          "file",
          420,
          "ff1cb3caf80a68f5cd0b6fdd8c62aeae005183189cc5d2a68e388282e3b23ad4"
        ],
        "tests/unit/test_trace_diagnostics.py": [
          "file",
          420,
          "13063af3b9184cd5bf4f436c95eed80d9366ef2644fcec0b66fb556e08173318"
        ]
      },
      "git_entries": {
        "README.md": [
          "100644",
          "527fe5f6ae09dd119b56b12bed187b169ce2703f"
        ],
        "docs/architecture.md": [
          "100644",
          "3c77baf0ba2bcd60d6e4e65f6b148dbfb99e836a"
        ],
        "docs/experiments.md": [
          "100644",
          "85d94546fb109aca0480862d7554a5ab4164ad75"
        ],
        "docs/implementation/evidence/mostaza-phase2-budget-retrieval/comparison.json": [
          "100644",
          "2844bb1c5416f7af7ede4c9922c63f05e0512985"
        ],
        "docs/implementation/evidence/mostaza-phase2-budget-retrieval/official-validation.json": [
          "100644",
          "2b7ded8b1af6b308acdfdc48aca34e9094839d55"
        ],
        "docs/implementation/evidence/mostaza-phase2-budget-retrieval/readiness.json": [
          "100644",
          "b563fe0a256d3e09c3b5d221cb7e89e67fbdec5b"
        ],
        "docs/implementation/evidence/mostaza-phase2-budget-retrieval/report.md": [
          "100644",
          "b469e011236a88276f9bdbc7fafb0d9c84b6896d"
        ],
        "docs/implementation/evidence/mostaza-phase2-budget-retrieval/resource-review.json": [
          "100644",
          "4ccf5e3f77c80f27d79b8e2300d33a9f7b5e5bfd"
        ],
        "docs/implementation/evidence/mostaza-phase2-budget-retrieval/trace-diagnosis.json": [
          "100644",
          "a952df6f74671caf3f32d8ca306843113ae40bc1"
        ],
        "docs/kaggle-setup.md": [
          "100644",
          "f1d7dcae61b313ed322f8b6fe9e34a49a7963625"
        ],
        "docs/specs/README.md": [
          "100644",
          "55bddb7b95bdc583cf8027539241eca8cc71560f"
        ],
        "docs/specs/budget-retrieval-calibration.md": [
          "100644",
          "8914b793ee9c99dddd30f3a9e6617d13505765c8"
        ],
        "experiments/E0-B180/manifest.json": [
          "100644",
          "6e9f24ca3d57559d3510ae79a48acd9134ee306a"
        ],
        "experiments/E0-B300/manifest.json": [
          "100644",
          "13ef516e0d5df4a69ce09b19f75c2fd710304fcd"
        ],
        "experiments/E1-B180/manifest.json": [
          "100644",
          "4854314928601e831f098aa8479d017357b8348a"
        ],
        "experiments/E1-B300/manifest.json": [
          "100644",
          "3bd8ca7bc4921feacbdc2f244ca60dcd9c7ea0ae"
        ],
        "experiments/E1-R180/manifest.json": [
          "100644",
          "d7a27771d859e7a5fc4719e5c5ff787c0c74e6ab"
        ],
        "notebooks/mostaza-phase2-budget-retrieval.ipynb": [
          "100644",
          "ce20a03ad3aa8bb899a3248fd705f4c17519634e"
        ],
        "scripts/check_official.py": [
          "100644",
          "1356b56b056dfa3b0d52a637ebbe8310ac003081"
        ],
        "scripts/check_phase2.py": [
          "100644",
          "1f3b9cef825de641f2e31622de4f4dddcc8b5b4d"
        ],
        "scripts/prepare_phase2.py": [
          "100644",
          "0380aad8e7b80876fd02bed20b699e351b1a4285"
        ],
        "src/mostaza/evaluation/phase2.py": [
          "100644",
          "bd7508f3591d328d90257249b66c193d382330a3"
        ],
        "src/mostaza/packaging.py": [
          "100644",
          "8dc0b7699f92a3e78abc9a685eb7577d8c682c3a"
        ],
        "src/mostaza/research/trace_diagnostics.py": [
          "100644",
          "bb2b1aa9fabcc8f4d0a1fb6dd84ba14876663956"
        ],
        "submission/prompts/hybrid-recovery.md": [
          "100644",
          "a3012363fa042bcbb8fa01d6219d93ad6555f24a"
        ],
        "tests/integration/test_official_contract.py": [
          "100644",
          "f2075ed42531037b120b5706ea2ff96431ba034b"
        ],
        "tests/integration/test_phase2.py": [
          "100644",
          "e44ec63c6dd47f3554a86fa1e388ecd337f7595f"
        ],
        "tests/integration/test_pipeline.py": [
          "100644",
          "a3f6a812fcdac351e66de2fba906c18972d13fba"
        ],
        "tests/unit/test_packaging.py": [
          "100644",
          "71078c2f087c19ff95e3872cfea884f6c4b1d059"
        ],
        "tests/unit/test_phase2.py": [
          "100644",
          "0da6c28a283b5d2a859fb409249b78a3698784b5"
        ],
        "tests/unit/test_retrieval_policy.py": [
          "100644",
          "7e2d67781e0e9f9e26e9efe90b861c7c51ff15a4"
        ],
        "tests/unit/test_trace_diagnostics.py": [
          "100644",
          "d866ebe25be58baa2b64b3e5d31c9457f07bdd03"
        ]
      },
      "acceptance": [
        {
          "id": "budget-retrieval-calibration:AC-1",
          "status": "SATISFIED",
          "evidence": "Original artifacts remain byte-exact. Five distinct variants preserve matched non-treatment conditions; budget-only prompts remain unchanged and archives reproduce deterministically."
        },
        {
          "id": "budget-retrieval-calibration:AC-2",
          "status": "SATISFIED",
          "evidence": "Pinned official resources and native API provenance verified. All five closures independently passed official compilation with one LlmAgent and native tools."
        },
        {
          "id": "budget-retrieval-calibration:AC-3",
          "status": "SATISFIED",
          "evidence": "Historical diagnosis reproduces from hash-bound native sources and exact event pointers. Requests findings remain host-only; event intervals are not attributed to model/tool execution."
        },
        {
          "id": "budget-retrieval-calibration:AC-4",
          "status": "SATISFIED",
          "evidence": "AUD-001 resolved: missing, malformed, inconsistent, unmatched or partially observed read responses produce null with coverage reasons. Known successes/failures retain faithful counts. Tokens remain single-counted; attempts, charges and backend uncertainty remain separate."
        },
        {
          "id": "budget-retrieval-calibration:AC-5",
          "status": "SATISFIED",
          "evidence": "Observable timing, graph nodes and explicit reads remain host-side and source-bound; unsupported metrics remain null. All 64 diagnostic tests passed, including coverage, fallback, truncation, rejection and double-counting cases."
        },
        {
          "id": "budget-retrieval-calibration:AC-6",
          "status": "SATISFIED",
          "evidence": "E1-R180 changes exploration only, records its exact diff and bounded retrieval policy, remains excluded from calibration, and makes no observed-adherence claim."
        },
        {
          "id": "budget-retrieval-calibration:AC-7",
          "status": "SATISFIED",
          "evidence": "GPU defaults off; the exact six-run proposal retains its ceilings. Launch remains unconditionally blocked because authorization and verified allocation-start/deadline/termination enforcement are unavailable."
        },
        {
          "id": "budget-retrieval-calibration:AC-8",
          "status": "SATISFIED",
          "evidence": "Only initial B180 appears in the prepared schedule. Later B300/recovery batches require separate decisions, prerequisite analysis and fresh matched evaluations; no automatic launch exists."
        },
        {
          "id": "budget-retrieval-calibration:AC-9",
          "status": "SATISFIED",
          "evidence": "Local preparation is complete. Six future records remain NOT_RUN with reasons and null outcomes; reports explicitly preserve pending real evaluation and claim no retrieval success."
        },
        {
          "id": "budget-retrieval-calibration:AC-10",
          "status": "SATISFIED",
          "evidence": "Full requirement, specifications, dependencies, current diff, tests and declared evidence reviewed. Exact read-only readiness checker independently passed, including native replay, legacy immutability, double compilation and notebook/source/payload/report recomputation. Recorded full gate passed. Before/after fingerprints match the reserved candidate."
        }
      ]
    }
  ],
  "findings": {
    "AUD-001": {
      "id": "AUD-001",
      "acceptance_id": "budget-retrieval-calibration:AC-4",
      "severity": "MEDIUM",
      "location": "/Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness/src/mostaza/research/trace_diagnostics.py:424",
      "issue": "Missing successful-read telemetry becomes measured zero. Reproduced with ATIF-v1.7 containing two valid agent steps, each read_file {filepath:'a.py',start_line:1,end_line:5}, valid token metrics, and no observation. repeated_explicit_read_ranges returns value=0, availability=measured, reason=null, denominator=0 despite matched_responses=0.",
      "expected": "Incomplete response coverage must produce null with a reason for metrics whose definition requires successful reads.",
      "correction": "Track response/status coverage for explicit-range read attempts separately from structural calls. Return null when successful-read membership is unknown; preserve known failures and fully observed counts. Add missing/malformed/unmatched response regression cases, regenerate affected declared evidence and rerun full gate.",
      "open": false,
      "stage": "stage-1"
    }
  },
  "stages": {
    "stage-1": {
      "done": [
        "legacy-provenance",
        "trace-metrics"
      ],
      "reviews": 0,
      "failures": 0,
      "review": null,
      "blocked": null,
      "checkpoint": {
        "item": "trace-metrics",
        "evidence": "AUD-001 correction: successful explicit-range read membership now requires matched valid response/status coverage, independently of structural calls; unknown membership yields null value/numerator/denominator with reason, known failures remain excluded. Added absent/malformed/mismatched/ambiguous/partial and observed success/failure regressions. 124 focused tests passed, zero skips; ruff format/check, strict mypy src scripts, owned diff whitespace, new diagnosis recomputation and exact legacy replay passed. Historical compact/normalizer bytes unchanged. Owned trace-diagnosis.json SHA256 b38d4a5d5eeeae6411c5c5604afa46f214e7efac05c13aec5e6a2d1f47c91f70. Self-review complete; stage3 dependent evidence untouched, full gate/audit pending; finding left open for Auditor.",
        "candidate": {
          "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
          "value": "76f623fe892f99df7b369ac989cf067342d9bb8f00ae69e04fc164b8b245c83a"
        }
      },
      "gate_history": [
        0,
        0
      ]
    },
    "stage-2": {
      "done": [
        "variant-packaging",
        "recovery-policy"
      ],
      "reviews": 0,
      "failures": 0,
      "review": null,
      "blocked": null,
      "checkpoint": {
        "item": "recovery-policy",
        "evidence": "Separate E1-R180 prompt replaces only exploration; loader/tests prove unchanged prefix, implementation, verification, anti-pattern and shared suffix bytes relative to E1-B180. Manifest records and validates exact unified exploration diff; budget/sampling/model/tools/policy bounds remain matched. Native synthetic graph/similarity tests and actual E1-R180 official compiler passed within 66-test focused suite. No task-specific diagnosis, reference patch or hidden-test content entered any prompt or archive; no GPU execution. Self-review completed.",
        "candidate": {
          "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
          "value": "e206113ca40e557e6c29464ec861933560e2e2bd99b768ee79eef30f1550b901"
        }
      },
      "gate_history": [
        0,
        0
      ]
    },
    "stage-3": {
      "done": [
        "notebook-preflight",
        "readiness-evidence"
      ],
      "reviews": 0,
      "failures": 0,
      "review": null,
      "blocked": null,
      "checkpoint": {
        "item": "readiness-evidence",
        "evidence": "Dependent AUD-001 correction regenerated only comparison.json using approved comparison(diagnosis); SHA256 78d1ffcd28ba312095d19c1329db92273ec0fd46e3a286384d11161703c0c327 now binds corrected diagnostic b38d4a5d5eeeae6411c5c5604afa46f214e7efac05c13aec5e6a2d1f47c91f70 and successful-read response coverage metadata. All six historical traces have known membership, so observed repeated counts remain zero with explicit coverage. Notebook/readiness/report recomputed byte-identically and left unwritten. Exact approved phase2-readiness CLI passed, including authentic legacy replay, all-five double compilation, source/payload/report comparisons. Whitespace check/self-review passed. GPU remains ABSENT and six NOT_RUN; no source/spec/other-stage/GPU/Git writes. Finding remains open for independent Auditor; parent full gate/audit pending.",
        "candidate": {
          "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
          "value": "3233342bc07e167ffd079a9e7dce91e8852072404859906e71e666b4db463074"
        }
      },
      "gate_history": [
        0,
        0
      ]
    }
  },
  "gate": {
    "candidate": {
      "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
      "value": "3233342bc07e167ffd079a9e7dce91e8852072404859906e71e666b4db463074"
    },
    "digest": "d717b316dcc468b577713b95fd5445f61a71a617c51fd0e2554e97f08652ea03",
    "results": [
      {
        "id": "spec-frozen",
        "stage": null,
        "code": 0,
        "spec_digest": "5335a0faaf2aba36d7cff8f638bfbcb4f856fedb579ce70663157827f7d1bcb5"
      },
      {
        "id": "git-diff-check-stage-1",
        "stage": "stage-1",
        "code": 0,
        "output_digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      },
      {
        "id": "git-diff-check-stage-2",
        "stage": "stage-2",
        "code": 0,
        "output_digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      },
      {
        "id": "git-diff-check-stage-3",
        "stage": "stage-3",
        "code": 0,
        "output_digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      },
      {
        "id": "repository-validation",
        "stage": "stage-3",
        "code": 0,
        "output_digest": "f2dbe7857ff7ad8714187a28c570a3a80c091c915548861785f09fa52de44905"
      },
      {
        "id": "phase2-readiness",
        "stage": "stage-3",
        "code": 0,
        "output_digest": "4a83392cd979f6f401221451c87a01c1bd37c76a7fe707f855d4d68f5e750426"
      }
    ]
  },
  "versioning": {
    "candidate": {
      "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
      "value": "3233342bc07e167ffd079a9e7dce91e8852072404859906e71e666b4db463074"
    },
    "status": "CLOSED_FOR_COMMIT",
    "paths": [
      "README.md",
      "docs/architecture.md",
      "docs/experiments.md",
      "docs/implementation/evidence/mostaza-phase2-budget-retrieval/comparison.json",
      "docs/implementation/evidence/mostaza-phase2-budget-retrieval/official-validation.json",
      "docs/implementation/evidence/mostaza-phase2-budget-retrieval/readiness.json",
      "docs/implementation/evidence/mostaza-phase2-budget-retrieval/report.md",
      "docs/implementation/evidence/mostaza-phase2-budget-retrieval/resource-review.json",
      "docs/implementation/evidence/mostaza-phase2-budget-retrieval/trace-diagnosis.json",
      "docs/kaggle-setup.md",
      "docs/specs/README.md",
      "docs/specs/budget-retrieval-calibration.md",
      "experiments/E0-B180/manifest.json",
      "experiments/E0-B300/manifest.json",
      "experiments/E1-B180/manifest.json",
      "experiments/E1-B300/manifest.json",
      "experiments/E1-R180/manifest.json",
      "notebooks/mostaza-phase2-budget-retrieval.ipynb",
      "scripts/check_official.py",
      "scripts/check_phase2.py",
      "scripts/prepare_phase2.py",
      "src/mostaza/evaluation/phase2.py",
      "src/mostaza/packaging.py",
      "src/mostaza/research/trace_diagnostics.py",
      "submission/prompts/hybrid-recovery.md",
      "tests/integration/test_official_contract.py",
      "tests/integration/test_phase2.py",
      "tests/integration/test_pipeline.py",
      "tests/unit/test_packaging.py",
      "tests/unit/test_phase2.py",
      "tests/unit/test_retrieval_policy.py",
      "tests/unit/test_trace_diagnostics.py",
      "docs/specs/plans/closed/mostaza-phase2-budget-retrieval.md"
    ],
    "files": {
      "tests/integration/test_pipeline.py": [
        "file",
        420,
        "1e8c856e8249b536a184c9b8aba98c0b2c2f838460ef6c7d713f6ce9a0af861a"
      ],
      "docs/implementation/evidence/mostaza-phase2-budget-retrieval/resource-review.json": [
        "file",
        420,
        "2beea775006a5bfcfda58839801c0b4d477f76f945e39a8bf2f69cecf4273797"
      ],
      "src/mostaza/research/trace_diagnostics.py": [
        "file",
        420,
        "af9834e18f1cfacb5a2bf3705994e31ec61cde829d864bfdb811186733e0686d"
      ],
      "docs/specs/README.md": [
        "file",
        420,
        "4a1a3d8016358ae1ce28e88189a2270e389d21fef9164cae26a1b3b3028dec8a"
      ],
      "experiments/E0-B300/manifest.json": [
        "file",
        420,
        "fad16d4d5e21df8aae052a55522d4b7fa230dfcea639aee1fa18170a708ac3b8"
      ],
      "README.md": [
        "file",
        420,
        "6fb7e729a6cb2aceddd4ee2eef420c8439adb9fad016b6f0ffacba451fc61358"
      ],
      "experiments/E1-B300/manifest.json": [
        "file",
        420,
        "2bad3f9ae84eb411d247542a4712ecbbef6206d5be564404d9b56d9a5e20ef9f"
      ],
      "tests/integration/test_phase2.py": [
        "file",
        420,
        "57f08b3f08bd74a8050afcf479c3ae712231c111fc92e79691502c221c52cd86"
      ],
      "notebooks/mostaza-phase2-budget-retrieval.ipynb": [
        "file",
        420,
        "02d410a2cec6d833426eed6cd8fcfee43d8b16c8e537592e92a87ec32cc0c4c2"
      ],
      "docs/architecture.md": [
        "file",
        420,
        "62935a9775c2fce4a93e11e96bbcdf130dfe3b0653cd920e3b706567bf561d89"
      ],
      "docs/implementation/evidence/mostaza-phase2-budget-retrieval/official-validation.json": [
        "file",
        420,
        "44d2580ed9a9c76d5ea7539423d6c85ebcfdcc06c16929ae9c095212b9c2eed0"
      ],
      "experiments/E0-B180/manifest.json": [
        "file",
        420,
        "400fa15b41cbe497d0c758b48cf10602a0563ea6bc60382266869a0c0e0bed88"
      ],
      "docs/implementation/evidence/mostaza-phase2-budget-retrieval/readiness.json": [
        "file",
        420,
        "fda3d9b9a2c08dc973ba64a7ebac62cb45a9927e616f3528bdac3214bdf5935d"
      ],
      "src/mostaza/packaging.py": [
        "file",
        420,
        "b1944c8e7dd66036cfc9679f0dca66386c2c30a5e2066cf2d559680b90ec029f"
      ],
      "scripts/check_phase2.py": [
        "file",
        420,
        "3e4b35ad19e6f88a54879ff44136a08e6e5fb49441d93ced9fef70ca260e0cee"
      ],
      "tests/unit/test_phase2.py": [
        "file",
        420,
        "edb1432e40392f62d2cd84399dd1d22f37ec429ef84504b67bfda050c34cc127"
      ],
      "docs/implementation/evidence/mostaza-phase2-budget-retrieval/report.md": [
        "file",
        420,
        "51f43590a496ae011aec55fa30beee18e42d18724c97454329fb1e485415f4f9"
      ],
      "docs/implementation/evidence/mostaza-phase2-budget-retrieval/comparison.json": [
        "file",
        420,
        "78d1ffcd28ba312095d19c1329db92273ec0fd46e3a286384d11161703c0c327"
      ],
      "docs/kaggle-setup.md": [
        "file",
        420,
        "3e473b617acefb6025e8c7348092d2bb04e23b66303816198ce76234a111cd9e"
      ],
      "docs/experiments.md": [
        "file",
        420,
        "0960153f0c1d3fb577bf7027cad49cbdaf6d4ec49cc495a34eefa96e0aeeea8e"
      ],
      "docs/specs/budget-retrieval-calibration.md": [
        "file",
        420,
        "b1e8eddef48a6bc770899ce6bd61c4f29fa81bf1024f9c637609d1b53a28c0c6"
      ],
      "submission/prompts/hybrid-recovery.md": [
        "file",
        420,
        "dc303ac516a09bbff118253f9bb90542d02cba0e6055af37754fb53a59b6fae5"
      ],
      "scripts/prepare_phase2.py": [
        "file",
        420,
        "0c30e2e1eeddd70d609f4cfc63073b79d18004e43746dbbeddbbd5061fd5f240"
      ],
      "tests/integration/test_official_contract.py": [
        "file",
        420,
        "7eeb0a0a4c9e65ed2790969bfe09f907014a67aa1c14221321e686fd2522c818"
      ],
      "tests/unit/test_retrieval_policy.py": [
        "file",
        420,
        "ff1cb3caf80a68f5cd0b6fdd8c62aeae005183189cc5d2a68e388282e3b23ad4"
      ],
      "experiments/E1-R180/manifest.json": [
        "file",
        420,
        "8204b9f04e4bc0f78c05271168a68cb500664abb539a2b06210821e0daab5b59"
      ],
      "tests/unit/test_packaging.py": [
        "file",
        420,
        "5f81133208564d52b3ac995b241812d6551bca2a36fcda74e740c23b31f59972"
      ],
      "docs/implementation/evidence/mostaza-phase2-budget-retrieval/trace-diagnosis.json": [
        "file",
        420,
        "b38d4a5d5eeeae6411c5c5604afa46f214e7efac05c13aec5e6a2d1f47c91f70"
      ],
      "src/mostaza/evaluation/phase2.py": [
        "file",
        420,
        "efd71b1c73a07a267b6a4a2f42ef5f8dcec4c2e9651c8a71879619265aeb8c7b"
      ],
      "experiments/E1-B180/manifest.json": [
        "file",
        420,
        "58409d7a173dfcc1f6892fbc95f0d94c5ea55d3a7513935b7040d3e7c08fa464"
      ],
      "scripts/check_official.py": [
        "file",
        420,
        "9a391ff31b750f3067685ec523149332cb7c32747748a65e2bee1c831397e9db"
      ],
      "tests/unit/test_trace_diagnostics.py": [
        "file",
        420,
        "13063af3b9184cd5bf4f436c95eed80d9366ef2644fcec0b66fb556e08173318"
      ]
    }
  },
  "legacy": null,
  "autonomy": {
    "policy": "audit-only-v1",
    "authorizations": []
  },
  "specification_policy": "planner-first-v1",
  "work_branch": {
    "name": "sdd/mostaza-phase2-budget-retrieval",
    "base": "develop",
    "base_head": "60ad0cec85bb36a1e65609ca2b1a743ba087384d",
    "initial_head": "60ad0cec85bb36a1e65609ca2b1a743ba087384d",
    "remote": "origin",
    "target": "develop",
    "push_url": "git@github.com:diego-escobar-git/mostaza-harness.git"
  },
  "spec_file_digest": "5335a0faaf2aba36d7cff8f638bfbcb4f856fedb579ce70663157827f7d1bcb5",
  "gate_sequence": 2,
  "last_gate": {
    "results": [
      {
        "id": "spec-frozen",
        "stage": null,
        "code": 0,
        "spec_digest": "5335a0faaf2aba36d7cff8f638bfbcb4f856fedb579ce70663157827f7d1bcb5"
      },
      {
        "id": "git-diff-check-stage-1",
        "stage": "stage-1",
        "code": 0,
        "output_digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      },
      {
        "id": "git-diff-check-stage-2",
        "stage": "stage-2",
        "code": 0,
        "output_digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      },
      {
        "id": "git-diff-check-stage-3",
        "stage": "stage-3",
        "code": 0,
        "output_digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      },
      {
        "id": "repository-validation",
        "stage": "stage-3",
        "code": 0,
        "output_digest": "f2dbe7857ff7ad8714187a28c570a3a80c091c915548861785f09fa52de44905"
      },
      {
        "id": "phase2-readiness",
        "stage": "stage-3",
        "code": 0,
        "output_digest": "4a83392cd979f6f401221451c87a01c1bd37c76a7fe707f855d4d68f5e750426"
      }
    ],
    "candidate": {
      "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
      "value": "3233342bc07e167ffd079a9e7dce91e8852072404859906e71e666b4db463074"
    },
    "definition_digest": "d717b316dcc468b577713b95fd5445f61a71a617c51fd0e2554e97f08652ea03"
  }
}
```

<!-- SDD-CONTINUITY:END -->
