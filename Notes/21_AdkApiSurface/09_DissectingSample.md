---
module: 21_AdkApiSurface
page: 09_DissectingSample
title: Dissecting currency-agent served three ways
estimated_minutes: 35
prereqs: [21_AdkApiSurface/08]
concepts: [adk run, adk api_server, to_a2a, the same agent, three surfaces]
icon: 🔬
in_production: false
detours_suggested: []
---

[← Prev: 08_AuthenticatingTheApi](08_AuthenticatingTheApi.md)  [↑ Map](../../MAP.md)  [Next: 10_InProduction →](10_InProduction.md)

You are here: 🗺 Deployment & Integration Track ▸ 21 ADK API Surface ▸ 09 Dissecting Sample

---

## 🔬 The sample

`/home/carloscabral/study/adk-samples/python/agents/currency-agent/`

```
currency-agent/
├── README.md
├── pyproject.toml
├── currency_agent/
│   ├── __init__.py
│   ├── agent.py            ← single LlmAgent + to_a2a() at module load
│   └── test_client.py      ← A2A client that talks to the agent
└── mcp-server/
    └── server.py           ← MCP server exposing get_exchange_rate
```

**Why this sample for this module.** A single ~40-line `agent.py` exposes the *same* `LlmAgent` through **three** different transport surfaces. It is the cleanest demonstration that ADK's "surface" is decoupled from the agent definition.

> 🛠 **Have the student run:** `ls /home/carloscabral/study/adk-samples/python/agents/currency-agent/` and confirm the layout.

## 🔬 File 1 — `currency_agent/agent.py`

Open `/home/carloscabral/study/adk-samples/python/agents/currency-agent/currency_agent/agent.py`. The whole file is 40 lines. Read top to bottom.

**Lines 1-13 — imports + dotenv + logging.** Nothing special, but notice `from google.adk.a2a.utils.agent_to_a2a import to_a2a` — the A2A wrapping is a separate import, kept opt-in.

**Lines 25-37 — the agent.**

```python
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
```

One `LlmAgent`. One MCP tool source. **This is the agent.** Everything else in the file is *publishing surfaces* over it.

**Line 40 — the A2A surface.**

```python
a2a_app = to_a2a(root_agent, port=10000)
```

`to_a2a(...)` returns an A2A-server Starlette app that wraps the runner. Notice the `port=` arg here is **metadata for the A2A AgentCard**, not the bind port of the process — uvicorn still picks the bind port at run-time.

> ❓ **Ask the student:** "Where in this file is the HTTP server defined?" *(Trick — it isn't. The README's `uvicorn currency_agent.agent:a2a_app` line *runs* the Starlette app `a2a_app` was bound to.)*

## 🔬 Surface #1 — `adk run`

```bash
adk run currency_agent
```

What happens (cross-link page 01A):
1. `AgentLoader.load_agent("currency_agent")` → fires `currency_agent/__init__.py` → fires `agent.py` → loads `root_agent`.
2. `_to_app(root_agent, "currency_agent")` → wraps to `App`.
3. REPL loop. Same as page 01.

Note: `a2a_app = to_a2a(root_agent, port=10000)` *also* executes during import — but `adk run` does nothing with it. The A2A server only starts when **uvicorn** is pointed at `a2a_app`. Three surfaces, one import; only the one you invoke runs.

## 🔬 Surface #2 — `adk web` / `adk api_server`

```bash
adk api_server currency_agent --port 8000
# or
adk web currency_agent --port 8501
```

Same loader path. Now the runner is wrapped in the FastAPI app from page 02. The same `root_agent` is exposed at `POST /run`, `POST /run_sse`, etc. URL `app_name` = `currency_agent` (the dir).

## 🔬 Surface #3 — `to_a2a()` + uvicorn

```bash
uv run uvicorn currency_agent.agent:a2a_app --host localhost --port 10000
```

Now we're running the Starlette app `a2a_app` directly. This serves the **A2A protocol** (agent card at `/.well-known/agent.json`, task endpoints at `/tasks`, etc.) — full coverage in module **10 A2A**. The agent it wraps is the same `root_agent`.

`test_client.py` then talks A2A:

```bash
uv run currency_agent/test_client.py
```

This calls the A2A client SDK to discover the agent, open a task, and stream responses.

## 🔬 The whole point in one diagram

```
                       currency_agent/agent.py
                              │
                              ▼
                         root_agent  (LlmAgent + McpToolset)
                          ╱     │     ╲
            ┌────────────┘      │      └────────────────┐
            ▼                   ▼                       ▼
       adk run            adk api_server          uvicorn a2a_app
       (TTY REPL)         (HTTP JSON+SSE+WS)     (A2A protocol)
```

One agent. Three transports. No coupling between the agent and the transport.

## 🛠 Question-driven dissection

Have the student answer (peeking is fair):

1. **What is the smallest change to `agent.py` to add a new tool?** *(Add it to `tools=[...]`; nothing else changes.)*
2. **If you drop `to_a2a(...)`, what breaks?** *(Only surface #3 — the other two still work.)*
3. **Why does the MCP server live in `mcp-server/` and not as a tool function in `agent.py`?** *(Because the MCP server is a separate process — the agent talks to it over `StreamableHTTPConnectionParams`. Module 08 MCP covers this.)*
4. **Which surface would you ship for a public mobile app?** *(Neither REPL nor A2A — you'd want `adk api_server` behind auth + your own SPA. Module 23 picks this up.)*

> 🤖 **Tutor:** if the student wants to actually run all three surfaces, have them set up `.env` per the README (Gemini API key route is fastest), then run the MCP server in one terminal, the agent in a second, and a client (curl for HTTP, `test_client.py` for A2A) in a third. This is the canonical "ADK in three terminals" demo.

## Module concepts present in this sample

| Module concept                | Where in the sample                                |
|-------------------------------|----------------------------------------------------|
| Agent loader contract (01A)   | `currency_agent/__init__.py` + `agent.py`          |
| `adk api_server` shape (02)   | runs against `currency_agent` package directly     |
| `to_a2a` + uvicorn (06)       | `agent.py` line 40 + README run command            |
| Auth at the boundary (08)     | **Absent** — the sample is dev-only; this is the gap we fix in M3 |

---

[← Prev: 08_AuthenticatingTheApi](08_AuthenticatingTheApi.md)  [↑ Map](../../MAP.md)  [Next: 10_InProduction →](10_InProduction.md)
