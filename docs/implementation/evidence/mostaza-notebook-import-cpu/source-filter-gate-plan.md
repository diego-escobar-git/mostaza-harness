# N-IMPORT-CPU-01 — source-link preservation and one gate, pending approval

Status: PROPOSED_NOT_AUTHORIZED. Ordinary CPU follow-up, no SDD restart.
All four gate allowances are consumed. Attempt5 remains rejected by CLI/admission;
no gate, native/setup case or Python3.12 transport probe may be replayed now.

## Observed failure and implemented host correction

Attempt4 passed commands1–10 and three new generic rows with correct setup and
verification imports, then stopped preparing R00 before its setup/native dispatch.
Total144.3997s; polled peak420152916bytes, below1GiB; all scoped cleanup complete.
Host pytest retention was confined to command1 and solved the previous cap failure.
There were23native calls,3setup probes and0stdlib transport probes in this gate.

The archive's131 tracked blobs/modes match its Git index. Python3.13.15's standard
[data_filter](https://docs.python.org/3.13/library/tarfile.html#tarfile.data_filter)
normalizes link targets. It changes tests/certs/mtls/client/ca from the tracked
'../../expired/ca/' to '../../expired/ca'. This makes git diff report the original
worktree changed. The source archive itself is unchanged; no product patch caused
this pre-setup host failure. See gate4-source-diagnosis.json for fingerprints.

The corrected host source_data_filter first runs the mandatory tarfile.data_filter.
It restores ONLY trailing separators of a symbolic link when removing those
separators exactly equals the filtered spelling and both paths resolve to the
same in-root target. Any other link/name normalization is rejected; absolute/
escaping/special members remain rejected, and hard-link restoration is rejected.
The pre-existing archive traversal, clean-worktree/index, exact one-link delta and
original/derived tree checks remain mandatory. No verifier, native tar command,
source archive, dependency, model/prompt/budget or frozen historical file changes.

Eight own small-fixture tests cover the preserved tracked link, data-filter
sanitization, other normalization, escapes and hard links.80 focused NON-NATIVE
tests, lint and strict typing on56source files PASS. A separate host-only source
extraction/Git proof on actual Requests confirms clean original tree683d44befe0d3519469011c35e46f332eebbc010 and only the allowlisted derived tree
change. This is not a native setup/verify_task/matrix or Python3.12 transport run.
The guarded GPU/network-disabled notebook has been regenerated with this host
correction; unchanged agent closures and manifests remain byte-identical.
No native validation of the revised candidate has run.

## Requested one additional gate

Approval would authorize a separate attempt5 admission pinned to this proposal,
gate4-source-diagnosis.json and all four consumed receipts, plus small non-native
admission tests. Preserve previous output paths and counters. Reuse the reviewed
host retention policy only in command1; record it in successful/failed receipts.

Exactly ONE serial complete gate5 with the following twelve commands (no retries):

~~~sh
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
.tools/official/bin/python scripts/check_notebook_import_cpu.py --check --output results/notebook-import-cpu/gate-5/matrix
/Users/diego/.pyenv/versions/3.12.8/bin/python3.12 -I -S scripts/check_notebook_import_portability.py --check --receipt results/notebook-import-cpu/gate-5/matrix/summary.json --output results/notebook-import-cpu/gate-5/portability
~~~

Entry point after approval/admission implementation:

~~~sh
.venv/bin/python scripts/run_notebook_import_cpu_gate.py --check --attempt 5
~~~

Same caps:1200s including cleanup, work stop1170s with30s reserve;1GiB polled
owned retained/temporary bytes including prior results;26native calls (11+9+6),
6setup probes,2stdlib-only3.12 probes;90s per row/probe and30s native commands.
No test exclusion, cap increase, deletion of prior files, automatic retry or
native matrix outside the outer runner (including auditor). Another failure
ends this allowance and never authorizes attempt6.

Cumulative gates1–4:64native starts,63retained native results,4setup and0stdlib
probes;576.0320wall seconds. Gate5, if approved, permits cumulative maxima90native
starts,10setup and2stdlib probes. Unused gate4 headroom does not extend its allowance.

Acceptance is unchanged: all12commands exit0,26/6/2started/completed/assessed,
source/function witnesses, controls, immutability, cleanup and independent audit
PASS with zero findings. After that, commit/push/update PR2 toward develop, no merge.
No GPU/model call, Kaggle mutation/publication/submission, Discussion, install,
service start or native verifier change. GPU readiness=false; private scorer
parity, full Linux/native3.12 and real Kaggle evaluation remain untested. Preserve
the dirty closed plan, phase1 worktree and all historical evidence.
