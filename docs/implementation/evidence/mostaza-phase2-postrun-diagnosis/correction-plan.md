# Approved CPU correction plan — 2026-10-14

The user approved stages A–D, the exact gate, independent audit/corrections and
commit/push/update of PR2 toward develop, without merge or GPU use. This remains
an ordinary follow-up, not an active SDD plan. Do not reopen the closed plan.
The approval concerns
CPU-only implementation, validation, independent audit and corrections. GPU
execution requires a later concrete notebook/quota decision. No merge is proposed.

## Proposed specification delta

Extend evaluation and agent-retrieval specifications with these acceptance rules;
leave phase1/B180/B300/R180 originals and real acquisition evidence byte-exact.

1. Distinguish context rejection, time limit, tool limit, verification failure
   and verification provenance uncertainty. Preserve the native outcome and add
   qualification metadata; never reinterpret the old Requests FAIL as PASS.
2. Before accepting verification as evidence of patch semantics, bind the imported
   package/function to the intended workspace source in both agent and verifier
   environments. Record interpreter, resolved module/file hash, working directory
   and effective import path without environment secrets. A failed or unavailable
   binding blocks new real evaluation readiness. Do not alter hidden tests,
   source expected values, score rules or patch application to obtain a pass.
3. New C8K configurations change only max_output_tokens from16384 to8192 in a
   matched pair. Keep thinking_budget4096, include_thoughts=true, temperature0.2,
   top_p0.95, model/revision,32768 context, cache/compaction null, native startup
   profile serial-memory-v3 and180s/30tools/50turns/300s verification unchanged.
   This provides8192 more nominal input tokens; it does not guarantee every future
   prompt fits. Maximum recorded successful completion was1915 tokens across
   the six traces, supporting a small cap correction rather than a sweep.
4. Additional Q1 instructions, if approved, apply identically to both arms:
   locate a symbol before requesting a bounded range; use exact argument keys;
   inspect returned start/end/truncation; after one unsuccessful duplicate read,
   switch to a bounded authorized shell read. Verify the edited workspace module
   is imported; use assertions with nonzero failure exit, meaningful negative and
   positive controls, and inspect the final source diff before submission. Include
   no task names, netrc examples, reference fixes or hidden expectations.
5. Retrieval R1 is a separate exploration-only treatment built from the already
   prepared recovery policy. At a lexical dead end or unresolved relation, name
   the question and select a verified-symbol graph/similarity query if useful,
   or briefly state why it is unnecessary/unavailable. No retrieval-call quota.
   Record reasons only when observed in native text; missing reasons stay null.
   Keep one-hop/10-neighbor and k5 pilot bounds; two hops need observed evidence.
6. Keep host diagnostics and evaluation-only fixtures outside every submitted
   archive and model-visible notebook/task payload. Preserve one official LlmAgent,
   native tools and official harness; no external service/model or model download.

## Implementation stages

### A — establish trustworthy verification first

Add a host-only module-origin/provenance diagnostic and CPU regression fixtures.
Replay both generated Requests patches against the public source and independent
cases, including a missing entry, without ingesting secret task fields. Exercise
native subprocess import selection on both flat and src package layouts and a
controlled shadow installed package. The control must reproduce wrong-source
execution and detect it; the correct binding must point to the actual patched
source with its expected hash. Validate fail-closed handling of a failed editable
install rather than hiding its exit status.

Instrument the supported sandbox adapter boundary for read-only origin receipts;
leave native verification semantics unchanged. If proving/correcting binding
requires changing the official setup, grader or test process, stop that branch,
report the incompatible/missing official setup resource and return the exact
proposed protocol change for approval. Do not silently set a new verifier
PYTHONPATH or patch a library dependency. Preserve historical receipts as unknown.

### B — a shared context-only correction

Create independent E0-C8K/E1-C8K manifests and deterministic archives, changing
only the output cap from their corresponding B180 agents. Add context/error
coverage diagnostics: recorded prompt/output count, requested cap, lower-bound
versus exact count, malformed argument keys, repeated returned ranges and output
truncation. Use fake-model/native-ADK CPU fixtures, not a real model. Replay the
known16385+16384 rejection boundary and test8192 reservation, unknown token count,
large tool response and exhausted-context cases without claiming future safety.

Keep automatic compaction disabled in this first change. Restoring native
compaction is a separate potential treatment: it adds same-model summarization
calls/latency, needs exact installed-source compatibility and accounting, and is
not approved implicitly here. If local checks establish that the selected
configuration still cannot respect context limits, return a revised compaction
proposal before marking GPU readiness.

### C — generic workflow quality and separate retrieval recovery

Create E0-C8K-Q1/E1-C8K-Q1 with the common Q1 additions and a separate
E1-C8K-Q1-R1 with only its exploration section changed. Preserve all original
files. Reject task-specific strings, analyst evidence, secret task fields and
post-run fixture paths in the packaging dependency closure. Validate graph/vector
APIs on synthetic data and retain the current host-only real-resource checks as
CPU evidence, not agent engagement. Assess generated reasoning only when a later
real trace exists; do not synthesize compliance metrics.

### D — notebook/readiness and review

Prepare a fresh private candidate, GPU disabled by default, with explicit variant
selection and all manifest/source hashes. Promote the bounded read-only observer
into the reusable control path and start it before external T0; test stalled
metadata/browser observations and exact-version fallback without remote sessions.
No Active Events absence is interpreted as zero activity or physical release.

After local gate and independent audit PASS, present the candidate and remaining
limits. Recommended first future real comparison is the context-only matched
E0-C8K/E1-C8K pair, six serial evaluations on the unchanged cohort. Any Q1/R1
comparison follows analysis of that batch and needs a fresh contemporaneous
control and separate authorization; it must not reuse historical baseline scores.
No automatic B300 run, retry or combined multi-batch authorization is requested.

## Exact proposed deterministic gate

From the dedicated phase2 worktree, run these commands in order after implementing
the proposed new local checker. The new command is a proposed deliverable, not a
check already executed during diagnosis.

```sh
bash scripts/validate.sh
.venv/bin/python scripts/check_phase2.py --check --cohort experiments/cohort.json
.venv/bin/python scripts/prepare_startup_phase2.py --check
.tools/official/bin/python scripts/check_startup_configuration.py
.venv/bin/python docs/implementation/evidence/mostaza-phase2-startup-run/recompute.py --check
.venv/bin/python scripts/check_context_verification.py --check
```

The final checker must validate all five new configurations with the actual pinned
official compiler; explicit allowed deltas and matched pair fields; CPU import
shadowing/detection; E0 None regression; ADK malformed optional-key filtering and
bounded-read recovery; context boundary/unknown coverage; no hidden/reference
leakage; immutable original evidence/candidates; GPU-disabled notebook payloads;
and a fixture of monitor startup before T0 plus hung-call timeout behavior. It
must execute no server.start, model inference, Kaggle save/run/cancel, submission,
paid action or installation from network. Fixture assertions must cover actual
failure modes rather than simply mirror proposed helper code.

Gate failure requires correction and a rerun of affected checks. Independent
review must inspect complete relevant changes, evidence limitations and all new
archive/notebook closures; PASS requires zero open findings. Local gate/audit
PASS is preparation readiness only, not a benchmark or guaranteed GPU startup.

## Approval boundary

Approve or reject stages A–D and this exact gate, including delegation of the
independent audit. Proposed Git closure, also requiring this approval: commit,
push and update existing PR2 toward develop, without merge. No GPU allocation,
new remote session, public notebook or competition submission is included. If
verification binding cannot be established within unchanged official semantics,
the deliverable is a concrete blocked-readiness report and a revised proposal,
not a fabricated successful correction.
