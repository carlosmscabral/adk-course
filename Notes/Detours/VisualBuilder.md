---
module: Detours
page: VisualBuilder
title: ADK Visual Builder — drag-and-drop AgentConfig authoring
estimated_minutes: 20
icon: 🗺
prereqs: [2A_AgentConfig]
concepts: [visual_builder, agent_config, yaml_agents, sub_agents_wiring]
---

[← Back to Map](../../MAP.md)

Triggered from: `2A_AgentConfig` (when the YAML starts feeling tedious to hand-write), `05_MultiAgent` (sketching a hierarchy for a stakeholder), `99_Capstone` (communicating designs visually).

> Take this detour if you'd rather *draw* an agent tree than type YAML — or if you need to hand a diagram to a stakeholder. The Visual Builder writes **AgentConfig YAML** (`root_agent.yaml`) — exactly the format you already learned in `[[2A_AgentConfig]]`. ~20 min. (You can skim this if you only ever author by hand.)

---

## 🗺 1. What it is

ADK ships a browser-based **Visual Builder** for composing agents visually. You drag boxes for `LlmAgent`, `SequentialAgent`, `ParallelAgent`, `LoopAgent`, fill in properties on the right panel, and the canvas writes a `root_agent.yaml` (plus a `sub_agent_*.yaml` per child) into your agents directory.

```
   ┌──────────────────────┐         ┌──────────────────────┐
   │   Visual Builder     │  save   │  root_agent.yaml     │
   │   (browser canvas)   ├────────►│  sub_agent_*.yaml    │
   │                      │         │  (AgentConfig YAML)  │
   │                      │◄────────┤                      │
   └──────────────────────┘  load   └──────────────────────┘
```

The Builder reads and writes **only YAML** — verified in `fast_api.py:109`: `_ALLOWED_EXTENSIONS = frozenset({".yaml", ".yml"})`. A YAML agent is detected by the presence of `root_agent.yaml` in the app folder (`api_server.py:658-661`: "All YAML agents are treated as visual builder agents"). Custom tool implementations stay as Python (`FunctionTool` bodies under your `tools/` dir) and are referenced from the YAML by import path.

❓ *So what's the relationship to the graph-workflow engine (`Workflow`) from Module 06?* No relationship — the Builder targets `LlmAgent` + the three orchestrator agents (`SequentialAgent`/`ParallelAgent`/`LoopAgent`). The graph-workflow `Workflow` has **no visual equivalent**; if you need fine-grained edges, you write it by hand.

---

## 🗺 2. When it's worth opening

| situation                                          | visual builder? |
|----------------------------------------------------|-----------------|
| Sketching an agent hierarchy with 3-10 nodes       | ✅ great        |
| Showing a non-engineer how the agents nest         | ✅ great        |
| You already know AgentConfig YAML and want speed   | ✅ great        |
| Many small agents of the same shape (codegen)      | ❌ loop in Python |
| Graph workflows with conditional edges             | ❌ `Workflow` only, no UI |
| Diff-friendly history in PRs                       | 🟡 YAML diffs OK, but hand-written is tidier |

Rule of thumb: **moderate hierarchy depth** is the sweet spot. Trivial → just hand-write the YAML. Dynamic graphs → `Workflow` in code, no visual path.

---

## 🗺 3. How to open it

Per `https://adk.dev/visual-builder/` (snapshot 2026-05-27):

```bash
$ adk web /path/to/agents_dir   # the dev UI we covered in [[a2UI]]
# In the UI, click the "+" icon in the top-left corner to start a new agent.
```

There is **no `adk web --builder` flag**. The Visual Builder ships as part of the standard dev UI — verified against `cli_tools_click.py:1731-1773` (no `--builder` click option on `adk web`; only `--logo-text`, `--logo-image-url`, and the common host/port/log options). `agents_dir` is a positional argument (`@click.argument("agents_dir")`), defaulting to the cwd.

The builder shares the dev-server process — same caveats apply (localhost only, no auth, dev-only). Builder endpoints are registered conditionally on `web=True` (`fast_api.py:74-85`) and require `python-multipart` to be installed.

⚠️ If `python-multipart` is missing, the dev server logs `"Builder UI endpoints will not be available."` and the UI silently degrades. Install it with `pip install python-multipart` if the **+** icon does nothing.

---

## 🗺 4. The round-trip

The Builder's persistence is **the YAML file itself**:

```
1. Drag boxes in the UI               → save → writes root_agent.yaml
2. Open root_agent.yaml in your editor → tweak an instruction
3. Re-open the Builder                → it re-parses the YAML
4. Your edit shows up on the canvas
5. Drag a new sub_agent               → save → root_agent.yaml updates
```

This works because the YAML *is* the source of truth — there's no `.builder.json` sidecar, no parallel state. The default save path is `root_agent.yaml` (`fast_api.py:352`), and uploads/saves reject anything that isn't `.yaml`/`.yml`. So `git diff` is meaningful, code review works, and the same file is exactly what `agent_loader` loads when the dev server runs your agent.

⚠️ One catch: **the parser only round-trips schema-conformant YAML.** If you hand-edit and add something outside `AgentConfig.json` (an unrecognized key, an `args:` block — `args` is explicitly blocked at upload, see `fast_api.py:111`), the Builder won't render that node correctly. Stick to the schema when hand-editing.

---

## 🗺 5. What it generates (the format you already know)

Even if you never open the Builder, knowing what it spits out helps — and you've already seen it in `[[2A_AgentConfig/02_RootAgentYaml]]`:

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
agent_class: LlmAgent
name: research_root
model: gemini-2.5-flash
instruction: "Coordinate research between specialists..."
sub_agents:
  - config_path: ./researcher.yaml
  - config_path: ./critic.yaml
```

A drawing of a root box with two child boxes produces exactly this — plus a `researcher.yaml` and a `critic.yaml` next to it. Sub-agents can either reference another YAML file (`config_path:`) or a Python object (`code: my_pkg.my_agent.agent`); the multi-agent sample at `contributing/samples/multi_agent/sub_agents_config/root_agent.yaml` shows both forms.

> **🚀 In Production**
>
> Don't let the Builder be the *only* place an agent lives. Commit the generated `.yaml` to git; review it like any other config. Treat the UI as a *productivity tool*, not a data store. If you'd be unhappy losing the canvas, you're using it wrong — but since the canvas just *is* the YAML, you can't really lose anything as long as the file is in git.

---

## 🛠 Have the student try

Sketch a 3-agent hierarchy on paper (or text), then write it as AgentConfig YAML from scratch — no UI required.

**The shape**: a `root` `LlmAgent` that delegates to two specialists — a `researcher` `LlmAgent` for factual lookups and a `summarizer` `LlmAgent` for compressing answers.

```
       root  (LlmAgent, decides who handles)
        │
   ┌────┴────┐
   ▼         ▼
researcher  summarizer
(LlmAgent)  (LlmAgent)
```

Have the student write `root_agent.yaml` with two `sub_agents:` entries using `config_path:`, plus `researcher.yaml` and `summarizer.yaml` next to it. Then, if the Builder is available, **open `adk web`** on that directory and confirm the canvas matches the drawing.

If the Builder isn't accessible, the exercise still works — the point is that "drawing" and "AgentConfig YAML" are isomorphic. Both produce the same agent tree the runtime loads.

---

[← Back to Map](../../MAP.md)

Back to: whichever page triggered this — likely `2A_AgentConfig/02_RootAgentYaml` or `05_MultiAgent/03_HierarchyDesign`.
