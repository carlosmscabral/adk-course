---
module: 16_ProductionSecurity
page: 09_DissectingPolicyAsCode
title: Dissecting policy-as-code
estimated_minutes: 30
prereqs: [16_ProductionSecurity/08]
concepts: [declarative policy, AST validation, sandboxed exec, deterministic checks]
icon: 🔬
in_production: true
detours_suggested: []
---

[← Prev: 16_ProductionSecurity/08_DissectingSafetyPlugins](08_DissectingSafetyPlugins.md)  [↑ Map](../../MAP.md)  [Next: 16_ProductionSecurity/10_InProduction →](10_InProduction.md)

You are here: 🗺 Production Track ▸ 16 Production & Security ▸ 09 Dissect policy-as-code

---

## 🔬 What we're reading

`/home/carloscabral/study/adk-samples/python/agents/policy-as-code/`

The agent automates data governance on Google Cloud Dataplex + BigQuery. *Policies* are expressed in natural language, but they execute as **generated Python code, validated and sandboxed**. This is the production answer to "the LLM judge is also an LLM" — for the parts of the policy that *must* be deterministic, write code.

## 🔬 Read order

### 1. `policy_as_code_agent/simulation.py` — the safe-exec engine

Open `/home/carloscabral/study/adk-samples/python/agents/policy-as-code/policy_as_code_agent/simulation.py`. Read top to bottom — it is only 144 lines.

**Lines 7-59 — `validate_code_safety(code)`.**

Two allow-lists masquerading as deny-lists:

```python
unsafe_modules  = {"os", "sys", "subprocess", "shutil", "pickle", "importlib",
                   "socket", "http", "urllib", "requests"}
unsafe_functions = {"eval", "exec", "open", "compile", "__import__"}
```

The function parses the candidate code with `ast.parse`, walks every `ast.Import`/`ast.ImportFrom`/`ast.Call` node, and refuses any that touch the deny-list. **AST is a deterministic check** — no LLM, no regex, no false positives from comments-vs-code.

**Lines 62-143 — `run_simulation(policy_code, metadata)`.**

Three-stage guard:

1. Static AST check (above).
2. Build a *restricted* `safe_globals` dict that only exposes the safe primitives:
   ```python
   safe_globals = {
       "__builtins__": {
           "abs": abs, "all": all, ..., "isinstance": isinstance,
           "__import__": __import__,
       },
       "json": json, "re": re, "datetime": datetime,
   }
   ```
3. `exec(policy_code, safe_globals)`; require the code to have defined `check_policy(metadata) -> list`; call it.

This is **sandbox-via-restricted-namespace**. Not bulletproof (a determined attacker can sometimes break out), but combined with the AST check it raises the bar significantly above "just `exec` whatever the LLM wrote." For untrusted code from the open internet you would layer in `ContainerCodeExecutor` (see [[12_CodeExecution/00_Overview]]) on top.

### 2. `policy_as_code_agent/agent.py` — the orchestration

Open `/home/carloscabral/study/adk-samples/python/agents/policy-as-code/policy_as_code_agent/agent.py`. Skim — it is long. Focus on:

- **Lines 57-88** — `generate_policy_code_from_gcs`: the LLM writes Python; we never trust it directly. It flows into `run_simulation`.
- **Lines 525-621** — `generate_compliance_scorecard`: runs a *suite* of named policies and produces a score. This is the **eval-suite-for-governance** pattern. Treat your policies the way you treat tests.
- **Lines 757-764** — `auto_save_session_to_memory_callback`: a normal `after_agent_callback` plumbing into long-term memory. Notice the agent has policies, memory, *and* a callback — separation of concerns matters.

### 3. `docs/HIGH_LEVEL_DETAILS.md`

Not required, but if you want the architecture rationale, skim that doc next. Note the deliberate *split* between LLM (generates code) and runtime (validates and sandboxes). That split is the whole point of the sample.

## 🧠 Lessons to extract

1. **LLM for fuzziness, code for enforcement.** The LLM translates English → Python; the deterministic AST + restricted exec actually enforces the policy. Don't use the LLM to enforce.
2. **AST analysis is your friend.** Many "is this string safe?" checks are unreliable. AST is exact for Python.
3. **Restricted globals are a real sandbox primitive.** Not perfect, but cheap. Layer with container isolation for untrusted code.
4. **Treat policies like tests.** A scorecard is the agent equivalent of a CI pipeline. Run it on a schedule.

## 🛠 Exercise

Have the student write *one* fake policy ("all tables in the finance dataset must have a description") and run `generate_compliance_scorecard` against synthetic metadata. They will see the LLM generate Python, the validator reject any unsafe import attempts, and the sandbox produce a violations list. Three concepts in one run.

> 🚀 **In Production**
>
> The `policy-as-code` pattern generalizes. Anywhere you can write the rule as code — billing thresholds, PII allow-lists, query cost caps — you should, because deterministic checks don't drift. Reserve LLM judgment for things that genuinely *need* fuzziness.

---

[← Prev: 16_ProductionSecurity/08_DissectingSafetyPlugins](08_DissectingSafetyPlugins.md)  [↑ Map](../../MAP.md)  [Next: 16_ProductionSecurity/10_InProduction →](10_InProduction.md)
