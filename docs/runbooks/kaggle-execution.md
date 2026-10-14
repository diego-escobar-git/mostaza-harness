# Kaggle integration and supervised execution runbook

Use this runbook to prepare, authorize, execute and close a private Kaggle run.
The workflow is reusable; the competition adapter, resource pins, GPU type and
budgets must be selected again for each competition. Reading this document or
preparing a notebook does not authorize GPU use, purchases, public publication
or competition submission.

Last source review: 2026-10-14. The reference implementation was exercised with
Kaggle CLI 2.2.4 and kagglesdk 0.1.37. Recheck installed help, official contracts,
account limits and browser controls before reuse. Browser labels may change.

## 1. Create a competition profile and run record

Assign an owner who can remain available through confirmed termination, with a
human fallback. Keep bulky private evidence in a new ignored directory such as
`results/<batch-id>/<run-uuid>/`; retain compact, reviewed evidence in Git.
Do not reuse a prior run directory, notebook target or consumed authorization.

Fill in this record before requesting compute. Unknown values remain null with
reasons; they are prerequisites to resolve rather than permissions to guess.
This is a planning template, not the executable Mostaza launch-receipt schema.

| Field | Required content |
| --- | --- |
| Competition | Slug, official rules/starter/API URLs, review date, enrollment and terms accepted by account owner |
| Account and tools | Kaggle username, CLI/SDK/Python versions, auth method and approved credential scope/storage |
| Resources | Dataset/model/wheelhouse refs, exact versions or byte hashes, licenses, expected mount paths and disk needs |
| Code | Branch and commit, dirty-file hashes when applicable, source/notebook/config/archive SHA-256 inventory |
| Experiment | Ordered tasks/folds/seeds, variants, model revision, sampling, evaluator, verification and repair policy |
| Compute | Actual accelerator type/count, internet mode, allocations, concurrency, retry policy |
| Limits | Per-task generation/tool/turn/verification limits, startup allowance, admission/work/export/stop deadlines |
| Spending | Total wall-clock ceiling, physical device-hour ceiling, minimum reported quota, paid-purchase limit |
| Control | Named operator/fallback, polling interval, exact-version cancellation route, escalation deadline and residual risks |
| Approval | Explicit human decision, timestamp, batch ID and limits; distinguish code approval from compute/publication/submission |
| Closure | Terminal observations, quota before/after, outputs, hashes, records, limitations and unresolved incidents |

Separate general Kaggle operations from a competition-specific adapter that
installs pinned dependencies, mounts inputs, starts its official runtime, executes
the approved workload and exports evidence. Never copy Mostaza's model, task IDs
or assumptions into a different competition without review.

## 2. Prepare locally without allocating an accelerator

1. Inspect Git/worktree status and relevant repository instructions. Work on the
   intended branch; preserve historical worktrees and raw outputs. If SDD is
   explicitly active, use its runtime and role/approval rules.
2. Review the current official competition rules, starter notebook, evaluator,
   permitted packages, internet policy, hardware, time limits and submission
   format. Record source versions/hashes. A sample default is not automatically a
   platform limit; document which source establishes each restriction.
3. Acquire only needed authentic inputs through official endpoints or the
   authenticated Data UI. Record provenance and SHA-256. If a dataset version is
   unavailable, state that and identify exact bytes. Do not invent version IDs.
4. Keep GPU dependencies isolated from host tooling. Use compiler/schema checks
   and CPU lifecycle fixtures locally. A passing compiler check is distinct from
   model execution and from a scored competition submission.
5. Prepare a notebook with accelerator disabled, no execution outputs, explicit
   resource pins, bounded serial scheduling and an unbound authorization guard.
   Verify private/offline settings both locally and on the actual launch request.
6. Freeze the evaluation cohort before outcomes. For comparisons, hold model,
   sampling, environment, tasks/order, verification, repair and budget equal
   within each pair. Change budget and retrieval instructions in separate stages.
7. Keep reference solutions, hidden tests and post-run diagnosis outside prompts,
   agent workspaces and submission packages. Allowlist notebook payloads and
   transitive package contents; do not serialize complete task metadata blindly.
8. Run the agreed local gate and, when required, an independent audit of the
   actual source and generated notebook. Hash the audited candidate. Revalidate
   affected checks if execution code or bound payload changes.

## 3. Authenticate through the official client

A browser login and SDK login are separate credential contexts. Check existing
credentials through metadata access first; avoid unnecessary login replacement.
An isolated client environment keeps competition dependencies separate. Select an
installed Python 3.11+ interpreter explicitly: system `python3` may be too old.
Replace `python3.13` below with that interpreter (Mostaza uses `.venv/bin/python`).

```sh
python3.13 -m venv .tools/kaggle
.tools/kaggle/bin/python -m pip install kaggle==2.2.4 kagglesdk==0.1.37
.tools/kaggle/bin/kaggle --help
.tools/kaggle/bin/kaggle auth login --help
```

These are the reference client versions, not a promise of future compatibility.
If authentication is needed, the official browser-based flow is:

```sh
.tools/kaggle/bin/kaggle auth login
```

Have the account owner approve on Kaggle; do not request passwords, tokens or
callback codes in chat. In the reviewed client, login requests `resources.admin:*`
and stores renewable credentials in `~/.kaggle/credentials.json` with mode 0600.
Explain that broad scope and obtain permission for its storage before a new
credential grant. Use remains limited to the task's authorized actions. Existing
valid grants need not be requested again. Never print tokens, credential contents
or authorization headers; keep credentials outside Git and notebook payloads.

The official [CLI authentication guide](https://github.com/Kaggle/kaggle-cli/blob/main/docs/README.md#authentication)
documents OAuth and alternative token methods. If browser login succeeds but the
CLI is still waiting, inspect its callback outcome before restarting the flow.
Report failed/expired authentication; do not work around access controls.

## 4. Read quota and inventory without starting a session

Use authenticated metadata/status/quota calls or existing version pages. Do not
click Run, start an interactive editor session, Save & Run, push/save a notebook,
or call session-start/cancel endpoints while performing read-only checks.
Reading metadata does not allocate the GPU runtime; authentication and metadata
access still involve network requests and may be rate limited.

The reviewed SDK exposes `get_accelerator_quota_statistics` with
`ApiGetAcceleratorQuotaStatisticsRequest`. Preserve the raw `gpuQuota` fields
`timeUsed`, `timeReserved`, `totalTimeAllowed`, reset time and observation UTC.
Typed SDK objects may supply defaults: retain raw field presence, and never
convert an absent field to a measured zero. The following read-only Python
example captures only the quota response through a version-sensitive SDK hook:

```python
from datetime import UTC, datetime
import json

from kaggle import api
from kagglesdk.kernels.types.kernels_api_service import (
    ApiGetAcceleratorQuotaStatisticsRequest,
)

captured = []
with api.build_kaggle_client() as client:
    http = client.http_client()
    previous = http._response_processor
    try:
        http._response_processor = lambda response: captured.append(response.json())
        client.kernels.kernels_api_client.get_accelerator_quota_statistics(
            ApiGetAcceleratorQuotaStatisticsRequest()
        )
    finally:
        http._response_processor = previous
if len(captured) != 1:
    raise RuntimeError("Quota response unavailable or ambiguous")
print(
    json.dumps(
        {
            "observed_at": datetime.now(UTC).isoformat(),
            "quota_response": captured[0],
        },
        indent=2,
    )
)
```

The private hook must be checked again when upgrading the SDK. Do not log other
HTTP responses with it. During an active run, execute network checks in bounded
workers so a stalled request cannot block the operator's browser cancellation.
A worker timeout is missing telemetry, not a terminal session state.

For the selected accelerator, compute reported remaining quota only from present,
valid durations: `totalTimeAllowed - timeUsed`. Preserve reported quota seconds
as platform accounting units. Do not equate them with physical GPU-device seconds
or assume a universal weekly allowance, reservation policy or reset schedule.
Physical device-hours are `device_count * allocation_wall_seconds / 3600`; actual
physical allocation boundaries may remain unknown.

List **all pages** of the account's own notebooks, including private notebooks.
The reviewed SDK supports `ApiListKernelsRequest` with
`KernelsListViewType.PUBLIC_AND_USERS_PRIVATE`. Verify private coverage against a
known owned private notebook. A 403 does not establish that a fresh target is
absent; an incomplete inventory does not either. Use a fresh UUID target and
record evidence that it will not overwrite prior work.

Before launch, inspect known own latest versions, empty Active Events, explicit
reserved zero and stable used quota across two reads at least 30 seconds apart.
Require the approved quota margin and refresh observations immediately before
T0. Treat disagreement or unavailable fields as unresolved. Reserved zero and
empty Active Events are corroboration; neither proves there is no allocation.

## 5. Bind the exact target and approve compute

These identifiers are different:

| Identifier | Meaning and use |
| --- | --- |
| `owner/notebook-slug` | Notebook reference; a dedicated fresh notebook avoids ambiguity about the latest version |
| Notebook numeric ID | Notebook object identity; not a version or an allocation |
| Version number | Human display number, for example version 1 |
| `scriptVersionId` | Opaque saved-version ID from the observed View full version URL |
| `kernel_session_id` | Session identity required by the SDK session-cancellation endpoint; do not derive it from another ID |

The browser route does **not** require obtaining `kernel_session_id`: select the
exact saved version and use its Cancel control. Record the notebook ref, display
version and URL containing the actual `scriptVersionId`. Never guess that ID.
The reviewed CLI `kernels status owner/slug` uses the latest session status; it
does not bind an arbitrary historical version even if a version suffix is passed.
Use it as corroboration only when the dedicated notebook's version identity is
unambiguous. Reconcile identity if any additional version appears.

Present the completed profile, candidate hashes, local validation/audit, number
of allocations/evaluations, GPU type/count, per-task and total budgets, retry
policy, spending ceiling, stop procedure and residual interruption/release risks.
Obtain an explicit decision before the first allocation-capable operation.
Permission for preparation, login or a previous batch is not a new compute grant.
A failed/aborted allocation consumes its single-allocation authorization; another
attempt requires a new decision when retries were excluded.

Use a single-use launch receipt tied to that approval and candidate. Capture UTC
and a local monotonic clock **before** the allocation-capable submission, not in
the first notebook cell. Include queueing, installation, loading, compilation,
tasks, verification and export conservatively. Record local suspend/restart or
clock discontinuity as loss of trustworthy supervision. A notebook timer,
`session_timeout_seconds` or stopping the model process alone cannot prove that
Kaggle released the accelerator.

## 6. Launch once and supervise the saved version

### Prepare the official launch package

For the CLI route, create a dedicated local staging directory containing the
reviewed notebook and `kernel-metadata.json`. This draft has no accelerator;
replace every placeholder and populate only authentic reviewed source refs:

```json
{
  "id": "OWNER/COMPETITION-BATCH-UUID",
  "title": "Competition Batch UUID",
  "code_file": "launched.ipynb",
  "language": "python",
  "kernel_type": "notebook",
  "is_private": true,
  "enable_gpu": false,
  "enable_tpu": false,
  "enable_internet": false,
  "dataset_sources": [],
  "competition_sources": [],
  "kernel_sources": [],
  "model_sources": []
}
```

Match title-derived slug to `id`. Pin resource versions using the formats
accepted by the installed client; inspect actual mounted paths rather than
assuming them from notebook labels. For offline runs, attach the needed wheel
and data inputs before launch; avoid unpinned network installation. Preserve
`docker_image` and `docker_image_pinning_type` when the approved runtime exposes
an exact image pin. An image tag alone may not be immutable.

After approval, bind the guarded notebook to the fresh receipt, prepare the
launch metadata with the approved accelerator flags and actual `machine_shape`,
and validate that no CPU/GPU choice conflicts. Capture T0 before invoking the
launch operation. The reviewed CLI interface is:

```sh
# ALLOCATION-CAPABLE: only after explicit compute approval and fresh preflight.
.tools/kaggle/bin/kaggle kernels push -p /path/to/new-launch-package --timeout APPROVED_RUNTIME_SECONDS --accelerator APPROVED_MACHINE_SHAPE
```

Do not run that placeholder command as a discovery probe. Verify valid machine
shape names without allocating compute. CLI `--timeout` is a secondary runtime
bound, not proof of allocation release. The client rewrites notebook JSON before
submission; distinguish the staged file hash from the serialized request and
saved-version bytes. For an SDK adapter, construct the equivalent inspected
`ApiSaveKernelRequest`, preserving resource/image/privacy settings explicitly.
For a browser route, inspect the same settings before **Save & Run**. None of
these routes is a competition submission, but all may consume compute quota.

Only after approval and successful preflight:

1. Create one new private notebook through the reviewed official save/push route
   or Save & Run UI, with the exact approved mounts, image, accelerator and
   internet setting. Saving/pushing may start execution and consume quota.
2. Record request/response metadata, source/notebook hashes and submission time.
   If the launch response times out, inspect the target read-only. Do not resubmit
   blindly: an uncertain response may already have created a running version.
3. Open the version history and capture the exact version URL and status. Confirm
   the approved hardware from actual runtime evidence. Keep its Cancel route
   available, without opening Edit or starting another interactive GPU session.
4. Poll within the approved interval. Persist each observation's UTC, external
   elapsed time, notebook/version IDs, SDK/browser status, quota and control
   availability. Preserve errors and missingness, not just successful readings.
5. Monitor startup stages and task admission. Start a task only when its full
   worst-case allowance plus export/stop reserve fits. Stop on the approved
   startup deadline, fatal error, broken instrumentation, completion or time limit.

Persist startup observations **before** long imports or installation: stage
begin/end, heartbeat, process PID/exit state, native health, log bytes and errors.
Use UTC for correlation and monotonic time for local durations, labeling clock
scope. Measure installation, compilation, server startup and evaluation separately.
Health readiness does not prove inference or task completion. Keep null with
reasons where a measurement is unavailable.

Retain native server stdout/stderr and lifecycle logs incrementally in the output
directory. An outer `finally` copy can be skipped by platform cancellation. In
Mostaza, a same-filesystem hard link preserves the native log despite unlink by
cleanup; test this behavior with the actual manager and fail before model startup
if unsupported. Other runtimes need an equivalent tested retention mechanism.
A heartbeat is useful evidence of observer activity, not proof of GPU progress.

### Browser fallback when Active Events fails

Open the target notebook's **More options → View versions → version N →
More options**. Confirm its exact-version URL/status and available **Cancel**
control. Active Events becomes auxiliary when it omits the target. A missing
event, failed live-log request or quiet loading interval alone is not a stop
signal while exact-version supervision remains available.

If identity is uncertain, identify the target before acting. If its stop control
cannot be restored within the approved interval (60 seconds in Mostaza), alert
the fallback operator with the exact URL and deadline; stop only the identified
target when required. Never cancel an unrelated session or replace this route
with a new editor session. Browser/network/agent failure can defeat supervision;
disclose that residual risk before approval.

Do not download notebooks, outputs or media while that operation could block
active supervision. In the historical run, a browser download blocked for about
944 seconds despite a requested timeout. Retrieve artifacts after terminal
confirmation; retain live observations through a separate bounded path.

## 7. Stop and confirm termination

1. Request cancellation through the exact saved version before the approved stop
   deadline, or earlier on completion/failure. Record the request UTC and target.
2. Continue bounded observation. `CANCEL_REQUESTED` is intermediate; do not leave
   supervision merely because a button was clicked or a model process stopped.
3. Require the SDK terminal result and corresponding exact-version browser
   terminal result. The reviewed SDK uses `COMPLETE`, `ERROR` and
   `CANCEL_ACKNOWLEDGED`; map browser wording such as canceled to its meaning and
   retain the original wording. Recheck mappings after client/platform changes.
4. Corroborate no active target and stable used quota over two observations at
   least 30 seconds apart. Reserved zero alone is insufficient. Record first
   terminal observation separately from the cancellation request.
5. If confirmation is late or sources disagree, mark termination unconfirmed,
   escalate immediately with the exact URL and continue closure checks. Do not
   launch another allocation or claim a guaranteed physical release timestamp.

A terminal version and stable reported quota support operational closure. They
are not direct telemetry of the physical GPU deallocation instant. Keep that
instant null when unavailable, and describe any remaining accounting uncertainty.

## 8. Export, validate and preserve evidence

For a dedicated notebook whose saved version is still unambiguous, the official
CLI provides `kaggle kernels status OWNER/SLUG` for corroborating status and
`kaggle kernels output OWNER/SLUG -p /path/to/new-download-directory` for outputs.
Check installed `--help` and use the exact-version browser download for the
executed notebook. Reconcile any newer version before trusting latest outputs;
retain version identity for every acquired file. Downloads are not new model
runs but can block, so schedule them after closure.

After terminal confirmation, download the executed notebook and complete output
inventory to the new private run directory. Record source version URL, retrieval
UTC, paths, sizes and SHA-256 values. Inventory omissions explicitly; never
substitute synthetic outputs for absent native results. Keep original downloads
immutable and perform normalization on separately identified derived artifacts.

Retain these artifacts, with secrets redacted before Git publication:

- Approval/profile and single-use launch receipt; client/runtime/resource pins.
- Prepared and submitted notebook hashes, executed notebook, exact-version IDs.
- Prelaunch/monitor/stop/terminal/quota observations, including errors and screenshots.
- Startup schema/events/status, retained server output and lifecycle log.
- Native per-task results, traces, generated patches, verification logs/exit codes.
- Complete acquisition inventory, derived records/report and validation/audit receipts.

Every planned task needs a record. Separate PASS, FAIL, ERROR and NOT_RUN; a
notebook that completed or was canceled does not determine task success. Record
attempted tools separately from charged calls, tokens by documented trace units,
timeouts, patch presence/applicability and verification results. Record coverage
and sources; absent telemetry is null with a reason, never an inferred zero.
Keep partial runs and failures in the comparison denominator. Do not infer
retrieval efficacy from configuration text or tool availability; inspect observed
calls and outcomes. Small exploratory cohorts do not establish significance.

Publication, competition submission and paid purchases are separate actions:
perform them only when authorized for that run. Local artifact validation never
implies permission to publish or submit.

## 9. Incident decision table

| Observation | Required action |
| --- | --- |
| CLI login pending after browser approval | Inspect callback/client completion; do not expose credentials or start GPU as a test |
| Private notebook returns 403 | Check account/private coverage and full inventory; do not assume absence |
| Reserved quota is zero while SDK says RUNNING | Continue exact-version supervision; do not declare release |
| Active Events empty or live logs fail | Use the exact version's status and Cancel route; preserve the discrepancy |
| Startup silent before deadline | Inspect stages, retained server log/process/health; preserve unknown cause if evidence is missing |
| Server process dead or observation instrumentation failed | Preserve available evidence and stop exact target under the approved failure policy |
| Save/push response uncertain | Read-only reconciliation of the dedicated target; no blind retry |
| Cancel requested but not acknowledged | Continue monitoring and escalate at deadline; no new allocation |
| Browser control unavailable | Restore within the approved interval or escalate with exact URL; do not cancel a guessed session |
| Output missing after cancellation | Record missing artifact and NOT_RUN/null where appropriate; no invented measurement |

## 10. Mostaza reference profile and reproducible local checks

This section is a worked adapter, not a universal Kaggle configuration.
A launch requires the current explicit user authorization to be bound into a
fresh single-use receipt after fresh preflight. The earlier single-allocation
authorization was consumed by the canceled run; it cannot authorize another run.

| Parameter | Mostaza proposed value |
| --- | --- |
| Workload | E0-B180 then E1-B180, each requests_7205 → fastapi_15589 → rich_3061; six evaluations |
| Runtime | Official harness, Gemma gemma-4-31b-it-qat-w4a16-ct revision 2, one private offline NVIDIA L4×4 allocation |
| Execution | Serial, concurrency 1, zero retries/restarts; original paired settings/prompts unchanged |
| Task | Generation 180 s, 30 charged tool calls, 50 turns, verification 300 s; outer allowance 600 s |
| Startup | Prove model readiness by minute 30 or stop |
| Admission/export | Last task admission minute 89; end task work minute 99; reserve 300 s for export |
| Stop | Request cancellation by minute 104; escalate unconfirmed closure at minute 105 |
| Ceiling | 120 minutes from external prelaunch T0, ≤8 physical GPU-device-hours, $0 purchases |
| Prelaunch quota | At least 28,800 reported quota seconds; stable ≥30 s; refresh ≤60 s before T0 |
| Observation | Startup heartbeat 5 s, supervisor checks ≤60 s; exact-version browser fallback |

Timing includes queue/startup/install/compile/export conservatively. Network,
operator and platform release delays prevent a guaranteed physical cutoff.
B300, E1-R180, other hardware/models, public notebooks and competition submissions
are outside this proposal. The reusable scheduling constraint is:
`admission_time + worst_case_task + export_reserve <= stop_request_time`.
Choose new limits from evidence and account rules for another competition.

From this repository root after the existing local setup and authentic resources
are available, the following checks do not launch Kaggle or perform inference:

```sh
export PATH="$PWD/.tools/uv/bin:$PATH"
uv run --frozen --no-sync python scripts/prepare_observed_phase2.py --check
uv run --frozen --no-sync python scripts/check_phase2.py --check --cohort experiments/cohort.json --evidence-dir docs/implementation/evidence/mostaza-phase2-budget-retrieval
.tools/official/bin/python scripts/check_startup_observation.py
bash scripts/validate.sh
```

The native startup check uses CPU HTTP/exit/timeout fixtures with the pinned
server manager. The complete gate includes compiler and retained historical real
evidence checks; it does not acquire a new benchmark. To regenerate the unbound
candidate locally, run `scripts/prepare_observed_phase2.py` without `--check`
through the same locked Python command, then recheck it.

Only after new approval and fresh checks, the local binding interface is:

```sh
uv run --frozen --no-sync python scripts/prepare_observed_phase2.py --receipt /path/to/new-approved-receipt.json --output results/NEW-RUN/launched.ipynb
```

That command creates a new local file, never launches Kaggle, and refuses to
overwrite the output. The executable receipt schema and policy are in
[`browser_supervision.py`](../../src/mostaza/evaluation/browser_supervision.py).
The generator is Mostaza-specific, including the permitted username/ref pattern;
it is not a generic competition launcher. Do not reuse the historical
`results/kaggle-phase2-browser-b180/controller.py`: it binds the consumed approval
and earlier supervision policy. Review a future launch adapter against this
runbook and the current receipt/candidate before any allocation.

Historical lessons: preflight finished in 123.759715 seconds, but the first B180
allocation was canceled around minute 12 following a supervision discrepancy,
before the 30-minute startup allowance. No retained native server log or task
trace established why readiness was not observed. The startup cause remains
unknown. Local validation of the new observer passed 217 unit tests, 38 integration
tests, lint/types/build and three CPU native lifecycle fixtures; its independent
audit returned PASS with zero findings. Those are historical local receipts,
not new GPU results or validation of every future competition adapter.

## 11. Sources and handoff checklist

Official contracts to recheck:

- [Kaggle CLI documentation](https://github.com/Kaggle/kaggle-cli/tree/main/docs): authentication and installed command help.
- [Kaggle SDK kernels service](https://github.com/Kaggle/kaggle-sdk-python/blob/main/kagglesdk/kernels/services/kernels_api_service.py) and [request/response types](https://github.com/Kaggle/kaggle-sdk-python/blob/main/kagglesdk/kernels/types/kernels_api_service.py): quota/status/session contracts. Pin the inspected client; main can change.
- [Kaggle GPU guidance](https://www.kaggle.com/docs/efficient-gpu-usage), actual account quota UI and each competition's own rules/runtime requirements. The guidance page did not expose readable body text during this review; derive no fixed numerical limit from it here.

Repository evidence and procedures:

- [Kaggle setup and official resource/compiler pins](../kaggle-setup.md).
- [Experiment isolation, metrics, immutable import and comparison commands](../experiments.md).
- [Startup investigation](../implementation/evidence/mostaza-phase2-observed-startup/investigation.json), [local native validation](../implementation/evidence/mostaza-phase2-observed-startup/local-native-validation.json), [validation receipt](../implementation/evidence/mostaza-phase2-observed-startup/validation.json), [independent audit](../implementation/evidence/mostaza-phase2-observed-startup/audit.json) and [pending quota proposal](../implementation/evidence/mostaza-phase2-observed-startup/quota-proposal.json).
- [Unbound observed notebook](../../notebooks/mostaza-phase2-observed.ipynb) and [startup observer](../../src/mostaza/evaluation/startup_observation.py).

Before handoff, confirm:

- [ ] Profile, source/resource hashes and exact target identity are recorded.
- [ ] Preparation, compute, publication and submission permissions are distinguishable.
- [ ] Operator/fallback, polling and exact-version stop route are ready.
- [ ] Cancellation request and terminal confirmation are separately evidenced.
- [ ] Quota units, clock coverage and unknown physical release time are explicit.
- [ ] Every planned evaluation is represented; missing data have reasons.
- [ ] Raw evidence is preserved, derived outputs trace to it, and secrets are excluded.
- [ ] Pending authorizations, unresolved diagnosis and any next allocation are explicit.


## 12. Instrumented allocation follow-up (2026-10-14)

The later authorized B180-observed-v2 allocation preserved its full startup log
and identified CUDA OOM during vLLM sampler warm-up with 256 dummy requests,
followed by EngineCore failed to start. The API process remained alive while
its engine workers had failed: PID liveness alone is not model readiness.
The operator canceled the exact saved version; SDK/browser terminal states
and stable reported quota confirmed operational closure. All six planned
tasks are NOT_RUN; no runtime correction or retry was attempted. See the
[acquisition report](../implementation/evidence/mostaza-phase2-observed-run/report.md).
The earlier uninstrumented allocation remains inconclusive; do not retroactively
attribute this later OOM to it. Bind a new authorization before any further run.

Unversioned owned notebook URLs can redirect automatically into the editor.
In this preflight, both old forks displayed Draft Session off and Starting Fresh
in Version History, corroborating absent saved-version metadata plus SDK404.
No cell was run. Never treat404 alone as no allocation, and leave the editor
without starting a draft session; use saved-version pages for active supervision.

Compare the actually executed successful notebook with a new prepared notebook
when investigating startup: include explicit environment assignments, not only
server constructor kwargs and package pins. This run exposed four source-level
omissions relative to phase1, documented in the [environment delta](../implementation/evidence/mostaza-phase2-observed-run/startup-environment-delta.json).
Effective inherited values were not recorded, so neither omission nor causality
is established merely by a missing assignment. Review before changing capacity.


## 13. Corrected serial startup profile (2026-10-14 preparation)

The prepared profile was **B180-startup-v3 / serial-memory-v3**. Its subsequent
single-allocation approval was consumed; section14 records the real outcome.
These preparation commands do not authorize a repeat.
Section 10's observed-v2 generator and approvals are historical; never reuse them
to launch the corrected profile. The new [diagnosis and reproducible checks](../implementation/evidence/mostaza-phase2-startup-correction/report.md)
and [quota proposal](../implementation/evidence/mostaza-phase2-startup-correction/quota-proposal.json)
bind the historical six-run batch. Any future batch needs fresh authorization.

For reuse in another competition, compare its successful executed environment
against the actual failing source, restore required variables before any library
imports, and size serving concurrency to the real workload. Never copy the L4,
allocator, model length, package versions or max-num-seqs values without reviewing
that competition's server API, model and scheduler requirements. Snapshot only
allowed child environment fields, installed package/source identities and memory
units/coverage. Keep runtime allocator state unknown unless directly observed.
A native memory error warrants review even if its API parent remains RUNNING.

The corrected Mostaza profile restores phase-1 startup flags, sets both PyTorch
allocator aliases consistently, and passes --max-num-seqs 1 through native
VllmConfig.extra_args. It keeps context32768, memory fraction0.90, Gemma31B,
TP4 and identical paired agent budgets. The notebook records native child values
and driver point samples; these cannot prove peak memory or a successful GPU fix.
No on-the-fly capacity changes or retries are authorized by the proposal.

```sh
.venv/bin/python scripts/prepare_startup_phase2.py --check
.tools/official/bin/python scripts/check_startup_configuration.py
.tools/official/bin/python scripts/check_startup_observation.py
bash scripts/validate.sh
```

After a fresh explicit approval and fresh prelaunch checks, prepare a new local
receipt-bound copy (this command does not submit it):

```sh
.venv/bin/python scripts/prepare_startup_phase2.py --receipt /path/to/new-approved-receipt.json --output results/NEW-RUN/launched.ipynb
```

Use a new UUID notebook and independently verify the launch adapter against the
new policy, notebook hash and common profile. Observe its exact saved version,
keep the browser Cancel route available, request stop by104minutes, seek terminal
confirmation before105, and retain the120minute ceiling with its documented
platform-release residual risk. All clocks include queue/startup/export.


## 14. Completed startup-v3 case and reusable closure lessons

The [real batch report](../implementation/evidence/mostaza-phase2-startup-run/report.md)
records six native results, an actual executed notebook and normal platform
completion around external minute25. Both arms had0PASS/2FAIL/1ERROR, with no
recorded similarity/graph invocation. This confirms startup and acquisition,
not hybrid retrieval effectiveness or task correctness. The approval is consumed.

For future competitions and launches:

- Start the bounded, read-only periodic monitor **before allocation** and keep
  the exact-version browser stop route available. Record monitor and browser
  observation times separately. This case retained a67.08s mixed-observation gap
  versus the60s plan, with incomplete early browser timestamp coverage. A
  periodic wrapper was added during execution and observed intervals under17s;
  it should have been ready initially. Never declare strict protocol compliance
  from a clean terminal state alone, and do not add an unreviewed automatic
  cancellation endpoint as an assumed cure.
- When an AX snapshot clips a log table (500rows here), unchanged clipped text
  is not stalled execution. Use a documented read-only DOM summary that processes
  the complete rendered text before returning a bounded result, or official logs.
  Filter source-code panes so embedded error strings are not mistaken for errors.
- A normal COMPLETE version needs no cancellation request after termination.
  Confirm its exact browser version, hardware/privacy, terminal SDK state, empty
  active events and stable reported quota. Physical release instant stays unknown
  without direct telemetry. Record the observed duration and units explicitly.
- After terminal confirmation, the official browser **Download > Download .ipynb**
  may provide the executed notebook with outputs/counts. This case returned
  counts1..5; SDK get_kernel/pull returned saved source with null counts. Inspect
  and label each artifact instead of assuming the downloads are equivalent.
- Distinguish notebook/platform success, native result acquisition SUCCESS and
  verified task resolution. Applicable reproduction-only patches do not establish
  an implementation. A context exception can coexist with failed verification
  of an earlier patch; retain both dimensions.
- Review the pinned trace serializer before treating omitted optional fields as
  missing telemetry. ATIF here omits empty tool_calls on text/final steps. Count
  explicit call events and recorded usage under declared coverage; retain stricter
  diagnostic nulls/reasons separately. Ignore default zero token counters when
  real usage is in step metrics. Invocation does not prove vector backend use.
- Snapshot audited dirty sources before editing evolving documentation after a
  run. A base Git commit plus content hashes identifies the executed correction;
  it must not be represented as clean commit-only provenance. Preserve native
  manifests and disclose any host-derived comparison identifiers or URL refinement.

Every new context/sampling/retrieval treatment needs its own reviewed proposal,
comparable conditions and explicit GPU authorization. Never retry a consumed
allocation to fill a failed or missing row without that decision.
