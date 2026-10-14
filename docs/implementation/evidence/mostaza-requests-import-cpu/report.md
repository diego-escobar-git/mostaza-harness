# R-IMPORT-CPU-01: Requests imports in a derived CPU layout

Status: final corrected gate PASS; independent final audit PASS, zero findings. No GPU/model,
Kaggle session, Discussion, native verifier change or production activation.

## Result and limits

The native patch_path delta binds Requests to the snapshot inside actual native
pytest processes. It adds only requests -> src/requests (Git symlink mode 120000),
leaving original archive/product bytes unchanged. Retained agent patches still
modify their original product paths. The native verifier, command, environment,
setup decisions, JUnit protections and cleanup remain unchanged. The derived CPU
layout is a distinct input, not the original unchanged-input protocol.

Both complete gates observed the same pattern:

| Requests case | Without alias | With alias and proven source binding |
| --- | --- | --- |
| Baseline | Installed 2.34.2; origin fails; four behavior tests pass on installed code | Snapshot 2.32.5; origin passes; empty machine/default fail; missing/valid pass |
| Retained E0-B180 | Same installed-code mismatch | Snapshot 2.32.5; origin passes; empty/valid pass; missing match raises TypeError |
| Retained E1-B180 | Same installed-code mismatch | Snapshot 2.32.5; all five own nodes pass; native resolved=true for this own Task |

These are independently authored CPU diagnostics, not original Kaggle task tests,
hidden tests, official task scores or new model-generated patches. E1's PASS
supports only these four behavior cases plus origin under this layout. It does
not establish general task resolution, statistical significance, E1 superiority
or hybrid retrieval efficacy. Historical Kaggle outcomes are unchanged and their
exact verifier imports remain unknown.

Generic src-package controls prove sensitivity: faulty baseline fails, correct
patch passes native verification/JUnit, and incorrect patch fails, all with verified
binding. Negatives count as controls only when intended assertions are reached.

## Comparable pairs and provenance

Each Requests U/B pair uses byte-identical test_patch, identical retained agent_patch,
archive, interpreter/dependencies, limits, five required nodes and native command.
Only patch_path absent/present differs. Pair hashes/conditions are checked, and
each stage reaches all five own nodes in one actual pytest process. Native task
IDs, sandbox paths and process IDs differ naturally. Shared receipt destinations
must be absent before execution; atomic events are moved to stage evidence after
return, preventing stale reuse.

Witnesses include raw/canonical parent package, utils and function filenames while
the alias exists; file hashes; expected loaded-code fingerprint; PID/parent PID;
interpreter/Python/pytest; cwd and ordered sys.path. Every B case selects
workspace/src/requests canonically, every U case selects installed site-packages.
Imported public version 2.32.5 and unchanged installed distribution metadata 2.34.2
are separate facts. Coverage is these reviewed modules/function inside own tests,
not every dependency/submodule/pytest phase.

Original archive SHA256:
42dc3d360f842a5c7a66d0008ac05447fcd807dc33ee8cc18d2f2d4876283106

Original pre-overlay tree: 683d44befe0d3519469011c35e46f332eebbc010. Each layout manifest
records the original tree, one-link delta hash and derived prebootstrap tree.
Native bootstrap later adds its usual pytest/config files; the derived complete
workspace is not mislabeled as the original tree. No install, PYTHONPATH/.pth/
sitecustomize repair, native interception/subclass/monkeypatch or custom loader.
No original Task.patch/test_patch was used as diagnostic input.

## Implementation and exact gate

New host-only requests_import_cpu.py validates deltas, immutable inputs, raw/
canonical witnesses and paired results. The fixture script calls unmodified
verify_task with the actual SubprocessManager. The checker runs nine new cases.
The gate runner reuses frozen watchdog/disk primitives and owns the whole-gate
deadline. New spec and append-only runbook guidance define the CPU-only boundary.
V-CPU-01 code/spec/tests/evidence, native pins and original experiments/notebooks/
manifests/locks remain unchanged. The unrelated dirty closed SDD plan is preserved.

From the phase2 worktree, the approved entry point is:

```sh
.venv/bin/python scripts/run_requests_import_cpu_gate.py --check --attempt 1
```

It executes the exact ten commands in plan-for-approval.md, including eleven old
regression native calls and nine new layout calls. Existing attempt directories
are exclusive evidence. Both approved attempts are now consumed; another native/
full-gate run requires a new budget.

Gate 1 passed ten commands in 142.79s. Audit then found
RI-A01: outer timeout stopped controllers without an explicit temporary cleanup
attempt. The correction derives current roots only from observed worker output
arguments, validates namespace/UUID/case scope, and sweeps only fixture/sandboxes
after process termination. Prior roots, results/logs and symlink targets are
preserved. Focused checks independently passed 26 tests, Ruff and strict typing.

Gate 2 passed all ten commands on corrected source in 176.90s,
below 1200s: 328 unit tests, 49 integration tests, strict typing on 46 source files,
Ruff, package build, official compiler validation, old source/evidence checks
and 20 serial native calls. The new matrix completed 9/9 started/results/assessed
in 33.40s. Outer cleanup was attempted and complete for both
observed new/legacy matrix roots. All native per-case cleanup flags are true;
no fixture/sandbox temporary directories remain there.

Total across two justified complete gates: 40 native calls (22 old regression,
18 new layout). No automatic retries or native auditor reruns. These are CPU
diagnostics, not 40 Kaggle evaluations. Limits: 30s native commands/pytest, 90s
per case, 20min per whole gate, 1GiB polled owned-artifact ceiling. Retained raw
evidence: 1693554 bytes. Actual peak disk and CPU-process time were not retained
and remain null with reasons. Native usage defaults are not measured inference/
billing metrics. Raw JUnit is consumed internally and removed: null with reason.

## Evidence, audit and next boundary

prerequisites.json pins original inputs and historical V-CPU-01 files.
tested-source-inventory.json preserves gate1 source; corrected-source-inventory.json
pins gate2 source. corrective-attempt.json records the actual audit finding/repair.
gate-attempts.json preserves both receipts. cpu-results.json retains actual
outcomes, pair/input hashes, witnesses and offline reclassification.
raw-inventory.json pins ignored raw logs, deltas, tests and native results.

Final independent audit returned PASS with zero findings, after reviewing the
complete relevant delta and actual final evidence. See audit.json. Commit/push/
update existing PR2 toward develop is authorized following these checks. No merge;
the unrelated dirty closed SDD plan is excluded from this commit.

GPU readiness remains false; actual_scorer_runtime_parity is null with a reason.
This demonstrates binding for this explicit macOS/Python 3.13.15/pytest 9.1.1 CPU
layout. Historical Linux/Python 3.12.13/pytest 8.4.2 portability, private scorer
identity and real notebook/runner integration remain separate work. No production
pipeline, notebook payload or agent context was changed to activate the alias.
No new GPU batch, native rerun or organizer outreach is implied.
