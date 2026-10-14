# B180 startup-v3: real batch acquired and operationally closed

One authorized private NVIDIA L4 x4 allocation completed all six planned native
evaluations on 2026-10-14. The corrected serving profile reached readiness and
avoided the previous startup OOM in this allocation. **No task resolved; E1 made
no recorded similarity or graph-tool invocation. Hybrid retrieval efficacy is
not established.** The single-allocation approval is consumed; no further GPU
execution is authorized.

[Exact private version1](https://www.kaggle.com/code/diegofescobar/mostaza-b180-ea1534a86873409b870b3b04d04e347f?scriptVersionId=358394257): notebook138700613,
opaque scriptVersionId358394257. Model Gemma4 31B QAT revision2, official harness,
Python3.12.13, torch2.10.0+cu128, vLLM0.19.1, swegemma0.2.11,
adk-submission0.2.13 and google-adk1.36.1 were retained. The same original agents,
sampling, tasks/order, verification, repair and B180 budgets were used in both
arms. No runtime retuning, allocation retry, purchase, publication or competition
submission occurred. E1-R180/B300 were not run.

## Observed outcomes

| Configuration | Task | Normalized result | Effective changed files | Official verification |
| --- | --- | --- | --- | --- |
| E0-B180 | requests_7205 | FAIL | src/requests/utils.py | 1 failed,205 passed,13 skipped |
| E0-B180 | fastapi_15589 | ERROR | none | not run |
| E0-B180 | rich_3061 | FAIL | repro.py only | 12 failed,100 passed |
| E1-B180 | requests_7205 | FAIL | src/requests/utils.py | 1 failed,205 passed,13 skipped |
| E1-B180 | fastapi_15589 | FAIL | repro.py only | 2 failed,5 passed |
| E1-B180 | rich_3061 | ERROR | none | not run |

Both arms: PASS0 / FAIL2 / ERROR1 / NOT_RUN0. Four applicable patches and four
native verification executions were observed. Applicability is not correctness;
two patches contain only reproduction scripts. Requests now changes library
source in both arms, unlike the reproduction-only patches from phase1, but still
fails the empty-default-credentials verification. No reference solution or hidden
test material was added to any agent prompt or workspace. Post-run verification
findings remain host-only, and full patches/test output remain in ignored results.

FastAPI exceeded the context window in both arms: at least16385 input tokens plus
16384 requested output tokens exceed32768. E0 left no patch; E1's reproduction
script was independently tested and failed, so its normalized outcome is FAIL
despite the recorded context exception. Rich reached the three-minute session
limit in both arms. Requests finished without a native timeout reason. The
native SUCCESS status describes result acquisition; notebook Successfully ran
and TaskResult.SUCCESS do not imply a resolved task.

## Recorded usage and recovery engagement

| Arm | Task | Tool events | Native charged | Recognized lexical commands | Recorded tokens |
| --- | --- | ---: | ---: | ---: | ---: |
| E0 | Requests | 16 | 13 | 2 | 148476 |
| E0 | FastAPI | 11 | 11 | 3 | 118137 |
| E0 | Rich | 19 | 18 | 9 | 142721 |
| E1 | Requests | 27 | 24 | 4 | 303315 |
| E1 | FastAPI | 14 | 14 | 4 | 164520 |
| E1 | Rich | 23 | 22 | 12 | 196834 |
| E0 total | three tasks | 46 | 42 | 14 | 409334 |
| E1 total | three tasks | 64 | 60 | 20 | 664669 |

Every retained trace contains zero named search_similar_code,
get_code_neighbors and get_code_subgraph events. This is an observed count in
the recorded tool-event domain, not an assertion of exhaustive backend telemetry.
Vector backend execution remains null: there is no invocation/backend receipt.
Thus the unchanged E1 adaptive hybrid instructions were not operationally
exercised here. There is no positive or negative effectiveness test of hybrid
retrieval itself, and no support for E1 superiority.

Tool events include exempt get_status and submit_patch; charged calls come from
the separate native counter. Both Requests traces contain two submit_patch calls.
Lexical counts recognize only simple rg/grep/git-grep shell commands; compound
commands and shell reads prevent complete lexical/read coverage. Token totals
sum recorded ATIF usage once, including repeated/cached prompt usage; they are
not unique context tokens, paid billing or a complete accounting of failed
requests. Native result.total_tokens0 is a default and was ignored.

The pinned ATIF StepObject serializer omits empty tool_calls. Requests ends with
text/final steps, one without usage. The old strict diagnostic conservatively
flags those optional omissions and returns null totals; those nulls/reasons are
retained separately. The existing normalizer's explicit-event/recorded-usage
contract yields the table above. The native serializer source hash and both
coverage definitions are in trace-observations.json; neither artifact was silently
rewritten. Missing pure model/tool/localization time, relevance/recall and full
repair coverage remain null with reasons.

## Startup, memory and environment evidence

External T0 was11:07:47.705 Bogotá /16:07:47.705 UTC, before the save request.
The first observer appeared at+165.04s. Native server start was requested at
+282.32s. Worker0 reported108.06s for loading weights. Native engine initialization
(profile/KV cache/warm-up) reported122.77s. Health readiness was observed near
+648.86s, and the post-readiness memory sample at+648.91s. These intervals have
different boundaries; do not add overlapping values or label the external clock
pure model startup time.

The actual native build_env return includes all15 approved keys, both allocator
aliases set consistently, and the restored graph-memory profiling/ready-timeout
flags. The command and config show max-num-seqs1, context32768, TP4, bfloat16 and
memory fraction0.90. Installed vLLM source hashes were acquired and compared to
reviewed upstream v0.19.1 bytes; acquisition.json reports each result.

Driver point samples in MiB:

| Point | Each GPU total | Each GPU used | Each GPU free |
| --- | ---: | ---: | ---: |
| Before server spawn | 23034 | 3 | 22561 |
| After native readiness | 23034 | 20263 | 2302 |

Driver-reserved accounting means these columns need not sum. They are point
samples, not peaks or model-only/PyTorch allocations. Worker-internal allocator
state is null with a reason. The new profile changes several startup/memory
settings together; this one successful startup cannot isolate which change
prevented OOM or guarantee future success.

## Session closure and supervision limitations

First SDK COMPLETE was observed at+1512.68s (about25min13s), before minute105.
The browser confirmed Successfully ran in1348.7s on the exact version with
L4x4 and zero Active Events. No manual cancellation was needed after normal
completion. Reported quota increased by2697.446 accounting seconds, from
4115.521071 to6812.967071. Terminal/post-terminal reads46.21s apart had the same
used quota. Physical GPU release time remains null; these signals establish
operational closure. Four devices times the external interval to first SDK
terminal is about1.681 device-hours, a conservative-clock arithmetic proxy,
not a directly measured physical allocation interval. No purchases occurred.

**Strict sixty-second polling compliance is not established.** A retained mixed
browser/SDK observation interval exceeded60s, and timestamps for some early UI
checks were not persisted. During the run, a read-only periodic wrapper was added
around the audited monitor. acquisition.json records the measured gap, coverage
and improved periodic interval. Future launches must start this bounded observer
before allocation, while preserving an available exact-version browser Cancel
route. It is monitoring, not a platform termination guarantee. The browser's AX
snapshot also clipped logs to500 rows; documented read-only DOM processing
restored full visible-log coverage. Neither issue justified guessing zero activity
or automatically canceling because Active Events was absent.

## Artifact integrity and reproducibility

All56 official output files (1061978 bytes) and the final native source inventory
were hash-checked. The official browser Download .ipynb yielded the actual
executed notebook, SHA256 df9c15aa2f34d1172612973e6ee8e445808e148c1864ab6da206b1a8e1c7f2d2,
with code execution counts1..5 and outputs. Its cell sources match the submitted
bound notebook. SDK pull/get_kernel yielded saved source with null counts; it
is preserved separately. Full native traces, patches, stdout, execution notebook,
request/response metadata, quota observations and the audited dirty-source
snapshots are in results/kaggle-phase2-startup-v3-ea1534a86873409b870b3b04d04e347f.
The code_commit is the base commit; source hashes/snapshots identify the additional
uncommitted operational correction that actually ran.

Native manifests identify E0-B180/E1-B180 separately, while the comparator requires
a shared experiment_id. The host-derived manifests explicitly use B180-startup-v3
and the observed version URL, retaining native manifests unchanged and recording
the exact changed fields/hashes. Normalized manifests/records were also published
locally to a content-addressed immutable store. No native results were altered.

```sh
.venv/bin/python docs/implementation/evidence/mostaza-phase2-startup-run/recompute.py --check
bash scripts/validate.sh
```

The recomputation verifies download/native inventories, submitted/executed source,
audited-source snapshots, six normalized records, trace observations and matched
conditions; it performs no GPU operation. Local validation and independent audit
receipts belong beside this report. Historical phase1 and both earlier phase2
allocation bundles remain unchanged.

## Interpretation and next work

Compared descriptively with phase1, both arms now have two failed verification
outcomes instead of one, and one ERROR instead of two, still zero PASS. New
Requests patches modify library source; reproduction-only patches explain two
other FAIL rows. This is an observation of implementation and verification, not
improved correctness. The larger generation budget and changed serving profile
prevent a causal budget-only comparison. Shared prefix cache and fixed E0-then-E1
order further limit timing interpretation. Three tasks support no significance
claim.

Before proposing any further GPU batch, review the fixed output-token reservation
against growing input context locally, the failed Requests patch semantics, and
why E1 never selected graph/vector tools. Preserve the current agents/results;
any new sampling/context/retrieval treatment needs an explicit specification delta
and separately approved comparable batch. No new GPU run is currently authorized.
