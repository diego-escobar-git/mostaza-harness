# Paired experiment: B180-startup-v3

Run kind: **real_kaggle**. Cohort: 3.
Differences are E1 minus E0; the direction of improvement depends on the metric.

| Metric | Unit | Measured pairs | Measured mean delta | Estimated pairs | Estimated mean delta |
| --- | --- | ---: | ---: | ---: | ---: |
| symbols_explored | count | 0 | unavailable | 0 | unavailable |
| files_explored | count | 0 | unavailable | 0 | unavailable |
| read_operations | count | 0 | unavailable | 0 | unavailable |
| search_operations | count | 0 | unavailable | 0 | unavailable |
| localization_seconds | seconds | 0 | unavailable | 0 | unavailable |
| tokens | tokens | 3 | 85111.66666666667 | 0 | unavailable |
| code_characters | characters | 0 | unavailable | 0 | unavailable |
| graph_expansions | count | 0 | unavailable | 0 | unavailable |
| repeated_context_characters | characters | 0 | unavailable | 0 | unavailable |
| recall_at_k | ratio | 0 | unavailable | 0 | unavailable |
| relevant_context_ratio | ratio | 0 | unavailable | 0 | unavailable |
| tool_calls | count | 3 | 6 | 0 | unavailable |
| total_seconds | seconds | 3 | 3.939157165666567 | 0 | unavailable |
| repairs | count | 0 | unavailable | 0 | unavailable |

| Arm | PASS | FAIL | ERROR | NOT_RUN | Cohort denominator |
| --- | ---: | ---: | ---: | ---: | ---: |
| E0 | 0 | 2 | 1 | 0 | 3 |
| E1 | 0 | 2 | 1 | 0 | 3 |

## Per-task outcomes

| Instance | Arm | Status | Patch present | Patch valid | Tests | Resolved | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fastapi_15589 | E0 | ERROR | False | unknown | NOT_RUN | unknown | Sandbox execution error: litellm.ContextWindowExceededError: litellm.BadRequestError: ContextWindowExceededError: OpenAIException - This model's maximum context length is 32768 tokens. However, you requested 16384 output tokens and your prompt contains at least 16385 input tokens, for a total of at least 32769 tokens. Please reduce the length of the input prompt or the number of requested output tokens. (parameter=input_tokens, value=16385) |
| fastapi_15589 | E1 | FAIL | True | True | FAIL | False | Sandbox execution error: litellm.ContextWindowExceededError: litellm.BadRequestError: ContextWindowExceededError: OpenAIException - This model's maximum context length is 32768 tokens. However, you requested 16384 output tokens and your prompt contains at least 16385 input tokens, for a total of at least 32769 tokens. Please reduce the length of the input prompt or the number of requested output tokens. (parameter=input_tokens, value=16385) |
| requests_7205 | E0 | FAIL | True | True | FAIL | False | none |
| requests_7205 | E1 | FAIL | True | True | FAIL | False | none |
| rich_3061 | E0 | FAIL | True | True | FAIL | False | Agent exceeded session timeout (3 min) |
| rich_3061 | E1 | ERROR | False | unknown | NOT_RUN | unknown | Agent exceeded session timeout (3 min) |

## Next research steps

- Inspect the failed verification and incomplete patch-generation traces.
- Assess whether the fixed budgets permit implementation and verification before another experiment.
- Instrument missing localization/context metrics before interpreting retrieval efficiency.

## Provenance

- E0: 24b2879a-40fa-41c0-b143-8c09832e05f7; source https://www.kaggle.com/code/diegofescobar/mostaza-b180-ea1534a86873409b870b3b04d04e347f?scriptVersionId=358394257; manifest SHA-256 `6a536462ebfab50a39189d4fd1c739231d4dd9e706463c8c0fd251be28ded52d`; records SHA-256 `ca97646f7ebc60ad00b6da7b57039af74b0671dc9cd32b61549ea7a324a75519`.
- E1: e108b892-8c66-4105-af66-59217928ec73; source https://www.kaggle.com/code/diegofescobar/mostaza-b180-ea1534a86873409b870b3b04d04e347f?scriptVersionId=358394257; manifest SHA-256 `e109b4382a54bd3c16814e3cf2ec50e41bdbc7ccc21a61cae2f4d02c015f0c17`; records SHA-256 `52927ddf5cdc4e61e4507253cd110a6868dec6324220474a9d3464eafa4cd1ca`.

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

- Exploratory cohort; no significance or superiority claim
- Host-derived pair ID B180-startup-v3; native configuration ID E0-B180
- Host-derived pair ID B180-startup-v3; native configuration ID E1-B180
- Missing measurements are excluded per metric, never imputed as zero.
- Native unversioned source URL refined to observed exact saved version
- Recorded usage excludes unreported failed-request usage; not physical token billing
- Small exploratory cohort; descriptive differences do not establish significance or superiority.
