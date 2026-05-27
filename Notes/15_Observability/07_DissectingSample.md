---
module: 15_Observability
page: 07_DissectingSample
title: Dissecting agent-observability-bq end-to-end
estimated_minutes: 30
prereqs: [15_Observability/06]
concepts: [sample read, BigQueryAgentAnalyticsPlugin wiring, dataset provisioning]
icon: 🔬
in_production: true
detours_suggested: []
---

[← Prev: 15_Observability/06_BigQueryAsSink](06_BigQueryAsSink.md)  [↑ Map](../../MAP.md)  [Next: 15_Observability/08_InProduction →](08_InProduction.md)

You are here: 🗺 Production Track ▸ 15 Observability ▸ 07 Dissecting Sample

---

## 🔬 What we're reading

`/home/carloscabral/study/adk-samples/python/agents/agent-observability-bq/`

```
agent_observability_bq/
├── __init__.py
├── agent.py
└── shared_libraries/
    ├── grant_permissions.sh
    └── prepare_dataset.py
README.md
Makefile
.env.example
pyproject.toml
```

A single-file agent that *both* uses BigQuery (via `BigQueryToolset`) and *logs to* BigQuery (via `BigQueryAgentAnalyticsPlugin`). Read it as the canonical "wire observability into a real agent" pattern.

## 🔬 Reading order

### 1. `agent.py` — top to bottom

Open `/home/carloscabral/study/adk-samples/python/agents/agent-observability-bq/agent_observability_bq/agent.py`.

**Lines 1-29 — setup.** `load_dotenv()`, `os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")`. Vertex is the default so the same code works on Cloud Run where `.env` isn't shipped.

**Lines 36-52 — config resolution.** ADC for `PROJECT_ID`, env for `DATASET_ID`, `TABLE_ID`, `LOCATION`. Sensible defaults (`adk_agent_analytics`, `agent_events`, `us-east1`). This is the production pattern: **never hard-code** project/dataset.

**Lines 55-62 — the plugin.**

```python
bq_logging_plugin = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID,
    dataset_id=DATASET_ID,
    table_id=TABLE_ID,
    location=LOCATION,
)
```

One object, four args, full observability sink. That is the entire investment.

**Lines 65-89 — agent definition.** `BigQueryToolset()` gives the agent SQL tools. The model is `gemini-2.5-flash`. The instruction is plain — no observability concerns leak into the prompt.

**Lines 92-96 — App wiring.**

```python
app = App(
    name="agent_observability_bq",
    root_agent=root_agent,
    plugins=plugins,  # contains bq_logging_plugin
)
```

Plugins live on the `App`, not the agent. That is what makes the observability *cross-cutting* — every sub_agent under `root_agent` is automatically logged.

### 2. `shared_libraries/prepare_dataset.py`

Open `/home/carloscabral/study/adk-samples/python/agents/agent-observability-bq/agent_observability_bq/shared_libraries/prepare_dataset.py`.

The plugin auto-provisions the *table*, not the *dataset*. This script creates the dataset (idempotent; refuses to clobber a dataset in the wrong location). Pattern to remember: **provision storage out-of-band; let the plugin manage schema**.

### 3. `README.md`

Open the README. Skim the *Try it out* section — the example queries are exactly the kind of analytics we built in page 06. Notice that the README does **not** talk about traces — this sample is logs-and-analytics first. For traces you would layer in the OTel exporters from page 03 on top.

## 🛠 Question-driven dissection

Have the student answer (peeking at the file is fair):

1. **What gets logged?** (Every event under `App`'s plugins — agent enter/exit, model call, tool call, tool result.)
2. **What is the schema?** (Generic event-row shape; per-event fields nested in `payload`.)
3. **What is the query pattern for "find slowest tool"?** (`GROUP BY tool_name`, `APPROX_QUANTILES(latency_ms, 100)[OFFSET(95)]`.)
4. **What happens if BigQuery is down?** (Plugin should buffer / fail open. See page 08 for the OTel-collector analog.)

> 🤖 **Tutor:** when the student finishes, ask them to *delete* the plugin from `app = App(...)` and re-run. The agent still works — observability is non-functional, which is the whole point of putting it in a plugin instead of the agent body.

---

[← Prev: 15_Observability/06_BigQueryAsSink](06_BigQueryAsSink.md)  [↑ Map](../../MAP.md)  [Next: 15_Observability/08_InProduction →](08_InProduction.md)
