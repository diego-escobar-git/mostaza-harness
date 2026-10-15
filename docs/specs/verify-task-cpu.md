# V-CPU-01: native end-to-end CPU verification

Status: approved for CPU implementation and validation.

The approved behavioral contract, exact eleven-case matrix, immutable inputs,
acceptance, nine-command gate and budget are recorded in
[the approved proposal](../implementation/evidence/mostaza-verify-task-cpu/plan-for-approval.md).
Approval and its plan SHA256 are retained beside that proposal.

Run the unmodified swegemma 0.2.11 verify_task with the real SubprocessManager.
Use independent owned test_patch inputs, actual required nodes and ordinary
complete-module imports. Do not use the reserved mock bypass or original
Task.patch/test_patch. Preserve native pytest invocation, setup and cleanup.
Observe module and loaded-function identity inside owned tests; preserve missing
telemetry as null with reasons. CPU binding diagnostics and native resolution
remain separate; neither establishes historical/private-scorer parity.

The eight synthetic controls must demonstrate the intended passing/failing
behavior. Three Requests runs must reach all five owned nodes and yield import
receipts, or this milestone is blocked. A measured binding mismatch is a valid
diagnosis but cannot promote real-evaluation/GPU readiness.

No native source/environment/path repair, plugin activation, GPU, model, remote
compute, Discussion publication, reference solution or secret test input.
Require all nine gate commands and independent audit PASS with zero findings
before commit/push/update PR2. Preserve prior evidence and the existing dirty
closed-plan bytes; never merge automatically.
