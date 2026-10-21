# 2026-10-20-search-code

## Known external prerequisites — full gate currently cannot pass

Planning review on 2026-10-20 confirmed two missing historical inputs. They are prerequisites to the unchanged mandatory regression gate, not search-code implementation defects:

1. `/Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness` does not exist. `tests/integration/conftest.py` requires that exact retained checkout, HEAD `1b86b19f7654212c1d9f95eeca84d0e2a05db16b`, its pinned historical manifests, and the sole dirty closed plan `docs/specs/plans/closed/mostaza-phase2-budget-retrieval.md` with SHA-256 `5457a535f1e8457789d73ef38f0346c04ded2d18424a172e12d7b3ed6e66a8d5`. A fresh checkout or current source clone is not evidence-equivalent.
2. The phase-1 original native packet `results/kaggle-v2-358139443` required by `scripts/check_evidence.py` is absent from both this worktree and the source checkout. Specifically absent are `private-run-evidence/99c637be-d945-4dd7-85d8-4042cfcc2bad` (including `source-inventory.json`), `mostaza-reviewed-input-836a861c-0811-4de8-b386-a2cedc7861d7`, `results.zip` and `mostaza-e0-e1-phase-1-paired-benchmark.ipynb`. The tracked receipt at `docs/implementation/evidence/mostaza-phase1-foundation/official-validation.json` supplies their immutable identity and hash requirements; tracked summaries cannot substitute for the missing originals.

After explicit plan/gate approval, independent implementation in stages 1–3 and the stage-4 driver/CPU benchmark work may proceed using available source assets. Stage-4 full regression completion, gate PASS, Auditor PASS and Versioner closure must stop while either historical prerequisite is absent or fails its existing identity checks. Report the exact prerequisite failure; preserve all checks and pending items. Do not mark complete, deselect historical tests, create synthetic historical evidence, reconstruct the retained checkout, rerun inference or fetch Kaggle results under this plan. Obtaining/restoring original retained artifacts requires a separate user-directed recovery action. If originals are supplied, verify existing pins before the unchanged full gate; different paths/identities or relaxed checks require a new material plan decision.

## Original user requirement
"Entonces prepara un plan concreto para implementar search_code mediante run_command y reemplazar esas tres tools, con búsqueda léxica, grafo ligero e indexación incremental compatible con Kaggle. Sin modificar código todavía."
User steering: "Lo ejecutaremos con el flujo '$sdd'".

## User context and intended behavior
The harness must help its agent locate source files and functions and navigate internal dependencies quickly, with a compact index, low memory use and good retrieval performance. The user wants search_code executed through the existing run_command tool, without registering a custom host tool. Its implementation must validate whether its index and graph are ready, build them on demand when necessary, and incrementally update them after workspace changes. It is intended to replace the exposed get_code_neighbors, search_similar_code and get_code_subgraph tools. Current scope is specification and concrete implementation planning only; no source, tests, prompts, submission config or packaging implementation before explicit plan/gate approval.

## Discussion context for Planner evaluation, not previously approved implementation details
A proposed design uses standard-library Python ast (including async definitions), sqlite3/FTS5, a lightweight graph, unambiguous symbol identities and real file/line locations. Graph navigation should cover callers/callees and a bounded induced subgraph, plus imports where safely resolved. Removing native search_similar_code does not imply preserving neural/vector similarity: lexical retrieval replaces it in the proposed initial scope; make this explicit in the spec/plan approval.
run_command can run a Python CLI in each task sandbox, but submitting a script does not automatically make it available there. The inspected pinned official runtime (swegemma 0.2.11, adk_submission 0.2.13, google-adk 1.36.1) supports ADK skill scripts via run_skill_script and a sandbox code executor. A candidate delivery route is one bootstrap skill that persists a self-contained search_code CLI under sandbox /tmp, optionally performs the first search, and subsequent searches use run_command. Skill resources are normally materialized transiently, so persistence, workspace root handling and subprocess/Docker path behavior must be validated. Evaluate this route from authoritative source; do not modify or monkey-patch official runtime, compiler, evaluator or verifier. A prompt-embedded bootstrap is a less attractive alternative, not a requirement.
The active submission currently exposes nine native tools; the new active candidate should retain run_command/read_file/edit_file/write_file/get_status/submit_patch and remove the three native retrieval tools from exposure and active instructions. Historical frozen E0/E1 experiments and retained evidence must remain reproducible and unchanged. Do not remove native registry compatibility globally if historical packaging uses it.
The current host packager permits only YAML/prompts, rejects skills and Python files, and collects only !include closure. A narrow skill packaging extension plus true official compiler/executor integration tests is needed; inert compiler bindings alone do not establish script execution. Keep one authoritative runtime implementation rather than divergent host/submission copies.
Only source visible in the task workspace may be indexed; never use solution/reference/test_patch fields or verifier-only material. Official precomputed resources live host-side and cannot be assumed accessible from the task script. No Internet, model downloads, GPU setup, new inference, Kaggle session mutation/submission or compute consumption is authorized for planning or implied by this requirement. Separate deterministic CPU/sandbox portability validation from future real Kaggle efficacy claims.
CLI output must remain valid JSON within the native run_command output limit (default 5000 chars per stream). Existing active budgets are timeout_seconds=60, max_time_minutes=5, max_tool_calls=20, max_turns=50; preserve unless a material change is explicitly approved. Account for bootstrap and cold indexing inside the agent budget, and avoid daemon/global in-memory full-repo graphs. Incremental consistency must cover changes by edit_file/write_file/run_command, file add/delete/rename, dependent imports/references, parse failures, interrupted builds and cache isolation. Cache/executable must not contaminate submitted patches.

## Prior read-only observations to verify as relevant
The source checkout was clean on develop at 1969aa509b6a161a159c79454e95100f6fba8b54; origin/develop matched that SHA via git ls-remote. Five real local graph/embedding pairs cover the five downloaded snapshots (requests_7205, requests_7315, requests_7502, fastapi_15589, rich_3061), not all 129 task rows. Graph nodes contain id/name/text without explicit paths/lines; all observed edges have type calls; embeddings are 256-dimensional float32. Native resolvers silently choose a suffix match. Some symbol IDs conflate definitions, and async source coverage is incomplete. These local resources and Python environments are ignored and will not automatically exist in the new worktree: plan explicit read-only reuse of reviewed absolute source assets/interpreters where appropriate, importing mostaza from the new worktree, and test sandbox Python 3.12 compatibility separately from host 3.13.
Use the durable worktree returned by sdd.py start for all planning artifacts. Draft a specification-first plan, exact deterministic gate commands, declared evidence and final Versioner push/PR-to-develop closure for user review. Do not implement before that approval.

## Approved objective and implementation boundary

This is a proposal for approval, not authorization to implement. Deliver the active search-code candidate specified by search-code:AC-1–AC-8. Lexical retrieval replaces vector similarity. Keep all frozen experiments and prior evidence unchanged. Exactly six native tools remain; the official skill adds its discovery/load/run helper tools, so “six” is not a claim about total ADK-visible tools. There is no Stage 0: specification edits below are the only planning changes.

## Repository and primary-source findings

- Host packaging currently rejects skills and Python files, validates nine native registry names and traverses only YAML !include references. Historical configuration_files uses experiments/historical-submission and must retain its behavior.
- Pinned adk_submission 0.2.13 schema accepts skills; compile_submission accepts a code_executor. swegemma 0.2.11 harness/agent_runner.py constructs AdkSandboxCodeExecutor with native task budgets. google-adk 1.36.1 SkillToolset materializes scripts under TemporaryDirectory, changes cwd there and removes it afterward. adk_eval_core sandbox/base.py executes a temporary wrapper with sandbox python3 and removes it. Therefore explicit sandbox root, persistent copy, cleanup and a real second run_command call are mandatory acceptance, not inferred from compilation.
- Current editable submission has nine native tools and 60 s / 5 min / 20 calls / 50 turns. Python host tooling is 3.13; /Users/diego/.pyenv/versions/3.12.8/bin/python3.12 exists for standalone execution compatibility. Official resource snapshots available locally are exactly the five listed in search-code:AC-8.
- Relevant specifications and dependencies reviewed: foundation, agent-retrieval and local-lmstudio-kaggle. Existing local connectivity evidence is historical and is not rerun. scripts/validate.sh defines format, lint, types, both test suites, temporary build, official E0/E1 compile and paired evidence checks; equivalent explicit child checks below retain all of them.

## Specification changes

Files: docs/specs/search-code.md (new), docs/specs/agent-retrieval.md, docs/specs/local-lmstudio-kaggle.md, docs/specs/README.md.

Added acceptance — exact new text:

search-code:AC-1: The active agent declares exactly run_command, read_file, edit_file, write_file, get_status and submit_patch as native tools. One official ADK skill supplies a bootstrap script; official skill-toolset discovery/load/run helpers may additionally be exposed and must be inventoried. No custom host tool, runtime/compiler/evaluator patch, neural search, model download or new inference is introduced. Historical experiment sources, manifests and retained evidence remain byte-identical and their native registry compatibility remains available.

search-code:AC-2: The packaged skill contains one authoritative standalone Python search_code implementation, runnable on Python 3.12 and 3.13 using only the standard library. The official compiler, SkillToolset and AdkSandboxCodeExecutor must execute it in a real disposable subprocess sandbox. Bootstrap requires an explicit absolute sandbox workspace root, copies the exact CLI bytes atomically to a versioned private temporary directory outside that root, returns the quoted run_command invocation, and may perform the first query. A later native run_command invocation succeeds after transient skill resources disappear. Executable/cache isolation binds canonical workspace, source version and index schema; symlinks, foreign cache ownership and cross-workspace reuse fail closed. No executable, database, lock or bootstrap residue appears in the submitted diff.

search-code:AC-3: Search accepts literal bounded query text and optional workspace-relative path filters; it indexes visible regular UTF-8 source/text files without following symlinks or escaping the workspace. Exclude .git, environments, caches, binary/generated/vendor bulk and explicit solution/reference/test_patch artifacts; do not ingest task metadata, verifier-only material or host graph/embedding stores. FTS5 lexical ranking combines exact path/name matches with token/source matches and deterministic tie breaking. Python AST extraction includes modules, classes, nested functions, methods and async definitions. Each symbol has a unique ID derived from relative path, qualified name, kind and definition location and exposes actual start/end lines. Duplicate names never silently select a suffix match. Missing FTS5 is an explicit unavailable capability with a safe lexical-shell fallback instruction, never a false successful empty index.

search-code:AC-4: The lightweight graph records containment, statically resolvable imports and conservative call edges. Neighbor queries distinguish callers/callees/imports/containment, and subgraph queries return the induced graph of explicit seeds plus a bounded expansion (default one hop, maximum two). Resolve same-module names, lexical nesting, import aliases and package-relative imports where unique; unresolved dynamic dispatch, wildcard imports and ambiguous symbols remain explicit unresolved data, never fabricated edges. Duplicate definitions and async/nested scopes have fixtures with exact expected nodes/edges. Non-Python text remains lexically searchable without a claim of semantic graph coverage.

search-code:AC-5: Every operation checks index/schema/source readiness and reconciles the current workspace before answering. Content fingerprints detect equal-size/equal-mtime edits as well as add/delete/rename and changes from edit_file, write_file and run_command. Reparse only changed files; refresh resolution for affected dependents, removing stale cross-file edges. Serialize writers with a bounded lock wait, use atomic committed generations, and never present a partial/interrupted/stale generation as current. Concurrent modification causes a bounded retry or an explicit incomplete/busy response. Parse failures preserve current lexical text and report graph incompleteness; removed or broken definitions never retain old graph edges. Corrupt/schema-incompatible caches rebuild safely; interrupted builds recover on the next call.

search-code:AC-6: All ordinary results, invalid arguments, ambiguity, unavailable capability, timeout and truncation responses use schema_version=1 JSON. The serialized stdout is at most 4500 characters including newline and stderr is empty for handled failures, fitting the native default 5000-character stream limit. Serialize then drop whole entries/snippets until valid JSON fits; report truncated/incomplete and counts. Return status, mode, workspace-relative locations, bounded results/nodes/edges, index generation and refresh counters, unresolved/omitted counts, and duration. Never return an unbounded traceback or source dump. Defaults: 8 results, 20 maximum; 40 nodes and 80 edges maximum; query length 512 characters; 45-second cooperative operation deadline and bounded lock wait. Large/binary/unreadable/excluded files and indexing limits are explicit counts/reasons. File and source limits are 1 MiB per file, 50000 eligible files and 256 MiB cumulative source bytes; reaching a bound returns incomplete, not complete.

search-code:AC-7: The host packager permits only the selected skills/search-code/SKILL.md and skills/search-code/scripts/search_code.py in addition to the existing YAML/prompt closure, validates the declared single skill and rejects extra code, traversal, symlinks, duplicate/unknown tools and resource injection. Deterministic ZIP and generated delivery notebook contain exactly the same approved source bytes; no credentials/data/cache/development files. The real pinned directory/schema/compiler accepts the active delivery and frozen E0/E1 packages. Active instructions teach bootstrap, quoting, bounded search/graph use, refresh behavior and plain-shell fallback; preserve model/generation settings and timeout_seconds=60, max_time_minutes=5, max_tool_calls=20, max_turns=50. Bootstrap and cold indexing consume the existing wall-clock budget; document actual helper/native budget accounting without changing official enforcement.

search-code:AC-8: Deterministic CPU checks cover all prior criteria, adversarial file/cache/packaging inputs and native edit/write/command refresh. A source-only benchmark uses the five locally available snapshots (requests_7205, requests_7315, requests_7502, fastapi_15589, rich_3061), with no solution/test-patch queries, plus synthetic nested/async/ambiguous/non-Python cases. A small deterministic query set derived only from visible source tests exact symbol/location retrieval in the top 5 and graph fixtures test exact supported edges. Record per-snapshot cold bootstrap/index/search, warm search and single-file refresh: each cold operation <=45 s, warm <=3 s, refresh <=10 s, peak child RSS <=256 MiB and database <=128 MiB. Unchanged warm runs reparse zero files; a single-file content edit reparses only that file while dependent edges update. Missing fixtures/interpreters or exceeded limits fail the CPU gate, never silently skip. Validate actual Python 3.12 execution and subprocess path behavior; inspect pinned Docker /workspace command semantics and test absolute/path-with-spaces contract fixtures without starting/changing Docker or Kaggle sessions. Reports explicitly distinguish measured local CPU behavior, source-reviewed Docker mapping and unexecuted Kaggle efficacy.

Modified acceptance — exact before/after text against branch start:

**agent-retrieval:AC-5 — before**

AC-5: Packaging requires an explicit E0 or E1 selection, produces a deterministic submission.zip with root agent.yaml and only its allowed dependency closure, and fails on traversal, symlinks, unknown tools/models, forbidden files or missing includes. Both archives pass current official directory/schema/compiler validation; archive creation alone never establishes official evaluation compatibility.

**agent-retrieval:AC-5 — after**

AC-5: Frozen E0/E1 packaging requires an explicit E0 or E1 selection, produces a deterministic submission.zip with root agent.yaml and only its allowed dependency closure, and fails on traversal, symlinks, unknown tools/models, forbidden files or missing includes. Both archives pass current official directory/schema/compiler validation; archive creation alone never establishes official evaluation compatibility. The active submission may instead use the narrowly allowlisted search-code skill and six native tools under search-code:AC-1/AC-7; historical archives retain their declarative closure.

**local-lmstudio-kaggle:AC-3 — before**

AC-3: The documented setup/run/pack entrypoints reuse existing installed official packages and task data when configured; every parent and compiler import resolves mostaza from this worktree even when using the source checkout interpreter. Do not edit official packages, verifier, scorer, prompts, submission files, or machine compute configuration.

**local-lmstudio-kaggle:AC-3 — after**

AC-3: The documented setup/run/pack entrypoints reuse existing installed official packages and task data when configured; every parent and compiler import resolves mostaza from this worktree even when using the source checkout interpreter. Do not edit official packages, verifier, scorer, prompts, submission files, or machine compute configuration during that original connectivity run. The separately approved search-code plan may change active submission/prompts and host packaging; original run evidence remains frozen.

**local-lmstudio-kaggle:AC-5 — before**

AC-5: Both local run and pack consume collect_submission(submission/) and its existing allowlisted include closure. The competition model in agent.yaml remains unchanged. The official directory/schema/compiler accepts the staged delivery; the ZIP contains exactly the collected agent bytes and excludes local configuration, credentials, task data, solutions, results and development tools.

**local-lmstudio-kaggle:AC-5 — after**

AC-5: Both local run and pack consume collect_submission(submission/) and its allowlisted dependency closure, including the narrowly scoped active search-code skill when selected. The competition model in agent.yaml remains unchanged. The official directory/schema/compiler accepts the staged delivery; the ZIP contains exactly the collected agent bytes and excludes local configuration, credentials, task data, solutions, results and development tools.

Removed/restored ACs: none. Product decisions: search-code PD-1–PD-4 explicitly choose lexical replacement, official bootstrap, conservative bounded coverage and CPU-only evidence; agent-retrieval PD-4 scopes the historical native-only MVP; local-lmstudio-kaggle PD-3 extends same-source delivery. The specification index gains one line. No historical acceptance is deleted or silently applied to a new experiment.

## Implementation stages

### Stage 1 [stage-core] — HIGH: isolated incremental source index

Own submission/skills/search-code/scripts/search_code.py and tests/unit/test_search_code.py. Items core-cli and incremental-graph implement the interface, lexical/AST index, identity/JSON bounds, conservative graph and transactional refresh. The security/concurrency risk is accepting workspace/cache paths and returning an index while files change; use no symlink traversal, unique root/version identity, bounded writer serialization and complete committed generations. Use SQLite FTS5 tables plus file/symbol/reference/edge tables with indexes, stream files and SQL queries, and never load a repository-wide graph in RAM. Persist unresolved references so changed exports/imports can invalidate their dependents. Hash current eligible content on every operation; unchanged files are not reparsed. Content hashes rather than mtime shortcuts are required. Bootstrap copies this same file, not a second host implementation. Tests import it by path and execute it as a subprocess. Covers search-code:AC-2/3/4/5/6. Checkpoint requires targeted tests and explanation of cache identity/atomicity, graph limits and JSON size behavior.

### Stage 2 [stage-package] — HIGH: constrained skill delivery

Depends on stage-core. Own src/mostaza/packaging.py and tests/unit/test_packaging.py. Items skill-closure and historical-compatibility add precisely the declared skill directory/SKILL.md/single script to the selected dependency closure, with existing secure file reads, size/count limits, deterministic archives and explicit top-level skills validation. The risk is broadening submitted-code trust: reject additional script/resource paths and skill declarations, retain traversal/symlink/unknown-tool protection, and never globally delete historical native registry names. Preserve E0/E1 generated archives and manifest validation. Covers search-code:AC-7, agent-retrieval:AC-5 and local-lmstudio-kaggle:AC-5. Checkpoint compares allowed/rejected archives and historical closure bytes against the initial HEAD.

### Stage 3 [stage-activate] — MEDIUM: official bootstrap and active instructions

Depends on stage-package. Own submission/agent.yaml, submission/prompts/baseline.md, submission/skills/search-code/SKILL.md and tests/integration/test_search_code_official.py. Items active-policy and official-bootstrap connect compiled SkillToolset to the unchanged official executor/native tools. Remove the three retrieval tools from the active list and baseline instructions, declare the one skill and explain its root/quoting/bounded-query procedure and fallback. Other inactive prompt files and historical copies stay unchanged. Test actual official compiler/toolset invocation without an LLM, native subprocess workspace creation, disappearance of transient skill resources, a second run_command query, native write/edit/command updates and patch cleanliness. Inventory helper tool names and observed budget accounting: do not assert skill helpers count exactly like native run_command unless source/execution proves it. ZIP/notebook parity uses existing mostaza.development.write_kaggle_notebook without source duplication. Covers search-code:AC-1/2/7 and local-lmstudio-kaggle:AC-3. Checkpoint includes concrete execution witnesses, not inert bindings alone.

### Stage 4 [stage-validate] — MEDIUM: bounded CPU evidence and full regression

Depends on stage-activate. Own scripts/check_search_code.py, tests/unit/test_search_code_validation.py and README.md; own the two declared evidence files. Items cpu-evidence and regression-delivery implement the deterministic gate driver, fail-closed report validation and concise usage/limits documentation. The interacting components are snapshot extraction, child process/RSS measurement, Python 3.12 execution, official subprocess integration, archive/notebook parity and repository quality checks. Safe extraction rejects archive traversal/symlinks and uses only the five visible source snapshots. Source-derived query cases require actual top-5 exact path/line matches and known graph fixtures; no task descriptions, solution metadata or reference patches seed retrieval. Preserve measured failures in reports and return nonzero; never tune thresholds silently. Covers search-code:AC-8. Checkpoint contains both compact evidence reports and all required checks. Historical verification tests also belong to this stage: run the original phase-2 verifier and readiness/compiler/resource/trace/source-hash recomputation against the authenticated original checkout, preserving before/after byte checks; retain a real unmocked negative operator-path/readiness mismatch check using only a disposable copy of declared evidence. Do not require the approved active agent YAML to equal the old submission. Current notebook provenance/tamper rejection, active skill execution, archive parity and six-tool/budget/import assertions remain independently mandatory. The P-CV-01 test runs the original checker with original host imports and retains its actual 14-control CPU matrix, zero GPU and compatibility assertions, without modifying originals or official runtime. Capture child exit/stdout/stderr so failures remain diagnosable.

## Prerequisites and safe validation setup

All writes remain in this durable worktree or disposable test directories, never the source checkout. Before gates, the Implementer may prepare ignored local prerequisites: copy only verified resource-manifest assets and five snapshot archives from the read-only source checkout into corresponding resources/official paths, verifying SHA-256 against the tracked manifest for declared entries and recording snapshot hashes. Do not symlink resource paths: resources.py explicitly forbids symlinks. Never overwrite unexpected local resources; report mismatches. Do not copy .env, model weights, credentials, arbitrary source state or unrelated results. The exact original phase-1 packet listed under Known external prerequisites is the sole results-input exception: once separately supplied, it must occupy its receipt-bound project-relative results paths for read-only verification, with all existing inventory/hash checks retained. It is never a search-code index input, generated report, submitted file or committed artifact. It is currently absent; this exception does not authorize recovering or reconstructing it. Precomputed graph/embedding resources are not search-code inputs.

Existing tests require worktree .venv and .tools/official paths. Use ignored links to the reviewed source checkout .venv and .tools/official environments (and .tools/harness only if an existing test requires it), without installing or editing them. Set PYTHONDONTWRITEBYTECODE=1 and PYTHONPATH to this worktree's absolute src for every active-candidate parent, compiler and child; assert mostaza imports resolve here. The sole historical-verification exception is the authenticated historical child execution in tests/integration/test_phase2.py and tests/integration/test_pcv01_cpu_contract.py: their child cwd, scripts, mostaza imports and PYTHONPATH must bind to the verified original historical root/src, while the parent and all active-candidate checks remain bound to this worktree. Preserve all other environment entries and verify actual imported module __file__ locations inside those children. Do not change the top-level gate argv/environment, use this exception for active execution, substitute historical code for current product checks, or suppress any historical verification. These ignored prerequisite links never enter a delivery archive or commit. Reuse /Users/diego/.pyenv/versions/3.12.8/bin/python3.12 for standalone tests; no interpreter downloads. The required historical fixture root /Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness is currently missing; existing fixture identity checks stay enabled. The required phase-1 raw packet is also missing, as detailed prominently above. Missing assets, version/hash drift or inaccessible retained evidence is a prerequisite failure requiring a precise report, never a skip or weakening of validation. Planning does not execute any of these setup steps or gates. Read-only review confirmed all 12 entries in the tracked resources/manifest.json are present in the source checkout and match their declared SHA-256. All five snapshot archive paths and both source interpreter environments exist; the three cohort snapshots additionally match hashes in the phase-1 receipt. No claim is made that the unavailable historical checkout/raw evidence is reusable or that all environment packages have passed execution checks. Stage-4 must preflight these exact missing historical identities before attempting full regression and report failure without changing its required command set.

## Exact deterministic gate

Executable argv arrays, cwd (this project root), timeouts and acceptance bases are defined once in continuity. Their shell-readable forms are:

- core (timeout 300 s): `/usr/bin/env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/src MOSTAZA_HISTORICAL_PHASE2_ROOT=/Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness '/Users/diego/Documents/Desarrollo/Mostaza Dev/PyCharm Projects/Mostaza-Harness/.venv/bin/python' -m pytest -q -p no:cacheprovider tests/unit/test_search_code.py`
- packaging (timeout 300 s): `/usr/bin/env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/src MOSTAZA_HISTORICAL_PHASE2_ROOT=/Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness '/Users/diego/Documents/Desarrollo/Mostaza Dev/PyCharm Projects/Mostaza-Harness/.venv/bin/python' -m pytest -q -p no:cacheprovider tests/unit/test_packaging.py`
- official-execution (timeout 600 s): `/usr/bin/env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/src MOSTAZA_HISTORICAL_PHASE2_ROOT=/Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness '/Users/diego/Documents/Desarrollo/Mostaza Dev/PyCharm Projects/Mostaza-Harness/.venv/bin/python' -m pytest -q -p no:cacheprovider tests/integration/test_search_code_official.py`
- complete-cpu-gate (timeout 1800 s): `/usr/bin/env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/src MOSTAZA_HISTORICAL_PHASE2_ROOT=/Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness '/Users/diego/Documents/Desarrollo/Mostaza Dev/PyCharm Projects/Mostaza-Harness/.venv/bin/python' scripts/check_search_code.py --check --source-assets '/Users/diego/Documents/Desarrollo/Mostaza Dev/PyCharm Projects/Mostaza-Harness' --official-python '/Users/diego/Documents/Desarrollo/Mostaza Dev/PyCharm Projects/Mostaza-Harness/.tools/official/bin/python' --python312 /Users/diego/.pyenv/versions/3.12.8/bin/python3.12 --evidence-dir docs/implementation/evidence/2026-10-20-search-code`

The gate additionally executes built-in git diff --check HEAD per stage over its exact declared paths. No new inference, model-catalog request, migration or generated-contract gate applies: the change neither runs a model nor changes a database migration, external API schema or model selection.

The complete-cpu-gate driver must execute, with the same bound worktree imports/interpreters and nonzero failure propagation:
1. Host interpreter -m ruff format --check .; -m ruff check .; -m mypy src scripts.
2. Host interpreter -m pytest -q -p no:cacheprovider tests/unit and then tests/integration, without deselection or historical-evidence skips. The new standalone script is also checked with ruff and parsed/executed by the explicit Python 3.12 interpreter; host mypy remains scoped as in scripts/validate.sh.
3. Host interpreter -m build --no-isolation --outdir TEMP/dist TEMP/project using a temporary copy of pyproject.toml, README.md, LICENSE and src/mostaza, as scripts/validate.sh does.
4. Host interpreter scripts/check_official.py --check --experiments E0 E1 --compiler-python OFFICIAL_PYTHON (existing script also builds with temporary output; ignored normal build caches are allowed, no tracked file mutation).
5. Host interpreter scripts/check_evidence.py --require-real-paired --cohort experiments/cohort.json --evidence-dir docs/implementation/evidence/mostaza-phase1-foundation, read-only historical validation.
6. Real active compile/toolset/executor/native-command witnesses and ZIP/notebook parity; the official packages remain unchanged. Python 3.12 runs the standalone CLI against the same deterministic fixture contract. Inspect Docker command construction and execute equivalent absolute /workspace/path-with-spaces fixtures locally; report that Docker and Kaggle themselves were not executed.
7. The five mandatory source-only snapshot benchmarks and synthetic/adversarial cases from search-code:AC-8; report cold/warm/refresh times, peak RSS with platform units normalized, database size, source/query hashes, Python version and reparse/graph counts. Measure actual child process peaks, not the parent driver RSS. No sampling of fewer snapshots or timeout-as-success.

Child commands are fixed by this proposal; the new driver is an implementation of this declared check, not permission to replace or weaken checks. Gate-generated durable outputs are limited to the declared evidence paths; temporary archives, notebook executions and benchmark caches live outside tracked product files. Source, specifications and frozen evidence are not mutated by checks.

## Declared evidence

- docs/implementation/evidence/2026-10-20-search-code/validation.json — exact checks/status and provenance, official exposure/execution/budget witnesses, Python compatibility and archive/notebook parity. No secrets, solution fields or bulky logs.
- docs/implementation/evidence/2026-10-20-search-code/benchmark.json — five source-only snapshot query hashes/locations, supported graph expectations, timing/memory/database size and incremental counters, with thresholds and local-environment limitations.

Reports contain validation facts, not workflow state. No workflow sidecar or generated contract declaration is needed. Plan continuity retains approvals/checkpoints/findings.

## Approval and closure

Approval covers this specification delta, all stage scope, numeric CPU thresholds, exact gate, evidence and Versioner commit/push of codex/search-code to origin plus publication of a PR targeting develop after a full successful gate and independent zero-finding PASS. No merge, deployment, Kaggle session/submission or additional model evaluation is included. The current request stops at this reviewable proposal; implementation requires explicit recorded approval. Only Orchestrator declares completion after Versioner closure.

<!-- SDD-CONTINUITY:START -->

```sdd-execution
{
  "version": 3,
  "id": "2026-10-20-search-code",
  "project": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness",
  "plan_path": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/docs/specs/plans/open/2026-10-20-search-code.md",
  "branch": "codex/search-code",
  "head": "1969aa509b6a161a159c79454e95100f6fba8b54",
  "definition": {
    "scope": "Implement search-code specification for the active submission only; preserve historical experiments and official runtime; deterministic CPU validation without inference or Kaggle operations.",
    "stages": [
      {
        "id": "stage-core",
        "level": "HIGH",
        "paths": [
          "submission/skills/search-code/scripts/search_code.py",
          "tests/unit/test_search_code.py"
        ],
        "depends": [],
        "items": [
          "core-cli",
          "incremental-graph"
        ],
        "satisfies": [
          "search-code:AC-2",
          "search-code:AC-3",
          "search-code:AC-4",
          "search-code:AC-5",
          "search-code:AC-6"
        ]
      },
      {
        "id": "stage-package",
        "level": "HIGH",
        "paths": [
          "src/mostaza/packaging.py",
          "tests/unit/test_packaging.py"
        ],
        "depends": [
          "stage-core"
        ],
        "items": [
          "skill-closure",
          "historical-compatibility"
        ],
        "satisfies": [
          "search-code:AC-7",
          "agent-retrieval:AC-5",
          "local-lmstudio-kaggle:AC-5"
        ]
      },
      {
        "id": "stage-activate",
        "level": "MEDIUM",
        "paths": [
          "submission/agent.yaml",
          "submission/prompts/baseline.md",
          "submission/skills/search-code/SKILL.md",
          "tests/integration/test_search_code_official.py"
        ],
        "depends": [
          "stage-package"
        ],
        "items": [
          "active-policy",
          "official-bootstrap"
        ],
        "satisfies": [
          "search-code:AC-1",
          "search-code:AC-2",
          "search-code:AC-7",
          "local-lmstudio-kaggle:AC-3"
        ]
      },
      {
        "id": "stage-validate",
        "level": "HIGH",
        "paths": [
          "scripts/check_search_code.py",
          "tests/unit/test_search_code_validation.py",
          "README.md",
          "notebooks/mostaza-phase2-preparation.ipynb",
          "tests/integration/test_phase2.py",
          "tests/integration/test_pcv01_cpu_contract.py"
        ],
        "depends": [
          "stage-activate",
          "stage-core"
        ],
        "items": [
          "cpu-evidence",
          "regression-delivery"
        ],
        "satisfies": [
          "search-code:AC-8"
        ]
      }
    ],
    "checks": [
      {
        "id": "core",
        "stage": "stage-core",
        "argv": [
          "/usr/bin/env",
          "PYTHONDONTWRITEBYTECODE=1",
          "PYTHONPATH=/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/src",
          "MOSTAZA_HISTORICAL_PHASE2_ROOT=/Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness",
          "/Users/diego/Documents/Desarrollo/Mostaza Dev/PyCharm Projects/Mostaza-Harness/.venv/bin/python",
          "-m",
          "pytest",
          "-q",
          "-p",
          "no:cacheprovider",
          "tests/unit/test_search_code.py"
        ],
        "timeout": 300,
        "basis": "search-code:AC-2/3/4/5/6 identity, conservative graph, atomic freshness, bounded JSON and path/cache boundaries"
      },
      {
        "id": "packaging",
        "stage": "stage-package",
        "argv": [
          "/usr/bin/env",
          "PYTHONDONTWRITEBYTECODE=1",
          "PYTHONPATH=/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/src",
          "MOSTAZA_HISTORICAL_PHASE2_ROOT=/Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness",
          "/Users/diego/Documents/Desarrollo/Mostaza Dev/PyCharm Projects/Mostaza-Harness/.venv/bin/python",
          "-m",
          "pytest",
          "-q",
          "-p",
          "no:cacheprovider",
          "tests/unit/test_packaging.py"
        ],
        "timeout": 300,
        "basis": "search-code:AC-7 and agent-retrieval:AC-5 allowlisted skill closure and frozen historical compatibility"
      },
      {
        "id": "official-execution",
        "stage": "stage-activate",
        "argv": [
          "/usr/bin/env",
          "PYTHONDONTWRITEBYTECODE=1",
          "PYTHONPATH=/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/src",
          "MOSTAZA_HISTORICAL_PHASE2_ROOT=/Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness",
          "/Users/diego/Documents/Desarrollo/Mostaza Dev/PyCharm Projects/Mostaza-Harness/.venv/bin/python",
          "-m",
          "pytest",
          "-q",
          "-p",
          "no:cacheprovider",
          "tests/integration/test_search_code_official.py"
        ],
        "timeout": 600,
        "basis": "search-code:AC-1/2/7 actual official skill executor and subsequent native run_command, editing freshness, delivery parity and budget preservation"
      },
      {
        "id": "complete-cpu-gate",
        "stage": "stage-validate",
        "argv": [
          "/usr/bin/env",
          "PYTHONDONTWRITEBYTECODE=1",
          "PYTHONPATH=/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/src",
          "MOSTAZA_HISTORICAL_PHASE2_ROOT=/Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness",
          "/Users/diego/Documents/Desarrollo/Mostaza Dev/PyCharm Projects/Mostaza-Harness/.venv/bin/python",
          "scripts/check_search_code.py",
          "--check",
          "--source-assets",
          "/Users/diego/Documents/Desarrollo/Mostaza Dev/PyCharm Projects/Mostaza-Harness",
          "--official-python",
          "/Users/diego/Documents/Desarrollo/Mostaza Dev/PyCharm Projects/Mostaza-Harness/.tools/official/bin/python",
          "--python312",
          "/Users/diego/.pyenv/versions/3.12.8/bin/python3.12",
          "--evidence-dir",
          "docs/implementation/evidence/2026-10-20-search-code"
        ],
        "timeout": 1800,
        "basis": "foundation:AC-4 and search-code:AC-8 complete formatting/lint/type/unit/integration/build/official/evidence checks plus five-snapshot CPU performance and Python 3.12 portability"
      }
    ],
    "spec_changes": {
      "files": [
        "docs/specs/README.md",
        "docs/specs/search-code.md",
        "docs/specs/agent-retrieval.md",
        "docs/specs/local-lmstudio-kaggle.md"
      ],
      "added": [
        "search-code:AC-1",
        "search-code:AC-2",
        "search-code:AC-3",
        "search-code:AC-4",
        "search-code:AC-5",
        "search-code:AC-6",
        "search-code:AC-7",
        "search-code:AC-8"
      ],
      "modified": [
        "agent-retrieval:AC-5",
        "local-lmstudio-kaggle:AC-3",
        "local-lmstudio-kaggle:AC-5"
      ],
      "removed": [],
      "restores": [],
      "justification": null
    },
    "evidence": [
      {
        "path": "docs/implementation/evidence/2026-10-20-search-code/validation.json",
        "stage": "stage-validate",
        "purpose": "Exact child check argv/status, interpreter and source provenance, official tool inventory, bootstrap/native execution and ZIP/notebook parity; no model execution."
      },
      {
        "path": "docs/implementation/evidence/2026-10-20-search-code/benchmark.json",
        "stage": "stage-validate",
        "purpose": "Source-only query provenance, real locations and graph expectations, per-snapshot cold/warm/refresh timing, peak RSS, DB size and reparse counters on five local snapshots."
      }
    ]
  },
  "baseline": {},
  "approval": {
    "digest": "3be8906a93c59332a9f2e5f399ca6f5605d50ede455b31bf401179547b377a73",
    "gate_digest": "351224b63e88caa3e872696125170c852da60c954ecd043a403573ab5ac1f03a",
    "evidence": "2026-10-20 user explicitly approved revised plan question: Sí, aprobar la excepción histórica y continuar SDD. Approval covers exact two historical verification tests binding original child cwd/scripts/imports/PYTHONPATH to verified restored original root/src, current candidate checks remaining current; all tests, negative controls, gate commands, specs, and push/PR to develop retained.",
    "publish": {
      "remote": "origin",
      "base": "develop"
    },
    "technical_revision": 18
  },
  "approvals": [
    {
      "digest": "1be5084ce9e6845488c57390f3114f9f8fc85c032b95052697f9336e43eb5fe2",
      "gate_digest": "351224b63e88caa3e872696125170c852da60c954ecd043a403573ab5ac1f03a",
      "evidence": "User 2026-10-20: Apruebo la especificación, el plan, el gate y el cierre con push y PR a develop. Continúa con la implementación, sin omitir pruebas ni reconstruir la evidencia histórica faltante.",
      "publish": {
        "remote": "origin",
        "base": "develop"
      }
    },
    {
      "technical_revision": 7,
      "reason": "Technical prerequisite review dispatch 7: phase2.HOST_MODULES embeds already-approved src/mostaza/packaging.py; existing test_phase2 and pipeline checks require current notebooks/mostaza-phase2-preparation.ipynb bytes to equal phase2.build_notebook(root). This path is clean and absent from baseline. Assign only that current unexecuted generated notebook to stage-validate regression-delivery (already pending; no checkpoint reopened). Implementer must call existing build_notebook(Path.cwd()) and write only its NOTEBOOK path, then check_notebook; never run scripts/prepare_phase2.py because it additionally rewrites historical evidence. No other notebook, generator, frozen experiment or evidence is authorized to change. Three ignored public scorer inputs are available unchanged in source resources/official/pcv01-access-20261014: sandbox/setup.py, docker/Dockerfile.sandbox, docker/Dockerfile.public; all bytes/sizes match tracked docs/implementation/evidence/mostaza-pcv01-access/public-sources.json and scorer_contract.PINS. They may be copied as original read-only public-source validation prerequisites to their identical ignored worktree paths, never executed, symlinked, indexed or altered; enforce exact three-file inventory and pins. Host missing typed dependencies dotenv, adk_submission.yaml_loader and swegemma.cli exist in source .tools/official/lib/python3.13/site-packages and .tools/harness/lib/python3.13/site-packages but not source .venv. No dependency installation, source-environment mutation, MYPYPATH/PYTHONPATH expansion, type-check suppression or gate modification is authorized by this revision. A diagnostic full-site MYPYPATH fails typing_extensions shadowing; alternate PYTHONPATH diagnostic was interrupted and establishes no PASS. The exact approved environment remains mandatory and its missing-import failure unresolved; changing that explicit environment requires material approval. Missing original historical checkout and phase1 packet remain external prerequisites with user no-reconstruction instruction unchanged. Scope/prose/specifications/checks/evidence/history remain byte/semantically unchanged; only technical stage-owned generated path added.",
      "digest": "3632fcafcb9dcc5f4cc167ca445499e0f1422a7f1c56dc4b2849cd256d9b8873"
    },
    {
      "technical_revision": 9,
      "reason": "Dispatch 9 technical prerequisite repair under actual user instruction 2026-10-20 recorded by external-authorize: resolve three dependencies and search local historical originals, no reconstruction/skipped checks. Raise stage-validate MEDIUM to HIGH for shared host-environment mutation/rollback risk; regression-delivery remains pending. Keep approved interpreter argv, PYTHONPATH, commands, specs, prose, evidence and source behavior unchanged. Verified source .venv has none of python-dotenv/adk-submission/swegemma; source .tools/official originals have python-dotenv1.2.4, adk-submission0.2.13, swegemma0.2.11. Source official environments are immutable. Narrow repair: use existing /Users/diego/.pyenv/versions/3.13.15/bin/python3.13 -m pip (26.2.1) --python /Users/diego/Documents/Desarrollo/Mostaza Dev/PyCharm Projects/Mostaza-Harness/.venv/bin/python install --no-deps --no-index --no-compile --no-cache-dir with exact local adk_submission0.2.13 and swegemma0.2.11 wheels from verified resources manifest, plus python_dotenv-1.2.4-py3-none-any.whl assembled in an ignored/private temporary directory solely from byte-identical verified cached wheel RECORD entries at source .tools/cache/archive-v0/yRI1HwvsBY5ysQ8n944SJ. All15 cached RECORD entries verified; RECORD SHA25618484783f2fe18fb4316b6f920c74e60d6a2e295ead668a6a30338cfa27bc158. Packaging that original dependency wheel is not historical evidence reconstruction. Before install verify exact expected missing names and no colliding package/dist-info/entrypoint files; capture environment distribution inventory and exact target files for reversible rollback, use official sandbox escalation for writes if necessary. Never upgrade unrelated packages, resolve transitive dependencies, add stubs, alter PYTHONPATH/MYPYPATH, modify official package bytes, or install pip into target. Verify installed source files/py.typed against wheel records and unchanged preexisting distributions, then retry unchanged mypy src scripts through approved interpreter/environment and full gate only after prerequisites change. Do not claim the minimal host type-discovery install supplies the full official inference dependency stack; official runtime stays separate. If extra missing dependencies or collisions emerge, report exact evidence for bounded review rather than broad install. Original archive discoveries may be inspected read-only and identities verified, but this revision does not authorize invented history/dirty plan bytes or checksum substitution. Preserve all historical blockers until Orchestrator verifies actual original-byte recovery within user authorization; no check may be skipped.",
      "digest": "b1490419d374ea29a7637d9e6c91dc207741e81a4ffa91eee6671a57c4eb6b81"
    },
    {
      "digest": "e702224183d6edf072a6649ec176c47fe53bd49b905258b8c1e8a25d3ef4e7ce",
      "gate_digest": "351224b63e88caa3e872696125170c852da60c954ecd043a403573ab5ac1f03a",
      "evidence": "2026-10-20 user explicitly approved revised plan question: Sí, aprobar la excepción histórica y continuar SDD. Approval covers exact two historical verification tests binding original child cwd/scripts/imports/PYTHONPATH to verified restored original root/src, current candidate checks remaining current; all tests, negative controls, gate commands, specs, and push/PR to develop retained.",
      "publish": {
        "remote": "origin",
        "base": "develop"
      }
    },
    {
      "technical_revision": 18,
      "reason": "Round2 AUD-004 existing AC4 repair: preserve explicit import provenance in SQLite bindings, distinguishing canonical bound module, import form, asname presence and loaded dotted-chain evidence; never infer explicit alias identity from string equality with package prefix. Separate direct import-target resolution from later module-attribute traversal. Canonical module names may identify imports, but disk presence alone never creates an attribute; walk only uniquely supported module bindings/package exports, preserving dynamic/wildcard/collision uncertainty and rejecting function containment as attributes. Support ordinary and same-prefix explicit aliases, unaliased dotted imports, explicit package reexports and relative imports without a Python execution framework. Guard cyclic reexports and lookup work with bounded per-query visited/depth state and existing deadlines/SQL indexes; no full graph RAM/dependency additions. If internal binding schema changes bump private cache schema/version and rebuild derived cache safely; public JSON/spec/gate unchanged. Core-owned two-file regression fixtures on Python3.12/3.13 must assert exact positive/negative calls and unresolved/incomplete behavior for unloaded child vs loaded child, same-prefix alias, ordinary alias, unaliased dotted import, explicit package reexport and package function/module collision, plus dependent refresh after import changes and all prior AUD001-003 regressions. Reopen both existing core items and both validation items; add direct stage-core dependency to stage-validate so runtime cannot dispatch report regeneration before the reopened core work despite intermediate stages remaining complete. All scopes/prose/spec/check argv/order/timeouts/bases/evidence/path ownership/history preserved. Auditor alone resolves findings; refreshed complete gate and independent complete audit required.",
      "digest": "3be8906a93c59332a9f2e5f399ca6f5605d50ede455b31bf401179547b377a73"
    }
  ],
  "normative_digest": "4bf94f5fa4f6731a3bcf74c2a2e52f1b257ec753509f6aaca5daf08644155f89",
  "normative_material_digest": "64e31478a118f60ae3cf0cf6fef50d0b230ca1cb6fa10c9eeb4b69442acf5582",
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
      "role": "planner",
      "stage": null,
      "status": "DONE",
      "review": null
    },
    {
      "id": 3,
      "role": "implementer-high",
      "stage": "stage-core",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 4,
      "role": "implementer-high",
      "stage": "stage-package",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 5,
      "role": "implementer-medium",
      "stage": "stage-activate",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 6,
      "role": "implementer-medium",
      "stage": "stage-validate",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 7,
      "role": "planner",
      "stage": "stage-validate",
      "status": "DONE",
      "review": 1
    },
    {
      "id": 8,
      "role": "implementer-medium",
      "stage": "stage-validate",
      "status": "DONE",
      "review": 1
    },
    {
      "id": 9,
      "role": "planner",
      "stage": "stage-validate",
      "status": "DONE",
      "review": 2
    },
    {
      "id": 10,
      "role": "implementer-high",
      "stage": "stage-validate",
      "status": "DONE",
      "review": 2
    },
    {
      "id": 11,
      "role": "planner",
      "stage": "stage-validate",
      "status": "DONE",
      "review": 3
    },
    {
      "id": 12,
      "role": "implementer-high",
      "stage": "stage-validate",
      "status": "DONE",
      "review": 3
    },
    {
      "id": 13,
      "role": "auditor",
      "stage": null,
      "status": "DONE",
      "review": null
    },
    {
      "id": 14,
      "role": "planner",
      "stage": null,
      "status": "DONE",
      "review": null
    },
    {
      "id": 15,
      "role": "implementer-high",
      "stage": "stage-core",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 16,
      "role": "implementer-high",
      "stage": "stage-validate",
      "status": "DONE",
      "review": 3
    },
    {
      "id": 17,
      "role": "auditor",
      "stage": null,
      "status": "DONE",
      "review": null
    },
    {
      "id": 18,
      "role": "planner",
      "stage": null,
      "status": "DONE",
      "review": null
    },
    {
      "id": 19,
      "role": "implementer-high",
      "stage": "stage-core",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 20,
      "role": "implementer-high",
      "stage": "stage-validate",
      "status": "DONE",
      "review": 3
    },
    {
      "id": 21,
      "role": "auditor",
      "stage": null,
      "status": "DONE",
      "review": null
    },
    {
      "id": 22,
      "role": "planner",
      "stage": null,
      "status": "DONE",
      "review": null
    },
    {
      "id": 23,
      "role": "implementer-high",
      "stage": "stage-core",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 24,
      "role": "implementer-high",
      "stage": "stage-validate",
      "status": "DONE",
      "review": 3
    },
    {
      "id": 25,
      "role": "auditor",
      "stage": null,
      "status": "DONE",
      "review": null
    },
    {
      "id": 26,
      "role": "planner",
      "stage": null,
      "status": "DONE",
      "review": null
    },
    {
      "id": 27,
      "role": "implementer-high",
      "stage": "stage-core",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 28,
      "role": "implementer-high",
      "stage": "stage-validate",
      "status": "DONE",
      "review": 3
    },
    {
      "id": 29,
      "role": "auditor",
      "stage": null,
      "status": "DONE",
      "review": null
    },
    {
      "id": 30,
      "role": "planner",
      "stage": null,
      "status": "DONE",
      "review": null
    },
    {
      "id": 31,
      "role": "implementer-high",
      "stage": "stage-core",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 32,
      "role": "implementer-high",
      "stage": "stage-validate",
      "status": "DONE",
      "review": 3
    },
    {
      "id": 33,
      "role": "auditor",
      "stage": null,
      "status": "DONE",
      "review": null
    },
    {
      "id": 34,
      "role": "planner",
      "stage": null,
      "status": "DONE",
      "review": null
    },
    {
      "id": 35,
      "role": "implementer-high",
      "stage": "stage-core",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 36,
      "role": "implementer-high",
      "stage": "stage-validate",
      "status": "DONE",
      "review": 3
    },
    {
      "id": 37,
      "role": "auditor",
      "stage": null,
      "status": "DONE",
      "review": null
    },
    {
      "id": 38,
      "role": "planner",
      "stage": null,
      "status": "DONE",
      "review": null
    },
    {
      "id": 39,
      "role": "implementer-high",
      "stage": "stage-core",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 40,
      "role": "implementer-high",
      "stage": "stage-validate",
      "status": "DONE",
      "review": 3
    },
    {
      "id": 41,
      "role": "auditor",
      "stage": null,
      "status": "DONE",
      "review": null
    },
    {
      "id": 42,
      "role": "planner",
      "stage": null,
      "status": "DONE",
      "review": null
    },
    {
      "id": 43,
      "role": "implementer-high",
      "stage": "stage-core",
      "status": "DONE",
      "review": 0
    },
    {
      "id": 44,
      "role": "implementer-high",
      "stage": "stage-validate",
      "status": "DONE",
      "review": 3
    },
    {
      "id": 45,
      "role": "auditor",
      "stage": null,
      "status": "DONE",
      "review": null
    },
    {
      "id": 46,
      "role": "versioner",
      "stage": null,
      "status": "INTERRUPTED",
      "review": null
    },
    {
      "id": 47,
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
        "value": "494bdcce085340bcbff5e1323dcd6876fecc502b4ed47ad63195041857f4e8b1"
      },
      "approval_digest": "e702224183d6edf072a6649ec176c47fe53bd49b905258b8c1e8a25d3ef4e7ce",
      "dispatch": 13,
      "acceptance": [
        {
          "id": "search-code:AC-1",
          "status": "SATISFIED",
          "evidence": "Active configuration exposes six native tools and one official skill; official witness inventories four helpers. Historical experiment files and registry remain preserved."
        },
        {
          "id": "search-code:AC-2",
          "status": "SATISFIED",
          "evidence": "Single standard-library implementation; actual official subprocess bootstrap, persistent-byte identity, resource removal, subsequent native execution and Python 3.12 execution are evidenced."
        },
        {
          "id": "search-code:AC-3",
          "status": "UNMET",
          "evidence": "AUD-001 reproduces prohibited-directory ingestion on both supported interpreters."
        },
        {
          "id": "search-code:AC-4",
          "status": "UNMET",
          "evidence": "AUD-002 and AUD-003 reproduce fabricated graph edges on both supported interpreters."
        },
        {
          "id": "search-code:AC-5",
          "status": "SATISFIED",
          "evidence": "Reviewed transactional generations, content scans, dependent-edge rebuilding, bounded locking and recovery. Independent focused suites passed freshness, interruption and concurrency fixtures."
        },
        {
          "id": "search-code:AC-6",
          "status": "SATISFIED",
          "evidence": "Reviewed JSON serialization, whole-entry truncation, output/count limits, cooperative deadline and explicit capability/indexing failures; focused tests passed."
        },
        {
          "id": "search-code:AC-7",
          "status": "SATISFIED",
          "evidence": "Reviewed exact skill allowlist, secure reads, deterministic archive/notebook parity, official execution and unchanged model/budgets. Independent packaging tests passed."
        },
        {
          "id": "search-code:AC-8",
          "status": "SATISFIED",
          "evidence": "All five snapshot hashes match original assets; measured CPU/RSS/database limits pass with warm zero-reparse and single-file refresh witnesses. Recorded full gate has 506 unit and 123 integration passes with zero skips; independent focused rerun passed 156 tests. Additional correctness defects are recorded under AC-3/AC-4."
        },
        {
          "id": "agent-retrieval:AC-5",
          "status": "SATISFIED",
          "evidence": "Frozen E0/E1 closure/hash regression tests passed independently; historical native tools remain available."
        },
        {
          "id": "local-lmstudio-kaggle:AC-3",
          "status": "SATISFIED",
          "evidence": "Active imports bind to this worktree. Approved historical children bind to authenticated original sources; historical HEAD and dirty-plan hash independently match their pins."
        },
        {
          "id": "local-lmstudio-kaggle:AC-5",
          "status": "SATISFIED",
          "evidence": "Shared collection path carries exactly the approved active closure; official compiler and ZIP/notebook parity evidence are consistent with current bytes."
        }
      ]
    },
    {
      "round": 2,
      "verdict": "FIX_REQUIRED",
      "candidate": {
        "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
        "value": "bbf88910d6d4a5374bb39d8f5deabfbcca8be37bbda87fc4c1a9248a79f5ab87"
      },
      "approval_digest": "e702224183d6edf072a6649ec176c47fe53bd49b905258b8c1e8a25d3ef4e7ce",
      "dispatch": 17,
      "acceptance": [
        {
          "id": "search-code:AC-1",
          "status": "SATISFIED",
          "evidence": "Actual pinned compiler/toolset/executor tests passed: six native tools plus four inventoried helpers, unchanged budgets and zero inference. Historical configuration closures remain unchanged."
        },
        {
          "id": "search-code:AC-2",
          "status": "SATISFIED",
          "evidence": "Real Python 3.12/3.13 bootstrap and subsequent commands passed. Official execution verifies exact persistent CLI bytes, transient-resource cleanup, private external caches and clean submitted patches."
        },
        {
          "id": "search-code:AC-3",
          "status": "SATISFIED",
          "evidence": "Reserved directory components and case variants are excluded on both interpreters, including rename invalidation. Reviewed literal FTS queries, source boundaries, symbol identities, locations and capability failure handling."
        },
        {
          "id": "search-code:AC-4",
          "status": "UNMET",
          "evidence": "Prior wildcard, nested-attribute and pattern-capture regressions pass. Independent import-binding fixtures expose fabricated unloaded-module calls and missed valid aliases, detailed in AUD-004."
        },
        {
          "id": "search-code:AC-5",
          "status": "SATISFIED",
          "evidence": "Reviewed content hashing, transactional generations, bounded locking, rollback/recovery and dependent resolution. Equal-stat edits, deletion/rename, native edits and concurrent-change tests passed."
        },
        {
          "id": "search-code:AC-6",
          "status": "SATISFIED",
          "evidence": "Reviewed argument, deadline, file/source and graph bounds. Tests passed for bounded valid JSON, empty handled stderr, truncation, ambiguity, incomplete indexing and unavailable FTS5."
        },
        {
          "id": "search-code:AC-7",
          "status": "SATISFIED",
          "evidence": "Packaging adversarial tests and real official execution passed. Independently compared all seven historical configuration closures with initial HEAD and verified current generated notebook source parity."
        },
        {
          "id": "search-code:AC-8",
          "status": "SATISFIED",
          "evidence": "Inspected unchanged full-gate evidence: 514 unit and 123 integration passes, zero skips. Independently reran 173 focused/historical tests and real paired-evidence verification. Recomputed all five snapshot/source/query hashes and expected locations; measured limits and incremental counters pass. Docker/Kaggle limitations remain explicit."
        },
        {
          "id": "agent-retrieval:AC-5",
          "status": "SATISFIED",
          "evidence": "Frozen E0/E1 closure/archive regressions and pinned official compilation passed; historical nine-tool registry compatibility remains intact."
        },
        {
          "id": "local-lmstudio-kaggle:AC-3",
          "status": "SATISFIED",
          "evidence": "Active checks bind current worktree imports. Approved historical children bind authenticated original sources; independent historical tests passed with exact HEAD, dirty-plan hash, real compiler/resource/trace/readiness recomputation and negative controls."
        },
        {
          "id": "local-lmstudio-kaggle:AC-5",
          "status": "SATISFIED",
          "evidence": "Shared collection produces precisely the approved active closure; real compiler acceptance and deterministic ZIP/generated-delivery-notebook byte parity passed."
        }
      ]
    },
    {
      "round": 3,
      "verdict": "FIX_REQUIRED",
      "candidate": {
        "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
        "value": "ef310006ac8c380c8deae7a412feb4a559a15d2c1dead62823a9f6daeb7ba590"
      },
      "approval_digest": "3be8906a93c59332a9f2e5f399ca6f5605d50ede455b31bf401179547b377a73",
      "dispatch": 21,
      "acceptance": [
        {
          "id": "search-code:AC-1",
          "status": "SATISFIED",
          "evidence": "Actual official execution passed: six native tools, four helpers, unchanged budgets and zero inference; historical closures remain identical."
        },
        {
          "id": "search-code:AC-2",
          "status": "SATISFIED",
          "evidence": "Real bootstrap and subsequent native execution passed, including exact persistent bytes, transient cleanup, external private caches and actual Python 3.12/3.13 execution."
        },
        {
          "id": "search-code:AC-3",
          "status": "SATISFIED",
          "evidence": "Reviewed source boundaries, literal lexical queries, identities and locations; reserved-directory, symlink, exclusion and capability regressions passed."
        },
        {
          "id": "search-code:AC-4",
          "status": "UNMET",
          "evidence": "Prior wildcard, nested-attribute and pattern-capture regressions pass. Independent package-collision fixtures still fabricate complete-looking call edges, as detailed in AUD-004."
        },
        {
          "id": "search-code:AC-5",
          "status": "SATISFIED",
          "evidence": "Reviewed transactional generations, content hashing, dependent resolution, bounded locking and recovery; equal-stat edits, native edits and concurrent-change tests passed."
        },
        {
          "id": "search-code:AC-6",
          "status": "SATISFIED",
          "evidence": "Reviewed deadlines, indexing/graph bounds and serialization; tests passed for bounded JSON, handled stderr, truncation, ambiguity and explicit incomplete/unavailable results."
        },
        {
          "id": "search-code:AC-7",
          "status": "SATISFIED",
          "evidence": "Adversarial packaging and actual compiler/executor tests passed; deterministic ZIP/notebook parity verified, and all seven historical configuration/archive variants independently match initial source."
        },
        {
          "id": "search-code:AC-8",
          "status": "SATISFIED",
          "evidence": "Recorded full gate passed 558 unit and 123 integration tests with zero skips. Independently ran 217 focused/historical tests and real paired-evidence verification; recomputed all five snapshot/source/query/edit hashes and reviewed measured limits and provenance. Graph correctness defect is assigned to AC-4."
        },
        {
          "id": "agent-retrieval:AC-5",
          "status": "SATISFIED",
          "evidence": "Frozen E0/E1 archives and all historical variants retain original bytes; native registry compatibility and real official compilation remain intact."
        },
        {
          "id": "local-lmstudio-kaggle:AC-3",
          "status": "SATISFIED",
          "evidence": "Active imports bind to the current worktree. Approved historical tests passed against authenticated original sources, including exact HEAD/dirty-plan pins, real verification and negative controls."
        },
        {
          "id": "local-lmstudio-kaggle:AC-5",
          "status": "SATISFIED",
          "evidence": "Shared collection delivers the exact approved active closure; model preservation, official acceptance and generated delivery-notebook archive parity passed."
        }
      ]
    },
    {
      "round": 4,
      "verdict": "FIX_REQUIRED",
      "candidate": {
        "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
        "value": "979e6a1047fc245b2e8c49781cb07df3cd40d3076a6966d8b2d8ea9e28122007"
      },
      "approval_digest": "3be8906a93c59332a9f2e5f399ca6f5605d50ede455b31bf401179547b377a73",
      "dispatch": 25,
      "acceptance": [
        {
          "id": "search-code:AC-1",
          "status": "SATISFIED",
          "evidence": "Actual official execution passed: six native tools, four helpers, unchanged budgets and zero inference. Historical sources and tool compatibility remain preserved."
        },
        {
          "id": "search-code:AC-2",
          "status": "SATISFIED",
          "evidence": "Actual Python 3.12/3.13 bootstrap and subsequent execution passed, including exact persistent bytes, transient cleanup, private external caches and clean submitted patches."
        },
        {
          "id": "search-code:AC-3",
          "status": "SATISFIED",
          "evidence": "Reviewed literal lexical queries, source boundaries, exclusions, symbol identities and locations. Prior prohibited-directory and capability regressions passed."
        },
        {
          "id": "search-code:AC-4",
          "status": "UNMET",
          "evidence": "Prior wildcard, attribute, capture and alias regressions pass; independently reproduced direct lexical package-collision bypass remains under AUD-004."
        },
        {
          "id": "search-code:AC-5",
          "status": "SATISFIED",
          "evidence": "Reviewed content fingerprints, transactional generations, dependent rebuilding, bounded locking and recovery. Equal-stat edits, native edits and concurrent-change tests passed."
        },
        {
          "id": "search-code:AC-6",
          "status": "SATISFIED",
          "evidence": "Reviewed cooperative deadlines, indexing/graph bounds and whole-entry JSON truncation. Handled failures, ambiguity, incomplete indexing and unavailable capability tests passed."
        },
        {
          "id": "search-code:AC-7",
          "status": "SATISFIED",
          "evidence": "Adversarial packaging, actual official execution and deterministic ZIP/notebook parity passed. All seven historical closures independently match initial HEAD; embedded packaging source matches current bytes."
        },
        {
          "id": "search-code:AC-8",
          "status": "SATISFIED",
          "evidence": "Recorded gate passed 662 unit and 123 integration tests with zero skips. Independently ran 321 focused/historical tests and real paired-evidence verification. Verified all five archive/source/query/edit hashes, measured bounds and current CLI provenance. Graph defect is assigned to AC-4."
        },
        {
          "id": "agent-retrieval:AC-5",
          "status": "SATISFIED",
          "evidence": "Historical closure/archive regressions and official compilation passed; all seven historical configurations retain original closure bytes."
        },
        {
          "id": "local-lmstudio-kaggle:AC-3",
          "status": "SATISFIED",
          "evidence": "Active imports bind current worktree. Approved historical children passed against original sources, including real PCV controls, readiness recomputation and negative controls. Historical HEAD, status and closed-plan hash match pins."
        },
        {
          "id": "local-lmstudio-kaggle:AC-5",
          "status": "SATISFIED",
          "evidence": "Shared collection delivers the approved active closure; model preservation, official acceptance and generated delivery-notebook archive parity passed."
        }
      ]
    },
    {
      "round": 5,
      "verdict": "FIX_REQUIRED",
      "candidate": {
        "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
        "value": "9aa4ed93a77c9a2649cd90635acc898a9f37ba5950774bc66ffd33ab5b1c090e"
      },
      "approval_digest": "3be8906a93c59332a9f2e5f399ca6f5605d50ede455b31bf401179547b377a73",
      "dispatch": 29,
      "acceptance": [
        {
          "id": "search-code:AC-1",
          "status": "SATISFIED",
          "evidence": "Actual official execution passed: six native tools, four inventoried helpers, unchanged budgets and zero inference. Historical sources and registry compatibility remain preserved."
        },
        {
          "id": "search-code:AC-2",
          "status": "SATISFIED",
          "evidence": "Actual Python 3.12/3.13 bootstrap and subsequent execution passed, including persistent-byte identity, transient cleanup, private external caches and clean patches."
        },
        {
          "id": "search-code:AC-3",
          "status": "SATISFIED",
          "evidence": "Reviewed literal lexical queries, source boundaries, exclusions, symbol identities and locations; exclusion, symlink, ambiguity and capability regressions passed."
        },
        {
          "id": "search-code:AC-4",
          "status": "UNMET",
          "evidence": "AUD-004 package-binding regressions are corrected. Independent actual Python 3.12/3.13 fixtures demonstrate fabricated edges from module-attribute mutations, comprehension captures and global/nonlocal writes: AUD-005–AUD-007."
        },
        {
          "id": "search-code:AC-5",
          "status": "SATISFIED",
          "evidence": "Reviewed content fingerprints, transactional generations, dependent rebuilding, bounded locking and recovery; equal-stat, native-edit, interruption and concurrent-change tests passed."
        },
        {
          "id": "search-code:AC-6",
          "status": "SATISFIED",
          "evidence": "Reviewed cooperative deadlines, indexing/graph bounds and whole-entry JSON truncation. Bounded output, handled stderr, ambiguity, incomplete indexing and unavailable-capability tests passed."
        },
        {
          "id": "search-code:AC-7",
          "status": "SATISFIED",
          "evidence": "Adversarial packaging, actual official execution and ZIP/notebook parity passed. Independently verified all seven historical closures against initial HEAD and current notebook embedded payload/hash parity."
        },
        {
          "id": "search-code:AC-8",
          "status": "SATISFIED",
          "evidence": "Recorded gate passed 694 unit and 123 integration tests with zero skips. Independently ran 353 focused/historical tests and real paired-evidence verification. Recomputed all five archive/source/query/edit/launcher hashes; measured limits and current CLI provenance match. Graph defects are assigned to AC-4."
        },
        {
          "id": "agent-retrieval:AC-5",
          "status": "SATISFIED",
          "evidence": "Historical closure/archive regressions and official compilation passed; all seven historical configurations retain initial closure bytes."
        },
        {
          "id": "local-lmstudio-kaggle:AC-3",
          "status": "SATISFIED",
          "evidence": "Active imports bind the current worktree. Approved historical children passed original-source verification, real PCV controls and readiness negative controls; historical HEAD/status/closed-plan hash match pins."
        },
        {
          "id": "local-lmstudio-kaggle:AC-5",
          "status": "SATISFIED",
          "evidence": "Shared collection delivers the approved active closure; model preservation, official acceptance and generated delivery-notebook byte parity passed."
        }
      ]
    },
    {
      "round": 6,
      "verdict": "FIX_REQUIRED",
      "candidate": {
        "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
        "value": "35d0e7558ef90b1a339104a5c03f44c85a2350e5b522b8ca03a89d6cfd376c09"
      },
      "approval_digest": "3be8906a93c59332a9f2e5f399ca6f5605d50ede455b31bf401179547b377a73",
      "dispatch": 33,
      "acceptance": [
        {
          "id": "search-code:AC-1",
          "status": "SATISFIED",
          "evidence": "Actual official execution passed: six native tools, four helpers, unchanged budgets and zero inference; historical sources remain unchanged."
        },
        {
          "id": "search-code:AC-2",
          "status": "SATISFIED",
          "evidence": "Real bootstrap and subsequent execution passed on both interpreters, including persistent-byte identity, transient cleanup, private caches and clean patches."
        },
        {
          "id": "search-code:AC-3",
          "status": "SATISFIED",
          "evidence": "Reviewed literal queries, source boundaries, exclusions, symbol identities and locations; focused exclusion, symlink, ambiguity and capability tests passed."
        },
        {
          "id": "search-code:AC-4",
          "status": "UNMET",
          "evidence": "Mutation provenance fixes resolve AUD-005–007; independent generic-binding fixtures establish AUD-008."
        },
        {
          "id": "search-code:AC-5",
          "status": "SATISFIED",
          "evidence": "Reviewed transactional generations, fingerprints, dependent rebuilding, bounded locking and recovery; freshness, mutation removal/restoration and concurrency tests passed."
        },
        {
          "id": "search-code:AC-6",
          "status": "SATISFIED",
          "evidence": "Reviewed deadlines, indexing/graph bounds and whole-entry serialization; bounded JSON, handled stderr and incomplete/unavailable responses passed."
        },
        {
          "id": "search-code:AC-7",
          "status": "SATISFIED",
          "evidence": "Adversarial packaging, actual official execution and ZIP/notebook parity passed. Seven historical closures match the original HEAD packager; notebook embeds current packaging bytes."
        },
        {
          "id": "search-code:AC-8",
          "status": "SATISFIED",
          "evidence": "Recorded full gate passed 826 unit and 123 integration tests with zero skips. Independent expanded suite passed 485 tests and real paired-evidence verification. Verified both reports and all five archive/source/query/edit/launcher hashes; measured limits pass. Docker/Kaggle remain NOT_RUN."
        },
        {
          "id": "agent-retrieval:AC-5",
          "status": "SATISFIED",
          "evidence": "Historical archive regressions and official compilation passed; all seven closures and historical experiment files retain original bytes."
        },
        {
          "id": "local-lmstudio-kaggle:AC-3",
          "status": "SATISFIED",
          "evidence": "Current imports remain worktree-bound. Approved historical children passed real verification and negative controls; original HEAD, sole dirty-plan identity and pinned plan hash match."
        },
        {
          "id": "local-lmstudio-kaggle:AC-5",
          "status": "SATISFIED",
          "evidence": "Shared collection delivers the approved active closure; unchanged model, official acceptance and generated delivery-notebook parity passed."
        }
      ]
    },
    {
      "round": 7,
      "verdict": "FIX_REQUIRED",
      "candidate": {
        "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
        "value": "2e5943bc34bba67124279f48287c3b260c590a81bb3e0902d72e4436006987b3"
      },
      "approval_digest": "3be8906a93c59332a9f2e5f399ca6f5605d50ede455b31bf401179547b377a73",
      "dispatch": 37,
      "acceptance": [
        {
          "id": "search-code:AC-1",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/tests/integration/test_search_code_official.py: independent execution passed; six native tools, four official helpers, unchanged budgets and zero inference."
        },
        {
          "id": "search-code:AC-2",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/tests/unit/test_search_code.py: both real interpreters passed bootstrap persistence, source identity, cache isolation and security checks."
        },
        {
          "id": "search-code:AC-3",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/submission/skills/search-code/scripts/search_code.py: reviewed literal FTS queries, source exclusions, safe traversal, symbol identities and real locations; independent regressions passed."
        },
        {
          "id": "search-code:AC-4",
          "status": "UNMET",
          "evidence": "AUD-009 and AUD-010 independently reproduce fabricated call edges on Python 3.12 and 3.13. AUD-008 type-parameter blocking and its regression coverage passed."
        },
        {
          "id": "search-code:AC-5",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/tests/unit/test_search_code.py: independent fingerprint, refresh, dependent-invalidation, rollback, locking and recovery checks passed."
        },
        {
          "id": "search-code:AC-6",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/tests/unit/test_search_code.py: bounded JSON, truncation, deadlines, graph limits and handled-failure checks passed."
        },
        {
          "id": "search-code:AC-7",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/tests/unit/test_packaging.py: 96 independent packaging tests passed; official integration confirmed exact delivery/notebook parity and budget enforcement."
        },
        {
          "id": "search-code:AC-8",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/docs/implementation/evidence/2026-10-20-search-code/benchmark.json: independent isolated remeasurement matched all five snapshots' hashes and 15 query locations; maximum cold 3.515s, warm 0.837s, refresh 2.222s and RSS 127909888 bytes. Both synthetic interpreters passed. Independent test batteries passed 553 retrieval/package/validation/official tests and six historical tests. Initial concurrent-load warm measurement exceeded 3s; isolated repeat passed. Docker/Kaggle remain NOT_RUN."
        },
        {
          "id": "agent-retrieval:AC-5",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/tests/unit/test_packaging.py: frozen E0/E1 archive hashes, historical registry compatibility and official compilation passed."
        },
        {
          "id": "local-lmstudio-kaggle:AC-3",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/tests/integration/test_phase2.py: independent historical verification and tamper rejection passed; active checks retain current-worktree imports."
        },
        {
          "id": "local-lmstudio-kaggle:AC-5",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/tests/integration/test_search_code_official.py: same-source collection, exact ZIP/notebook bytes and real official compiler/executor checks passed."
        }
      ]
    },
    {
      "round": 8,
      "verdict": "FIX_REQUIRED",
      "candidate": {
        "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
        "value": "ce2072317c6e4adc1c18c9eac81f1b433f242ea3ac87b3a45185b76f6ab7c227"
      },
      "approval_digest": "3be8906a93c59332a9f2e5f399ca6f5605d50ede455b31bf401179547b377a73",
      "dispatch": 41,
      "acceptance": [
        {
          "id": "search-code:AC-1",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/tests/integration/test_search_code_official.py: independent execution verified six native tools, four official helpers, unchanged budgets and zero inference."
        },
        {
          "id": "search-code:AC-2",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/tests/unit/test_search_code.py: independent both-interpreter tests passed bootstrap persistence, exact source bytes, parser-specific cache identity and isolation."
        },
        {
          "id": "search-code:AC-3",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/submission/skills/search-code/scripts/search_code.py: reviewed literal FTS queries, exclusions, safe traversal, symbol identities and locations; independent retrieval regressions passed."
        },
        {
          "id": "search-code:AC-4",
          "status": "UNMET",
          "evidence": "AUD-011 independently demonstrates fabricated private-name call edges on both interpreters. AUD-009 decorator eligibility and AUD-010 implicit class/cell bindings passed independent fixtures and regression tests."
        },
        {
          "id": "search-code:AC-5",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/tests/unit/test_search_code.py: independent content-fingerprint, dependent-refresh, rollback, locking and recovery tests passed."
        },
        {
          "id": "search-code:AC-6",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/tests/unit/test_search_code.py: independent bounded JSON, truncation, deadlines, graph limits and handled-failure tests passed."
        },
        {
          "id": "search-code:AC-7",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/tests/unit/test_packaging.py: independent packaging tests passed; official integration verified exact ZIP/notebook delivery, narrow closure and budget enforcement."
        },
        {
          "id": "search-code:AC-8",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/docs/implementation/evidence/2026-10-20-search-code/benchmark.json: isolated independent remeasurement matched all five snapshots' hashes and 15 exact query locations. Maximum cold 3.263s, warm 1.732s, refresh 2.203s, child RSS 125304832 bytes and database 72429568 bytes; both synthetic interpreters passed. Independent batteries passed 672 focused tests and six historical tests. Retained full-gate evidence reports 1019 unit and 123 integration passes with zero skips. Docker/Kaggle remain NOT_RUN."
        },
        {
          "id": "agent-retrieval:AC-5",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/tests/unit/test_packaging.py: frozen E0/E1 archive hashes, historical native registry compatibility and official compilation passed."
        },
        {
          "id": "local-lmstudio-kaggle:AC-3",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/tests/integration/test_phase2.py: independent authenticated historical verification and unmocked operator-path rejection passed; active checks retain current-worktree imports."
        },
        {
          "id": "local-lmstudio-kaggle:AC-5",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/tests/integration/test_search_code_official.py: independent same-source collection, exact delivery bytes and real official compiler/executor checks passed."
        }
      ]
    },
    {
      "round": 9,
      "verdict": "PASS",
      "candidate": {
        "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
        "value": "bf2aa6ae353d5e654c5f5a442b4ac5f1918b06c0387cea75c1bbe55c80d7b909"
      },
      "approval_digest": "3be8906a93c59332a9f2e5f399ca6f5605d50ede455b31bf401179547b377a73",
      "dispatch": 45,
      "files": {
        "README.md": [
          "file",
          420,
          "47f3d16acc0038cf489219d8c4cecf3a1e7252385b504a25a4e7490db5cd039b"
        ],
        "docs/implementation/evidence/2026-10-20-search-code/benchmark.json": [
          "file",
          420,
          "27331f5b59619f7ae3c0a52adf3f6e74f6f3d6308886828cfa1957e2000d5abc"
        ],
        "docs/implementation/evidence/2026-10-20-search-code/validation.json": [
          "file",
          420,
          "c81f071aa707a570203c4a899a65759a7c251cb327b3b6736030984d25959a72"
        ],
        "docs/specs/README.md": [
          "file",
          420,
          "d7f6cde195a944d287929b234af2a6012b49211c39aa515720a166942d2af818"
        ],
        "docs/specs/agent-retrieval.md": [
          "file",
          420,
          "48710df116fc2e3acfbde3e0a8f1cf0584a7cfa199193da776ecc91f9decbec6"
        ],
        "docs/specs/local-lmstudio-kaggle.md": [
          "file",
          420,
          "7ef9fbd773c681ece1aea838aee649869abfdb569749af040aa18ae8534bfcac"
        ],
        "docs/specs/search-code.md": [
          "file",
          420,
          "f80c02356395f83f0e8f08c35d32c8fee1f81c7ab8b98a21febe7675e153b8d1"
        ],
        "notebooks/mostaza-phase2-preparation.ipynb": [
          "file",
          420,
          "fca095a65347daa8a1c8f42d4f0dd1160eae54b3735b2d3429d92e622c4723a1"
        ],
        "scripts/check_search_code.py": [
          "file",
          420,
          "41af4b9899e2a1bfefee39ad19411196236aa82f9efc90beaf9ba262032caf1a"
        ],
        "src/mostaza/packaging.py": [
          "file",
          420,
          "55a695e51f2e01bcd30f238bb6681721f168a7b4886ca43765957940f065116a"
        ],
        "submission/agent.yaml": [
          "file",
          420,
          "4ed5c70aa6b7e3a8fae65858ef1ac25900ffd5779f8e8b6d110d7c32e3f267e8"
        ],
        "submission/prompts/baseline.md": [
          "file",
          420,
          "4e8fb458276547aedc607f1fdc5b41b90751a58aa0aa8bbbadef8f453d000295"
        ],
        "submission/skills/search-code/SKILL.md": [
          "file",
          420,
          "aa3dc1cdd08e99b27acb44ea90085969a2f403acdee5e2a5dedc2eee3d156e3e"
        ],
        "submission/skills/search-code/scripts/search_code.py": [
          "file",
          420,
          "0d59569235517dc64f88d55cceaee11897c0b9a2a7a32941b66216a74c7a3367"
        ],
        "tests/integration/test_pcv01_cpu_contract.py": [
          "file",
          420,
          "a9e0b29483253e0f3ab1989328c8c8c264acb7701a4d5e62dbff8397e5d1c29d"
        ],
        "tests/integration/test_phase2.py": [
          "file",
          420,
          "266063e65359d02b5f3092d8f0f928450b90adbe4e069a7e3a5dfea50e1d1377"
        ],
        "tests/integration/test_search_code_official.py": [
          "file",
          420,
          "35a4e476b96fe35095f47bcae7463cf1a956b9f91bfac77bcb7cb61eafc77734"
        ],
        "tests/unit/test_packaging.py": [
          "file",
          420,
          "21831c52bd7a63a8819c1d6989db31c19cf0fe5578c34199d733746847483968"
        ],
        "tests/unit/test_search_code.py": [
          "file",
          420,
          "4d4818a8ab79da796343f7b0b124cab8b66f5b93ba77f86d907190440c934bd0"
        ],
        "tests/unit/test_search_code_validation.py": [
          "file",
          420,
          "926ccea525b458d2e8bd67e2fcd65d1fcd4d1177be5ed1d12e954575a8fe1ab5"
        ]
      },
      "git_entries": {
        "README.md": [
          "100644",
          "ba6cf897d27e0491c0a27758c9f34d32b7402c8d"
        ],
        "docs/implementation/evidence/2026-10-20-search-code/benchmark.json": [
          "100644",
          "7e0b64755c3cb6ee15bd8a8b46d337570bde385e"
        ],
        "docs/implementation/evidence/2026-10-20-search-code/validation.json": [
          "100644",
          "5f4c1b02356e534a9701a077f3818a9733f06a31"
        ],
        "docs/specs/README.md": [
          "100644",
          "dd8c87f7c5942387ac609e28aa15073613045dcb"
        ],
        "docs/specs/agent-retrieval.md": [
          "100644",
          "21ec67f582b70861eefa54674200c9f3fb9dc931"
        ],
        "docs/specs/local-lmstudio-kaggle.md": [
          "100644",
          "130bf1a97dd2db79c5d1b1396b15ceb51f801901"
        ],
        "docs/specs/search-code.md": [
          "100644",
          "d7163a38c692215ec1b89bfac8b6b121ac405223"
        ],
        "notebooks/mostaza-phase2-preparation.ipynb": [
          "100644",
          "5ff75648685f38e333feec0e657a3443fa90c481"
        ],
        "scripts/check_search_code.py": [
          "100644",
          "c57ffc2473f8cb2585f290563a5295131bd0e97f"
        ],
        "src/mostaza/packaging.py": [
          "100644",
          "15fd1d13f52e77ce7f49ead0283000162924492f"
        ],
        "submission/agent.yaml": [
          "100644",
          "c08639aeba951630fa4630aad10a5bfed8615eba"
        ],
        "submission/prompts/baseline.md": [
          "100644",
          "a5e300117fa9d1b02b5e8832a8bb5037972db01e"
        ],
        "submission/skills/search-code/SKILL.md": [
          "100644",
          "1d64c5202fcce94e93924e18fb331613a30c03bd"
        ],
        "submission/skills/search-code/scripts/search_code.py": [
          "100644",
          "3f35563153538cccbd1664188a9b8da1e61fd939"
        ],
        "tests/integration/test_pcv01_cpu_contract.py": [
          "100644",
          "b27bce00e2e1da4c8a727b2ed740c46c09b7e960"
        ],
        "tests/integration/test_phase2.py": [
          "100644",
          "de0037825cd78a03afe58bedfe1be7ade8de0a33"
        ],
        "tests/integration/test_search_code_official.py": [
          "100644",
          "153119d5841c941190527cc82ceaa407c1719eaf"
        ],
        "tests/unit/test_packaging.py": [
          "100644",
          "b2e437dce3fb68018c6e48438fcd504763a44f6b"
        ],
        "tests/unit/test_search_code.py": [
          "100644",
          "30ae117e488e0ac5d69194df65c6402e03b6f570"
        ],
        "tests/unit/test_search_code_validation.py": [
          "100644",
          "ef885f53303f21ece140ea9b0242b32c20ad41bc"
        ]
      },
      "acceptance": [
        {
          "id": "search-code:AC-1",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/submission/agent.yaml: six native tools and one skill; actual official execution inventories four helpers and preserves historical compatibility."
        },
        {
          "id": "search-code:AC-2",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/tests/integration/test_search_code_official.py: real compiler/toolset/executor, persistent exact-byte bootstrap, transient cleanup, workspace isolation and actual Python 3.12 execution passed."
        },
        {
          "id": "search-code:AC-3",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/tests/unit/test_search_code.py: literal lexical retrieval, exact locations, unique identities, exclusions, symlink boundaries, ambiguity and unavailable-FTS5 handling passed."
        },
        {
          "id": "search-code:AC-4",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/submission/skills/search-code/scripts/search_code.py: complete resolver reviewed. Both-interpreter graph regressions passed. Independent AUD-011 reproduction resolves only the canonical mangled target, or returns unresolved/incomplete when absent."
        },
        {
          "id": "search-code:AC-5",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/tests/unit/test_search_code.py: content-based refresh, dependent invalidation, equal-stat edits, add/delete/rename, atomic rollback, locking, corrupt-cache recovery and private-name mutation refresh passed."
        },
        {
          "id": "search-code:AC-6",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/submission/skills/search-code/scripts/search_code.py: bounded JSON serialization, handled failures, empty stderr, deadlines, indexing limits and graph/output truncation verified by passing tests."
        },
        {
          "id": "search-code:AC-7",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/src/mostaza/packaging.py: narrow skill closure, adversarial rejection, deterministic ZIP/notebook byte parity, real official compilation and unchanged model/generation/budgets verified."
        },
        {
          "id": "search-code:AC-8",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/docs/implementation/evidence/2026-10-20-search-code/benchmark.json: independent serial remeasurement matched all five snapshot identities and 15 exact query locations. Maximum cold 3.506s, warm 1.584s, refresh 2.870s, child RSS 136577024 bytes and database 72900608 bytes; both synthetic interpreters passed. Independent regression battery: 764 passed. Final validation report retains 1105 unit/123 integration passes with zero skips. Docker/Kaggle remain NOT_RUN."
        },
        {
          "id": "agent-retrieval:AC-5",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/tests/unit/test_packaging.py: frozen E0/E1 archive identities, nine-tool compatibility, secure closure and actual official compiler checks passed."
        },
        {
          "id": "local-lmstudio-kaggle:AC-3",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/tests/integration/test_phase2.py: approved historical-child exception preserves authenticated original imports and real negative controls; active checks remain bound to the current worktree. Original HEAD and dirty-plan pin independently verified unchanged."
        },
        {
          "id": "local-lmstudio-kaggle:AC-5",
          "status": "SATISFIED",
          "evidence": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/tests/integration/test_search_code_official.py: collected delivery contains exactly five approved files; real directory/schema/compiler acceptance and ZIP/notebook parity passed."
        }
      ]
    }
  ],
  "findings": {
    "AUD-001": {
      "id": "AUD-001",
      "acceptance_id": "search-code:AC-3",
      "severity": "HIGH",
      "location": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/submission/skills/search-code/scripts/search_code.py:196",
      "issue": "Directory exclusions bypass the reserved-artifact name checks. Independent Python 3.12 and 3.13 fixtures returned source snippets from solution/hidden.py, reference/hidden.py, test_patch/hidden.py and ground_truth/hidden.py.",
      "expected": "Explicit solution, reference, test-patch and ground-truth artifacts are excluded before traversal or indexing.",
      "correction": "Apply reserved-artifact exclusions to directory components, including nested and case variants. Add regression tests proving their contents never enter lexical or graph results.",
      "open": false,
      "stage": "stage-core"
    },
    "AUD-002": {
      "id": "AUD-002",
      "acceptance_id": "search-code:AC-4",
      "severity": "MEDIUM",
      "location": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/submission/skills/search-code/scripts/search_code.py:607",
      "issue": "resolve_export fabricates callable exports. Both supported interpreters produced calls to wildcard-shadowed wild.wildcard_target and to nested.outer.inner for nested.outer.inner(), although a nested function is not an attribute of its enclosing function. Both answers reported incomplete=false.",
      "expected": "Wildcard ambiguity and unsupported attribute traversal remain explicit unresolved references.",
      "correction": "Reject wildcard-shadowed exports and validate that every qualified traversal represents a supported static attribute/export. Add exact negative-edge fixtures for both cases.",
      "open": false,
      "stage": "stage-core"
    },
    "AUD-003": {
      "id": "AUD-003",
      "acceptance_id": "search-code:AC-4",
      "severity": "MEDIUM",
      "location": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/submission/skills/search-code/scripts/search_code.py:489",
      "issue": "Pattern captures are not registered as dynamic local bindings. With a global captured_target and case {\"key\": captured_target}: captured_target(), both Python 3.12 and 3.13 fabricated an edge to the global function and reported incomplete=false.",
      "expected": "Calls through pattern-bound values remain unresolved rather than resolving to shadowed outer definitions.",
      "correction": "Track capture bindings from MatchAs, MatchStar and MatchMapping.rest in the owning scope. Add fixtures asserting no fabricated calls and explicit unresolved records.",
      "open": false,
      "stage": "stage-core"
    },
    "AUD-004": {
      "id": "AUD-004",
      "acceptance_id": "search-code:AC-4",
      "severity": "MEDIUM",
      "location": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/submission/skills/search-code/scripts/search_code.py:620",
      "issue": "Import resolution loses binding provenance. Independently reproduced on Python 3.12 and 3.13 with empty pkg/__init__.py and pkg/child.py defining target(): return 42. For consumer.py containing `import pkg as alias; def use(): return alias.child.target()` on separate valid lines, neighbors fabricates a call to pkg/child.py::target and reports incomplete=false; actual execution raises AttributeError because child was never imported. Conversely, `import pkg.child as pkg; def use(): return pkg.target()` executes successfully but returns no call edge because resolve_call at line 710 mistakes the explicit alias for an unaliased package binding.",
      "expected": "Disk presence alone must not establish package attributes. Unsupported traversal remains explicitly unresolved. Unique explicit aliases, including aliases matching the package prefix, resolve correctly.",
      "correction": "Preserve explicit alias/bound-module identity and require supported import/export evidence for additional module-attribute traversal. Add exact negative and positive fixtures on both interpreters, including unloaded children, same-prefix aliases, ordinary aliases and unaliased dotted imports; verify dependent edges after import edits.",
      "open": false,
      "stage": "stage-core",
      "observations": [
        "Import provenance remains unsound for package function/module collisions. Independently reproduced on actual Python 3.12 and 3.13: pkg/__init__.py defines child(), pkg/child.py defines target(), and consumer imports pkg.child plus pkg as alias. Calling alias.child() fabricates an edge to the initializer function with incomplete=false, although runtime raises TypeError because importing the child replaced that attribute with a module. Conversely, when the initializer imports child before defining child(), both `import pkg.child; pkg.child.target()` and `import pkg.child as alias; alias.target()` fabricate edges to target with incomplete=false although runtime raises AttributeError. namespace() ignores loaded-child collisions, while bound_call()/binding() can bypass conflicting package attributes.",
        "Package collisions still bypass protection through direct lexical lookup. Independently reproduced on actual Python 3.12 and 3.13: pkg/__init__.py contains `def child(): return 1\\nimport pkg.child\\ndef use(): return child()\\n`, and pkg/child.py defines target(). Querying use's callees fabricates an edge to the initializer's child function with incomplete=false and unresolved_count=0. Actual pkg.use() raises TypeError because child now refers to the imported module. Resolver.call returns unique definitions without checking the package collision."
      ]
    },
    "AUD-005": {
      "id": "AUD-005",
      "acceptance_id": "search-code:AC-4",
      "severity": "MEDIUM",
      "location": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/submission/skills/search-code/scripts/search_code.py:491",
      "issue": "Explicit module-attribute writes and deletions are ignored. Independently reproduced on actual Python 3.12 and 3.13: provider.py defines target(); consumer.py contains `import provider\\nprovider.target = 7\\ndef use():\\n    return provider.target()\\n`. Callees fabricates an edge to provider.target with incomplete=false and no unresolved references, although runtime raises TypeError. Replacing the assignment with `del provider.target` similarly fabricates the edge although runtime raises AttributeError.",
      "expected": "Explicit mutation of a supported module binding makes affected calls unresolved rather than retaining the original callable edge.",
      "correction": "Track Attribute Store/Del operations affecting statically identifiable imported namespaces, or conservatively reject affected traversal. Add both-interpreter assignment/deletion fixtures, positive controls and dependent-refresh checks. Conservative invalidation is sufficient; execution simulation is unnecessary.",
      "open": false,
      "stage": "stage-core"
    },
    "AUD-006": {
      "id": "AUD-006",
      "acceptance_id": "search-code:AC-4",
      "severity": "MEDIUM",
      "location": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/submission/skills/search-code/scripts/search_code.py:527",
      "issue": "Skipping comprehension bodies loses assignment-expression bindings in the containing scope. Independently reproduced on actual Python 3.12 and 3.13: `def target():\\n    return 42\\ndef use():\\n    [target := 7 for value in [1]]\\n    return target()\\n`. Callees fabricates use→target, although target is a local integer and runtime raises TypeError. Only <comprehension> is unresolved; the affected target call remains a fabricated edge.",
      "expected": "A comprehension assignment expression that binds the containing scope prevents fallback to an outer same-name definition.",
      "correction": "Extract assignment-expression bindings from comprehensions while preserving their actual binding owner and ordinary comprehension-local isolation. Add both-interpreter negative-edge fixtures and controls proving unrelated outer calls remain supported.",
      "open": false,
      "stage": "stage-core"
    },
    "AUD-007": {
      "id": "AUD-007",
      "acceptance_id": "search-code:AC-4",
      "severity": "MEDIUM",
      "location": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/submission/skills/search-code/scripts/search_code.py:495",
      "issue": "Global/nonlocal mutations are recorded only against the inner function, leaving the actual outer binding eligible. Independently reproduced on actual Python 3.12 and 3.13: a module target() plus use() containing changer(), where changer declares `global target` and assigns target=7, followed by `changer(); return target()`, produces use→target with incomplete=false although runtime raises TypeError. The equivalent nested target()/`nonlocal target` fixture has the same defect.",
      "expected": "Explicit writes through global/nonlocal declarations invalidate the affected module or enclosing-function binding and remain unresolved where execution order is unsupported.",
      "correction": "Associate declared-scope Store/Del operations with their actual binding owner, or conservatively block affected candidates. Add global/nonlocal fixtures on both interpreters, graph-view consistency and refresh tests, preserving unaffected lexical positives.",
      "open": false,
      "stage": "stage-core"
    },
    "AUD-008": {
      "id": "AUD-008",
      "acceptance_id": "search-code:AC-4",
      "severity": "MEDIUM",
      "location": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/submission/skills/search-code/scripts/search_code.py:479",
      "issue": "Generic type parameters are absent from lexical binding resolution. Independently reproduced on actual Python 3.12 and 3.13: `def T():\\n    return 42\\ndef use[T]():\\n    return T()\\n` fabricates use→T with incomplete=false and unresolved_count=0, while execution raises TypeError because T is a TypeVar. TypeVarTuple, ParamSpec and generic-class method fixtures also fabricate edges. Forward, reverse and induced graph views all reproduce the defect.",
      "expected": "Type-parameter bindings block fallback to same-named outer callable definitions; unsupported generic scope semantics remain explicitly unresolved.",
      "correction": "Account conservatively for type_params and their function/class lexical visibility, including methods and nested scopes. Add both-interpreter negative-edge fixtures, unaffected-binding controls and dependent-refresh coverage.",
      "open": false,
      "stage": "stage-core"
    },
    "AUD-009": {
      "id": "AUD-009",
      "acceptance_id": "search-code:AC-4",
      "severity": "MEDIUM",
      "location": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/submission/skills/search-code/scripts/search_code.py:473",
      "issue": "Decorated definitions remain certain callable bindings. On actual Python 3.12 and 3.13, `def replace(value): return 7`, followed by `@replace` on target() or class target, and use() calling target(), fabricates use→target. Callees, callers and zero-hop induced views report incomplete=false and unresolved_count=0, although execution raises TypeError because target is an integer.",
      "expected": "Decorator-produced bindings with unsupported callable identity remain explicitly unresolved rather than targeting the original definition.",
      "correction": "Separate definition identity from decorator-produced binding eligibility. Conservative rejection is sufficient. Add both-interpreter function/class, imported-alias, graph-view and dependent-refresh regressions while preserving undecorated positive controls.",
      "open": false,
      "stage": "stage-core"
    },
    "AUD-010": {
      "id": "AUD-010",
      "acceptance_id": "search-code:AC-4",
      "severity": "MEDIUM",
      "location": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/submission/skills/search-code/scripts/search_code.py:801",
      "issue": "Implicit class bindings are absent from lookup. On actual Python 3.12 and 3.13, a global __class__() returning 42 plus Box.method() calling __class__() fabricates method→global __class__, although execution constructs Box. Forward, reverse and induced views report incomplete=false. Class-body calls to __module__, __qualname__ and docstring-created __doc__ likewise fabricate edges to same-named outer functions, although runtime raises TypeError because the class bindings are strings.",
      "expected": "Compiler-created class namespace and closure bindings prevent fallback to shadowed outer callables.",
      "correction": "Model applicable implicit class bindings or conservatively leave affected lookups unresolved. Add both-interpreter class-body/method/nested-scope fixtures, explicit-binding and evaluation-context controls, graph-view checks and incremental-refresh coverage.",
      "open": false,
      "stage": "stage-core"
    },
    "AUD-011": {
      "id": "AUD-011",
      "acceptance_id": "search-code:AC-4",
      "severity": "MEDIUM",
      "location": "/Users/diego/.codex/worktrees/sdd/2026-10-20-search-code/Mostaza-Harness/submission/skills/search-code/scripts/search_code.py:679",
      "issue": "Class-private name mangling is ignored. Independently reproduced on Python 3.12 and 3.13: define module functions __target() returning 42 and _Box__target() returning 99; define Box.method(self) returning __target(). Actual execution returns 99, but forward, reverse and zero-hop induced graphs fabricate Box.method→__target with incomplete=false and unresolved_count=0. Without _Box__target, execution raises NameError while the same edge remains.",
      "expected": "Calls use Python's class compilation binding names or remain explicitly unresolved; raw private spellings must not resolve to unrelated outer definitions.",
      "correction": "Apply class-private mangling consistently across reference and binding resolution, or conservatively reject unsupported private-name lookups. Preserve source identities and locations. Add both-interpreter regressions covering class bodies, methods/nested scopes, imported attributes, graph views and incremental refresh, with ordinary-name and trailing-dunder controls.",
      "open": false,
      "stage": "stage-core"
    }
  },
  "stages": {
    "stage-core": {
      "done": [
        "core-cli",
        "incremental-graph"
      ],
      "reviews": 0,
      "failures": 0,
      "review": null,
      "blocked": null,
      "checkpoint": {
        "item": "incremental-graph",
        "evidence": "AC5: schema6 rebuilds disposable lookup identities; normalized writes still use independent potential import addresses, preserving physical imports and prior mutation eligibility. Actual3.12/3.13 equal-stat Box/Dog class changes reparse1 provider, replace canonical callees in all graph views, preserve raw physical symbols and unchanged consumer import resolution, and remove stale targets after provider deletion. Private attribute assignment/deletion context changes reparse only mutator, invalidate the matching canonical provider member, restore other members and keep raw nonprivate calls positive; mutator removal deletes provenance. Canonically equivalent comprehension locals stay isolated. Indexed symbol_scope now uses lookup_name; existing deadline/guard/streamed SQL limits remain. Exact core632 PASS171.40s; scoped quality PASS. Reports/specs unchanged; final test SQL wrapping verified AST-identical.",
        "candidate": {
          "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
          "value": "29e30be7a6f4566ae98e968b3026a40a348a8414028ccad7f9611ac0734a02cc"
        }
      },
      "gate_history": [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0
      ]
    },
    "stage-package": {
      "done": [
        "skill-closure",
        "historical-compatibility"
      ],
      "reviews": 0,
      "failures": 0,
      "review": null,
      "blocked": null,
      "checkpoint": {
        "item": "historical-compatibility",
        "evidence": "Exact packaging check: 96 PASS in 4.02s, including pinned E0/E1 archive SHA regressions and existing variant/manifest-drift tests. Independently executed original packaging.py read from initial HEAD 1969aa509b6a161a159c79454e95100f6fba8b54; all seven historical configuration closures and generated ZIPs remain byte-identical. E0 SHA256 aa40c075b2bf77c62cca80b9a9b1ec8fd5f28131295c9bf03926fce241464fe4; E1 be8ebd8e660c75b6a7e467b6590e0ff4f093077055e7aeee0db6fa6a0ddd375e. Both E0/E1 passed real pinned directory/schema/compiler. Self-review: TOOLS still equals original nine native names; historical source/manifests untouched; no absent historical checkout/raw packet reconstructed or checks skipped. Ruff lint/format, mypy and scoped whitespace PASS.",
        "candidate": {
          "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
          "value": "aaa31a8d31e56eecfba84b1a4c0f6c9874af9bc6331add52785fe131dbdd9e8a"
        }
      },
      "gate_history": [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0
      ]
    },
    "stage-activate": {
      "done": [
        "active-policy",
        "official-bootstrap"
      ],
      "reviews": 0,
      "failures": 0,
      "review": null,
      "blocked": null,
      "checkpoint": {
        "item": "official-bootstrap",
        "evidence": "Exact official-execution PASS: 3 tests in 7.42s. Pinned swegemma0.2.11/adk-submission0.2.13/google-adk1.36.1 actual compiler, SkillToolset, AdkSandboxCodeExecutor and disposable SubprocessManager executed without inference or runtime changes. Inventory: six native + list_skills/load_skill/load_skill_resource/run_skill_script. Discovery/load/resource use zero native calls; bootstrap executor uses one; witness total 11, real callback/native budget exhaustion denies execution. Transient resources/wrapper removed; persistent CLI bytes equal packaged source; warm/native write/edit/command refresh reparses [0,1,1,1], stale names absent; submitted patch contains only intended source. Physical Python root and absolute /workspace shell aliases with spaces exercised. Deterministic ZIP and actual generated notebook cell byte parity, real Python3.12 bootstrap/warm execution PASS. Docker quoting reviewed only; Docker/Kaggle NOT_RUN. official_witness(delivery,base) returns facts for stage4 report. R",
        "candidate": {
          "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
          "value": "fd9ae23945db13434be7d84496ad3220cdeef3b4813b580e1ecb569585d7c7c4"
        }
      },
      "gate_history": [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0
      ]
    },
    "stage-validate": {
      "done": [
        "cpu-evidence",
        "regression-delivery"
      ],
      "reviews": 3,
      "failures": 0,
      "review": null,
      "blocked": null,
      "checkpoint": {
        "item": "regression-delivery",
        "evidence": "Exact unchanged complete-cpu-gate exit0:11/11 checks PASS,1105 unit/123 integration tests,0 skips;types60,Python3.12 standalone1 and actual official-active3 PASS. Ruff format/lint/build,historical E0/E1 compilation and real paired evidence PASS. Official subprocess witness matches current0d5956923551... CLI,six native tools,original budgets,transient removal,incremental edits and clean patch;no model/Kaggle calls. Authentic original-source historical phase2 compiler/resource/trace/readiness recomputation/operator-path negative control and real PCV14 matrix remain enabled. Original checkout Git status remains sole expected dirty closed plan. Self-review: only two declared reports regenerated in dispatch44,no source/test/spec/original evidence/gate/threshold/fixture changes,no omissions. AUD011 remains open for complete Auditor review.",
        "candidate": {
          "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
          "value": "62b478b1ca9cd0bb9f5ea31f1fd6e609f784c555695385fd0d716b3d54b6dfa1"
        }
      },
      "gate_history": [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0
      ],
      "decisions": [
        {
          "cause": "EXTERNAL",
          "block": {
            "scope": {
              "decision_id": "search-code-original-validation-inputs",
              "item": "regression-delivery",
              "paths": [
                "scripts/check_search_code.py"
              ],
              "policy": "original-historical-validation-inputs-v1",
              "semantics": "Full approved regression remains pending until receipt-bound original historical checkout/raw phase-1 packet and the approved host validation dependencies are available and verified. User reports original locations unknown; no recovery, reconstruction or restoration is authorized. The unchanged approved host environment lacks dotenv, adk_submission.yaml_loader and swegemma.cli. Actual failures and exact prerequisites are in declared validation.json. No further retry without new verified prerequisites.",
              "limits": [
                "No reconstruction or new inference",
                "No omitted tests, relaxed pins or changed gate commands",
                "No dependency/environment mutation without separate authorization",
                "No gate PASS, audit PASS or Versioner closure before full validation succeeds"
              ]
            },
            "scope_digest": "202e7839491d9141c45d89c84933f77eab4a33bf052dbe8aca1d5e463cf9a57a"
          }
        },
        {
          "cause": "EXTERNAL",
          "authorization": 1,
          "scope_digest": "202e7839491d9141c45d89c84933f77eab4a33bf052dbe8aca1d5e463cf9a57a",
          "evidence": "2026-10-20 user: Resuelve las tres dependencias faltantes y busca los originales históricos en el equipo, sin reconstruir evidencia ni omitir pruebas. Continúa con el flujo SDD si logras desbloquear el gate. Authorizes narrow dependency repair and local original-artifact search/identity verification only; unchanged gate, no evidence reconstruction or skipped tests."
        }
      ],
      "external_block": {
        "scope": {
          "decision_id": "search-code-original-validation-inputs",
          "item": "regression-delivery",
          "paths": [
            "scripts/check_search_code.py"
          ],
          "policy": "original-historical-validation-inputs-v1",
          "semantics": "Full approved regression remains pending until receipt-bound original historical checkout/raw phase-1 packet and the approved host validation dependencies are available and verified. User reports original locations unknown; no recovery, reconstruction or restoration is authorized. The unchanged approved host environment lacks dotenv, adk_submission.yaml_loader and swegemma.cli. Actual failures and exact prerequisites are in declared validation.json. No further retry without new verified prerequisites.",
          "limits": [
            "No reconstruction or new inference",
            "No omitted tests, relaxed pins or changed gate commands",
            "No dependency/environment mutation without separate authorization",
            "No gate PASS, audit PASS or Versioner closure before full validation succeeds"
          ]
        },
        "scope_digest": "202e7839491d9141c45d89c84933f77eab4a33bf052dbe8aca1d5e463cf9a57a"
      }
    }
  },
  "gate": {
    "candidate": {
      "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
      "value": "bf2aa6ae353d5e654c5f5a442b4ac5f1918b06c0387cea75c1bbe55c80d7b909"
    },
    "digest": "c58ea311ba5c6afc4888a850a12685f4a062ef6d56cb2afc0b112756da5ee4f3",
    "results": [
      {
        "id": "spec-frozen",
        "stage": null,
        "code": 0,
        "spec_digest": "d2d2a4c012cd9689229d01094067f52d9df213a728ca3842b570d2614c5c0105"
      },
      {
        "id": "git-diff-check-stage-core",
        "stage": "stage-core",
        "code": 0,
        "output_digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      },
      {
        "id": "git-diff-check-stage-package",
        "stage": "stage-package",
        "code": 0,
        "output_digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      },
      {
        "id": "git-diff-check-stage-activate",
        "stage": "stage-activate",
        "code": 0,
        "output_digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      },
      {
        "id": "git-diff-check-stage-validate",
        "stage": "stage-validate",
        "code": 0,
        "output_digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      },
      {
        "id": "core",
        "stage": "stage-core",
        "code": 0,
        "output_digest": "b5691ccc80f99ccf3fad7b538ae484816fbafda1bbc3a32f5b83ae5cca6ed938"
      },
      {
        "id": "packaging",
        "stage": "stage-package",
        "code": 0,
        "output_digest": "c86483ac57b83af68929b90edeeed1ec9ad23c4434bde30761943b80263bfe29"
      },
      {
        "id": "official-execution",
        "stage": "stage-activate",
        "code": 0,
        "output_digest": "be9a0f3be619fa8faa6beaaf6ef9efaeef7939ab9dcab003456f89efd391c4c2"
      },
      {
        "id": "complete-cpu-gate",
        "stage": "stage-validate",
        "code": 0,
        "output_digest": "e42b1633252750a92f6e2e1d5c5287f592d5fb9d5d9f8e5b19a2a73de06a5c32"
      }
    ]
  },
  "versioning": {
    "candidate": {
      "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
      "value": "bf2aa6ae353d5e654c5f5a442b4ac5f1918b06c0387cea75c1bbe55c80d7b909"
    },
    "status": "CLOSED_FOR_COMMIT",
    "paths": [
      "README.md",
      "docs/implementation/evidence/2026-10-20-search-code/benchmark.json",
      "docs/implementation/evidence/2026-10-20-search-code/validation.json",
      "docs/specs/README.md",
      "docs/specs/agent-retrieval.md",
      "docs/specs/local-lmstudio-kaggle.md",
      "docs/specs/search-code.md",
      "notebooks/mostaza-phase2-preparation.ipynb",
      "scripts/check_search_code.py",
      "src/mostaza/packaging.py",
      "submission/agent.yaml",
      "submission/prompts/baseline.md",
      "submission/skills/search-code/SKILL.md",
      "submission/skills/search-code/scripts/search_code.py",
      "tests/integration/test_pcv01_cpu_contract.py",
      "tests/integration/test_phase2.py",
      "tests/integration/test_search_code_official.py",
      "tests/unit/test_packaging.py",
      "tests/unit/test_search_code.py",
      "tests/unit/test_search_code_validation.py",
      "docs/specs/plans/closed/2026-10-20-search-code.md"
    ],
    "files": {
      "docs/specs/README.md": [
        "file",
        420,
        "d7f6cde195a944d287929b234af2a6012b49211c39aa515720a166942d2af818"
      ],
      "tests/unit/test_search_code.py": [
        "file",
        420,
        "4d4818a8ab79da796343f7b0b124cab8b66f5b93ba77f86d907190440c934bd0"
      ],
      "submission/skills/search-code/scripts/search_code.py": [
        "file",
        420,
        "0d59569235517dc64f88d55cceaee11897c0b9a2a7a32941b66216a74c7a3367"
      ],
      "tests/integration/test_search_code_official.py": [
        "file",
        420,
        "35a4e476b96fe35095f47bcae7463cf1a956b9f91bfac77bcb7cb61eafc77734"
      ],
      "README.md": [
        "file",
        420,
        "47f3d16acc0038cf489219d8c4cecf3a1e7252385b504a25a4e7490db5cd039b"
      ],
      "src/mostaza/packaging.py": [
        "file",
        420,
        "55a695e51f2e01bcd30f238bb6681721f168a7b4886ca43765957940f065116a"
      ],
      "submission/agent.yaml": [
        "file",
        420,
        "4ed5c70aa6b7e3a8fae65858ef1ac25900ffd5779f8e8b6d110d7c32e3f267e8"
      ],
      "tests/unit/test_packaging.py": [
        "file",
        420,
        "21831c52bd7a63a8819c1d6989db31c19cf0fe5578c34199d733746847483968"
      ],
      "submission/skills/search-code/SKILL.md": [
        "file",
        420,
        "aa3dc1cdd08e99b27acb44ea90085969a2f403acdee5e2a5dedc2eee3d156e3e"
      ],
      "docs/implementation/evidence/2026-10-20-search-code/benchmark.json": [
        "file",
        420,
        "27331f5b59619f7ae3c0a52adf3f6e74f6f3d6308886828cfa1957e2000d5abc"
      ],
      "docs/specs/agent-retrieval.md": [
        "file",
        420,
        "48710df116fc2e3acfbde3e0a8f1cf0584a7cfa199193da776ecc91f9decbec6"
      ],
      "docs/implementation/evidence/2026-10-20-search-code/validation.json": [
        "file",
        420,
        "c81f071aa707a570203c4a899a65759a7c251cb327b3b6736030984d25959a72"
      ],
      "submission/prompts/baseline.md": [
        "file",
        420,
        "4e8fb458276547aedc607f1fdc5b41b90751a58aa0aa8bbbadef8f453d000295"
      ],
      "docs/specs/local-lmstudio-kaggle.md": [
        "file",
        420,
        "7ef9fbd773c681ece1aea838aee649869abfdb569749af040aa18ae8534bfcac"
      ],
      "notebooks/mostaza-phase2-preparation.ipynb": [
        "file",
        420,
        "fca095a65347daa8a1c8f42d4f0dd1160eae54b3735b2d3429d92e622c4723a1"
      ],
      "scripts/check_search_code.py": [
        "file",
        420,
        "41af4b9899e2a1bfefee39ad19411196236aa82f9efc90beaf9ba262032caf1a"
      ],
      "tests/integration/test_pcv01_cpu_contract.py": [
        "file",
        420,
        "a9e0b29483253e0f3ab1989328c8c8c264acb7701a4d5e62dbff8397e5d1c29d"
      ],
      "tests/unit/test_search_code_validation.py": [
        "file",
        420,
        "926ccea525b458d2e8bd67e2fcd65d1fcd4d1177be5ed1d12e954575a8fe1ab5"
      ],
      "tests/integration/test_phase2.py": [
        "file",
        420,
        "266063e65359d02b5f3092d8f0f928450b90adbe4e069a7e3a5dfea50e1d1377"
      ],
      "docs/specs/search-code.md": [
        "file",
        420,
        "f80c02356395f83f0e8f08c35d32c8fee1f81c7ab8b98a21febe7675e153b8d1"
      ]
    }
  },
  "legacy": null,
  "autonomy": {
    "policy": "audit-only-v1",
    "authorizations": [
      {
        "limit": 6,
        "evidence": "2026-10-21 user explicitly answered: Sí, iteración completa y una auditoría adicional. Authorizes Planner -> Implementer -> unchanged gate -> one additional independent Auditor for AUD-005/AUD-006/AUD-007, retaining specifications/all tests and push/PR to develop upon PASS."
      },
      {
        "limit": 7,
        "evidence": "User reply 2026-10-21: «Autorizo tres iteraciones más completas.» Authorizes three additional full Planner→Implementer→gate→Auditor iterations after audit6, each with one additional audit; consume grant 1 of 3 now (audit7), retain remaining two for audit8/9 only if needed. Specifications, all tests, exact gate and push/PR to develop upon zero-finding PASS retained."
      },
      {
        "limit": 8,
        "evidence": "User reply 2026-10-21: «Autorizo tres iteraciones más completas.» Consume grant 2 of 3 following audit7 FIX_REQUIRED AUD009/010 (AUD008 resolved). One additional full Planner→Implementer→gate→Auditor cycle for audit8; one remaining grant may authorize audit9 if needed. Preserve specifications/all tests/exact gate and approved push/PR develop on zero-finding PASS."
      },
      {
        "limit": 9,
        "evidence": "User reply 2026-10-21: «Autorizo tres iteraciones más completas.» Consume grant 3 of 3 following audit8 FIX_REQUIRED sole AUD011 (AUD009/010 resolved). Authorizes full Planner→Implementer→gate→Auditor cycle with audit9; no further additional audit grants remain after this. Preserve specifications/all tests/exact gate and approved push/PR develop on zero-finding PASS."
      }
    ]
  },
  "specification_policy": "planner-first-v1",
  "work_branch": {
    "name": "codex/search-code",
    "base": "develop",
    "base_head": "1969aa509b6a161a159c79454e95100f6fba8b54",
    "initial_head": "1969aa509b6a161a159c79454e95100f6fba8b54",
    "remote": "origin",
    "target": "develop",
    "push_url": "git@github.com:diego-escobar-git/mostaza-harness.git"
  },
  "spec_file_digest": "d2d2a4c012cd9689229d01094067f52d9df213a728ca3842b570d2614c5c0105",
  "external_authorizations": [
    {
      "id": 1,
      "decision_id": "search-code-original-validation-inputs",
      "stage": "stage-validate",
      "item": "regression-delivery",
      "scope": {
        "decision_id": "search-code-original-validation-inputs",
        "item": "regression-delivery",
        "paths": [
          "scripts/check_search_code.py"
        ],
        "policy": "original-historical-validation-inputs-v1",
        "semantics": "Full approved regression remains pending until receipt-bound original historical checkout/raw phase-1 packet and the approved host validation dependencies are available and verified. User reports original locations unknown; no recovery, reconstruction or restoration is authorized. The unchanged approved host environment lacks dotenv, adk_submission.yaml_loader and swegemma.cli. Actual failures and exact prerequisites are in declared validation.json. No further retry without new verified prerequisites.",
        "limits": [
          "No reconstruction or new inference",
          "No omitted tests, relaxed pins or changed gate commands",
          "No dependency/environment mutation without separate authorization",
          "No gate PASS, audit PASS or Versioner closure before full validation succeeds"
        ]
      },
      "scope_digest": "202e7839491d9141c45d89c84933f77eab4a33bf052dbe8aca1d5e463cf9a57a",
      "source": "user",
      "evidence": "2026-10-20 user: Resuelve las tres dependencias faltantes y busca los originales históricos en el equipo, sin reconstruir evidencia ni omitir pruebas. Continúa con el flujo SDD si logras desbloquear el gate. Authorizes narrow dependency repair and local original-artifact search/identity verification only; unchanged gate, no evidence reconstruction or skipped tests.",
      "status": "CONSUMED"
    }
  ],
  "gate_sequence": 9,
  "last_gate": {
    "results": [
      {
        "id": "spec-frozen",
        "stage": null,
        "code": 0,
        "spec_digest": "d2d2a4c012cd9689229d01094067f52d9df213a728ca3842b570d2614c5c0105"
      },
      {
        "id": "git-diff-check-stage-core",
        "stage": "stage-core",
        "code": 0,
        "output_digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      },
      {
        "id": "git-diff-check-stage-package",
        "stage": "stage-package",
        "code": 0,
        "output_digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      },
      {
        "id": "git-diff-check-stage-activate",
        "stage": "stage-activate",
        "code": 0,
        "output_digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      },
      {
        "id": "git-diff-check-stage-validate",
        "stage": "stage-validate",
        "code": 0,
        "output_digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      },
      {
        "id": "core",
        "stage": "stage-core",
        "code": 0,
        "output_digest": "b5691ccc80f99ccf3fad7b538ae484816fbafda1bbc3a32f5b83ae5cca6ed938"
      },
      {
        "id": "packaging",
        "stage": "stage-package",
        "code": 0,
        "output_digest": "c86483ac57b83af68929b90edeeed1ec9ad23c4434bde30761943b80263bfe29"
      },
      {
        "id": "official-execution",
        "stage": "stage-activate",
        "code": 0,
        "output_digest": "be9a0f3be619fa8faa6beaaf6ef9efaeef7939ab9dcab003456f89efd391c4c2"
      },
      {
        "id": "complete-cpu-gate",
        "stage": "stage-validate",
        "code": 0,
        "output_digest": "e42b1633252750a92f6e2e1d5c5287f592d5fb9d5d9f8e5b19a2a73de06a5c32"
      }
    ],
    "candidate": {
      "algorithm": "SDD_CANDIDATE_SHA256_V3_EVIDENCE",
      "value": "bf2aa6ae353d5e654c5f5a442b4ac5f1918b06c0387cea75c1bbe55c80d7b909"
    },
    "definition_digest": "c58ea311ba5c6afc4888a850a12685f4a062ef6d56cb2afc0b112756da5ee4f3"
  }
}
```

<!-- SDD-CONTINUITY:END -->
