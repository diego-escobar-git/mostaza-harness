# Reproducible experiments

E0 is the minimal single-agent baseline; E1 changes exploration instructions only.
The exact three-task cohort has been frozen and executed in both arms on Kaggle
with Gemma 4 31B and four NVIDIA L4 GPUs. Kaggle notebook version 2, run 358139443,
completed all six official task executions; notebook completion is separate from
task resolution. The retained ZIP SHA-256 is
`a654d3f18055d87e7715bab681ff7a055cbd70098414abeb8f093d9da3144cb3`.

All six tasks reached the preserved one-minute session timeout. Requests produced
an applicable generated patch in each arm; official verification reported one
failed, 205 passed and 13 skipped tests in each case. The failing assertion still
observed empty credentials instead of no credentials. FastAPI and Rich produced
no patch, so their verification was not run and their resolution remains unknown.
No task was resolved successfully. This evidence establishes actual model/harness
execution, not a successful software fix or a retrieval superiority claim.

The native trace `tool_calls` measurement counts recorded attempts, including
exempt `get_status` calls and attempts rejected by budget checks. E0 Requests,
FastAPI and Rich recorded 7, 10 and 12 attempts; their native charged counts were
7, 10 and 10. E0 Rich's extra two attempts were one exempt status call and one
BudgetExceeded rejection. E1 recorded 6, 8 and 8 attempts, charged 6, 8 and 7.
The official `check_budget` increments accepted charged calls before the target
executes, so subsequent CommandError responses remain charged; `get_status` and
`submit_patch` are exempt, and budget-rejected attempts are not charged. Native
counts are preserved without capping them to the configured allowance.

E0 Rich made one `search_similar_code` call; all E1 tasks made none. Neither arm
called `get_code_neighbors` or `get_code_subgraph`, and neither called
`submit_patch`. Thus these time-limited runs did not exercise the E1 graph/vector
retrieval strategy. Missing localization, context relevance and full shell/native
search measurements remain null with reasons. Descriptive token/tool differences
cannot establish that hybrid retrieval improved outcomes.

Raw source files are retained read-only under the ignored
`results/kaggle-v2-358139443` directory; only the five declared compact artifacts
enter Git. The executed notebook embedded normalizer SHA-256
`57c94f88cf97fdc0ed9bbf168ffe5334076a11b6a71c30ecd6e0ea3e77564859`.
Host postprocessing now preserves native timeout reasons for FAIL records and
renders deterministic per-task and source-linked tool diagnostics. This correction
changes neither the original model execution nor measured numeric values; the
acquisition/postprocessing receipt records both source versions separately.
Unit/integration fixtures remain exclusively synthetic source-protocol checks.


## Agent inputs and reference isolation

`mostaza.evaluation.tasks.agent_task` accepts only instance ID, repository,
exact base commit and issue text. Never serialize an official Task object into
agent inputs, logs, prompts or submissions: it contains private `patch`,
`test_patch`, test-node and hint fields. Task metadata and source repositories
remain on the host outside the agent workspace. `export_base_snapshot` exports
exactly the task base commit without `.git`, refs, future commits, untracked files
or symlinks. It is a local isolation utility; official execution continues to use
the organizer's generation/verification sandbox pipeline. Reference mappings for
recall and relevance belong exclusively to post-generation analysis.

## Immutable result contract

Manifest schema 1 requires experiment/run IDs, E0/E1 arm, run kind, UTC timestamp,
40-character code commit, SHA-256 working-tree/config/archive digests, the exact
required 31B model, and harness/wheelhouse/dataset version/hash/source pins.
The ordered cohort contains instance ID, repository, base commit, snapshot hash
and selection rationale. Inference, budgets, environment, limitations and durable
source run ID are explicit. The cohort is frozen before outcomes are observed.

Every cohort task gets exactly one record, including a NOT_RUN record when an
execution is missing. Records distinguish PASS, FAIL, ERROR and NOT_RUN, patch
presence and independently verified validity, test outcome/exit code, resolution,
result/trace artifact hashes, and all metrics. Missing metrics have null value and
source, availability `unavailable`, and a reason. Measured and estimated values
have source identifiers; estimates never enter measured averages. Characters are
characters, not tokens. PASS requires a present valid patch and verified passed
tests/resolution. Real execution records require result and trace hashes.

Import checks the full schema and publishes canonical JSONL plus a manifest bundle
under SHA-256 filenames. Atomic create-only publication supports repeated or
concurrent imports; a create-only experiment/run identity binding rejects conflicting
re-imports, and reload verifies both hashes. Files are read-only to discourage
accidental edits; hashes detect drift even if an owner changes permissions. Raw
traces stay outside Git. This is tamper detection, not a cryptographic attestation
that a user-supplied source was actually executed.

```bash
scripts/run_experiment.sh import /path/to/manifest.json /path/to/records.jsonl --output /path/to/immutable-store
scripts/run_experiment.sh report /path/to/E0-bundle.json /path/to/E1-bundle.json --json /path/to/comparison.json --markdown /path/to/report.md --resource-review docs/implementation/evidence/mostaza-phase1-foundation/resource-review.json
```

Run these from the locked host environment prepared by `scripts/setup.sh`.
For the actual benchmark, `--resource-review` loads source-derived native tool
analysis from the declared review and reproduces the diagnostic report exactly.
Omit it for fixture reports without native source analysis.
Comparison requires identical experiment, run kind, code/tree, model, resource
pins, cohort ordering, inference settings, budgets and environment. Configuration
and archive digests may differ between treatment arms. Duplicate and absent task
records are rejected; NOT_RUN remains in the cohort denominator. Every metric
reports its measured/estimated pair count, unavailable reasons, E1-minus-E0 values
and raw provenance. Failures remain represented. Recall@K and relevance require
an explicit content-addressed post-run mapping and matching definitions across
arms. These small exploratory reports make no significance or superiority claim.

## Verified official API and actual integration

The inspected official starter notebook version 3 and pinned organizer wheel
`swegemma==0.2.11` demonstrate:

```python
from swegemma.config import EvalConfig
from swegemma.evaluate import Evaluator
from swegemma.models import load_tasks

# Set up models with the notebook's adk_submission.VllmServer and
# create_model_registry; retain Gemma 4 31B and the official L4x4 settings.
# Construct EvalConfig with exact task/snapshot/graph/embedding/wheels paths,
# models, submission_dir, results_dir, sandbox="subprocess" and approved budgets.
# The official runner calls:
result = await evaluator.evaluate_task(task=task, task_index=1, total_tasks=3)
```

`mostaza.evaluation.runner.describe_runtime(config, vllm_config)` captures actual
inference/cache/compaction, budget and submission configuration digests. The thin
`evaluate_official(config, manifest, server=server_instance,
archive_path=archive_path, wheelhouse_dir=wheelhouse_dir)` adapter requires a live
local model server and validates model registry/endpoint, exact model mount,
actual configuration/budgets, archive bytes/closure, task bytes, frozen snapshot
reconstruction inputs and the pinned organizer/full wheelhouse content before
calling the official evaluator. It does not start the server or replace the harness.

`environment.snapshot_validation` maps task IDs to full authenticated snapshot
resource receipts. The runner verifies each standalone archive hash and extracts
only Git metadata for read-only checks: exported HEAD/tree must match the verified
original-base tree, every ref must be an exported HEAD ancestor, and every commit
object must belong to that ancestry. The original commit ID can be rewritten by
the official fast-export/import workflow; no timestamp heuristic or missing-object
exception establishes safety. Unreviewed reconstruction receipts fail closed.

The raw result extension identifies the effective patch after the official
protected-file filter and retains the original generated patch digest. The pinned
evaluator's host-only secret hydration supplies the exact target-test protection
paths; reference patch and test contents are never copied into result extensions.
`normalize_official_result(result_path, manifest, private_bundle_root)` checks task
and trace identities, hashes raw evidence, preserves apply failures versus pytest
failures versus infrastructure/verification errors, and leaves unknown resolution
null on ERROR. Passing official verification establishes effective-patch validity;
patch presence alone does not. Raw traces/patches/test output remain private.

Recorded ATIF-v1.7 (or native legacy) usage supplies token counts. Default zero
`TaskResult.total_tokens` and trace final-summary zeros do not establish a
measurement. Total tool calls count recorded native calls. Full read/search counts remain
unavailable because native `read_file`/similarity counts omit shell operations. Unique explored files,
localization time, repairs, graph expansion counts and relevance remain unavailable
unless separately instrumented and sourced. ATIF step usage already aggregates
its tool-call usage and is counted once. `official_execution_receipt` requires a
recorded native agent response for its inference-observed flag; server readiness
alone does not establish inference.

Native protocol tests exercise the actual pinned EvalConfig, ModelRegistry,
VllmConfig/VllmServer, TaskResult and SessionTrace classes with synthetic fixtures,
without starting a model or sandbox. This source-contract validation establishes
no real compatibility or outcome on their own. The separate retained live run
now provides actual official execution evidence with the failed outcomes above.

Official sources: [starter notebook](https://www.kaggle.com/code/ryanholbrook/getting-started-gemma-4-developer-agent)
and [organizer wheelhouse](https://www.kaggle.com/datasets/metric/gemma-4-developer-agent-wheelhouse).
The phase plan records notebook/wheel versions and hashes. Do not upgrade one arm
independently. HARNESS_README and authentic submission defaults are required
before completing the official-run integration.

## Declared real evidence

The real benchmark stage owns all five approved evidence outputs. This stage
creates none while actual runs are unavailable. The read-only gate is:

```bash
uv run --frozen --no-sync python scripts/check_evidence.py --require-real-paired --cohort experiments/cohort.json --evidence-dir docs/implementation/evidence/mostaza-phase1-foundation
```

`cohort.json` schema 1 uses `frozen_at` (UTC), `selection_basis: pre-outcome`, and
`tasks` matching the manifest cohort: one psf/requests, one fastapi/fastapi, and one
textualize/rich or encode/httpx task. `resource-review.json` needs status VERIFIED
and `official_resources_reviewed: true` plus the resource-review evidence.
`official-validation.json` schema 1 contains `manifests` keyed E0/E1 and `compiler`
receipts keyed E0/E1 with PASS status, matching archive digest and source reference.
Its `execution` receipts keyed E0/E1 require the exact `model`,
`model_inference_observed: true`, a matching `source_run_id`, and an inspected
trace `source` showing actual inference; token measurements may still be null.
Real manifests identify environment platform `kaggle`, gpu_count 4 and gpu_model
`NVIDIA L4`, with durable `https://www.kaggle.com/code/...` run identifiers.
`paired-results.jsonl` contains exactly six completed real records, with sourced
trace evidence of the required model inference. `comparison.json` and `report.md` must
match recomputation byte-for-byte. Missing resources, compiler receipts, actual
runs or metrics cannot be replaced with simulation; this check fails closed.

The gate also verifies the acquisition receipt's project-relative retained source
root, original ZIP and executed notebook paths under ignored `results/`. It checks
all native inventory hashes, ZIP-retained byte equality, the executed notebook's
literal embedded payload and retained inputs, actual manifests/archives/config
bindings and required-model trace/server provenance. It then recomputes task
records and tool analysis from the native files and compares every declared value.
Regenerating summaries cannot legitimize a measurement inconsistent with its
trace. Missing, changed, escaped or symlinked sources fail verification. The
executed code commit and payload hashes are checked against the immutable executed
notebook; current host postprocessing hashes are bound separately and refreshed
when those helpers change. A later Git commit does not rewrite the runtime overlay.

The next research steps follow observed real outcomes: examine localization and
missing metrics, inspect repeated context and verification failures, and plan
further experiments from those measurements. Each arm recorded PASS 0, FAIL 1,
ERROR 2 and zero resolved tasks. All six sessions timed out; E1 made no vector or
graph tool call. These authentic observations provide no retrieval-benefit or
performance-superiority conclusion.


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
