---
description: What we're testing — does hierarchical TOC-based context improve agent performance over raw markdown files?
---

# Hypothesis

A hierarchical CONTEXT/ folder with auto-generated TOC indexes helps LLM coding agents:

1. Find relevant information faster (fewer tool calls / file reads)
2. Produce more accurate answers (especially for architectural questions)
3. Use fewer tokens overall
4. Surface non-obvious context that grep/RAG wouldn't find

Secondary hypothesis: the benefit is larger for smaller/weaker models, since they are more sensitive to context noise and benefit more from structured progressive disclosure.

## What we're NOT testing

- Whether context files are better than no context at all (the ETH Zurich study covers this)
- Whether LLM-generated context helps (research says it hurts — we use human-written context only)
- RAG vs lexical search (tool-dependent, not something we control)

## What we ARE testing

Whether the context-md scaffolding (TOC indexes, description-based filtering, bootstrap rules, hierarchical navigation) adds value on top of the same underlying content. Both branches have the same markdown documents — one has the discovery mechanism, the other doesn't.
