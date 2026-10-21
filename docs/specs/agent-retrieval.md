# agent-retrieval

Depends on: foundation

## Purpose

Define the controlled baseline and adaptive hybrid retrieval treatment.

## Requirements

REQ-1: Use one LlmAgent and the user-required 31B model for both experiments.
REQ-2: Adaptively combine lexical search, symbol embeddings, graph navigation and context selection using official tools.
REQ-3: Produce minimal patches and perform targeted verification within official budgets.

## Rules and constraints

AC-1: E0 is a single Google ADK LlmAgent derived minimally from the official starter, using gemma-4-31b-it-qat-w4a16-ct, authorized tools, no LoRA and no Graph-SDD retrieval optimization; every removal or adjustment from the official sample is documented and its source hashed.

AC-2: E1 preserves E0 model, generation parameters, tool availability, repair policy, budgets and environment; only exploration instructions change. It prioritizes exact lexical clues, then relevant one-hop graph neighbors and symbol-seeded similarity when useful; two-hop expansion needs explicit evidence, neighbors are bounded, visited symbols are reused and unproductive searches stop.

AC-3: E1 applies understandable context priorities: issue/test/stack-trace evidence and exact matches first, structural proximity and similarity next, then minimum sufficient code and low context cost; no learned ranker or claim of optimal weights. Understand, Explore, Implement and Verify remain phases of one agent, with E0-equivalent implementation and repair behavior.

AC-4: Both configurations use official budget enforcement, check get_status at meaningful transitions, preserve time for patching and verification, and record observed model/tool calls, time, reads, graph expansions and repairs when exposed; starting numeric limits are copied from the inspected official baseline, shared across arms and labeled provisional until measured.

AC-5: Frozen E0/E1 packaging requires an explicit E0 or E1 selection, produces a deterministic submission.zip with root agent.yaml and only its allowed dependency closure, and fails on traversal, symlinks, unknown tools/models, forbidden files or missing includes. Both archives pass current official directory/schema/compiler validation; archive creation alone never establishes official evaluation compatibility. The active submission may instead use the narrowly allowlisted search-code skill and six native tools under search-code:AC-1/AC-7; historical archives retain their declarative closure.

AC-6: Official graph/embedding fixtures and source-based contract tests verify symbol lookup, missing/ambiguous symbols, unavailable graph data and bounded retrieval behavior without external encoders or databases; prompt-policy tests are never represented as proof that a real agent followed those policies.

## Product decisions

PD-1 — E0 is a documented minimal single-agent/no-LoRA derivation, not a claim of byte-identical official sample reproduction; remove only sample delegation/adapters needed to honor MVP constraints (plan: mostaza-phase1-foundation, 2026-10-13).
PD-2 — E1 changes the exploration section only; a broader Graph-SDD repair/planning treatment is deferred to avoid confounding E1-minus-E0 (plan: mostaza-phase1-foundation, 2026-10-13).
PD-3 — Implement retrieval policy in instructions using native tools; omit custom skill scripts in this MVP because native capabilities suffice. Use symbol queries rather than a text encoder, one-hop first and evidence-based two-hop expansion (plan: mostaza-phase1-foundation, 2026-10-13).

PD-4 — Scope the native-only MVP to frozen E0/E1 and permit the active search-code bootstrap skill without changing historical experiments (plan: 2026-10-20-search-code, 2026-10-20).

## Interfaces and data contracts

The frozen E0/E1 submissions contain declarative YAML and referenced prompt files only. The active search-code candidate follows search-code interfaces; the remaining native retrieval statements here describe historical E0/E1. Tool names and signatures come from the pinned official harness, including search_similar_code(query, k), get_code_neighbors(node, edge_type, max_neighbors), get_code_subgraph(nodes), get_status and patch/workspace tools. Use fully qualified verified symbols where available; ambiguous suffixes are disambiguated with repository evidence before query. Local Python helpers never become submitted tools. Lexical search uses available grep/find/git grep, without assuming rg.

## Out of scope

Fine-tuning, reinforcement learning, specialized multiagents, external embedding/vector/graph services, public APIs, dashboards, deployment and exhaustive hyperparameter tuning are outside Phase 1. No model downloads on the Mac.
