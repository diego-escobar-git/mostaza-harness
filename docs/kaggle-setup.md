# Official resources and compiler checks

For the reusable end-to-end procedure, see the
[Kaggle execution runbook](runbooks/kaggle-execution.md). This page retains the
Mostaza-specific resource pins, integration details and operational history.

The official starter notebook version 3 and organizer wheelhouse version 31 were inspected on 2026-10-13. `resources/manifest.json` records the three pinned wheel SHA-256 values, Python requirements and actual retrieval provenance. Downloads stay in ignored `resources/official`; third-party data and model assets are not redistributed. Wheel metadata does not declare a license; inspect applicable Kaggle terms before redistribution. Original Mostaza code uses Apache-2.0.

## Authenticated resource review

On 2026-10-13 the enrolled user obtained individual authentic competition files through the official Data UI. The README, root agent, evaluation config, sampling config, system/analyzer prompts, analyzer config and task metadata now live in ignored `resources/official/`; original Downloads files remain intact. All hashes and review notes are recorded in `resources/manifest.json`. Its sample inventory was generated locally from these downloads and is explicitly not an organizer-supplied file. Numeric competition dataset version was not exposed by the individual downloads; the exact SHA-256 values identify the reviewed bytes without inventing a version.

The task metadata contains 129 unique instances: 67 FastAPI, 13 Requests, 48 Rich and 1 HTTPX. Only instance IDs, repository names and base commits were reviewed for inventory. Reference patch/test_patch bytes remain in ignored raw metadata and never enter agent inputs or submission archives. The selected snapshot, graph and embedding assets were acquired and hashed; the three-task cohort was frozen before outcomes and executed in both arms. Model weights remained in Kaggle.

The full official README and sample declarations were reviewed against the existing pinned wheels. The README permits four quantized competition models; Mostaza retains the specifically required 31B model. Its illustrative timeout of 300 seconds does not override the authentic sample's 60 seconds. The original delegated analyzer's `../` includes are removed with that agent; compiler security is unchanged. Native similarity supports stored symbol lookup and lexical fallback, without a live text encoder. No material incompatibility requiring a new specification was found.

## Minimal E0 derivation

`experiments/E0-baseline/manifest.json` binds each source and exact change. E0 preserves the original root name, 31B model, all nine native tools, generation parameters and source evaluation config. It removes `adapter: main_lora` and the delegated `code_analyzer` AgentTool, omitting the analyzer declaration/prompt and both dummy adapters from the submitted closure. Adapter weights were not needed or downloaded. The exact sampling mapping is inlined into the owned root YAML and the instruction include points to `prompts/baseline.md`.

The original system prompt remains a byte-exact prefix. The only added shared instruction is the documented `Shared Budget Checkpoints` suffix required by agent-retrieval:AC-4: call get_status before exploration, implementation and verification, preserving official time for patching, targeted verification and submission. Both arms use this same clause. E0's original retrieval, implementation, verification and repair text otherwise remains unchanged; no Graph-SDD exploration optimization was added to E0.

Source values used unchanged in the actual paired run are temperature 0.2, top_p 0.95, max_output_tokens 16384, thinking_budget 4096 and include_thoughts true. The exact evaluation file sets timeout_seconds 60, max_tool_calls 10, max_time_minutes 1 and max_turns 50. Phase 2 verification_timeout_seconds remains the pinned harness default 300; it is absent from the sample file. None of these values were tuned from outcomes.

E0 passed current official directory/schema/compiler validation and deterministic selected-closure archive reproduction locally. These are actual derived-config compiler checks with inert registry bindings, distinct from synthetic boundary tests. They perform no Gemma inference or benchmark task execution and do not establish actual evaluation compatibility. E1 receives the same frozen conditions and changes only the exploration instruction section.

## Reproduce public pins

From the repository root, after `sh scripts/setup.sh`:

```sh
uv run --frozen --no-sync python scripts/fetch_resources.py --resource swegemma --resource adk_submission --resource adk_eval_core
uv run --frozen --no-sync python scripts/fetch_resources.py --check --resource swegemma --resource adk_submission --resource adk_eval_core --resource notebook
```

The fetch command downloads one explicitly named small file at a time through official Kaggle endpoints, verifies the pin before atomic publication and refuses to overwrite conflicting files. It does not fetch authenticated competition assets or bulk datasets. All three per-wheel endpoints were re-downloaded independently and matched the approved hashes on 2026-10-13. Notebook API response metadata can change; the retained exact response hash identifies the bytes actually inspected.

## Isolated compiler environment

Local tooling uses Python 3.13; the official GPU notebook reports Python 3.12.13. Keep compiler dependencies out of the locked host environment and never install the GPU wheel stack on macOS:

```sh
uv venv --python .venv/bin/python .tools/official
uv pip install --python .tools/official/bin/python resources/official/adk_submission-0.2.13-py3-none-any.whl google-adk==1.36.1 pytest rich docker
uv pip install --python .tools/official/bin/python cachetools==5.5.2 networkx==3.4.2 numpy==2.2.6
uv pip install --no-deps --python .tools/official/bin/python resources/official/swegemma-0.2.11-py3-none-any.whl resources/official/adk_eval_core-0.1.0-py3-none-any.whl
```

The isolated environment supports compiler and native retrieval contract checks; it does not install all SWE evaluation dependencies. The native dependency pins were verified installed: cachetools 5.5.2, networkx 3.4.2 and numpy 2.2.6. They satisfy the inspected swegemma 0.2.11 wheel requirements cachetools>=5.0.0, networkx>=3.0 and numpy>=1.26.0. Native graph/embedding tests use local synthetic fixtures and perform no inference. Integration tests execute actual directory validation, the current restricted schema and compiler against synthetic declarations with inert tool/model registry values. They also exercise the actual native tool registry, get_status budget response and workspace path boundary. These tests perform no inference and do not establish real E0/E1 compatibility. Missing compiler modules are errors, not skipped tests.

## Package and validate

Both authentic E0 derivation and the E1 exploration treatment are available. Reproduce the existing archives and compiler checks with:

```sh
sh scripts/package.sh --experiment E0 --output /tmp/mostaza-e0-submission.zip
sh scripts/package.sh --experiment E1 --output /tmp/mostaza-e1-submission.zip
uv run --frozen --no-sync python scripts/check_official.py --check --experiments E0 E1
```

Packaging requires an experiment manifest with schema_version 1, status `ready`, ready_for_evaluation `true`, experiment_id `E0` or `E1`, a submission-relative prompt path (for example `prompts/hybrid-retrieval.md`) and baseline_source_sha256 matching the authenticated starter bytes. A pending/draft manifest remains ineligible even after resources are available. These markers accompany the actual prerequisite review and do not establish real evaluation compatibility.

Each archive has root agent.yaml, optional eval_config.yaml and only the selected prompt's transitive include closure. The host MVP accepts declarative config/prompt files, one LlmAgent, the fixed 31B model and the nine native tools verified in `swegemma/tools/__init__.py:create_tools`. Traversal, symlinks, unknown tools/models, executable features, forbidden files, missing/cyclic includes and existing output files fail. ZIP metadata and ordering are fixed for deterministic byte reproduction. Current official directory/schema/compiler checks execute before publication. Existing archive outputs must be moved by their owner before rerunning.

The approved official check also requires authenticated resource pins and builds the host package. It fails if any resource pin, derivation or ready experiment prerequisite is missing or changed. Archive creation and local synthetic compiler tests never satisfy actual Gemma execution requirements.

## Official execution route

Follow the inspected [starter notebook](https://www.kaggle.com/code/ryanholbrook/getting-started-gemma-4-developer-agent) in the Kaggle offline L4x4 environment. Its current demonstration selects 12B; Mostaza must explicitly retain `gemma-4-31b-it-qat-w4a16-ct`. The notebook mounts model revision 2, serves with VllmServer, uses `swegemma.models.load_tasks`, `swegemma.config.EvalConfig` and `swegemma.evaluate.Evaluator.evaluate_task`, then validates with `adk_submission.validate_directory`. The approved frozen cohort—requests_7205, fastapi_15589 and rich_3061—was executed in both arms in actual Kaggle notebook version 2, run 358139443, on four NVIDIA L4 GPUs. Each arm recorded PASS 0, FAIL 1, ERROR 2 and zero resolved tasks; all six sessions reached the unchanged one-minute budget. Requests produced applicable patches that failed official verification; FastAPI and Rich produced no patch, so verification did not run. E1 made no vector or graph tool call, and these results establish no retrieval benefit. Retained native files and the declared compact evidence document actual execution separately from local compiler tests.

For a future rerun, attach the same required task/snapshot/graph/embedding inputs, pinned wheelhouse, 31B model revision 2 and L4x4 GPU runtime, and freeze any new cohort before observing outcomes. These are prerequisites for another execution, not blockers of the completed six runs. Never substitute illustrative first tasks for the approved cohort or describe mocks as model results. See [experiments.md](experiments.md) for result import, source-integrity verification and deterministic report commands.


## Phase-2 budget calibration preparation

The five new configuration IDs are E0-B180, E1-B180, E0-B300, E1-B300 and
E1-R180. Budget-only B180/B300 retain the original prompts; the distinct recovery
variant changes only E1 exploration. All pairs preserve model, sampling, native
tools, environment, verification and repair policy. Original phase-1 manifests,
submission files, raw sources and evidence remain immutable.

The locally generated [private offline notebook](../notebooks/mostaza-phase2-budget-retrieval.ipynb)
embeds an exact positive allowlist of execution modules, pre-outcome cohort,
resource pins and the two B180 archives. Post-run diagnosis, raw task metadata,
reference patches, hidden tests and normalizer/analysis modules are excluded.
The official Evaluator retains generated native results/traces privately; no
post-run findings enter agent prompts or submission archives.

Local preparation is complete independently of GPU permission. The default
notebook accelerator and internet are disabled. All six phase-2 records are
NOT_RUN with null outcomes/metrics and reasons. Its complete official serial
execution loop is blocked before bootstrap/install/model startup until a separate
human quota decision and verified platform allocation deadline/termination exist.
A timer beginning in the first cell misses allocation startup; VllmServer.stop
only stops the model process and does not prove Kaggle released GPUs.

The exact initial proposal is six evaluations (E0-B180/E1-B180 on requests_7205,
fastapi_15589, rich_3061), one private offline NVIDIA L4 x4 session, concurrency 1,
zero retries, 180-second generation/30 charged tools/50 turns and 300-second
verification per task. Generation totals at most 18 minutes; verification 30.
The inclusive ceiling is 120 wall-clock minutes from allocation start (startup,
loading, compiler and export included), at most 8 GPU-device-hours and $0 paid
purchases. Actual remaining quota/accounting units must be checked before launch.
Scheduling reserves full worst-case task allowance and export time. No remote
notebook has been pushed or started. Authenticated allocation-start and confirmed
allocation-termination support are currently unverified, so execution remains
blocked even if a generic GPU authorization flag is manually changed.

B300 requires persistent B180 time/tool constraints before implementation or
verification; E1-R180 requires analyzed, held-fixed budget calibration and a new
contemporaneous E0-B180 baseline. Each is a separate later six-run quota decision
with its own 120-minute/8-device-hour/$0 ceiling; neither launches automatically.
Retain failures, do not select on success, and make no significance or retrieval
superiority claim from this exploratory three-task cohort.

From this repository root with scoped uv on PATH:

```sh
uv run --frozen --no-sync python scripts/prepare_phase2.py
uv run --frozen --no-sync python scripts/check_phase2.py --check --cohort experiments/cohort.json --evidence-dir docs/implementation/evidence/mostaza-phase2-budget-retrieval
```

The preparation command regenerates only the notebook and declared readiness,
comparison and report evidence. The read-only checker recompiles all five variants,
replays native historical sources, binds legacy bytes to the merged baseline and
compares every declared artifact and all notebook/payload/source bytes. It rejects
invented real outcomes. Native phase-2 acquisition remains pending; any subsequent
authorized acquisition needs full provenance replay and a new gate/audit before
outcome reporting. Absolute reproducible local commands, exact input hashes,
limitations and the concrete quota proposal are in the declared
[phase-2 report](implementation/evidence/mostaza-phase2-budget-retrieval/report.md).


## Observed startup and exact-version supervision (new authorization pending)

The first B180 allocation was cancelled by the operator after Active Events
stopped showing it while the authenticated SDK still reported RUNNING. This
was a conservative supervision decision before the 30-minute startup allowance,
not evidence of a model-startup timeout. Its executed notebook proves that
preflight completed in 123.759715 seconds. No model-ready marker, task result or
agent trace was acquired. Preserve the original six NOT_RUN rows and raw bundle
under `results/kaggle-phase2-browser-b180`; never turn missing telemetry into zero
agent calls or tokens. The remaining silent execution interval cannot be assigned
solely to weight loading, compilation or health checks without the missing server
log.

The pinned native manager creates a temporary log, redirects subprocess stdout
and stderr there, and reports health-wait progress through its INFO logger.
Copying that log only in the outer finally block misses abrupt platform
cancellation; native stop can also unlink its own log. The observed preparation
adds stage timestamps and five-second heartbeats from before bootstrap through
installation, imports, compiler, native server start, registry and tasks. A second
hard link in `/kaggle/working` retains the exact native output as it is written,
including when native cleanup unlinks the source. The official start/stop methods
and model configuration remain in use. Lack of hard-link support fails before
model startup. The source log and retained name share an inode; only the source
name may be removed by native cleanup.

`startup-schema.json` defines units and coverage. `startup-events.jsonl` and
`startup-status.json` record stage, UTC and monotonic durations, process PID/exit
state, native health result during startup and log byte count. Unobserved fields
remain null with reasons. A native false health result does not distinguish a
refused connection, timeout or non-200 response. Health checks perform no model
inference. During task evaluation, no extra health probe is added. Full output
remains in `server-retained.log`; bounded new chunks also reach the notebook log.
These files are private host observations and never enter the agent prompt or
submission archives. Existing archive and input hashes remain unchanged.

Generate and check without GPU:

```bash
uv run --frozen --no-sync python scripts/prepare_observed_phase2.py
uv run --frozen --no-sync python scripts/prepare_observed_phase2.py --check
.tools/official/bin/python scripts/check_startup_observation.py
```

The last command uses CPU-only local HTTP/exit/timeout fixtures with the pinned
native manager. It is a lifecycle test, not a model evaluation. The generated
`notebooks/mostaza-phase2-observed.ipynb` has GPU/internet disabled and no human
authorization. The consumed B180 authorization is invalid for the observed-v2
policy. After a new explicit decision, a fresh JSON receipt can be bound locally
with `--receipt PATH --output results/NEW-RUN/launched.ipynb`; the command never
launches Kaggle. It rejects unknown receipt fields, unsafe identity, stale quota,
nonterminal previous versions and missing new approval. The receipt uses an
external clock recorded before the first allocation-capable operation. Binding
is separate from submitting the new private notebook through the official client.

Before any future launch, confirm all known own latest versions terminal and
observe stable reported quota for at least 30 seconds, besides explicit reserved
zero and an empty Active Events view. Require at least eight hours of reported
quota as a conservative threshold; quota seconds are not assumed to be physical
GPU-device seconds. Fresh UUID naming, complete own private inventory and exact
source hashes must establish a new target, never overwrite the earlier notebook.

After submission, record notebook ref, version number and the opaque
`scriptVersionId` from the browser's **View full version** link. These are distinct
identifiers. `VersionIdentity` validates that exact browser URL. The SDK's latest
status is corroborating evidence for a dedicated notebook with one saved version;
it is never represented as an arbitrary historical-version query. If another
version appears, reconcile identity before any action.

Poll at most every 60 seconds and retain observations. If Active Events is absent
or disagrees, open that notebook's **More options → View versions → version N →
More options**. Continue supervision using the exact version's status and verify
its **Cancel** control; do not cancel solely because Active Events is empty or a
live-log request failed. The old run proved that version-history cancellation
works even in that discrepancy. If target identity or stop control cannot be
restored within 60 seconds, escalate with the exact URL and try to stop only
that target. If cancellation is still unconfirmed at minute 105, escalate
immediately; never treat CANCEL_REQUESTED as release.
Never open Edit, create an interactive GPU session or substitute another run.
Do not block active supervision on browser downloads; retrieve artifacts after
terminal confirmation. Silence alone is not a startup error; persistent stage
and server observations determine what is known.

For the proposed new single six-evaluation B180 batch, preserve the frozen model,
sampling, cohort/order, official harness, verification, repair and original arm
prompts. No B300 or recovery treatment is included. Startup remains limited to
30 minutes. Stop admitting tasks after minute 89, reserving a full 600 seconds
per task and 300 seconds for export. End task work by minute 99 and request browser
cancellation by minute 104, with minute 105 the latest operational stop threshold
and 120 minutes the total authorization ceiling (at most eight physical GPU-device
hours for four devices, zero purchases). Stop earlier on completion or fatal error.
A single allocation, serial execution and no retries/restarts remain mandatory.

A missing event or reserved zero cannot prove release. Require terminal SDK and
exact-version browser states, corroborate no active target and stable quota over
two observations at least 30 seconds apart. Cancellation requested is intermediate.
Do not claim an exact physical release timestamp or guaranteed platform latency.
Browser/network/agent availability and platform release delay remain residual
risks to disclose before the next authorization. All six task records remain
NOT_RUN until real task evidence is acquired; there is no claim of retrieval
benefit from this local preparation or from the aborted allocation.


## Observed B180 allocation outcome (2026-10-14)

The separately authorized B180-observed-v2 allocation exposed CUDA OOM during
vLLM sampler warm-up before any agent task. The exact version was canceled and
closure confirmed by browser, SDK and stable quota. All six task rows remain
NOT_RUN with null metrics; no retrieval comparison was obtained. The startup
observer retained the complete native log. See the [acquisition report](implementation/evidence/mostaza-phase2-observed-run/report.md)
for provenance, timings, quota units and limitations. This single-allocation
authorization is consumed; another GPU attempt needs a new decision.


## Corrected startup candidate and consumed allocation

The locally prepared B180-startup-v3 candidate restores the successful phase-1
startup environment and limits native serving concurrency to one. See the
[startup correction and limits](implementation/evidence/mostaza-phase2-startup-correction/report.md)
and runbook section13 for the historical preparation. The subsequent authorized
six-run batch reached readiness and completed with no resolved tasks; see the
[real batch report](implementation/evidence/mostaza-phase2-startup-run/report.md).
Original notebooks/results remain unchanged. That allocation is consumed; another
GPU run needs a fresh decision. Startup success in one run is not a guarantee.
