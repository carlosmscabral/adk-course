---
module: Detours
page: a2UI
title: adk web — the ADK dev UI
estimated_minutes: 15
icon: 🗺
prereqs: []
concepts: [adk_web, dev_ui, event_timeline, session_inspector]
---

[← Back to Map](../../MAP.md)

Triggered from: `02_FirstAgent` (first time you want to *see* a run, not just print events), `04_SessionsState` (visualizing state mutations).

> Take this detour the first time event-stream prints feel like reading the matrix. `adk web` gives you a chat window, an event timeline, and a session/state inspector. Dev-only — but you'll use it constantly. ~15 min.

---

## 🗺 1. What it gives you

```
   ┌────────────────────────────────────────────────────┐
   │  chat panel       │  event timeline                │
   │  user: hi         │  ▶ user_message                │
   │  agent: hello     │  ▶ model_thought               │
   │  user: weather?   │  ▶ function_call get_weather   │
   │  agent: 22°C…     │  ▶ function_response           │
   │                   │  ▶ model_final                 │
   ├────────────────────────────────────────────────────┤
   │  session inspector: state, artifacts, sub-agents   │
   └────────────────────────────────────────────────────┘
```

Three things you couldn't get from `print(event)` in a script:

1. **Per-event drill-down** — click an event, see the full `content.parts`, `actions.state_delta`, raw tool args.
2. **State viewer** — current session state with `user:` / `app:` / `temp:` scopes color-coded. Changes flash.
3. **Sub-agent visibility** — for multi-agent or graph runs, the timeline groups events by author.

---

## 🗺 2. The 30-second quick-start

`adk web` discovers agents by walking the current directory for files that define `root_agent`:

```bash
$ cd ~/study/adk-samples/python/agents/fun-facts
$ adk web
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Open the URL, pick the agent from the dropdown, type a message. That's it.

Common flags:

```bash
adk web --port 8001                # different port
adk web --host 0.0.0.0             # accept LAN connections (NOT for prod)
adk web --reload                   # watch for code changes, reload agent
adk web --session-service sqlite:///dev.db   # persist sessions across restarts
```

---

## 🗺 3. The workflow tip — iterate prompts here

This is what makes `adk web` worth the disk space:

```
1. Edit agent instruction in code           ↑
2. --reload picks it up                     │
3. Re-send the same user message            │  tight loop, ~10s
4. Click the model_thought event            │  inspect why it
5. Adjust instruction                       │  picked that tool /
6. Repeat                                   ↓  emitted that text
```

Scripted runners are better for *regression* (does the change still pass my evals?). `adk web` is better for *exploration* (why did the model do that?).

---

## 🗺 4. State inspection in `04_SessionsState`

When you start writing `state_delta`s, `adk web` becomes invaluable:

```python
@FunctionTool
def remember(key: str, value: str, tool_context: ToolContext) -> str:
    tool_context.state[f"user:{key}"] = value
    return f"saved {key}"
```

In `adk web` you'll watch `user:<key>` appear in the state panel in real-time. The scope prefix is color-coded — `user:` (purple), `app:` (blue), `temp:` (gray), no-prefix (white). One glance tells you "did my callback write to the right scope?".

---

## 🗺 5. What it's NOT

⚠️ **Not production observability.** `adk web` is in-process, single-user, no tracing export, no metrics. For real ops, you want OpenTelemetry → Cloud Trace + Cloud Monitoring. See [[OpenTelemetry]] and module `15_Observability`.

⚠️ **Not an authoring tool.** It surfaces what your code already does. Compare with [[VisualBuilder]] which actually *generates* code.

⚠️ **Not safe to expose.** No auth, prints request payloads to logs, hot-reloads code from disk. Localhost only.

⚠️ **Session service defaults to in-memory.** Restart `adk web` and you lose every conversation. Pass `--session-service sqlite:///dev.db` if you want persistence across reloads.

> **🚀 In Production**
>
> Treat `adk web` as you would `flask run` — fine for `127.0.0.1` during dev, never the front door for users. Production traffic goes through `to_a2a(root_agent)` (A2A server) or `adk deploy` (Cloud Run / Agent Engine), both of which have auth and observability.

---

## 🛠 Have the student try

Run `adk web` against a real sample and inspect a multi-turn event timeline:

```bash
$ cd ~/study/adk-samples/python/agents/fun-facts
$ adk web
# open http://127.0.0.1:8000
# select fun-facts agent
# send: "tell me a fun fact about octopuses"
# send: "another one"
```

Then in the UI:

1. Click the **event timeline** for turn 2. How many events fired between the user message and the final model response?
2. Click the `function_call` event (if there is one) — what arguments did the model pick?
3. Click the **session inspector** — is there any state? (Fun-facts is mostly stateless, so probably not — but the panel is the answer.)
4. Click any model event — find `content.parts[0].text`. That's the raw model output before any post-processing.

The goal is muscle memory: when something looks weird in a scripted run, your first move should be "let me reproduce it in `adk web` and click around."

---

[← Back to Map](../../MAP.md)

Back to: whichever page triggered this — likely `02_FirstAgent/05_DissectingSample` or `04_SessionsState/03_InspectingState`.
