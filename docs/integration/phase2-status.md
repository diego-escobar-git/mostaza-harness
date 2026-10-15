# Iteration 2 integration boundary

This note describes the combined source tree prepared on 2026-10-15. GitHub PR state and commit ancestry determine whether it is published on develop; a successful CPU gate alone does not establish publication.

PR3 was merged first with merge commit `e343692fc6b45585932a3a0ff20a28c3c80ce372`. The integration candidate preserves PR2's original head `1b86b19f7654212c1d9f95eeca84d0e2a05db16b` and PR3's original head `7bd3cf29ca6256178c3da1764563794ac4dc79cf`. Integration uses additive merge commits, without rebasing or squashing the pinned evidence history.

The [reconciliation report](../implementation/evidence/mostaza-phase2-reconciliation/report.md) and its source inventory are immutable historical snapshots against develop `60ad0cec85bb36a1e65609ca2b1a743ba087384d`. Their `pr2_integrated: false` and references to an unmerged PR2 describe that snapshot, not the later branch state. Do not regenerate or relabel those artifacts to announce integration. New integration receipts live separately under `docs/implementation/evidence/mostaza-phase2-integration/`.

The original formal SDD preparation closure and later ordinary CPU work retain their own validation and authorization boundaries. This integration is the separately approved ordinary continuation; it does not reopen or rewrite their plans, audits or consumed allowances.

## Validation and remaining work

The integration gate exercises local CPU unit/integration fixtures, package/compiler checks, historical evidence verification, and the separate reconciliation tests/checker. It does not rerun the consumed V/R/N verification matrices or call a model. Integration receipts identify the candidate, commands, observed results, resource limits and independent audit. No historical PASS transfers to the combined candidate.

GPU readiness remains false. Native macOS/Python3.13 CPU diagnostics do not establish Linux/native Python3.12 portability, private Kaggle scorer parity, a full notebook/model/agent loop, a Kaggle task score, or hybrid retrieval efficacy. Those remain separate follow-up work with fresh scope and authorization. Missing telemetry remains null with reasons.

No GPU, Kaggle session mutation, notebook publication, submission, Discussion, verifier modification, model download or service change is authorized by this integration. Original experiments, agent payloads, native verifier and historical evidence remain unchanged.
