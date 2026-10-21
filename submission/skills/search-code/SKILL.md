---
name: search-code
description: Bootstrap bounded lexical source search and conservative Python graph navigation in the task workspace, then query through run_command.
---

Use this skill to locate source paths, text and Python symbols. Retrieval is lexical; it does not provide vector similarity. Index only source visible inside the task workspace.

1. Obtain the real absolute Python workspace root with native `run_command`: `python3 -c "import os; print(os.getcwd())"`. Do not assume that the shell alias `/workspace` is a real Python path in subprocess sandboxes. Docker normally returns `/workspace`; use the actual returned value in either environment.
2. Invoke `run_skill_script` with `skill_name="search-code"`, `file_path="scripts/search_code.py"` and `args=["bootstrap", "--root", "ABSOLUTE_ROOT", "--query", "literal keywords"]`. Use a JSON argument list, not a shell command string. The optional query performs the first search. The skill runs in a temporary resource directory; always provide the explicit workspace root.
3. Parse its schema_version=1 JSON. Save `executable_path` and `command`. Bootstrap persists the exact standalone CLI outside the repository; its executable and cache are private, disposable and bound to this workspace/version. Skill resources disappear after execution. Do not copy them into the repository.
4. Use native `run_command` for subsequent queries. The returned `command` already quotes the executable and root and contains a `QUERY` placeholder. Replace that argument with shell-quoted literal text, preserving the other quoting. Never interpolate untrusted text as shell syntax. Examples below use placeholders that must be shell-quoted individually:

   `python3 'EXECUTABLE_PATH' search --root 'ABSOLUTE_ROOT' --query 'literal keywords' --path 'relative/path' --limit 8`

   `python3 'EXECUTABLE_PATH' neighbors --root 'ABSOLUTE_ROOT' --symbol 'EXACT_SYMBOL_ID' --edge-kind callees --limit 20`

   `python3 'EXECUTABLE_PATH' subgraph --root 'ABSOLUTE_ROOT' --symbol 'EXACT_SYMBOL_ID' --hops 1`

   `python3 'EXECUTABLE_PATH' status --root 'ABSOLUTE_ROOT'`

Every operation reconciles content fingerprints, including native write_file/edit_file/run_command changes, additions, deletions and renames. An unchanged warm query reparses no files. No manual refresh or daemon is required. Resolve ambiguous names using returned exact IDs. Graph edges cover statically resolvable Python calls/imports/containment; dynamic or ambiguous references stay unresolved. Non-Python source has lexical coverage only.

Queries are literal and at most 512 characters. Default 8 results, maximum 20; subgraphs default to one hop, maximum two, with at most 40 nodes/80 edges. Each operation has a 45-second cooperative deadline. JSON stdout fits 4500 characters and reports status, truncation/incompleteness, refresh counters and omitted/unresolved counts. Read only the returned relevant lines with read_file. Never equate incomplete, parse-failed, limited or ambiguous results with absence.

If bootstrap, FTS5 or indexing is unavailable, use native run_command for a narrow literal shell search: `grep -n -F -- 'literal text' 'relative/source.py'`. Quote query/path independently, bound the paths/output and remain in the task workspace. Do not search host packages, task metadata, solutions, reference patches, precomputed graphs or verifier data. Do not place caches/scripts in source or the submitted patch.

Keep the existing 60-second command timeout, 5-minute task, 20 native-call and 50-turn budgets. Bootstrap and cold indexing consume wall time. The pinned executor checks the native context budget for script execution; native run_command/read/write/edit also count, while get_status/submit_patch do not increment that counter. Skill discovery/load/resource helpers are additional official ADK tools and are not evidence of free time or extra turns. Check get_status before exploration, implementation and verification; reserve time for a minimal fix, targeted test and submit_patch.
