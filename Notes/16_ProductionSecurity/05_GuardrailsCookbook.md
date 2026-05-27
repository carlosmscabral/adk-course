---
module: 16_ProductionSecurity
page: 05_GuardrailsCookbook
title: Guardrails cookbook — seven recipes you copy-paste
estimated_minutes: 35
prereqs: [16_ProductionSecurity/04, 07_Callbacks/06, 13_Plugins/06]
concepts: [callbacks, plugins, PII redaction, toxicity filter, rate limiting, cost cap, sandbox policy]
icon: 🍳
in_production: true
detours_suggested: []
---

[← Prev: 16_ProductionSecurity/04_SecretsHandling](04_SecretsHandling.md)  [↑ Map](../../MAP.md)  [Next: 16_ProductionSecurity/06_AgentIdentityVsUser →](06_AgentIdentityVsUser.md)

You are here: 🗺 Production Track ▸ 16 Production & Security ▸ 05 Cookbook

---

## 🍳 How to use this page

Each recipe is 5-15 lines, callback or plugin, drop-in. They are intentionally small — combine three or four to cover most of your threat model. Every recipe cross-links to the module's `06_InProduction.md` page where the underlying gotcha was first introduced.

---

### Recipe 1 — Input PII redaction (regex)

Origin: [[03_Tools/11_InProduction]] (tool args), [[15_Observability/08_InProduction]] § 2.

```python
import re
PATTERNS = {
    "<email>": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "<ssn>":   re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "<phone>": re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
}
def redact(text: str) -> str:
    for repl, pat in PATTERNS.items():
        text = pat.sub(repl, text)
    return text

def before_model_callback(callback_context, llm_request):
    for c in llm_request.contents:
        for p in c.parts:
            if p.text:
                p.text = redact(p.text)
```

Cheap, deterministic, no LLM call. Regex misses *meaning*-level PII (names of celebrities) but catches the structured PII that costs you.

---

### Recipe 2 — Output toxicity filter (LLM-as-judge)

Origin: [[02_FirstAgent/06_InProduction]], inspired by `safety-plugins/`.

```python
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner

JUDGE = LlmAgent(
    model="gemini-2.5-flash-lite",
    name="toxicity_judge",
    instruction="Reply only SAFE or UNSAFE. UNSAFE = hateful, harassing, sexually explicit, or self-harm content.",
)
_judge_runner = InMemoryRunner(agent=JUDGE, app_name="judge")

async def after_model_callback(callback_context, llm_response):
    text = "".join(p.text or "" for p in llm_response.content.parts).strip()
    if not text: return None
    # ... run JUDGE on text; if "UNSAFE", replace content with canned message
```

See `safety-plugins/safety_plugins/plugins/agent_as_a_judge.py` for the full implementation including session-poisoning protection.

---

### Recipe 3 — Tool arg whitelist (block destructive patterns)

Origin: [[12_CodeExecution/08_InProduction]], [[08_MCP/07_InProduction]].

```python
import re
DANGEROUS = re.compile(r"\b(rm\s+-rf|DROP\s+TABLE|sudo|chmod\s+777)\b", re.I)

def before_tool_callback(tool, args, tool_context):
    blob = " ".join(str(v) for v in args.values())
    if DANGEROUS.search(blob):
        return {"error": "Tool args matched a forbidden pattern."}
    return None
```

Pair with structured tool schemas — a tool that takes `(table_name: str, column: str)` is harder to misuse than a tool that takes `(sql: str)`.

---

### Recipe 4 — Rate limit per user (state counter)

Origin: [[04_SessionsState/12_InProduction]], `customer-service` sample.

```python
import time
WINDOW_SEC = 60
LIMIT = 10

def before_model_callback(callback_context, llm_request):
    s = callback_context.state
    now = time.time()
    if s.get("user:rl_start", 0) + WINDOW_SEC < now:
        s["user:rl_start"] = now
        s["user:rl_count"] = 0
    s["user:rl_count"] = s.get("user:rl_count", 0) + 1
    if s["user:rl_count"] > LIMIT:
        raise RuntimeError(f"Rate limit exceeded: {LIMIT}/{WINDOW_SEC}s")
```

Note the `user:` prefix — the counter follows the user across sessions. (See `customer_service/shared_libraries/callbacks.py` lines 39-86 for the time.sleep variant.)

---

### Recipe 5 — Cost cap per session (token accumulator)

Origin: [[15_Observability/08_InProduction]] § 6.

```python
COST_CAP_USD = 1.00
# illustrative prices per 1M tokens
PRICE = {"gemini-2.5-flash": (0.075, 0.30), "gemini-2.5-pro": (1.25, 5.00)}

def after_model_callback(callback_context, llm_response):
    usage = getattr(llm_response, "usage_metadata", None)
    if not usage: return
    p_in, p_out = PRICE.get(llm_response.model, (0, 0))
    cost = usage.prompt_token_count * p_in / 1e6 + usage.candidates_token_count * p_out / 1e6
    s = callback_context.state
    s["session:cost_usd"] = s.get("session:cost_usd", 0.0) + cost
    if s["session:cost_usd"] > COST_CAP_USD:
        raise RuntimeError(f"Session cost cap exceeded: ${s['session:cost_usd']:.2f}")
```

The exception bubbles out of the run; the runner emits an error event. Surface as an opaque error to the user.

---

### Recipe 6 — Sandbox-only code execution policy

Origin: [[12_CodeExecution/08_InProduction]].

The "recipe" here is a *negative* one — refuse to start the agent if a wrong executor is wired in prod.

```python
import os
from google.adk.code_executors import UnsafeLocalCodeExecutor

def make_app():
    if os.environ.get("ENV") == "prod":
        from google.adk.code_executors import VertexAiCodeExecutor
        executor = VertexAiCodeExecutor()
    else:
        executor = UnsafeLocalCodeExecutor()
    # ... build agent with executor
    return app

if os.environ.get("ENV") == "prod" and isinstance(executor, UnsafeLocalCodeExecutor):
    raise RuntimeError("UnsafeLocalCodeExecutor is forbidden in prod.")
```

This is a *deploy-time* guardrail, not a runtime one. The runtime version is "fail closed if the sandbox is unavailable."

---

### Recipe 7 — BigQuery scan-byte cap

Origin: [[10C_BigQueryAgents/07_InProduction]], [[15_Observability/08_InProduction]] § 6.

```python
from google.cloud import bigquery

def before_tool_callback(tool, args, tool_context):
    if tool.name != "execute_sql":
        return None
    client = bigquery.Client()
    cfg = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    job = client.query(args["sql"], job_config=cfg)
    if job.total_bytes_processed > 10 * 1024**3:  # 10 GiB
        return {"error": f"Query would scan {job.total_bytes_processed/1024**3:.1f} GiB > 10 GiB cap."}
    return None
```

A dry-run before the real run. Costs you a metadata call; saves you a runaway query.

---

> 🛠 **Have the student run:** pick *three* of these seven recipes and add them to the M4 auditor. Confirm at least one of them fires on a crafted prompt (an email in the input, a rate-limit-busting loop, etc.).

> 🚀 **In Production**
>
> The cookbook is a *menu*, not a manifest. The discipline is: for every threat in the page-01 table, name which recipe (or combination) covers it. Threats with *no* covering recipe are accepted risk — document them.

---

[← Prev: 16_ProductionSecurity/04_SecretsHandling](04_SecretsHandling.md)  [↑ Map](../../MAP.md)  [Next: 16_ProductionSecurity/06_AgentIdentityVsUser →](06_AgentIdentityVsUser.md)
