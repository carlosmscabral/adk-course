---
module: 01_Foundations
page: 01_WhatIsAnAgent
title: What is an agent? The loop, drawn.
estimated_minutes: 15
prereqs: [01_Foundations/00]
concepts: [agent-loop, tool-call, reply]
icon: 🧠
in_production: false
detours_suggested: []
---

[← Prev: 01_Foundations/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 01_Foundations/02_RunnerSessionEvent →]

You are here: 🗺 Foundation Track ▸ 01 Foundations ▸ 01 What is an Agent?

# 🧠 What is an agent?

> An **agent** is a piece of software that drives an LLM in a loop: each turn it sends the conversation to the LLM, parses the response as either a final text reply or a tool-call request, executes the tool, feeds the result back, and repeats — until the LLM produces a reply (or you cap the loop).

The LLM itself is stateless and tool-less; it just emits tokens. The **agent** is the program that interprets those tokens as actions and keeps the loop running. Hold this distinction precisely — when you build `Runner` + `Session` by hand in Module 02, you are building exactly that program.

That's it. The whole field of "agentic AI" reduces to that loop. Everything else — multi-agent, callbacks, plugins, A2A — is plumbing around it.

## 🧠 The loop, drawn

```
              ┌─────────────────────────────────────────┐
              │            THE AGENT LOOP               │
              └─────────────────────────────────────────┘

       user msg
            │
            ▼
   ┌─────────────────────────────────────────────────────┐
   │   AGENT  ── your loop code (the program)            │
   │                                                     │
   │   while True:                                       │
   │      append latest_msg to history                   │
   │                                                     │
   │      tokens = LLM(history + tool_catalog) ──────────┼──┐
   │      parsed = parse(tokens)                         │  │   ┌─────────┐
   │                                                     │  └──►│   LLM   │
   │      if parsed is a TEXT REPLY:                     │      │ (Gemini)│
   │          return parsed.text to user  ── DONE        │ ◄────┤ tokens  │
   │                                                     │      │ in/out, │
   │      else:  # parsed is a TOOL CALL                 │      │ no state│
   │          # the AGENT runs the tool — not the LLM    │      └─────────┘
   │          result     = tool(parsed.args) ────────────┼──┐
   │          latest_msg = result                        │  │   ┌─────────┐
   │          continue                                   │  └──►│  TOOL   │
   │                                                     │      │ (Python │
   │                                                     │ ◄────┤  func)  │
   └─────────────────────────────────────────────────────┘      └─────────┘

   The AGENT is the box: the loop, the history, the parse, the tool
   execution, the decision to stop. The LLM and TOOL are services the
   agent invokes. The LLM never runs your tools — it emits a request
   as tokens; the AGENT parses those tokens and runs the tool.
```

> 🤖 **Tutor:** display this ASCII drawing **verbatim** to the student before any prose around it. The page's whole reading order assumes the drawing is on screen. If you skip it, the bullets below have nothing to refer to.

Reading it left-to-right, top-to-bottom:

1. The **user message** is appended to the conversation.
2. The whole conversation (system prompt + history + this message) is sent to the **LLM**, along with the JSON schema of every tool the agent knows about.
3. The LLM returns tokens. The agent parses those tokens as either:
   * A **text reply** → the turn is over.
   * A **tool-call request** with a name + JSON arguments — the LLM is asking the agent to run a specific tool. The LLM does not run it; it just emits the request.
4. If it was a tool-call request, **the agent** looks up the matching Python function, runs it, appends the result to the conversation, and sends the whole thing back to the LLM.
5. Loop until the LLM produces a text reply (or you cap iterations and bail).

That's the agent loop. Burn it in.

## 🧠 Three examples (inductive, then deductive)

**Example 1 — chatbot (no tools).** `fun-facts` if you delete `tools=[google_search]`. Agent forwards the user message to the LLM; LLM emits a text reply; agent returns it to the user. One iteration, no tool round-trip.

**Example 2 — single-tool agent.** `fun-facts` as-shipped. User asks *"tell me a fact about octopuses."* The LLM emits a tool-call request for `google_search("octopus facts")`, the search runs, the result is fed back into the LLM, and the LLM emits a final text reply summarizing it. **Two iterations** (one tool round-trip + one final reply).

> ⚠️ **Built-in vs custom tools — important nuance.** `google_search` is a Gemini **built-in**: the search itself runs **server-side at Google**, not inside your agent's Python process. The "agent runs the tool" framing from the loop diagram applies to *custom* tools — Python functions you wrap as `FunctionTool`. For built-ins, the model and Google's infrastructure handle dispatch; the agent just sees the grounded response come back through the event stream. We use `google_search` in Example 2 because it ships as the simplest one-line agent in the samples — but **Example 3 is the canonical "agent runs the tool" case.** Module 03 makes the built-in vs custom distinction precise.

**Example 3 — multi-tool agent (Module 03 preview).** User asks *"what's 3 * (2 + 5)?"* with `[add, multiply]` tools.
1. LLM emits tool-call `add(2, 5)`; **agent** runs it → `7`; appends; calls LLM again.
2. LLM emits tool-call `multiply(3, 7)`; **agent** runs it → `21`; appends; calls LLM again.
3. LLM emits a final text reply. Done.

**Three iterations.** Notice the pattern: the LLM only ever emits — text or a tool-call request. The agent does all the running.

The rule: **iterations = (number of tool calls) + 1 final reply.**

> ❓ **Ask the student:** in Example 3, what would the LLM see in its context window on the third call?
> *(Expected: the full chat so far — user message, first tool call, first tool result, second tool call, second tool result. Each tool exchange adds two events.)*

## ⚠️ The "it loops forever" risk

Nothing in the diagram prevents the LLM from calling tools forever. Maybe a tool keeps returning errors and the LLM keeps retrying. Maybe the system prompt is ambiguous and the model keeps "thinking." Production agents always cap the loop somehow — Module 02 introduces `LoopAgent(max_iterations=N)` and Module 07 introduces `escalate` for early-exit. For now, just notice the failure mode exists.

> 🛠 **Have the student do this on paper:** draw the loop for the question *"What's the weather in Tokyo and Madrid?"* given tools `[get_weather(city)]`. How many iterations? What's in the LLM's context on each call?
> *(Expected: 3 iterations — call 1: `get_weather("Tokyo")`; call 2: `get_weather("Madrid")`; call 3: final text reply with both temps.)*

---

[← Prev: 01_Foundations/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 01_Foundations/02_RunnerSessionEvent →]
