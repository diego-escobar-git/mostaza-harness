# N-IMPORT-CPU-01 — fourth gate consumed; host source-link repair validated

Status: BLOCKED_CPU_GATE_ALLOWANCE_EXHAUSTED. No complete gate PASS or final
completion. No commit/push/PR update; HEAD remains bcec689aadc9be0801de6b1c7e560d776e17299e.
The old phase1 worktree, verifier,234 frozen files and11 external pins are preserved.

## Prepared notebook integration

The new guarded GPU/network-disabled notebook uses E0-C8K-L1/E1-C8K-L1 host
identities and unchanged original C8K agent closures. The official snapshot
resolver supplies the same base-plus-layout tuple to pre-model setup and native
verification. One exact Requests root symlink is the only layout delta. Parent
binding and actual derived inputs are identified separately; original runner,
notebooks/configs, model/prompts/sampling/budgets/cohort and repair strategy remain
unchanged. Native APIs, code, commands and environments are not modified.

Historical evidence remains byte-exact in checkpoints/before-additional-gate/ and
checkpoints/before-resource-gate/. Original and additional plans/approvals and all
four raw receipts are preserved. No closed SDD plan is reopened or rewritten.

## Actual gates

| Attempt | Wall seconds | Outcome | Native starts/results | Setup | Stdlib3.12 |
| --- | ---: | --- | --- | ---: | ---: |
|1|253.4993|Commands1–9 PASS; interrupted10 PermissionError|20/19|0|0|
|2|171.2035|Commands1–10 PASS; first setup assessment stopped11|21/21|1|0|
|3|6.9295|Command1 stopped by observed artifact cap|0/0|0|0|
|4|144.3997|Commands1–10 PASS;3generic rows accepted; R00 host proof failed|23/23|3|0|

Cumulative64native starts,63native results,4setup,0stdlib probes and576.0320wall
seconds. All four attempt allowances are consumed. Unused per-call headroom never
extends an allowance. No native/setup/stdlib rerun or auditor matrix occurred.

Gate4 command1 passed370unit and79integration tests, lint/format, typing56files,
package build, official compiler checks and historical evidence validation.
Commands9–10 passed their complete11+9 native regression cases. The retention
policy applied ONLY to command1, as recorded in receipt environment_overrides;
commands2–11 have no override. Command12 was not started.

The new generic rows N-L01/N-L02/N-L03 each passed setup and verification source/
function/process binding. L01 faulty and L03 wrong patch were correctly unresolved
with exit1; L02 correct patch resolved with exit0. These are owned generic controls,
not official task scores. All three were assessed by the controller. Gate2's
historical first L01 remains unassessed and is never relabeled retrospectively.

R00 failed during host preparation, before setup-started or native-started. No new
Requests pipeline verification result exists; N-R01/N-R02 and both3.12 transport
probes remain NOT_RUN. Earlier Requests regressions are not substituted for these.

## Repairs and concrete failure diagnosis

Earlier repairs preserve the original PermissionError uncertainty, strengthen
owned descendant exit checks, retain failure telemetry, distinguish setup coverage
and interpret only the first empty Python -c sys.path entry as witnessed cwd in a
validation copy. Raw witnesses/processes and frozen old validators remain intact.

Gate3 genuinely exceeded the1GiB cap with sampled1405596992bytes because several
old parametrized unit tests retained463659201byte resource copies. The approved
pytest retention option releases passed-test temporaries, retains failed-test data
and leaves nodes/assertions unchanged. Gate4 stayed below cap: sampled420152916bytes
(about401MiB). Every process-group cleanup and owned scratch cleanup completed.

Gate4 found a different issue in the HOST source proof. Requests archive131tracked
blobs/modes match its index. Python3.13.15 tarfile.data_filter normalizes the tracked
certificate link tests/certs/mtls/client/ca from '../../expired/ca/' to
'../../expired/ca'. A host-only extraction reproduced exactly that Git difference;
the original archive bytes are unchanged. Python documents link normalization in
[data_filter](https://docs.python.org/3.13/library/tarfile.html#tarfile.data_filter).
Local installed-library/function fingerprints and real source trees are recorded
in gate4-source-diagnosis.json; the online version may advance independently.

The corrected source_data_filter always calls the standard data_filter first.
It restores only a symbolic link's trailing separators when the stripped spelling
exactly matches the filtered target and both resolve identically inside the owned
root. Other link/name normalization and hard-link restoration are rejected; unsafe
members still fail. Worktree/index cleanliness and exact one-link delta checks
remain enforced. No native verifier/extractor or original source is changed.

Eight new tiny fixture cases validate this behavior. Current corrected sources pass
80 focused NON-NATIVE tests, lint and strict typing56files. A separate actual Requests
HOST-only source proof now passes, retaining original tree683d44befe0d3519469011c35e46f332eebbc010 and derived prebootstrap treeafa1dfc5e511f6dafe4e47eb435226c1dbc850b5.
Its temporary extraction was cleaned. This is source/Git diagnosis, not a native
setup/verify_task/case or3.12 transport probe. The candidate notebook was regenerated
without executing it. No native candidate validation occurred after this repair.

## Coverage and next step

Times are wall seconds and sizes bytes. CPU time and instantaneous physical peak
remain null with reasons; samples cannot prove a physical maximum. Earlier gates'
host-temporary coverage gaps stay documented. Missing native results are not zero
failures or completed/assessed calls. Raw JUnit is consumed/removed natively.

Native coverage remains macOS/ARM/Python3.13.15/pytest9.1.1, with host relocation/cwd
spaces and Unicode but ASCII native sandbox paths. No full notebook/model/agent
loop, Linux/native3.12 or private scorer was executed. real_evaluations=NOT_RUN,
GPU readiness=false and scorer parity=null with reason. No hybrid efficacy claim.

[source-filter-gate-plan.md](source-filter-gate-plan.md) proposes one separately
authorized gate5 using the same twelve commands,1GiB/1200s/26native+6setup+2stdlib
limits and command1-only retention. It is NOT enabled or authorized. Full PASS and
independent audit PASS with zero findings are required before commit/push/update
PR2 toward develop. No merge, GPU/model call, Kaggle mutation/publication/submission,
Discussion, installation/model download or Docker/Colima/service change occurred.
