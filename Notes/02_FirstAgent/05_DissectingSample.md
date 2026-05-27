---
module: 02_FirstAgent
page: 05_DissectingSample
title: Dissecting currency-agent
estimated_minutes: 20
prereqs: [02_FirstAgent/04]
concepts: [LlmAgent, McpToolset, currency-agent]
icon: 🧠
in_production: false
detours_suggested: []
---

[← Prev: 02_FirstAgent/04_TheGeminiPayload](04_TheGeminiPayload.md)  [↑ Map](../../MAP.md)  [Next: 02_FirstAgent/06_InProduction →]

You are here: 🗺 Foundation Track ▸ 02 First Agent ▸ 05 Dissecting currency-agent

# 🧠 Dissecting `currency-agent`

Open [`adk-samples/python/agents/currency-agent/currency_agent/agent.py`](../../../adk-samples/python/agents/currency-agent/currency_agent/agent.py). ~40 lines. Reproduced here:

```python
import logging
import os
from dotenv import load_dotenv
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

load_dotenv()

SYSTEM_INSTRUCTION = (
    "You are a specialized assistant for currency conversions. "
    "Your sole purpose is to use the 'get_exchange_rate' tool to answer "
    "questions about currency exchange rates. "
    "If the user asks about anything other than currency conversion or "
    "exchange rates, politely state that you cannot help with that topic "
    "and can only assist with currency-related queries. "
    "Do not attempt to answer unrelated questions or use tools for other purposes."
)

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="currency_agent",
    description="An agent that can help with currency conversions",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=os.getenv("MCP_SERVER_URL", "http://localhost:8080/mcp")
            )
        )
    ],
)

a2a_app = to_a2a(root_agent, port=10000)
```

## 🧠 What's the same as `fun-facts`?

* `LlmAgent(name=, model=, instruction=, description=)`. Same constructor.
* `model="gemini-2.5-flash"` — pinned (good).
* `load_dotenv()` for the API key.
* The agent exposes `root_agent` so `adk run currency_agent` works.

## 🧠 What's new?

1. **`McpToolset`** — instead of a function tool, the agent connects to an **MCP server** (Model Context Protocol — a tool transport) over HTTP. The MCP server exposes `get_exchange_rate` and possibly more. ADK auto-discovers tools from the connected server. We cover MCP in depth in Module 08; for now, treat it as "tools coming from a remote process."
2. **`to_a2a(root_agent, port=10000)`** — wraps the agent as an A2A (Agent-to-Agent) HTTP server. Other agents can call this one over the network. Covered in Module 10.

## 🧠 Where's the runtime?

Same as `fun-facts` — nowhere in the file. `adk run currency_agent` builds Runner + Session for you. The added `to_a2a(...)` doesn't change that; it just exposes a *second* way to invoke the agent (via HTTP).

## 🛠 Run it by hand (without `adk run`)

You now have everything you need to run `currency-agent` without the CLI. The MCP server requirement makes a full end-to-end run beyond this page, but the runner setup is identical to page 03 — only the agent import changes:

```python
# Work/currency_by_hand.py
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv
load_dotenv()

# Skip the import if no MCP server is running. This is for illustration.
# from currency_agent.agent import root_agent

# Otherwise the loop is exactly what you wrote on page 03.
```

The point isn't to run currency-agent right now (that's Module 08). The point is: **the by-hand pattern from this module scales to every sample in `adk-samples/`**. They all expose a `root_agent`. They all run through `Runner.run_async`. The complexity scales with the *agent config*, not the *plumbing*.

## ❓ Quick check

> ❓ **Ask the student:** if `adk run currency_agent` does all this for you, why did we bother building it by hand?
> *(Expected: a few reasons.* (a) *Understanding the seams means you can swap session backends, attach plugins, wrap the runner in a web server, or embed an agent in a non-CLI app — none of which `adk run` supports.* (b) *Debugging a real production deploy means knowing what each line does.* (c) *Engine-first learning sticks; abstraction-first leaves gaps.)*

> 🛠 **Have the student do this:** open the file in their editor and physically annotate each line with which by-hand step (from `_figures/by_hand_vs_cli.txt`) it corresponds to. The `adk` CLI hides them; the student now knows where they are.

---

[← Prev: 02_FirstAgent/04_TheGeminiPayload](04_TheGeminiPayload.md)  [↑ Map](../../MAP.md)  [Next: 02_FirstAgent/06_InProduction →]
