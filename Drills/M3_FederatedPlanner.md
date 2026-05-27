---
module: Drills
page: M3_FederatedPlanner
title: Milestone M3 — Federated Travel Planner (Callbacks + MCP + Skills + A2A)
estimated_minutes: 960
prereqs: [00_Setup/last, 01_Foundations/last, 02_FirstAgent/last, 03_Tools/last, 04_SessionsState/last, 05_MultiAgent/last, 07_Callbacks/last, 08_MCP/last, 09_Skills/last, 10_A2A/last]
concepts: [SequentialAgent, sub_agents, MCPToolset, FastMCP, Skill, SkillToolset, to_a2a, RemoteA2aAgent, before_tool_callback]
icon: 🏁
in_production: false
detours_suggested: [FastMCP, a2UI, VisualBuilder]
---

[← Prev: 10_A2A/09_MiniDrill](../Notes/10_A2A/09_MiniDrill.yml)  [↑ Map](../MAP.md)  [Next: 11_Memory/00_Overview →](../Notes/11_Memory/00_Overview.md)

You are here: 🗺 Drills ▸ 🏁 M3 Federated Travel Planner

## 🏁 What you're building

A **federated travel planner** that exercises every primitive from the Integration Track at once:

```
                       ┌─────────────────────────────────────────────────────┐
                       │   PLANNER PROCESS  (port 10002, A2A endpoint)       │
                       │                                                     │
   client.py           │   root: travel_planner (LlmAgent)                   │
   ──── A2A ────►      │   ├── itinerary_agent  (LlmAgent sub_agent)         │
   RemoteA2aAgent      │   └── booking_agent    (LlmAgent sub_agent)         │
                       │           ├── SkillToolset(booking_skill)           │
                       │           └── MCPToolset ──► hotels_mcp (port 8090) │
                       └─────────────────────────────────────────────────────┘
                                                          │
                                                          ▼
                                            ┌──────────────────────────┐
                                            │  HOTELS MCP SERVER       │
                                            │  fastmcp, port 8090      │
                                            │  tools: search_hotels,   │
                                            │         book_hotel       │
                                            └──────────────────────────┘
```

Three OS processes, one network, every M07-M10 primitive touched at least once.

## 🎯 Goals

- **Compose A2A + MCP** in the same agent: one protocol facing the caller, the other facing the data source.
- **Package a sub-agent's domain logic as a Skill** so the booking flow has reusable, progressively-disclosed instructions.
- **Wire a callback policy** that enforces a real business rule (price ceiling) at the sub-agent boundary.
- **Survive the two-process / three-process debugging loop** — separate terminals, separate logs, real network calls.
- See first-hand why the AgentCard reflects sub-agents and tools (the card you publish at port 10002 will mention the booking flow that itself reaches an MCP server).

## 📋 Prereqs

- Completed `Notes/00_Setup` through `Notes/10_A2A`, including all mini-drills.
- `google-adk` installed (2.0 GA or later) — needs `to_a2a`, `RemoteA2aAgent`, `SkillToolset`, `MCPToolset`.
- `fastmcp` installed (for the hotels MCP server).
- `uvicorn` installed (for the A2A ASGI app).
- LLM credentials configured (Gemini API key or Vertex auth).
- Python ≥ 3.11.
- Three terminals or a tmux session you can split. (Seriously — debugging this in one terminal is misery.)

## ⏱ Time

**2 days** (~12-16 hours actual).

- **Day 1** (~6-8h): MCP hotels server + planner agent tree + Skill packaging + local sanity check (no A2A yet).
- **Day 2** (~6-8h): `to_a2a` wrapper + client with `RemoteA2aAgent` + callback policy + verification + stretch goals.

## 📐 Spec

Place everything under `Work/M3/`:

```
Work/M3/
├── hotels_mcp/
│   └── server.py                ← FastMCP server, port 8090
├── planner/
│   ├── __init__.py
│   ├── agent.py                 ← root + itinerary + booking sub-agents, exports a2a_app
│   ├── callbacks.py             ← price_ceiling_guard
│   └── skills/
│       └── booking/
│           ├── SKILL.md         ← frontmatter + L2 instructions
│           └── resources/
│               └── booking_policy.md   ← L3 resource (fees, cancellation rules)
├── client.py                    ← uses RemoteA2aAgent against http://localhost:10002
└── run_all.md                   ← short notes on terminal layout (optional)
```

### Part 1 — `hotels_mcp/server.py` (FastMCP, port 8090)

A `FastMCP` server with exactly two tools:

```python
from fastmcp import FastMCP

mcp = FastMCP("Hotels MCP Server")

_FAKE_DB = {
    "NYC": [
        {"id": "nyc-1", "name": "Hudson Loft", "price_per_night": 220},
        {"id": "nyc-2", "name": "Times Sq Tower", "price_per_night": 480},
    ],
    "LIS": [
        {"id": "lis-1", "name": "Alfama Stay", "price_per_night": 140},
        {"id": "lis-2", "name": "Chiado Suites", "price_per_night": 260},
    ],
}

@mcp.tool()
def search_hotels(city_code: str, max_price: int = 500) -> list[dict]:
    """Search hotels in a city. city_code is a 3-letter code (NYC, LIS, ...)."""
    rows = _FAKE_DB.get(city_code.upper(), [])
    return [r for r in rows if r["price_per_night"] <= max_price]

@mcp.tool()
def book_hotel(hotel_id: str, nights: int) -> dict:
    """Book a hotel by id for N nights. Returns confirmation + total_price."""
    for rows in _FAKE_DB.values():
        for r in rows:
            if r["id"] == hotel_id:
                return {
                    "confirmation_id": f"CONF-{hotel_id}-{nights}",
                    "hotel": r["name"],
                    "nights": nights,
                    "total_price": r["price_per_night"] * nights,
                }
    return {"error": "hotel not found"}

if __name__ == "__main__":
    import asyncio
    asyncio.run(mcp.run_async(transport="http", host="0.0.0.0", port=8090))
```

Run it: `python Work/M3/hotels_mcp/server.py`. Verify with `curl http://localhost:8090/mcp` (you should get the MCP handshake response, not a 404).

### Part 2 — The booking `Skill` (`planner/skills/booking/SKILL.md`)

```markdown
---
name: hotel-booking-flow
description: |
  Guides a hotel booking from intent through confirmation. Use when the user
  has stated a city, dates (or nights), and either a budget or a preference.
  Resolves city names to IATA-style codes, calls search_hotels, narrows to
  one candidate, calls book_hotel, then reports the confirmation.
---

# Hotel booking flow

When invoked, do exactly these steps:

1. Extract `city`, `nights`, and `max_price` (default 500) from context.
2. If the city is a name (e.g. "New York"), resolve to a 3-letter code
   ("NYC"). Common ones: NYC, LIS, SFO, LON, TYO.
3. Call `search_hotels(city_code, max_price)`.
4. If 0 results, ask the user to relax budget or change city. STOP.
5. If 1+ results, pick the cheapest unless the user said "premium".
6. Call `book_hotel(hotel_id, nights)`.
7. Return the `confirmation_id` and `total_price` in a one-sentence summary.

Refer to `resources/booking_policy.md` for cancellation and fee details
when the user asks about post-booking changes.
```

The `resources/booking_policy.md` file is a freeform Markdown doc with
2-3 paragraphs about cancellation windows, deposit handling, and a
support phone number. (Make it up; this is a drill in the wiring.)

### Part 3 — `planner/agent.py` (the agent tree + A2A wrapper)

```python
import os
from pathlib import Path

from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents import LlmAgent
from google.adk.skills import load_skill_from_dir
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
# NOTE: `MCPToolset` is deprecated in favor of `McpToolset` per `mcp_toolset.py:66,500`.
from google.adk.tools.skill_toolset import SkillToolset

from .callbacks import price_ceiling_guard

# Load the booking skill from the filesystem.
booking_skill = load_skill_from_dir(
    Path(__file__).parent / "skills" / "booking"
)

# Sub-agent #1: itinerary planning (pure LLM, no tools).
itinerary_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="itinerary_agent",
    description="Drafts a day-by-day itinerary given a city and N days.",
    instruction=(
        "You produce concise day-by-day travel itineraries. Output a "
        "Markdown list, one bullet per day. Do NOT book anything."
    ),
)

# Sub-agent #2: booking (MCP + Skill + callback).
booking_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="booking_agent",
    description=(
        "Searches and books hotels via the hotels MCP server, guided by "
        "the hotel-booking-flow skill."
    ),
    instruction=(
        "You handle hotel bookings. Always call load_skill('hotel-booking-flow') "
        "first and follow the steps it gives you. Use the search_hotels and "
        "book_hotel tools from MCP."
    ),
    tools=[
        SkillToolset(skills=[booking_skill]),
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=os.getenv("HOTELS_MCP_URL", "http://localhost:8090/mcp"),
            )
        ),
    ],
    before_tool_callback=price_ceiling_guard,  # enforces $X cap on book_hotel
)

# Root agent: routes between itinerary and booking sub-agents.
root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="travel_planner",
    description=(
        "Federated travel planner. Plans itineraries and books hotels."
    ),
    instruction=(
        "You are a travel planner. For itinerary requests, transfer to "
        "itinerary_agent. For hotel search or booking, transfer to "
        "booking_agent. For mixed requests, do itinerary first then booking."
    ),
    sub_agents=[itinerary_agent, booking_agent],
)

# Expose as A2A.
a2a_app = to_a2a(root_agent, port=10002)
```

Run it: `uvicorn Work.M3.planner.agent:a2a_app --host localhost --port 10002`.

Verify the AgentCard: `curl http://localhost:10002/.well-known/agent-card.json | jq` (modern canonical path — `AGENT_CARD_WELL_KNOWN_PATH` from `a2a/utils/constants.py:3`). Legacy fallback is `/.well-known/agent.json` (`PREV_AGENT_CARD_WELL_KNOWN_PATH`). The card should mention `travel_planner` and reflect the sub-agent topology.

### Part 4 — `planner/callbacks.py` (the price-ceiling policy)

```python
from google.adk.tools.tool_context import ToolContext

PRICE_CEILING = 1500  # dollars total — stretch goal makes this configurable

async def price_ceiling_guard(tool, args, tool_context: ToolContext):
    """Block book_hotel calls whose implied total exceeds PRICE_CEILING."""
    if tool.name != "book_hotel":
        return None
    nights = args.get("nights", 0)
    # We don't know price here without re-querying — but we know the booking_agent
    # was just shown the search_hotels result. Grab the most recent search result
    # from session state if you persisted it; otherwise allow and rely on the
    # post-hoc check. For this drill, do the simpler thing: short-circuit on
    # an absurd `nights` value as a sanity gate.
    if nights > 14:
        return {
            "error": (
                f"Refusing to book {nights} nights — policy ceiling is 14. "
                "Ask the user to confirm a shorter stay."
            )
        }
    return None
```

(The full price-aware version is a stretch goal — it requires the booking sub-agent to write the chosen hotel's `price_per_night` into session state before calling `book_hotel`, then the callback reads it and multiplies by nights.)

### Part 5 — `client.py` (consumes via `RemoteA2aAgent`)

```python
import asyncio
from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

remote_planner = RemoteA2aAgent(
    name="travel_planner_remote",
    description="Remote travel planner over A2A.",
    agent_card="http://localhost:10002/.well-known/agent.json",
)

boss = LlmAgent(
    model="gemini-2.5-flash",
    name="boss",
    instruction="Delegate travel requests to the travel_planner_remote sub-agent.",
    sub_agents=[remote_planner],
)

async def main():
    runner = InMemoryRunner(agent=boss, app_name="m3_client")
    session = await runner.session_service.create_session(
        app_name="m3_client", user_id="u1"
    )
    prompt = (
        "Plan a 3-day Lisbon trip and book me a hotel under $200/night "
        "for 3 nights."
    )
    async for event in runner.run_async(
        user_id="u1",
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=prompt)]),
    ):
        if event.is_final_response():
            print("FINAL:", event.content.parts[0].text)

if __name__ == "__main__":
    asyncio.run(main())
```

Run it (after MCP + planner are up): `python Work/M3/client.py`.

## ✅ Verification rubric

Run order matters. Three terminals:

| # | Terminal | Command | Expected |
|---|---|---|---|
| 1 | T1 (MCP) | `python Work/M3/hotels_mcp/server.py` | "MCP server running on port 8090" or equivalent. |
| 2 | T2 (Planner) | `uvicorn Work.M3.planner.agent:a2a_app --host localhost --port 10002` | Uvicorn boots, listens on 10002. |
| 3 | T3 (curl) | `curl http://localhost:10002/.well-known/agent-card.json` | JSON `AgentCard` with `name: travel_planner`, version, skills array. |
| 4 | T3 (client) | `python Work/M3/client.py` | Final response mentions a Lisbon itinerary AND a hotel confirmation id (e.g. `CONF-lis-1-3`). |

| Check | Pass criterion |
|---|---|
| MCP server reachable | Curl on `http://localhost:8090/mcp` returns the MCP handshake, not a 404. |
| AgentCard is real | `/.well-known/agent-card.json` returns a non-empty card whose `name` is `travel_planner`. |
| End-to-end round-trip | `client.py` final response contains BOTH a 3-day itinerary AND a confirmation id starting with `CONF-lis-`. |
| Skill actually loaded | Planner log shows `load_skill('hotel-booking-flow')` was invoked (look for the skill_toolset trace). |
| MCP tool actually called | Planner log shows `book_hotel` was called with `nights=3`. |
| Callback fires when triggered | Re-run the client with the prompt mutated to `"book for 30 nights"`. The booking sub-agent's response includes the policy refusal language; `book_hotel` is NOT called with `nights=30`. |
| Two-process discipline | You can show the grader three running processes (MCP, Planner, Client run). One-terminal solutions fail. |

## 🌟 Stretch goals

1. **Real price-aware guard.** Make the booking agent write the chosen hotel's `price_per_night` to session state before calling `book_hotel`. Update `price_ceiling_guard` to read state, multiply by `nights`, and block if `> PRICE_CEILING`. Demonstrate a blocked $1700 booking.
2. **Logging callback on the parent.** Add `before_agent_callback` on `root_agent` that logs which sub-agent it routes to. Confirm in the planner log that itinerary requests go to `itinerary_agent` and booking requests go to `booking_agent`.
3. **Auth on the A2A endpoint.** Add a Starlette middleware that requires `Authorization: Bearer <token>`. Update `client.py` to send the header (RemoteA2aAgent accepts an `httpx.AsyncClient` you can pre-configure with headers).
4. **Multi-turn with `context_id`.** Have the client send TWO messages: first "plan a Lisbon trip", then (in the same session) "ok, book the first option for 3 nights". Confirm both turns share state via `RemoteA2aAgent`'s `context_id` plumbing.
5. **Second remote agent.** Stand up a separate `flights_planner` agent at port 10003. Add it as a second remote sub-agent on `boss`. Now `client.py` is orchestrating two remotes. Cross-link to [[a2UI]] for a visual view of multi-remote topologies.
6. **Stream the response.** Switch the client to streaming and surface partial deltas. Confirm streaming events propagate through A2A and the parent's event stream.

## 🤖 Tutor notes

Common pitfalls — call them out before they bite:

- **Forgot to start the MCP server first.** The planner boots fine because the `MCPToolset` connects lazily, but the first `search_hotels` call fails with a connection error. Symptom: client final response says "I couldn't reach the hotels system." Fix: always start MCP first, planner second.
- **Ran planner with `python agent.py` instead of `uvicorn`.** The module defines `a2a_app` but no `if __name__ == "__main__": uvicorn.run(...)` block. Symptom: script exits immediately with no error. Fix: use the uvicorn CLI exactly as written.
- **`agent_card="http://localhost:10002/"` instead of the full `.well-known/agent.json` path.** `RemoteA2aAgent` does not auto-discover. Symptom: client crashes at startup with "card not found". Fix: include `/.well-known/agent.json` in the URL.
- **MCP session not cleaned up.** Symptom: stale sessions accumulate, eventually port 8090 connections refuse. Fix: see [[08_MCP/04_LifecycleManagement]] — wrap the toolset's `__aexit__` properly when running long-lived planners.
- **Skill frontmatter mismatch.** `name` must be kebab-case ≤ 64 chars and `description` ≤ 1024 chars. If you write `Hotel Booking Flow` you get a validation error at `load_skill_from_dir`. Fix: `name: hotel-booking-flow`.
- **Callback returns the wrong shape.** `before_tool_callback` returning a string short-circuits the tool — but only if it returns a `dict` (the tool result schema). Returning a bare string usually triggers a downstream parsing error. Fix: return `{"error": "..."}`.
- **Client's `boss` parent agent over-summarizes.** Sometimes the parent strips the confirmation id. Fix: tighten the boss's instruction to "Always include any confirmation ids verbatim in your final response."
- **One terminal, then debugging hell.** Insist on three terminals OR a tmux split. If they fight you, run the drill in one terminal once just to demonstrate why it's miserable.

## ❓ Self-check questions

> ❓ **Before coding:**
> 1. Which protocol does the client speak to the planner — A2A or MCP? Which one does the booking sub-agent speak to the hotels server? (A2A in front, MCP in back.)
> 2. Why is the booking flow packaged as a Skill instead of just a string in the sub-agent's `instruction`? (Progressive disclosure: only the description goes to the model until the agent actually loads it.)
> 3. Where does the `price_ceiling_guard` callback fire — on the client side, the planner root, or the booking sub-agent? Why? (On the sub-agent — the boundary closest to the tool call we want to block.)

> ❓ **After the planner boots but before the client runs:**
> 1. Read the AgentCard. Which sub-agents are reflected in it? Are MCP tools surfaced as skills?
> 2. Hit `curl http://localhost:10002/.well-known/agent-card.json | jq '.skills'`. Did the booking sub-agent's MCP tools propagate up, or only the planner's own tools?

> ❓ **After the round-trip works:**
> 1. Trace one full request in your head: which process did the LLM token at each step originate in? Count the network hops (client → planner; planner → MCP; MCP → planner; planner → client).
> 2. If you swapped the planner to live on a remote VM (different IP), what changes in `client.py`? (Just the `agent_card` URL.)
> 3. If the hotels MCP server crashed mid-request, what would the client see? What would you change to make the failure mode less ugly? (`on_tool_error_callback` on `booking_agent`; cross-link [[07_Callbacks/05_ErrorCallbacks]].)
> 4. If you scaled the planner to 3 replicas behind a round-robin LB, what breaks? (In-memory session state; sticky sessions or a `DatabaseSessionService` needed — see [[10_A2A/07_InProduction]].)

## 🔗 Cross-links

- [[07_Callbacks/03_BeforeAfterTool]] — `before_tool_callback` short-circuit pattern.
- [[08_MCP/02_MCPToolset]] — `StreamableHTTPConnectionParams` shape.
- [[08_MCP/05_ServingViaFastMCP]] — `FastMCP` server pattern.
- [[09_Skills/03_SkillToolset]] — how `SkillToolset` exposes `list_skills`, `load_skill`, `load_skill_resource`.
- [[10_A2A/03_ServeWithToA2a]] — `to_a2a` wrapper details.
- [[10_A2A/04_ConsumeWithRemoteA2aAgent]] — `RemoteA2aAgent` usage as a sub-agent.
- [[10_A2A/05_A2A_vs_MCP]] — the "A2A in front, MCP in back" pattern this drill embodies.
- [[10_A2A/07_InProduction]] — sticky sessions, AgentCard versioning, auth.
- [[a2UI]] — visual composer for multi-remote A2A flows (stretch goal 5).
- [[FastMCP]] — server framework reference.

---

[← Prev: 10_A2A/09_MiniDrill](../Notes/10_A2A/09_MiniDrill.yml)  [↑ Map](../MAP.md)  [Next: 11_Memory/00_Overview →](../Notes/11_Memory/00_Overview.md)
