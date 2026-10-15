# Iteration 2 integration validation

This is the separately approved ordinary integration of PR3 then PR2, not a reopening of their closed SDD plans. User approval covers additive commits, CPU validation, independent audit, push and merge only after PASS. GPU, Discussion and changes to earlier worktrees remain forbidden.

## Source and publication boundary

- Original develop: `60ad0cec85bb36a1e65609ca2b1a743ba087384d`.
- PR3 source: `7bd3cf29ca6256178c3da1764563794ac4dc79cf`; merged first into develop as `e343692fc6b45585932a3a0ff20a28c3c80ce372`.
- Original PR2 source: `1b86b19f7654212c1d9f95eeca84d0e2a05db16b`.
- Local combined merge candidate: `3581e209dbe49015ea83e32753578b7a2c95013f`.
- Corrected tested source commit: `dcd0371196e2a2eeb83551b0816f5c01c8413850`; tree `13ecb02b71613a3b6c17d4a2b7be20b8943eb923`.

Final evidence-only commits may follow this tested source commit. Publication is established by GitHub merge state and Git ancestry, not by this report. The independent verdict belongs in `audit.json`; PR2 merge is conditional on PASS and exact source preservation. No merge authorization is inferred from absent CI checks.

## Changes

Resolved the single specification-index conflict, retaining all ten specifications. Added the current integration-boundary note and README link. All original production sources, scripts, experiment manifests, submission payloads, native verifier, notebooks and historical evidence are byte-identical to their pinned commits. PR3's six non-index artifacts also remain byte-identical. The only original PR2 files changed beyond README/index are four integration-test files; a new test fixture supports the explicit historical domain.

The first gate failed because tests applied historical run-admission pins and absolute operator paths to the new checkout. The closed-plan pin exists only in retained unpublished historical continuity. It was neither copied nor overwritten. The production admission functions remain unchanged and reject the current checkout.

An independent technical review confirmed the test-only repair: historical positives run against an explicit root whose path/HEAD/ancestry/sole dirty-plan digest are verified; the same APIs must reject the current root. The current notebook is separately rebuilt and checked against immutable Git bytes, disabled GPU/network metadata, empty outputs, source binding and Python3.12 syntax. The phase2 verifier recomputes current compiler/resource/trace components and rejects historical readiness identity. Only operator command paths are normalized in memory for full snapshot equivalence; no historical artifact is regenerated.

## Observed gates and timing correction

| Gate | Source | Result | Observed coverage | Wall seconds | Cleanup |
| --- | --- | --- | --- | --- | --- |
| 1 | `3581e20` | FAIL | 378 unit passed; 115 integration passed, 4 failed; later commands not run | 54.098712 | Confirmed |
| 2 | `dcd0371` | Commands PASS; full cap unverified | 378 unit, 120 integration, 20 reconciliation tests; format/lint, mypy57source files plus strict checker/test typing, package builds, official compiler, original paired evidence and read-only reconciliation | 58.463475 | Confirmed |

Gates1/2 record **112.562187s of supervised commands and cleanup**, not total gate time. Their preflight duration is **null: not measured**. No retrospective cumulative total-cap claim is made. The original raw receipts and controllers remain unchanged; their PASS fields do not override this coverage limit. The first independent integration audit returned FIX_REQUIRED (INT-AUD-001) for this defect.

The corrected controller starts its clock before preflight imports/product I/O, measures owned space before source hashing/invariants, clamps every Git timeout and checks walks/hash chunks against the global deadline. Three synthetic controls passed before launch: expired preflight blocks Git, preflight size excess rejects, and a storage walk observes the deadline.

**Gate3 is the sole accepted full gate:** PASS, 67.366917s through cleanup before receipt export; 67.367157s through the first export, including 8.082695s preflight. Final export is checked against the same600s deadline and cannot leave PASS if late; its separate duration is not measured. All five commands exited0:378 unit tests,120 integration tests,20 reconciliation tests, formatting/lint/types, package/compiler validation, historical paired-evidence checks and reconciliation recomputation. Global work stops at570s, retaining30s for cleanup/export. The cap is600s, stricter than the approved1200s per candidate.

Gate3 sampled peak: **1386203692bytes**, below2GiB(2147483648bytes), across56 observations. The scope includes copied tools/resources, all retained local results, builds/caches and unique owned scratch/output. Sampling does not prove an instantaneous physical peak. Owned cleanup and tracked-source stability were confirmed. No historical V/R/N matrices, model calls or native auditor reruns were performed. Gates1/2 preflight coverage remains unknown, not zero; gate3 does not retroactively attest those attempts.

The last paragraph of the integration-boundary note records the earlier proposed cumulative allowance and first repair; it is not an observation of total prior gate time. This timing correction and validation.json are the authoritative integration measurement coverage. The immutable historical reconciliation is unchanged.

## Reproduction and evidence

`gate-driver.txt` and `gate-driver-2.txt` preserve the initial controllers; `gate-driver-3.txt` preserves the accepted full controller and exact argv/limits. Inputs and tooling were independently copied into this worktree; local entry points/editable host source were relocated only in the copies. No package/model download or service change occurred. `MOSTAZA_HISTORICAL_PHASE2_ROOT` identifies the retained read-only root for historical tests, not an execution permission.

`validation.json` contains all three command/result/supervision receipts, timing coverage and source identities. Only gate3 attests the full cap. `source-inventory.json` binds the tested tracked files. `raw-inventory.json` binds the ignored logs, raw receipts and prerequisites. `preserved-worktrees.json` records all three previous HEADs, statuses and unchanged pre-existing dirty-plan hashes. Raw results remain at `results/phase2-integration/`; no credentials or bulk task/model data are committed.

## Remaining limits

The immutable reconciliation still reports its historical base and `pr2_integrated:false`; use the separate integration note and actual Git ancestry for later branch state. No old PASS or authorization transfers to this candidate.

GPU readiness remains false. Linux/native Python3.12 Requests verification, private scorer parity, a full Kaggle notebook/model/agent loop, another real paired comparison and observed hybrid efficacy remain pending. The retained E1 diagnostic successes are not Kaggle task scores. No GPU, Kaggle session mutation, submission or Discussion occurred.
