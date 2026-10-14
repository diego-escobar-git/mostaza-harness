# R-IMPORT-CPU-01: CPU workspace binding

Status: approved for bounded CPU implementation and validation.

The [approved contract](../implementation/evidence/mostaza-requests-import-cpu/plan-for-approval.md)
records the exact layout delta, nine-case new matrix, ten-command gate, budgets
and closure. Approval pins that plan. Preserve V-CPU-01 and its historical results.

Use unmodified native verify_task with actual SubprocessManager and patch_path
for one allowlisted root package symlink to its existing src package. No changes
to source packages by the layout delta, native code/command/env, dependencies,
agent payloads, original archive or original task reference/test patches.

Requests U/B pairs must use identical test_patch and agent_patch, with five owned
nodes observed in the actual pytest process. Validate raw/canonical parent/module/
function paths and expected code fingerprints while the alias exists. Record
actual behavior separately from binding; never require a fabricated E1 success.

Require all ten gate commands, twenty serial native invocations per gate at most,
one initial and one justified corrective attempt,1200s per gate,90s per case,
30s native timeouts,1GiB owned artifact ceiling, no automatic retries. Independent
audit must PASS with zero findings before commit/push/update PR2 toward develop.
No merge, GPU, Kaggle actions, Discussion, verifier modification or production
activation. CPU success never promotes private-scorer parity or GPU readiness.
