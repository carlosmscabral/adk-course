---
module: 21_AdkApiSurface
page: 01C_FullCliFamily
title: The full adk CLI family
estimated_minutes: 20
prereqs: [21_AdkApiSurface/01B]
concepts: [adk create, adk eval, adk deploy, adk api_server, click subcommands]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 01B_AdkWebUnderTheHood](01B_AdkWebUnderTheHood.md)  [↑ Map](../../MAP.md)  [Next: 02_AdkApiServer →](02_AdkApiServer.md)

You are here: 🗺 Deployment & Integration Track ▸ 21 ADK API Surface ▸ 01C Full CLI family

---

## 🛠 The full map

`adk --help` shows the click subcommand tree. Everything is one of:

```
adk
├── run            ← page 01, 01A
├── web            ← page 01B
├── api_server     ← page 02
├── eval           ← module 14 Evaluation
├── create         ← scaffolds a new agent package
├── test           ← pytest runner for agent test JSON files
├── optimize       ← GEPA prompt optimizer (module 14)
├── conformance    ← record + test, less common; cross-link 14
├── eval_set
│   ├── create               ← creates an empty EvalSet
│   ├── add_eval_case        ← appends cases from a scenarios file
│   └── generate_eval_cases  ← synthesises cases automatically
├── migrate
│   └── session    ← upgrades a session DB schema (sqlite/postgres URLs)
└── deploy
    ├── cloud_run        ← module 22 page 02
    ├── agent_engine     ← module 22 page 03
    └── gke              ← module 22 page 03A
```

All defined in `src/google/adk/cli/cli_tools_click.py`. Each is a click `@main.command(...)`.

## 🛠 `adk create <app_name>`

Scaffolds a package skeleton — agent.py + `__init__.py` + an `.env.example` + a `pyproject.toml`. Useful as a starting template; pass `--model gemini-2.5-flash` to pre-fill the model in agent.py.

```bash
adk create my_agent --model gemini-2.5-flash
```

Output:

```
my_agent/
├── __init__.py
├── agent.py            # bare LlmAgent with name + model + instruction
├── .env.example        # GOOGLE_API_KEY / GOOGLE_GENAI_USE_VERTEXAI placeholders
└── README.md
```

After this you can immediately `adk run my_agent`.

## 🛠 `adk eval <agents_dir> <eval_set.json>`

Replays an `EvalSet` against the agent and prints pass/fail. Full coverage in **14 Evaluation** — here we just note that the eval CLI shares the same `AgentLoader` + `_setup_runner_context` as `adk run`. That is why the same `--session_service_uri` flags apply.

```bash
adk eval my_agent eval/regression.evalset.json
```

## 🛠 `adk conformance record` / `adk conformance test`

A specialised eval flavour: **record** captures real LLM + tool I/O into a fixture file, **test** replays the fixture without re-calling the LLM. Use for: deterministic CI, regression tests, contract tests against MCP servers. Not the same as the trajectory evaluator in 14 — this records the *raw* interaction.

## 🛠 `adk test <folder>`

Runs pytest under the hood on agent test JSON files in the folder (default `.`). Pass `--rebuild` to regenerate the test fixtures by running the live agent against the seed user messages. Anything after `--` is forwarded to pytest verbatim:

```bash
adk test Work/21_AdkApiSurface -- -k research_assistant
```

## 🛠 `adk optimize <agent_path> --sampler_config_file_path ...`

Runs the **GEPA** root-agent prompt optimizer. Reads a `LocalEvalSamplerConfig` JSON (eval set + metrics), iterates on the agent's `instruction`, and prints the best-scoring version. `--optimizer_config_file_path` is optional. Full coverage in module 14.

## 🛠 `adk eval_set` (subgroup)

Curate evaluation sets without writing JSON by hand:

```bash
adk eval_set create ./research_assistant my_regression
adk eval_set add_eval_case ./research_assistant my_regression \
    --scenarios_file scenarios.json --session_input_file session.json
adk eval_set generate_eval_cases ./research_assistant my_regression \
    --num_cases 20
```

`create` makes an empty set; `add_eval_case` hashes each scenario into a stable `eval_id`; `generate_eval_cases` uses an LLM to synthesise cases for you.

## 🛠 `adk migrate session --source_db_url ... --dest_db_url ...`

Upgrades a `DatabaseSessionService` schema from an older ADK version to the current one. Both flags are required SQLAlchemy URLs (e.g. `sqlite:///old.db` → `sqlite:///new.db`). Use during ADK upgrades that change the session table layout. Cross-link: **04 SessionsState** for what's in those tables.

## 🛠 `adk deploy cloud_run`

Builds a Docker image for your agent and pushes it to Cloud Run.

```bash
adk deploy cloud_run \
    --project=my-gcp-project \
    --region=us-central1 \
    --service_name=research-assistant \
    --app_name=research_assistant \
    --with_ui  \
    --session_service_uri=sqlite:///./sessions.db \
    ./research_assistant
```

Key flags:

| Flag                       | What it does                                                      |
|----------------------------|-------------------------------------------------------------------|
| `--service_name`           | Cloud Run service name (DNS-safe).                                |
| `--with_ui`                | Also serve the Angular dev UI (you usually don't want this in prod). |
| `--session_service_uri`    | Persisted session backend; required if you want sessions across container restarts. |
| `--artifact_service_uri`   | Persisted artifact backend.                                       |
| `--port`                   | Container port (Cloud Run injects `PORT` env var anyway).         |
| `--no_allow_origins_*`     | Lock CORS down. Default `*` for dev.                              |

Full coverage in **22 Deployment Models page 02**.

## 🛠 `adk deploy agent_engine`

Uploads to **Vertex AI Agent Engine** — the managed runtime where sessions, scaling, and observability are platform-provided. Different mental model: you ship an `AdkApp` (a Pydantic-typed Vertex resource), not a container.

```bash
adk deploy agent_engine \
    --project=my-gcp-project \
    --region=us-central1 \
    --staging_bucket=gs://my-staging \
    --display_name="research-assistant" \
    ./research_assistant
```

Full coverage in **22 Deployment Models page 03**.

## 🛠 `adk deploy gke`

Builds the same Docker image as `cloud_run` then renders Kubernetes manifests (Deployment + Service + optional HPA) and applies them. Use when you already run GKE and want pod-level control (sidecars, network policies, Workload Identity). Full coverage in **22 Deployment Models page 03A**.

## 🛠 The shared flags

Every command that touches a runner accepts `--session_service_uri`, `--artifact_service_uri`, and `--memory_service_uri` (plus `--use_local_storage / --no_use_local_storage` to gate the `.adk` fallback). They flow into `_setup_runner_context` (page 01A). This consistency is the entire reason the CLI feels coherent — there is *one* runner config code path.

## 🚀 In Production

> **🚀 In Production**
>
> The three deploy subcommands are **convenience wrappers**, not the only way. You can always write your own Dockerfile, your own Kubernetes manifests, or your own Agent Engine upload script. The CLI saves a half-day of YAML; it does not lock you in. For non-trivial prod (custom sidecars, weird CI, multi-region) most teams graduate off `adk deploy` and own their build/release pipeline. Module 22 shows both paths.

> ❓ **Ask the student:** "If you have a CI that already builds your container, which `adk deploy` flag matters?" *(None — bypass `adk deploy` entirely and call `gcloud run deploy` on your image. The agent boots the same either way.)*

---

[← Prev: 01B_AdkWebUnderTheHood](01B_AdkWebUnderTheHood.md)  [↑ Map](../../MAP.md)  [Next: 02_AdkApiServer →](02_AdkApiServer.md)
