# Paired experiment: mostaza-phase1-foundation

Run kind: **real_kaggle**. Cohort: 3.
Differences are E1 minus E0; the direction of improvement depends on the metric.

| Metric | Unit | Measured pairs | Measured mean delta | Estimated pairs | Estimated mean delta |
| --- | --- | ---: | ---: | ---: | ---: |
| symbols_explored | count | 0 | unavailable | 0 | unavailable |
| files_explored | count | 0 | unavailable | 0 | unavailable |
| read_operations | count | 0 | unavailable | 0 | unavailable |
| search_operations | count | 0 | unavailable | 0 | unavailable |
| localization_seconds | seconds | 0 | unavailable | 0 | unavailable |
| tokens | tokens | 3 | -25738.333333333332 | 0 | unavailable |
| code_characters | characters | 0 | unavailable | 0 | unavailable |
| graph_expansions | count | 0 | unavailable | 0 | unavailable |
| repeated_context_characters | characters | 0 | unavailable | 0 | unavailable |
| recall_at_k | ratio | 0 | unavailable | 0 | unavailable |
| relevant_context_ratio | ratio | 0 | unavailable | 0 | unavailable |
| tool_calls | count | 3 | -2.3333333333333335 | 0 | unavailable |
| total_seconds | seconds | 3 | -0.08725939033327752 | 0 | unavailable |
| repairs | count | 0 | unavailable | 0 | unavailable |

| Arm | PASS | FAIL | ERROR | NOT_RUN | Cohort denominator |
| --- | ---: | ---: | ---: | ---: | ---: |
| E0 | 0 | 1 | 2 | 0 | 3 |
| E1 | 0 | 1 | 2 | 0 | 3 |

## Per-task outcomes

| Instance | Arm | Status | Patch present | Patch valid | Tests | Resolved | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fastapi_15589 | E0 | ERROR | False | unknown | NOT_RUN | unknown | Agent exceeded session timeout (1.0 min) |
| fastapi_15589 | E1 | ERROR | False | unknown | NOT_RUN | unknown | Agent exceeded session timeout (1.0 min) |
| requests_7205 | E0 | FAIL | True | True | FAIL | False | Agent exceeded session timeout (1.0 min) |
| requests_7205 | E1 | FAIL | True | True | FAIL | False | Agent exceeded session timeout (1.0 min) |
| rich_3061 | E0 | ERROR | False | unknown | NOT_RUN | unknown | Agent exceeded session timeout (1.0 min) |
| rich_3061 | E1 | ERROR | False | unknown | NOT_RUN | unknown | Agent exceeded session timeout (1.0 min) |

## Native tool engagement

Native trace attempts include exempt and denied invocations; reported charged calls come from official result.tool_calls. get_status/submit_patch are exempt; check_budget rejects before incrementing, while accepted calls that later fail are charged. Source: swegemma0.2.11 context.py:check_budget and tools/base.py:budget_gated.

| Arm | Recorded attempts | Reported charged calls | Vector calls | Graph calls |
| --- | ---: | ---: | ---: | ---: |
| E0 | 29 | 27 | 1 | 0 |
| E1 | 22 | 21 | 0 | 0 |

E1 made no recorded vector or graph tool call. Under the observed time limits, these runs do not test the efficacy of vector/graph retrieval.

## Next research steps

- Inspect the failed verification and incomplete patch-generation traces.
- Assess whether the fixed budgets permit implementation and verification before another experiment.
- Instrument missing localization/context metrics before interpreting retrieval efficiency.

## Provenance

- E0: 91f4d0fd-ef6a-41dd-a309-5503cb169ea6; source https://www.kaggle.com/code/diegofescobar/mostaza-e0-e1-phase-1-paired-benchmark; manifest SHA-256 `feb15462fe30bcf0b8d43a021b98aa037f3faa23f712518099f0e32c666cdf6b`; records SHA-256 `e7a198489beeeeb96b5de6f557a34627c0ab522d8fbf18488f88b33ecb115de6`.
- E1: 0e208445-edfa-4ae7-8b09-45e52aa9991c; source https://www.kaggle.com/code/diegofescobar/mostaza-e0-e1-phase-1-paired-benchmark; manifest SHA-256 `497f2d8bf9f8a35386a576b767ef5243fe7f2d8ff65c7392b37020bd0ca869b0`; records SHA-256 `bc9578948ef2928f336667459848f3f6306d1fb6e6fd5ecbb75d44f2fd58a9c8`.

## Unavailable or noncomparable measurements

- symbols_explored, fastapi_15589: E0: Not measured by the pinned result/trace contract; E1: Not measured by the pinned result/trace contract.
- symbols_explored, requests_7205: E0: Not measured by the pinned result/trace contract; E1: Not measured by the pinned result/trace contract.
- symbols_explored, rich_3061: E0: Not measured by the pinned result/trace contract; E1: Not measured by the pinned result/trace contract.
- files_explored, fastapi_15589: E0: Not measured by the pinned result/trace contract; E1: Not measured by the pinned result/trace contract.
- files_explored, requests_7205: E0: Not measured by the pinned result/trace contract; E1: Not measured by the pinned result/trace contract.
- files_explored, rich_3061: E0: Not measured by the pinned result/trace contract; E1: Not measured by the pinned result/trace contract.
- read_operations, fastapi_15589: E0: Native read_file events omit shell reads; full read coverage unavailable; E1: Native read_file events omit shell reads; full read coverage unavailable.
- read_operations, requests_7205: E0: Native read_file events omit shell reads; full read coverage unavailable; E1: Native read_file events omit shell reads; full read coverage unavailable.
- read_operations, rich_3061: E0: Native read_file events omit shell reads; full read coverage unavailable; E1: Native read_file events omit shell reads; full read coverage unavailable.
- search_operations, fastapi_15589: E0: Native similarity events omit lexical shell searches; full search coverage unavailable; E1: Native similarity events omit lexical shell searches; full search coverage unavailable.
- search_operations, requests_7205: E0: Native similarity events omit lexical shell searches; full search coverage unavailable; E1: Native similarity events omit lexical shell searches; full search coverage unavailable.
- search_operations, rich_3061: E0: Native similarity events omit lexical shell searches; full search coverage unavailable; E1: Native similarity events omit lexical shell searches; full search coverage unavailable.
- localization_seconds, fastapi_15589: E0: Not measured by the pinned result/trace contract; E1: Not measured by the pinned result/trace contract.
- localization_seconds, requests_7205: E0: Not measured by the pinned result/trace contract; E1: Not measured by the pinned result/trace contract.
- localization_seconds, rich_3061: E0: Not measured by the pinned result/trace contract; E1: Not measured by the pinned result/trace contract.
- code_characters, fastapi_15589: E0: Not measured by the pinned result/trace contract; E1: Not measured by the pinned result/trace contract.
- code_characters, requests_7205: E0: Not measured by the pinned result/trace contract; E1: Not measured by the pinned result/trace contract.
- code_characters, rich_3061: E0: Not measured by the pinned result/trace contract; E1: Not measured by the pinned result/trace contract.
- graph_expansions, fastapi_15589: E0: Not measured by the pinned result/trace contract; E1: Not measured by the pinned result/trace contract.
- graph_expansions, requests_7205: E0: Not measured by the pinned result/trace contract; E1: Not measured by the pinned result/trace contract.
- graph_expansions, rich_3061: E0: Not measured by the pinned result/trace contract; E1: Not measured by the pinned result/trace contract.
- repeated_context_characters, fastapi_15589: E0: Not measured by the pinned result/trace contract; E1: Not measured by the pinned result/trace contract.
- repeated_context_characters, requests_7205: E0: Not measured by the pinned result/trace contract; E1: Not measured by the pinned result/trace contract.
- repeated_context_characters, rich_3061: E0: Not measured by the pinned result/trace contract; E1: Not measured by the pinned result/trace contract.
- recall_at_k, fastapi_15589: E0: Not measured by the pinned result/trace contract; E1: Not measured by the pinned result/trace contract.
- recall_at_k, requests_7205: E0: Not measured by the pinned result/trace contract; E1: Not measured by the pinned result/trace contract.
- recall_at_k, rich_3061: E0: Not measured by the pinned result/trace contract; E1: Not measured by the pinned result/trace contract.
- relevant_context_ratio, fastapi_15589: E0: Not measured by the pinned result/trace contract; E1: Not measured by the pinned result/trace contract.
- relevant_context_ratio, requests_7205: E0: Not measured by the pinned result/trace contract; E1: Not measured by the pinned result/trace contract.
- relevant_context_ratio, rich_3061: E0: Not measured by the pinned result/trace contract; E1: Not measured by the pinned result/trace contract.
- repairs, fastapi_15589: E0: Not measured by the pinned result/trace contract; E1: Not measured by the pinned result/trace contract.
- repairs, requests_7205: E0: Not measured by the pinned result/trace contract; E1: Not measured by the pinned result/trace contract.
- repairs, rich_3061: E0: Not measured by the pinned result/trace contract; E1: Not measured by the pinned result/trace contract.

## Limitations

- Missing measurements are excluded per metric, never imputed as zero.
- Small exploratory cohort; descriptive differences do not establish significance or superiority.
- Small exploratory cohort; no significance or superiority claim.
- Unmeasured telemetry must remain null with reasons during normalization.
