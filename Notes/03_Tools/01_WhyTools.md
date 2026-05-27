---
module: 03_Tools
page: 01_WhyTools
title: Why tools? Agents without them are chatbots
estimated_minutes: 10
prereqs: [03_Tools/00]
concepts: [chatbot, tool, side-effect, IO]
icon: 🧠
in_production: false
detours_suggested: []
---

[← Prev: 03_Tools/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 03_Tools/02_FunctionTool →]

You are here: 🗺 Foundation Track ▸ 03 Tools ▸ 01 Why tools?

# 🧠 Why tools?

> An LLM with no tools can only **say** things. An LLM with tools can **do** things.

That's the whole pitch. Everything past this page is *how*.

## 🧠 Three things tools let an agent do

1. **Read the world** — fetch data the model doesn't have. Current weather, exchange rates, the contents of your inbox, the result of a SQL query.
2. **Compute deterministically** — math, hashing, formatting. The LLM is bad at arithmetic; a one-line `multiply(a, b)` tool is perfect at it.
3. **Change the world** — send a message, create a calendar event, file a JIRA ticket, write to a database.

Without tools, you have a chatbot that can suggest doing things. With tools, you have an agent that does them.

## 🧠 Inductive — three example agents

| Agent | Tools | Without tools |
|---|---|---|
| Weather assistant | `get_weather(city)` | "I'm a language model and can't access real-time data." |
| Calculator | `add`, `subtract`, `multiply`, `divide` | Gives wrong answers to "what's 47 * 31?" |
| Calendar manager | `list_events`, `create_event`, `send_invite` | "I can't see your calendar." |

The rule: **any time the model needs fresh data, deterministic math, or to change state, give it a tool.**

## 🧠 What tools are NOT

* Tools are not magic. They're Python functions ADK exposes to the LLM via a JSON schema.
* Tools are not "what the agent does." The agent (the LLM) *decides* what to do; tools are what it can choose from.
* Tools are not stateful by themselves. State lives on the Session (Module 04). A tool can *write* to state via `ToolContext` (page 04).

## ❓ Pop check

> ❓ **Ask the student:** the user asks the agent *"what is 7 * 8?"*. If you give the agent no tools, will the LLM answer correctly?
> *(Expected: usually yes for small numbers, but the model has no guarantee — it's pattern-matching. For 47 * 31 it might be off by one. A `multiply` tool makes the answer deterministic.)*

> 🛠 **Have the student do this:** open the `fun-facts` agent and *remove* `tools=[google_search]`. Re-run `adk run fun_facts` and ask "what's the most recent news about whales?" Note the response — it'll happily fabricate or refuse, because it has no way to know. Then add `google_search` back and ask again. The before/after is the case for tools.

> 🤖 **Tutor:** this page is short on purpose. The student doesn't need to be persuaded of the *value* of tools at length — they need to start *writing* them. Push on to page 02 quickly.

---

[← Prev: 03_Tools/00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 03_Tools/02_FunctionTool →]
