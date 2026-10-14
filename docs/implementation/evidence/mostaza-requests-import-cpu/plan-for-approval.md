# R-IMPORT-CPU-01: Requests workspace import binding — proposal

Status: PROPOSED, awaiting approval. Ordinary CPU follow-up; no SDD restart.
This proposal and prerequisites.json are the only new artifacts. No layout delta,
new test implementation, installation, sandbox or native verify_task execution
was performed during planning. No commit, push or PR change is part of planning.

## Objective and verified starting point

Correct and measure Requests imports inside the actual native CPU pytest process,
so diagnostics exercise the snapshot's patched product. Preserve native verification
source, command, protection rules, JUnit decisions and cleanup. Separate import
correction from whether the retained agent patches satisfy our own behavior tests.

Worktree: /Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness.
Branch: sdd/mostaza-phase2-budget-retrieval. Inspected HEAD:
bf9760d4bbcfca94410469966c6a50abd970e34f. Existing PR2 targets develop.
The pre-existing dirty closed SDD plan must remain byte-identical and unstaged:
SHA256 5457a535f1e8457789d73ef38f0346c04ded2d18424a172e12d7b3ed6e66a8d5.
No modification to the phase1 worktree.

V-CPU-01 completed eleven native CPU invocations and an independent PASS audit.
Its three Requests cases imported the same installed requests.utils rather than
workspace/src/requests/utils.py. All four own behavioral tests passed on installed
code; origin assertions failed. This did not validate either workspace patch.
Native subprocess setup returns before editable/dependency installation. Its
PYTHONPATH contains the workspace root, without automatically adding workspace/src.
Changing the caller's PYTHONPATH would not override the manager's own environment.

Pinned swegemma 0.2.11 verify_task publicly accepts patch_path and forwards it to
extract_snapshot. That routine applies an incremental delta before creating the
verification baseline; agent_patch and the test_patch follow later. This provides
an existing input route without intercepting sandbox creation or changing native
code. The original Requests archive has no root requests entry; its pyproject
selects packages under src and src/requests/__init__.py exists.

These source facts establish API availability. They do not establish that the
proposed alias works, is supported by the private scorer or may be used in a real
competition run. CPU validation is the next test, not an already proven repair.

## Proposed correction: explicit CPU-only layout delta

Use the unchanged acquired Requests archive plus a separately identified, hashed
layout delta through the native patch_path argument. The complete delta is one
new relative symbolic link at workspace root:

```
requests -> src/requests
```

Use Git symlink mode 120000. No Requests source bytes, tests, configuration,
packaging metadata or existing links are edited by the layout delta. The target
must be an existing in-workspace package directory with __init__.py. The root alias
must not exist, be tracked or be ignored before application. Refuse conflicts,
absolute/escaping/circular targets, extra paths, renames or other file modes.
Generate and verify the delta in owned scratch data; retain its exact patch bytes,
SHA256 and path/mode/target manifest. Do not accept arbitrary user-supplied patches
as layout deltas or fall back to another import trick.

The archive remains byte-identical. Its original exported Git tree remains pinned
and checked BEFORE overlay application. The source layout before native bootstrap is
an explicitly derived input: its delta adds this link, so its complete tree must
not be labeled identical to the original tree. Native bootstrap later generates
its normal pytest/config files as well; distinguish those native additions from
the layout delta, which must touch only the declared link. Record original archive/tree,
layout-delta hash, derived layout and retained agent_patch hash separately.
The native eval_baseline may include the added alias; document this fact.

This changes CPU workspace layout, not the native verification command or source.
It is NOT the unchanged-input V-CPU-01 protocol, and must use new case/run IDs.
Do not alter that protocol's strict raw-path assertions to make its old cases pass.
Do not modify its evidence/readiness or silently enable this route in experiments,
runner.py, notebooks, agent contexts, Kaggle inputs or submissions.

No pip/editable install, dependency change, .pth, sitecustomize, conftest repair,
PYTHONPATH change, sys.path injection, custom loader, module reload, verifier/sandbox interception wrapper,
subclass/name spoof or monkeypatch. Keep the real SubprocessManager with inherited
site-packages and the exact native pytest/JUnit behavior. No Docker/Colima changes,
image/VM creation or new services. If native behavior rejects/removes the valid
link, record BLOCKED; propose a different route for approval instead of improvising.

## Specification delta and implementation stages after approval

Add docs/specs/requests-import-cpu.md for this contract and append a clearly scoped
section to docs/runbooks/kaggle-execution.md. Preserve all earlier sections and the
V-CPU-01 specification, code, tests and evidence pinned in prerequisites.json.
The old no-further-execution statement is a historical authorization checkpoint;
new approval would cover the eleven regression invocations explicitly listed here.
It would not reopen any previous GPU authorization.

1. Implement host-only src/mostaza/evaluation/requests_import_cpu.py: allowlisted
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

Do not change old files merely to make their frozen checks accept the new route.
Freeze the current runbook as an append-only prefix. Freeze original experiments,
notebooks, manifests/locks, native wheel/install files and historical evidence.
No fresh source/data/model downloads; use the existing pinned resources.

## New matrix: nine native invocations

Use ordinary owned Git baselines and explicit own required test nodes; no reserved
mock bypass and no original Task.patch/test_patch. A test failure is a valid
negative control only when it reaches the intended assertion with proven binding.
Unrelated setup/collection/dependency failures are BLOCKED, never successful controls.

| ID | Input | Required result |
| --- | --- | --- |
| L01 | Owned generic src package, valid root alias, faulty baseline | Origin/function binding true; required behavior fails; native resolved=false. |
| L02 | Same package/tests/alias with a generic correct patch | Binding true; native resolved=true, exit 0, required passing nodes validated natively. |
| L03 | Same package/tests/alias with a deliberately wrong patch | Binding true; required behavior fails; native resolved=false. |
| R00-U | Requests baseline, no layout delta | Five own nodes reached; installed-code binding mismatch measured and origin rejected. |
| R00-B | Same baseline plus layout delta | Five nodes reached; parent requests and requests.utils bind canonically to workspace/src/requests; origin passes. |
| R01-U | Retained E0-B180 agent_patch, no layout delta | Same unbound control with that exact agent patch. |
| R01-B | Same E0 agent_patch plus layout delta | Verified binding to the actual E0-patched utils file/function, origin passes. |
| R02-U | Retained E1-B180 agent_patch, no layout delta | Same unbound control with that exact agent patch. |
| R02-B | Same E1 agent_patch plus layout delta | Verified binding to the actual E1-patched utils file/function, origin passes. |

Each U/B pair has the same pinned archive, agent_patch, interpreter, dependencies,
manager, sampling-not-applicable status, limits, own test_patch bytes, five required
nodes and native verification command. Only patch_path (absent versus the manifest-
controlled layout delta) differs. Native instance IDs and generated sandbox/PID/
JUnit paths naturally differ and are recorded, not experimental knobs.

The same generated test_patch bytes must be used in BOTH stages of each Requests
pair. To avoid embedding stage-specific receipt paths into tests, use one owned
host receipt destination per pair, outside native cleanup. Require it absent before
each invocation, atomically publish the test-body events, archive/move it to the
stage evidence after return, then require it absent again. Fail on stale data.
Bind stage to returned TaskResult.task_id, observed process and host invocation
record, not an event's self-reported stage. Never reuse a prior stage's witness.

The four behavioral tests remain the independently authored V-CPU-01 cases:
empty matching machine credentials, empty default credentials, missing match and
valid credentials. Select temporary local netrc files through NETRC inside each
owned test body, restore it afterwards, and perform no network access. A fifth
origin assertion checks the parent package, utils module and loaded target function.
Keep diagnostics and forensic outcomes outside all agent/submission payloads.
Do not introduce a newly corrected Requests patch or any reference solution.

The new protocol permits a declared alias, so __file__/co_filename spelling can
include workspace/requests while the canonical target is workspace/src/requests.
Record BOTH raw and resolved paths inside pytest while the alias still exists;
after cleanup a host Path.resolve alone cannot reconstruct a removed symlink.
Require the exact manifest alias/target, canonical in-workspace paths, actual file
hashes and expected loaded-code fingerprint for each retained patch. Independently
validate raw path spelling against the declared mapping; a forged resolved-path
claim, arbitrary outside alias or matching file with different loaded code fails.

Require parent requests.__file__ and requests.utils.__file__ to select the expected
workspace package and utils files. Record the loaded function's __module__, raw and
canonical co_filename, fingerprint/algorithm, PID/parent PID, executable, Python/
pytest, cwd and ordered sys.path. Record imported Requests' public version separately
from installed distribution metadata; they need not agree. Coverage is exactly
these reviewed modules/function inside own diagnostic test bodies, not every
Requests submodule, every pytest phase or all dependencies. No such broader claim.

## Acceptance and interpretation

All ten gate commands must exit 0 and independent audit must return PASS with zero
findings. All three generic control expectations must hold. All six Requests stages
must execute all five own nodes, return valid in-process witnesses, use the exact
paired test_patch and reach the intended native assertions. Every U stage must
reproduce the installed-code mismatch; every B stage must prove actual patched
workspace binding and pass the origin test. If the control no longer reproduces,
stop for environmental diagnosis, not automatic baseline relabeling.

Behavioral results for baseline/E0/E1 are separate observations. Do not require or
manufacture an E1 PASS to accept a correctly demonstrated import remedy. Preserve
native resolved/exit/error_message and each behavioral outcome. Bound behavioral
failures can be meaningful results with correct imports; report them exactly.
Unexpected setup/import/collection failure, skipped required observation or missing
receipt blocks this milestone. The generic correct/wrong controls prove that the
protocol can distinguish real patch effects with verified binding.

The successful milestone label is CPU_REQUESTS_IMPORT_BINDING_VALIDATED only if
those structural/control requirements pass. It is never a Kaggle task-score label.
Use null plus reasons for absent coverage, raw JUnit (removed by native cleanup),
CPU process time, unrecorded peak space and private-scorer parity. Retain numeric
units and measurement scope. Track started/native-results-present/assessed counts
separately, wall seconds, native errors, cleanup, delta and source hashes. Native
TaskResult usage defaults are not independently measured inference/billing metrics.

Keep ready_for_gpu=false and existing binding_readiness unchanged. No promotion of
historical verifier origins, private scorer equality, organizer permission or
hybrid retrieval efficacy. CPU success would demonstrate this explicit layout
variant only; its applicability to a future real Kaggle environment is a separate
decision with its own provenance, comparability and execution authorization.

## Exact gate proposed for approval

From the phase2 worktree above, the new gate runner executes these ten commands
in this order. All are mandatory; command 9 preserves the old eleven-case matrix.
Command 10 executes exactly the nine NEW cases. No baseline is borrowed from an old
run and neither matrix may be rerun implicitly by tests/auditor.

```sh
bash scripts/validate.sh
.venv/bin/python scripts/check_phase2.py --check --cohort experiments/cohort.json
.venv/bin/python scripts/prepare_startup_phase2.py --check
.tools/official/bin/python scripts/check_startup_configuration.py
.venv/bin/python docs/implementation/evidence/mostaza-phase2-startup-run/recompute.py --check
.venv/bin/python scripts/check_context_verification.py --check
.venv/bin/python scripts/check_pcv01.py --check
.venv/bin/python scripts/check_pcv01_scorer_contract.py --check
.tools/official/bin/python scripts/check_verify_task_cpu.py --check
.tools/official/bin/python scripts/check_requests_import_cpu.py --check
```

After implementation, the bounded entry point is:

```sh
.venv/bin/python scripts/run_requests_import_cpu_gate.py --check --attempt 1
```

The new checker and runner do not exist yet and have not been executed. The runner
must own the whole-gate deadline and track/stop detached native child groups;
per-case timeouts alone do not enforce a whole-gate budget. Capture source/input
inventories before execution, exact argv, versions, command exits/times/log hashes,
result/receipt inventories and immutable-input checks after cleanup. Do not change
source during a gate. A later source correction requires affected focused checks
and a complete final gate; evidence-only reporting must not rewrite raw results.

## Proposed limits, audit and closure

CPU only. Per complete gate attempt: 20 native verify_task invocations maximum,
serial (11 old regression + 9 new), 30s native command/verification timeout, 90s
per-case ceiling, 1200s TOTAL wall deadline for all ten commands. Some old checks
also spawn their existing pytest/fixture processes; those are included in the
1200s wall budget, not counted as extra verify_task calls or model evaluations.

At most TWO full gate attempts: one initial and one only after a demonstrated
failure/audit finding, a concrete repair and focused non-native regression checks.
This is a corrective attempt, not a silent replay. No automatic case/command retry.
Max 40 native invocations and 40 min gate wall time across both. Auditor uses raw
records/source and focused non-native checks; no extra native matrix. If another
full run is needed, report the exact blocker and seek a new budget before running.

At most 1 GiB additional owned temporary/retained artifacts at any time, checked
before launch and during execution across both new outputs and newly generated
V-CPU-01 regression outputs. Record the sampled peak if implemented, otherwise null
with a reason; do not claim a physical instantaneous peak from polling alone.
Retain prior evidence; cleanup only this run's owned temporary trees. No bulk copy
of wheelhouses/site-packages or download/install/upgrade. Missing cached inputs,
resource ceiling, cleanup failure or pin drift are BLOCKED outcomes.

Approval would cover the specification delta, narrowly scoped CPU implementation,
exact ten-command gate/runner, those budgets, independent audit/corrections and
commit/push/update existing PR2 toward develop after final gate/audit PASS. No merge.
This authorizes no GPU/model call, Kaggle session/API/browser mutation, submission,
Discussion/message/notebook publication, real-verifier activation or production input change.
No worktree migration/new SDD state and no change to the previous worktree.

## Primary references and what they establish

- Pinned local swegemma 0.2.11 verification.py, container_setup.py and subprocess.py:
  native patch_path route, application order, skip behavior and actual command/env.
  Hashes and current V-CPU-01 evidence pins are in prerequisites.json.
- https://docs.python.org/3.13/reference/import.html — ordinary package/path search
  and module caching. Do not clear sys.modules or install a loader to force a result.
- https://docs.python.org/3.13/library/sys_path_init.html — path initialization;
  effective native arguments/environment still govern this subprocess.
- https://docs.python.org/3.13/library/pathlib.html#pathlib.Path.resolve — canonical
  paths resolve symlinks; raw spellings and in-process observations remain needed.
- https://git-scm.com/docs/diff-format — patch extended headers/file modes; the exact
  accepted symlink delta must still be proven through the pinned native path.

Online Python3.13 documentation currently identifies 3.13.16; actual cached CPU
runtime is 3.13.15. Documentation and this source review are not an execution receipt
or an organizer/private-scorer compatibility attestation.
