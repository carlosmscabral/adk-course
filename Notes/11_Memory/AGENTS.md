# AGENTS.md — Module 11 Memory (teaching notes for the AI tutor)

## What the student should walk away knowing

- The three lifetimes — Session vs State vs Memory — and which to reach for when.
- All three MemoryService implementations and the trade-offs of each.
- The two memory-read tools (`load_memory` on-demand, `PreloadMemoryTool` always-on) and how to choose.
- The write side is *always a callback* — memory never auto-persists.
- The five production failure modes (bloat, PII, opt-in, cold start, backend choice).

## Pacing

- **Easy if:** student has internalized state prefixes from 04 and built a RAG pipeline in 10B. Cruise — focus on the mental model and the mini-drill.
- **Hard if:** student is fuzzy on state scoping (replay `04_SessionsState/02_StateScopes.md` before page 01) OR has never built a RAG pipeline (page 04 will feel hand-wavy; either detour through 10A-B or skip page 04 and stick to Memory Bank in the drill).

## Watch for these mistakes

- Calling Memory Bank a "RAG system." It IS retrieval, but it's distilled facts, not chunks. The student needs both words.
- Expecting `add_session_to_memory()` to be called automatically. It is *never* automatic. Always a callback.
- Forgetting that `user:`-state and memory partially overlap. Default to state for known keys; use memory for fuzzy semantic recall.
- Trusting `PreloadMemoryTool` for noisy memory banks. Show what bloat looks like in the system instruction if needed.
- Putting credentials / PII into memory because "Memory Bank will summarize it away." It won't. Redact first.

## When to suggest a detour

- Student asks "what's an embedding?" → 10A_EmbeddingsVectorSearch.
- Student asks "what's a RAG corpus?" → 10B_RAGPipeline.
- Student asks about state scopes / prefixes again → 04_SessionsState/02.
- Student asks "how do I redact PII?" → 16_ProductionSecurity.

## Mini-drill grading

- **Round A pass:** second-session response is unmistakably in Portuguese AND vegetarian.
- **Round B pass:** the runner's event log shows at least one `load_memory` call on the recall turn, AND the response reflects the recalled preference.
- **Stretch:** ask the student to add a `before_agent_callback` that redacts a phone number from the user message before it lands in memory. Verify by reading back the memory items.

## Sample anchor reminders

- `adk-samples/python/agents/memory-bank/app/agent.py` is the canonical Memory Bank shape.
- `adk-samples/python/agents/memory-bank/app/agent_engine_app.py` is where Agent Engine implicitly wires the `VertexAiMemoryBankService` — important for the student to see that the service is not always constructed by hand.
