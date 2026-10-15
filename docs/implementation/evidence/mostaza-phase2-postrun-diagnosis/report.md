# Post-B180 diagnosis: context, verification provenance and retrieval selection

Date: 2026-10-14. Base code commit: 129e76d58d82a8af40d02cefd39218ae70f08f9c.
Scope: six retained real B180-startup-v3 traces/results and independent CPU
experiments. No new GPU session, remote notebook execution, model call, reference
solution or hidden-test fixture was used. This report is host-only research and
must never enter submission archives or agent/notebook inputs.

## Findings and confidence

| Finding | Evidence strength | Consequence |
| --- | --- | --- |
| FastAPI exceeded combined input/output context, not its time/tool allowance | Direct native error in both arms | Fix context management before increasing time |
| Malformed optional tool arguments silently reverted reads to line1 | Native event/response pairs; reproduced with actual ADK FunctionTool on CPU | Validate returned ranges and avoid duplicate reads |
| Both B180 arms explicitly disabled event compaction | Actual submitted/executed source and native inference.compaction=null | The official sample's compaction configuration was not active |
| E0 Requests introduces a no-match TypeError | Generated source and CPU snapshot-function replay | Genuine regression even though empty-entry handling works in isolation |
| E1 Requests source handles isolated empty entries; official verification still failed | CPU replay plus original native FAIL receipt | Do not assume semantic failure explains the verifier result |
| Requests import binding differed during E1 generation | Native steps16/17 changed only PYTHONPATH and returned different results | Verify exactly which source each test process executes |
| E1 never selected graph/vector tools despite an availability notice | All three real traces; zero named invocations | No observed operational hybrid treatment |
| Retained native graph/vector resources work on CPU | Actual native tools, three repositories, verified symbol seeds | Missing resources are not supported as the primary explanation |

## FastAPI: confirmed failure chain

Both native results report input of **at least16385** tokens plus a fixed16384
output reservation against max_model_len32768. The failed request's complete
input count is unavailable; the error's lower bound must not be treated as the
exact token count. The observed native task durations were40.42s for E0 and89.61s
for E1; their recorded charged calls were11 and14, below the180s/30-call budgets.
Increasing those budgets alone does not address this failure.

E0 read_file calls at steps5,8,12 contain the key `start_line"`, not `start_line`.
Responses start at1 and repeat previously seen150-line imports/declarations.
E1 has the same malformed key at step5. E0 also requested400..600 and received
400..549 because of the150-line cap; E1 requested from500 without locating the
class first and received500..649. Correct tools were available; these are
argument/planning mistakes plus silent adapter fallback, not evidence that valid
start_line requests were ignored.

ADK FunctionTool filters unknown argument names before invoking its callable;
the optional start_line therefore defaults toNone and native read_file starts
at1. A CPU invocation of the installed official FunctionTool, using a harmless
callable with the native read_file signature, reproduced line1 versus line400.
See [ADK v1.36.1 FunctionTool](https://raw.githubusercontent.com/google/adk-python/v1.36.1/src/google/adk/tools/function_tool.py).
No tool or dependency source was patched for this test.

The native successful-step maximum input counts were16281(E0) and15827(E1).
E1's last successful response wrote a reproduction script with1230 completion
tokens; it was never run by the agent before the next request failed. The harness
then verified the reproduction-only patch independently. Thus E1 is normalized
FAIL, while E0 has ERROR without a patch. These are different consequences of
the same context failure, not one successful FastAPI implementation.

Both actual manifests record inference.compaction=null and cache=null; the
executed source explicitly supplies events_compaction_config=None. The retained
official getting-started example instead supplies interval15/overlap2/token
threshold14336/retention5. Disabling this was a shared experimental condition,
not an E1-only error. Native compaction uses model summarization: it requires
separate accounting, exact API/source compatibility and a test of when it actually
triggers. Simply copying sample fields is not a proven fix. Current ADK documentation
also distinguishes compaction behavior and costs:
[ADK context compression](https://adk.dev/context/compaction/).

## Requests: semantic regression versus questionable verification binding

Actual E0 patch: `if any(_netrc):`. Actual E1 patch:
`if _netrc and any(_netrc):`. Their only final changed product file is
src/requests/utils.py. The original native verdicts remain FAIL with1 failed,
205 passed,13 skipped in each arm. Nothing in this diagnosis reclassifies them.

CPU replay extracted only get_netrc_auth from the retained public source
snapshot, applied the generated one-line changes in temporary memory, and used
independent synthetic hostnames/cases. It did not load hidden tests or a reference
patch. Python3.13.15 results:

| Independent case | Original snapshot | E0 generated change | E1 generated change |
| --- | --- | --- | --- |
| Empty explicit machine | empty credentials | None | None |
| Empty fallback default | empty credentials | None | None |
| Host has no matching/default entry | None | TypeError | None |
| Complete credentials | correct pair | correct pair | correct pair |

The standard library returns None when no entry/default matches; E0 calls any
on that value. The E1 short-circuit preserves that case. These observations follow
[Python netrc semantics](https://docs.python.org/3.12/library/netrc.html), not a
reference solution. Python3.13 CPU behavior is not a complete Linux/Python3.12
scorer replay and cannot establish E1's complete correctness.

More importantly, E1 real step16, after editing source, runs a plain import and
still returns empty credentials. Step17 runs the same probe with
PYTHONPATH=/workspace/src and returnsNone. Step24's targeted two existing tests
pass, but they do not cover the new empty-default behavior. E0's scripts print
observations rather than asserting expectations; their zero exit does not prove
correctness, and some purported positive netrc examples are malformed.

The pinned native SubprocessManager exposes host site-packages by default and
sets PYTHONPATH to workspace, not workspace/src. Editable install errors are
suppressed by the native setup command. Native verification runs python3 -s -m
pytest with the normal sandbox environment; no module.__file__ or executing
function source hash was retained. This combination can select a different
installed Requests than the patched src tree.

A separate CPU import replay confirms that a workspace-only PYTHONPATH selects
the host installed Requests regardless of the snapshot patch, while src-first
selects each patched function. The local installed package already handles empty
credentials, so the replay demonstrates the **import-selection mechanism**, not
the exact Kaggle failure output. The exact historical verifier import origin
remains **null**. Verification import contamination is a strong hypothesis,
supported by the same real-run step16/17 discrepancy; it is not yet proven for
the verifier process. Do not fix this by copying hidden expected values into
agent prompts or by silently changing the official verifier.

## E1: available tools, unobserved strategy execution

All three real E1 user prompts include the native Code Intelligence Tools notice;
the archived agent declares all three tools. There are64 recorded tool events
but zero search_similar_code/get_code_neighbors/get_code_subgraph calls. The
missing backend execution receipt stays null. A notice is not proof of backend
health; an analyst's subsequent tool invocation is not an agent invocation.

CPU native-tool checks using retained graphs/embeddings and symbols already
visible in the source yielded:

| Repository | Graph nodes | Bounded neighbors returned | Similarity results |
| --- | ---: | ---: | ---: |
| Requests | 732 | 4 | 5 |
| FastAPI | 4259 | 8 | 5 |
| Rich | 1920 | 1 | 5 |

All seed embeddings were finite/nonzero and all native responses status=ok.
These calls were analyst-driven CPU diagnostics, not benchmark or relevance
results. They cannot retrospectively prove the historical GPU backend state.

The observed decision paths explain the absence better than unavailable tools:
Requests found its exact function immediately; useful hybrid recovery was not
established as necessary. FastAPI kept following exact names and rereading files
until context failure. Rich corrected a misspelled symbol lexically, then kept
looking for methods/attributes instead of recording an unresolved structural
question. E1's instructions permit that lexical-first path and make graph/vector
usage conditional. There is no explicit retrieval decision/skip reason in the
trace, so the model's internal motive is unknown. A prompt that allows a skip
must not be evaluated as a mandatory-call policy.

Adherence was incomplete beyond retrieval: E1's status checks occur only at
Requests step25, none in FastAPI, and Rich step3. No operational visited-symbol
ledger is evidenced. The instruction to use under8–10 turns also remains common
to both arms despite a50-turn hard budget; its causal influence is unmeasured.
The prepared E1-R180 prompt was **not executed**, so this batch says nothing
about whether that revised policy would help.

## Reproducibility and pending decision

trace-evidence.json records source hashes, event IDs, returned ranges, runtime
configuration and unknown verifier origins. CPU replay JSONs distinguish local
experiments from real outcomes. validation.json lists the retained reproduction
scripts/commands under ignored results/postrun-diagnosis-20261014. Previous raw
and compact evidence is unchanged; original source/sampling/prompts remain frozen.

The proposed specification delta, stages and exact gate are in
[correction-plan.md](correction-plan.md). No proposed correction is implemented
or authorized by this diagnostic record, and no new GPU authorization is requested
at this point.
