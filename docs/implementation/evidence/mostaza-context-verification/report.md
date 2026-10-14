# Approved CPU context and verification correction

The CPU implementation prepares five new configurations and a fresh output-free,
GPU-disabled notebook. It preserves the original agents, manifests, B180 outcome
records, raw bundles and the closed phase2 SDD plan. No GPU/model inference,
remote notebook execution, paid action, public notebook or submission was used.

## Implemented behavior

- E0-C8K/E1-C8K render their corresponding B180 archive with only the output cap
  changed from16384 to8192. Generation remains180s/30 charged tools/50 turns;
  verification300s, model/revision, sampling, thinking4096, cache/compaction null
  and serial-memory-v3 remain common. This is additional nominal headroom, not a
  guarantee against future context overflow.
- E0-C8K-Q1/E1-C8K-Q1 append identical generic workflow checks: exact read_file
  keys, bounded ranges, returned-range/truncation inspection, one duplicate then
  bounded alternate read, workspace import binding, nonzero assertions with
  negative/positive controls, and source-diff cleanup. Original prompts stay exact.
- E1-C8K-Q1-R1 is a separate exploration-only change from the Q1 E1 control using
  the already prepared recovery policy and short observable query/skip decisions.
  No call quota is imposed, no task-specific hint is added, and no actual model
  adherence is claimed. Missing decision/backend evidence stays null.
- Host context diagnostics preserve native outcomes and distinguish exact counts,
  lower bounds and unknowns; they retain malformed keys, repeated returned ranges
  and truncation. No character-to-token estimate or missing-as-zero substitution.
- Read-only module-origin observation uses the official sandbox exec boundary,
  collecting interpreter/cwd/import paths, module/file hash and coverage without
  changing environment, package setup, verifier command, hidden tests or scoring.
  The adapter explicitly cannot produce an exact-test-process receipt: even a
  forged coverage label cannot upgrade its readiness result.
- The reusable external read-only monitor starts before external T0, bounds each
  metadata subprocess to25s plus15s polling by default, records timestamps,
  supports exact-version observations without Active Events, and escalates stale,
  failed or persistently unavailable stop controls. It has no Kaggle save/start/
  cancel API. Its caller must supply an audited read-only metadata reader and
  preserve an exact-version browser stop route; it does not guarantee physical
  release or OS scheduling latency.

## Concrete verification blocker

The original verifier's imported Requests module/function location and hash were
not retained. A sibling preflight cannot establish what pytest plugins or other
imports selected in the actual scoring process. Native setup suppresses editable
install failures, so its final zero shell exit alone is insufficient evidence.

An authenticated official CLI ListDatasetFiles request for
metric/gemma-4-developer-agent-metric-data returned HTTP403. The setup script was
not acquired. The client did not bypass permissions or start a session. See
official-setup-access.json. Therefore readiness is deliberately
PREPARED_BLOCKED_VERIFICATION_ORIGIN, and the new notebook raises before its
legacy bootstrap or any model/server work. Old Requests outcomes stay FAIL.

Required next protocol decision, not silently applied: obtain the authorized
organizer setup/source pin and establish an organizer-supported import receipt
inside the actual verifier process, then correct setup binding if needed. Any
change to verifier PYTHONPATH, pytest plugins, official setup or grading needs a
separate concrete review and approval. No such mutation is implemented here. The exact proposed invocation/plugin
contract and its import-order limitations are in
[protocol-proposal.md](protocol-proposal.md); it is not authorized or applied.

## CPU evidence versus real outcomes

The native SubprocessManager fixtures actually reproduce a controlled installed
package shadowing src-layout code and detect the mismatch; flat-layout binding
and an explicitly synthetic source-binding control match expected hashes. This
is not a repair of the historical Kaggle verifier. Unknown/nonzero editable-install
results and sibling receipt coverage block readiness.

The actual ADK FunctionTool plus native read_file reproduce malformed optional
key filtering, repeated line1 output, correct bounded300..330 reads and character
truncation. Fake model requests use native ADK/genai request/configuration objects
to exercise the known context boundary; no model is invoked. Twelve independent
netrc cases reproduce the E0 missing-entry TypeError and E1's isolated behavior
without using hidden fixtures/reference patches. Existing native synthetic graph/
vector integration tests cover the retrieval APIs; real-resource CPU results from
the diagnostic report remain explicitly analyst-driven.

The exact six-command gate passed: 250 unit tests,39 integration tests, strict
types on34 source/script files, format/lint/build, all five new official
compilations and historical provenance/recomputation. validation.json records
command log hashes; independent audit and supplemental protocol review returned
PASS with zero findings (audit.json). These local PASS receipts
certify CPU preparation and honest blocked readiness, not a newly successful
benchmark, GPU startup or resolved task.

## Reproducible commands

```sh
.venv/bin/python scripts/prepare_context_verification.py
# Optional: use a NEW ignored directory; existing archives are never overwritten.
.venv/bin/python scripts/prepare_context_verification.py --output-dir results/context-new/archives
.venv/bin/python scripts/check_context_verification.py --check
```

The exact approved six-command gate is in the approved
[correction plan](../mostaza-phase2-postrun-diagnosis/correction-plan.md).
The first candidate selects E0-C8K/E1-C8K only. Q1/R1 comparisons require later
analysis and a fresh contemporaneous matched control; no historical outcome reuse.
A further real batch needs new explicit GPU authorization after verifier readiness
is established. This delivery does not request or consume that authorization.
