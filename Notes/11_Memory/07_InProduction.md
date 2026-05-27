---
module: 11_Memory
page: 07_InProduction
title: Memory in production
estimated_minutes: 20
prereqs: [11_Memory/06]
concepts: [memory bloat, PII, TTL, opt-in, cold start]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 11_Memory/06_DissectingMemoryBank]  [↑ Map](../../MAP.md)  [Next: 11_Memory/08_KnowledgeCheck →]

You are here: 🗺 Runtime Track ▸ 11 Memory ▸ 07 In Production

# 🚀 The five things that will bite you

## 1. Memory bloat → cost creep

Every session you keep growing the memory store. Retrieval gets slower; if you use `PreloadMemoryTool`, every turn gets a bigger system instruction; every memory write costs an LLM call (with Memory Bank) or an embedding (with Rag).

**Mitigations.**

- Set a **TTL** on memory items (per-user retention window — 30, 90, 365 days).
- Periodic **summarize-and-evict**: a nightly job that takes the oldest N items, asks an LLM to compress them into a single rolling summary, and deletes the originals.
- Cap `similarity_top_k` on retrieval; never let it grow unbounded.

## 2. PII in memory

If a user pastes their credit card or someone else's name, Memory Bank will happily summarize and persist it. That's now a record-keeping system you didn't intend to operate.

**Mitigations.**

- `before_agent_callback` that runs the user message through a PII detector (DLP, regex, a small classifier) and redacts before the session events get committed.
- Tighter: gate `add_session_to_memory()` on a "is this turn worth remembering" check; default-deny for anything that pattern-matches as sensitive.
- Document the data retained per user; surface a "wipe my memory" admin path. See `16_ProductionSecurity` for the GDPR/right-to-be-forgotten plumbing.

## 3. Memory as a feature flag (per-user opt-in)

Not every user should have memory enabled. Some products are *expected* to be amnesiac (anonymous browsing modes; high-privacy verticals like medical or legal until consent).

**Mitigation.**

- Wrap memory wiring in a per-user check:

```python
async def maybe_remember(ctx):
    if ctx.state.get("user:memory_opt_in"):
        await ctx.add_session_to_memory()
    return None
```

- Same for reads: gate `load_memory` behind an instruction conditional or omit `PreloadMemoryTool` for opt-out users (would require two agent variants — fine for prod).

## 4. Cold start: memory needs population time

Day 1 of launch, memory is empty for every user. Your beautiful personalization tells you nothing. Plan for a "no-memory" graceful fallback in the instruction.

## 5. Choosing the backend

| If you... | Use |
|-----------|-----|
| Want zero ops, accept Google's summarization | `VertexAiMemoryBankService` |
| Already operate a Vector Search corpus from 10A/10B | `VertexAiRagMemoryService` |
| Need offline tests, local dev only | `InMemoryMemoryService` |

## Quick checklist before launch

- [ ] TTL set on memory store (or eviction job scheduled).
- [ ] PII redaction runs before any `add_session_to_memory()` call.
- [ ] Per-user opt-in / opt-out plumbing in place.
- [ ] Memory backend choice documented (with the reason).
- [ ] "Wipe my memory" admin path tested end-to-end.
- [ ] `similarity_top_k` capped explicitly (not left at default).
- [ ] Instruction includes a no-memory fallback ("if you don't recall, ask").

> 🤖 **Tutor:** The PII point is the easiest place to lose a product. Don't let the student ship a memory-enabled agent without at least a basic redactor in `before_agent_callback`. Cross-link `16_ProductionSecurity` here.

---

[← Prev: 11_Memory/06_DissectingMemoryBank]  [↑ Map](../../MAP.md)  [Next: 11_Memory/08_KnowledgeCheck →]
