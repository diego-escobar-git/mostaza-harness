# N-IMPORT-CPU-01 — Notebook integration and bounded CPU portability

Status: PROPOSED; awaiting approval. Planning only, ordinary follow-up to the closed
SDD workflow. No new native matrix, notebook execution, package installation,
Kaggle action or implementation has been performed for this proposal.

## Objective and evidence

Integrate the R-IMPORT-CPU-01 layout remedy into a NEW, GPU-disabled notebook
candidate and prove that its actual host preparation selects the same native
reconstruction inputs for agent setup and verification. Test relocatability in
CPU and explicitly delimit platform coverage.

Worktree: /Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness.
HEAD: bcec689aadc9be0801de6b1c7e560d776e17299e.
PR2 is OPEN, targets develop, and has that head (authenticated read-only query).
Do not modify the phase1 worktree or the already dirty closed plan. Its current
SHA256 is 5457a535f1e8457789d73ef38f0346c04ded2d18424a172e12d7b3ed6e66a8d5.

R-IMPORT-CPU-01 already proved, using unmodified verify_task and SubprocessManager,
that one native layout delta makes Requests resolve to workspace/src/requests.
Bound baseline tests fail; retained E0 produces a TypeError on the missing-match
case; retained E1 passes five independently authored diagnostic nodes. These are
local diagnostic results, not official task scores or a hybrid-retrieval success.
Both previously authorized full-gate attempts were consumed. This proposal requests
a NEW CPU budget; it does not reuse any earlier authorization.

Pinned swegemma 0.2.11 source establishes:
- resolve_task_snapshot_paths accepts base_snapshots/base_<repo>.tgz plus
  patches/<instance>.patch; a fallbacks/<instance>.tgz has higher precedence.
- Evaluator.evaluate_task resolves once, forwards base_snapshot_path/patch_path
  into its agent phase and into verify_task.
- Agent setup calls extract_snapshot before baseline creation. Verification
  applies the layout delta before eval_baseline, then agent_patch and test_patch.
- The existing notebook and runner.validate_bindings require standalone inputs.
  Merely adding a patch file would either be ignored or rejected by provenance.
These facts establish the pinned public API, not the private scorer's deployment.

Available CPU environment: macOS/ARM, Python3.13.15, pytest9.1.1 in the existing
official environment. Python3.12.8 also exists at the absolute path used below.
Historical Kaggle was Linux/Python3.12.13/pytest8.4.2. Colima reports stopped;
Docker image availability could not be read through its socket. Do not start
Colima/Docker, pull/build an image, provision a VM or infer Linux compatibility.

## Proposed specification delta

After approval add docs/specs/notebook-import-cpu.md and append a scoped section
to docs/runbooks/kaggle-execution.md. Preserve the current runbook as a byte-exact
prefix and all previously tracked files except that append, as pinned by
prerequisites.json. New files may be added. Do not rewrite historical notebooks,
experiment manifests, runner.py, CPU protocols/results or the closed SDD plan.

1. Candidate identity and unchanged comparison:
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

2. Small host-only adapter and native data route:
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

3. Honest actual-input provenance without weakening the old guard:
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

4. Packaging, isolation and safe CPU extraction:
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

## Implementation stages after approval

A. Add the new specification, minimal host adapter, derived-input envelope and
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

## New CPU matrix: six native verifications and six setup probes

Run each row serially from a fresh relocated root outside the repository, with
spaces and Unicode in its path and a different launch cwd. Materialize the
notebook's allowlisted host payload there and use its actual layout-preparation
function. Do not rely on the developer checkout being importable. Original inputs
are hash-checked and treated as read-only. A distinct invocation/receipt binds every
setup and verification sandbox; no receipt borrowed from historical runs.

| ID | Input after notebook preparation | Required observations |
| --- | --- | --- |
| N-L01 | Owned faulty src package + generic alias | Setup binds source; native verification reaches intended behavior failure, resolved=false. |
| N-L02 | Same with own generic correct patch | Setup binds baseline source; verification binds patched source and resolved=true. |
| N-L03 | Same with own generic incorrect patch | Setup binds baseline source; verification binds wrong patched source and intended behavior fails. |
| N-R00 | Pinned Requests baseline + Requests alias | Setup and verification bind canonical snapshot source; five own diagnostic nodes reached. |
| N-R01 | Same plus exact retained E0 agent_patch | Setup binds baseline; verification binds the actual E0-patched source; all five own nodes reached. |
| N-R02 | Same plus exact retained E1 agent_patch | Setup binds baseline; verification binds the actual E1-patched source; all five own nodes reached. |

A setup probe uses the REAL SubprocessManager and unmodified native setup functions
in the reviewed agent pre-model sequence: wheels, extraction, Git exclude,
editable/dependency setup (native subprocess skips these), workspace config and
baseline. Execute an owned, read-only import witness after that sequence. This is
a reconstruction/setup probe, NOT an execution of run_agent_in_sandbox,
Evaluator.evaluate_task, a model or an agent loop. Pin/review the official agent
prefix and statically verify evaluator forwarding separately. Do not intercept
the native loop or monkeypatch it to claim an end-to-end agent execution.

Then call unmodified native verify_task using the EXACT resolver input tuple from
that notebook view and a fresh real manager sandbox. For Requests retain the five
owned R-IMPORT diagnostic nodes and unchanged agent_patch bytes; do not use original
Task.patch/test_patch. Setup observes baseline; verification observes baseline or
the respective retained patch. Record raw/canonical paths, alias target, module/file
hash, loaded function fingerprint, PID, executable, Python/pytest and native results.
Require actual source binding in BOTH phases; compare structural receipts to the
pinned originals. Show alias is in the native baseline and does not leak into
agent_patch. No new Requests solution is authored.

Do not require a particular retained E0/E1 behavioral PASS. Unexpected setup,
collection, unrelated import error, absent node or stale witness is BLOCKED, not a
successful negative control. Generic correct/wrong controls must discriminate.
FastAPI/Rich get full native resolver/provenance and byte-identity checks, but no
new native sandbox/verifier run here; do not claim their imports are fixed.

Production preparation accepts only the pinned three-task cohort and the Requests
alias. Generic src-package controls are explicitly CPU fixture inputs, never
accepted as production tasks or included in production payload data. Test fixture
support must not broaden the production allowlist.

## Additional Python3.12 portability checks: two stdlib-only probes

Use the EXISTING Python3.12.8 executable, no new environment/dependencies. The
isolated checker uses only stdlib plus installed Git. Reconstruct one generic
source fixture and the real Requests baseline through the same retained,
versioned layout artifact contract in fresh relocated roots. Verify manifest
hashes, Git patch/symlink mode/target, in-root canonical paths and unchanged
Requests product-file hashes. Import the generic dependency-free package from
an ordinary workspace-root Python process; record the actual interpreter.

This proves transport/layout behavior under another interpreter. It does NOT
import Requests in3.12, run native verify_task in3.12, or establish Linux/Kaggle
dependency compatibility. Do not expose Python3.13 site-packages to3.12, install
missing dependencies, copy compiled extensions or report a skipped probe as PASS.
AST/compile checks for Python3.12 syntax cover all new notebook cells and payload
sources. No Docker/Colima execution is authorized.

## Exact deterministic gate

All commands run from the worktree, serially and once per attempt. Commands1–10
are unchanged regression checks; command9 runs eleven legacy native verifications,
command10 runs nine R-IMPORT native verifications. Command11 runs exactly the six
NEW native verifications plus six setup probes. Command12 runs exactly two
stdlib-only3.12 probes and no native verifier.

For initial attempt1 the exact commands are:

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
.tools/official/bin/python scripts/check_notebook_import_cpu.py --check --output results/notebook-import-cpu/gate-1/matrix
/Users/diego/.pyenv/versions/3.12.8/bin/python3.12 -I -S scripts/check_notebook_import_portability.py --check --receipt results/notebook-import-cpu/gate-1/matrix/summary.json --output results/notebook-import-cpu/gate-1/portability
```

Proposed bounded entry point (not implemented/executed yet):

```sh
.venv/bin/python scripts/run_notebook_import_cpu_gate.py --check --attempt 1
```

Only a justified corrective attempt2 is permitted; same twelve commands with
gate-1 replaced by gate-2 in commands11–12. Attempt directories must be created
exclusively. Preserve every earlier raw run. Record exact argv, current source and
input inventories, command exits/wall times/log hashes and all started/completed/
assessed counts. No implicit native calls in unit/integration tests or audit.

The outer runner owns the deadline and detached native child groups, not just its
controller. Extend the proven owned-output discovery/cleanup pattern in NEW code
for these worker paths. Remove only this attempt's temporary input views, fixtures
and sandboxes, never retained results or symlink targets outside owned scratch.
For interrupted controllers perform scoped cleanup explicitly; Python finally
alone is insufficient after termination. Cleanup failure blocks PASS.
No source mutation during the gate; a source repair requires the corrected full
gate before closure. Auditor may run focused non-native tests, not extra matrices.

## Acceptance, limits and interpretation

All twelve commands must exit0; immutable checks before/after and cleanup pass;
all six new rows, setup witnesses, paired actual inputs, generic controls and both
3.12 probes meet the contract; independent audit returns PASS with zero findings.
Payload isolation, fail-closed execution guard and actual-vs-parent provenance are
mandatory acceptance criteria. Local import success alone is insufficient.

Budget per complete gate: max26 verify_task calls (11+9+6), six setup probes and
two stdlib portability probes; all serial. Native verification/commands30s,
each new row90s, each3.12 probe90s; one1200s outer wall deadline for ALL commands,
including regressions, build/fixtures, export and cleanup. Reserve30s for cleanup:
terminate owned work by1170s and finish cleanup/receipts by1200s. Start no new
90s case/probe with less than120s left. If cleanup cannot finish within the total
deadline, report BLOCKED and the outstanding owned paths/processes; do not declare
PASS. No automatic command/case retry.

Maximum TWO full gate attempts: initial plus one actual failure/audit repair
documented with focused non-native checks. Total ceilings:52 native verifications,
12 setup probes,4 stdlib portability probes,40min gate wall time. Any additional
native call or gate attempt requires a new authorization. Other existing CPU
fixtures/subprocesses are included in wall/artifact ceilings and are not model
evaluations. Do not run native matrices outside this runner, including for audit.

At most1GiB additional owned temporary/retained files at any time across all fresh
gate outputs and legacy regression outputs; require sufficient free disk, poll
usage and record sampled peak(bytes), not a guaranteed physical peak. Stream/copy
only the selected archives; original resources are not counted as newly created
but copies are. No download/install/upgrade, model access, service or image/VM
creation. Cap/deadline/pin drift/missing input means BLOCKED, no improvised fallback.

Report notebook integration, native macOS/3.13 binding and3.12 layout checks as
separate dimensions. Label success CPU_NOTEBOOK_LAYOUT_INTEGRATION_VALIDATED,
with linux_runtime_portability=NOT_TESTED, private_scorer_parity=null(reason),
gpu_readiness=false and real_evaluations=NOT_RUN. This label does not certify a
full notebook run, Kaggle task score or recovery strategy. An actual Linux3.12
CPU run, and later a real Kaggle run, remain separate pending decisions.
Absence of telemetry is null with coverage/reason, never zero.

## Approval boundary and deliverables

Approval would cover the described specification delta, CPU-only implementation,
exact gate and NEW bounded budget, independent audit/corrections, commit/push and
update of PR2 toward develop after PASS. It would NOT authorize merge, GPU/model
calls, Kaggle API/browser/session mutations, notebook publication, submissions,
Discussion/outreach, a Linux service start or changes to the real verifier.

Deliver: fresh blocked notebook, explicit derived-input manifests, reproducible
commands, CPU/setup/portability receipts, raw inventory, audit and limitations,
runbook append and updated PR2. Preserve all historical evidence.
