---
module: 3A_ProjectStructure
page: 06_DeploymentExpectations
title: What deployment expects — Cloud Run, Agent Engine, pyproject
estimated_minutes: 22
prereqs: [3A_ProjectStructure/05]
concepts: [pyproject-toml, cloud-run-dockerfile, agent-engine-packing, fastapi-wrapper]
icon: ☁️
in_production: true
detours_suggested: []
---

[← Prev: 05_AdkCliExpectations](05_AdkCliExpectations.md)  [↑ Map](../../MAP.md)  [Next: 07_SharedUtilities →](07_SharedUtilities.md)

You are here: 🗺 Foundation Track ▸ 3A Project Structure ▸ 06 What deployment expects

# ☁️ What deployment expects on disk

> 🤖 **Tutor:** the student should not deploy yet. This page teaches **what shape to put the project in *now*** so that when they reach [Module 22](../22_DeploymentModels/) the deploy is a one-liner instead of a refactor.

Two deployment paths exist (full treatment in [22_DeploymentModels](../22_DeploymentModels/)):

1. **Cloud Run** — you give Google a container; it gives you HTTPS.
2. **Agent Engine** (Vertex AI Runtime) — you give Google a Python package; it runs it.

Each wants the project in a slightly different shape. The good news: the shapes overlap, and both are reachable from the growing layout (page 04) with no restructure.

## What both paths require

### `pyproject.toml` — at the project root, one level above the agent package

```
my_project/                     ← deploy from here
├── pyproject.toml
├── my_agent/                   ← the package (or agents/my_agent/)
│   ├── __init__.py
│   └── agent.py
├── uv.lock                     ← pinned
└── README.md
```

```toml
[project]
name = "my-agent"
version = "0.1.0"
description = "What this agent does."
requires-python = ">=3.11"
dependencies = [
    "google-adk>=1.31.0",
    "google-auth>=2.30.0",
    "python-dotenv>=1.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["my_agent"]            # ← THIS LINE is what makes the package shippable
```

The `[tool.hatch.build.targets.wheel] packages = ["my_agent"]` line is the one beginners miss. Without it, building a wheel succeeds but ships an empty package — Agent Engine deploys the wheel, finds no `root_agent`, and silently fails.

> ⚠️ Always pin a lower bound on `google-adk` (`>=1.31.0`). Don't pin an upper bound unless you've got a specific reason — minor versions are backward-compatible. We revisit version pinning in [10_InProduction](10_InProduction.md).

## Cloud Run shape

Cloud Run runs your agent as **a container behind HTTP**. You write a tiny FastAPI app that wraps the agent:

```python
# main.py — at the project root, next to pyproject.toml
import os

import uvicorn
from dotenv import load_dotenv
from google.adk.cli.fast_api import get_fast_api_app

load_dotenv()

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_URI = os.getenv("SESSION_SERVICE_URI")

app = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=os.getenv("SERVE_WEB_INTERFACE", "false").lower() == "true",
    session_service_uri=SESSION_URI,
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
```

This is the `data-science` sample's `main.py`, distilled. Note:

- `AGENT_DIR` is **the parent of the agent package**, exactly like `adk web`'s CWD rule.
- `SESSION_SERVICE_URI` defaults to in-memory (lost on restart); for prod, point at a managed session store.
- `PORT` comes from the Cloud Run environment.

### Dockerfile — minimal, generic

```dockerfile
# Dockerfile — at the project root
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip uv>=0.7.19

# Copy lockfile first for layer caching, then sync, then copy code
COPY uv.lock pyproject.toml ./
RUN uv sync --frozen

COPY . .

EXPOSE 8080
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

That's `data-science`'s Dockerfile — generic enough to work for any ADK agent that follows the layout above.

## Agent Engine shape

Agent Engine is **not a container**. It's a managed runtime — you ship a Python package and Google runs it. Shape:

```
my_project/
├── pyproject.toml
├── my_agent/                ← packaged, shipped wholesale
│   ├── __init__.py
│   └── agent.py
└── deployment/
    └── deploy.py            ← one-shot CLI that calls agent_engines.create()
```

`deployment/deploy.py` packs the agent and pushes it:

```python
# deployment/deploy.py
import vertexai
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp
from my_agent.agent import root_agent

vertexai.init(project="my-gcp-project", location="us-central1",
              staging_bucket="gs://my-staging-bucket")

adk_app = AdkApp(agent=root_agent, enable_tracing=True)

remote_agent = agent_engines.create(
    adk_app,
    display_name=root_agent.name,
    requirements=[
        "google-adk>=1.31.0",
        "google-cloud-aiplatform[agent_engines]>=1.88.0",
    ],
    extra_packages=["./my_agent"],     # ← the line that ships your code
)
print(f"Deployed: {remote_agent.resource_name}")
```

Two things that are easy to miss:

1. **`extra_packages=["./my_agent"]`** — the path to your agent **package directory**, not the project root, not the `agent.py` file. Get this wrong and Agent Engine ships an empty package.
2. **`requirements=[...]`** is independent of `pyproject.toml`. You list runtime deps inline. Why? Because Agent Engine's environment is different from your dev environment — you may want stricter pins for the deployed version.

`llm-auditor`'s `deployment/deploy.py` is the production-ready version of this script (with `absl` flags for create/delete/list). Read it as the canonical reference.

## The shape that works for both

```
my_project/
├── pyproject.toml            # both paths
├── uv.lock                   # both paths
├── README.md
├── main.py                   # Cloud Run entrypoint
├── Dockerfile                # Cloud Run only
├── my_agent/                 # the package — both paths
│   ├── __init__.py
│   ├── agent.py
│   ├── prompts/
│   ├── tools/
│   └── sub_agents/
├── deployment/               # Agent Engine only
│   └── deploy.py
├── eval/                     # see page 08
└── tests/                    # see page 08
```

This shape is what every "real" sample in `adk-samples/python/agents/` converges to. The student can start with the minimal layout, escalate to small, then growing, and **never have to rearrange anything** — they just add `main.py`, `Dockerfile`, `deployment/deploy.py` when deploy day comes.

> 🛠 **Have the student** open `adk-samples/python/agents/data-science/` and `adk-samples/python/agents/llm-auditor/`. The first ships via Cloud Run (`main.py` + `Dockerfile`); the second ships via Agent Engine (`deployment/deploy.py`). Both have the same internal agent package shape.

> **🚀 In Production**
>
> Don't commit `.env` files. Don't commit `uv.lock` if your `pyproject.toml` allows it but **do** commit it for reproducible deploys (almost always). Pin Python version with `requires-python = ">=3.11"`. The most painful production bug from layout is "works locally, breaks in container because Python version drifted." Hard-pin at deploy time.

> ❓ **Ask the student:** "Why does Cloud Run need a `main.py` but Agent Engine doesn't?"
>
> *(Expected: Cloud Run wants an HTTP-serving process; you give it FastAPI. Agent Engine wraps the `root_agent` itself with its own HTTP layer — you just hand over the package.)*

---

[← Prev: 05_AdkCliExpectations](05_AdkCliExpectations.md)  [↑ Map](../../MAP.md)  [Next: 07_SharedUtilities →](07_SharedUtilities.md)
