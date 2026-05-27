---
module: 12_CodeExecution
page: 08_InProduction
title: Code execution in production
estimated_minutes: 30
prereqs: [12_CodeExecution/07]
concepts: [executor choice, package allowlist, audit log, resource limits, retry semantics, prompt-executor coupling, observability]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 12_CodeExecution/07_DissectingSample]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/09_KnowledgeCheck →]

You are here: 🗺 Runtime Track ▸ 12 Code Execution ▸ 08 In Production

# 🚀 The production hardening pass

Every item below is shaped as **Risk → Mitigation → Source/anchor** so you can lift them straight into a runbook. The synthesis at the bottom — the *checklist* — is your launch gate.

## 1. `UnsafeLocalCodeExecutor` never reaches prod

- **Risk:** code runs in your agent's own Python process; one prompt-injected payload owns your service. There is no in-process sandbox in CPython.
- **Mitigation:** swap by deploy target — Vertex deploy → `VertexAiCodeExecutor` (or `AgentEngineSandboxCodeExecutor` for Agent Engine); self-hosted → `ContainerCodeExecutor` or `GkeCodeExecutor` (`executor_type="job"`); pure math/plots only → `BuiltInCodeExecutor`. Add a CI check that grep-fails on `UnsafeLocalCodeExecutor` outside test paths.
- **Source/anchor:** `unsafe_local_code_executor.py:88-107` (multiprocessing `spawn` is NOT a sandbox — it's a fresh interpreter with full host access). Forward: [[16_ProductionSecurity/02_PromptInjectionDefense]], [[16_ProductionSecurity/05_GuardrailsCookbook]] Recipe 6.

## 2. Fill in every `DEPENDS` cell of the bypass matrix

- **Risk:** `ContainerCodeExecutor` and `GkeCodeExecutor` ship hardened *seams*, not hardened *postures*. A `DEPENDS` cell in `02A_SandboxBypassClasses` is a vulnerability whose presence you've documented but whose state you haven't.
- **Mitigation:** for each executor your team ships, fill the matrix against your actual config. Network egress in particular: GKE-job ships with **no `NetworkPolicy`** (`gke_code_executor.py:265-336` writes no networking field). Apply a `default-deny` NetworkPolicy in the sandbox namespace, then explicitly allow only what tools need.
- **Source/anchor:** `02A_SandboxBypassClasses.md` (the matrix is at `_figures/bypass_matrix.txt`). For Container: the `docker run` flags on the daemon are authoritative — never `--privileged`, `--net=host`, or bind-mount `/`.

## 3. Set per-execution timeouts explicitly

- **Risk:** `BaseCodeExecutor.timeout_seconds` default is `None` (`base_code_executor.py:79-80`). An unbounded model snippet (`while True: pass`, infinite recursion, runaway pandas join) can hold a runner thread until the host kills it. For `GkeCodeExecutor` the default is 300s (`gke_code_executor.py:94`) — fine for analytics, far too long for a calculator.
- **Mitigation:** set `timeout_seconds=` to the smallest value that supports your workload. Multi-modal analytics: 60-120s. Single-shot math: 5-10s. Pair with executor-side limits — `mem_limit`, `cpu_limit` on GKE; daemon-side limits on Container; sandbox config for Agent Engine.
- **Source/anchor:** `base_code_executor.py:79-80`, `gke_code_executor.py:94`. The retry math interacts (next item) — total worst-case wall time = `timeout_seconds * (error_retry_attempts + 1)`.

## 4. Pin `error_retry_attempts`

- **Risk:** `BaseCodeExecutor.error_retry_attempts` defaults to `2` (`base_code_executor.py:59`). On a transient `ResourceExhausted` or sandbox timeout, the runtime re-submits the code three times total before surfacing the failure. For a 60s-timeout sandbox that hung, your user waits 3 minutes for an error.
- **Mitigation:** for interactive UX, lower to `1` or `0` and surface the failure fast so the model can write different code. For unattended batch jobs where transient sandbox errors are common, the default `2` is fine.
- **Source/anchor:** `base_code_executor.py:59`. Note retries re-submit *new* code from the model (not the same submission to the same sandbox) — see `GkeCodeExecutor` `backoff_limit=0` at `:320` for why.

## 5. The LLM will try to install packages

- **Risk:** `subprocess.run(["pip", "install", "...]")`, `!pip install requests`, `import urllib.request; urllib.request.urlretrieve(...)` — all are within the model's repertoire and all of them are network operations that may succeed silently in your sandbox.
- **Mitigation:** decide explicitly between **Deny** (pin image, reject `pip install` calls via callback), **Allowlist** (pre-vetted package set enforced at sandbox layer), or **Open** (only for trusted data-science workloads where ops controls egress). The decision belongs in your design doc, not in the silent default.
- **Source/anchor:** `before_tool_callback` is the policy enforcement point ([[07_Callbacks]]). For Vertex/AgentEngineSandbox the allowlist is Google's; for Container/GKE it's whatever your image has installed.

## 6. Audit-log every executed snippet

- **Risk:** code execution is functionally a privileged operation. Without a log you cannot answer "what did the model run last Tuesday at 14:32?" in an incident.
- **Mitigation:** for runtime-side executors (everything except BuiltIn), the runtime persists results under `_CODE_EXECUTION_RESULTS_KEY` in session state (`code_executor_context.py:167-191`). Ship that key to a queryable store. The `BigQueryAgentAnalyticsPlugin` from [[13_Plugins]] does this naturally; for self-hosted, write a `before_model_callback` that copies the `_code_execution_results` key into your audit pipeline.
- **Source/anchor:** `code_executor_context.py:167-191`. For BuiltIn you can log the `executable_code` parts that come back in the model's response, but you cannot log stdout/stderr — the sandbox is Google-side.

## 7. The prompt and the executor are coupled — version them together

- **Risk:** a `VertexAiCodeExecutor(stateful=True)` agent whose prompt says "variables stay in the environment" is one constructor edit away from a silent bug. Flip to `stateful=False` without rewriting the prompt and every multi-turn analysis returns wrong answers — the model references variables the kernel no longer has.
- **Mitigation:** treat constructor kwargs and prompt as one artifact. Code-review them together. Add a smoke test that asserts the prompt's "Imported Libraries" block matches `_IMPORTED_LIBRARIES` (`vertex_ai_code_executor.py:36-85`) when targeting Vertex; same for any pre-imports your image bakes in.
- **Source/anchor:** `data-science/sub_agents/analytics/prompts.py:40-55` (the statefulness + imports contract). See `07_DissectingSample` "File 2."

## 8. `stateful=True` has a context-bloat cost

- **Risk:** the Vertex kernel's stickiness is free; the conversation transcript's growth is not. Every prior `code_execution_result` part accumulates in the model's input on the next turn. By turn 20 a chatty analytics session can carry 10k extra input tokens (illustrative — verify against your model's price card).
- **Mitigation:** measure `turns_per_session` for your agent. If the average is below 3, you're paying the bloat without the UX benefit — set `stateful=False`. If you're running on Pro pricing, the threshold to revisit is even lower.
- **Source/anchor:** `04_VertexAiCodeExecutor.md` "Stateful execution: what it actually costs." Cross-link: [[15_Observability]] for measuring it.

## 9. Filter the egress *and* the inputs

- **Risk:** even a hardened sandbox doesn't stop the model from emitting code that exhausts its own egress allowlist or returns a poisoned answer crafted by an upstream attacker (indirect prompt injection). Sandbox isolation is necessary; sandbox isolation is not sufficient.
- **Mitigation:** treat user-supplied data files as untrusted (run `explore_df`-style checks before passing them in); treat the *output* of code execution as untrusted before re-feeding it to the model (a `before_model_callback` can strip suspicious payloads); deny-by-default egress at the sandbox layer.
- **Source/anchor:** [[16_ProductionSecurity/02_PromptInjectionDefense]] for the upstream story; [[16_ProductionSecurity/05_GuardrailsCookbook]] for the callback recipes.

## 10. Choose by deploy target, not by familiarity

- **Risk:** "we'll switch to a real sandbox later" is the modal sentence preceding a security incident. `UnsafeLocal` is two lines; so is `VertexAiCodeExecutor`. There is no actual savings to deferring.
- **Mitigation:** pick the executor on day one based on your deploy target (Vertex → Vertex; Agent Engine → AgentEngineSandbox; GKE → GKE-job; self-hosted small fleet → Container; math-only → BuiltIn). Document the choice in your `agent.py` with a one-line comment naming the alternative you rejected and why.
- **Source/anchor:** the trade-off tables in `03`-`06` of this module.

## Quick checklist before launch

- [ ] No `UnsafeLocalCodeExecutor` in the deploy artifact (CI-enforced).
- [ ] Every `DEPENDS` cell of the `02A` matrix filled in (in writing, in the runbook) for the chosen executor.
- [ ] `timeout_seconds=` set explicitly; `error_retry_attempts` chosen on purpose.
- [ ] For GKE: `NetworkPolicy` applied (default-deny + allowlist); for Container: daemon `docker info` audited; for Vertex/AgentEngineSandbox: current allowlist confirmed with security team.
- [ ] CPU + memory limits set at the executor or sandbox layer.
- [ ] Executed code + result logged to a queryable store (BQ, Cloud Logging, whatever).
- [ ] Package-install policy decided (deny / allowlist / open) and enforced.
- [ ] Prompt and `code_executor=` kwargs cross-checked (statefulness, imports, output protocol).
- [ ] For `stateful=True`: average `turns_per_session` measured; threshold for flipping it off documented.
- [ ] An incident playbook exists: "what to do when the sandbox runs unexpected code" — who pages, how to revoke session, how to pull the audit log.

> 🤖 **Tutor:** the package-install question and the retry-math question catch most teams off guard. Walk the student through what happens when (a) the model writes `subprocess.run(['pip','install','requests'])` against a Container with full egress, and (b) the model writes `time.sleep(120)` against a Vertex executor with `timeout_seconds=None` and `error_retry_attempts=2`. The numbers in each scenario are the teaching.

> 🚀 **In Production**
>
> The single best forcing function for this checklist is a launch-gate doc that
> lists every line of it as a yes/no question with the source-of-truth file path
> next to each. If a row says "no," ship is blocked. The discipline of writing
> down "we accept the risk because X" — and getting a security review sign-off
> on that line — is what separates "we have a sandbox" from "we have a posture."

---

[← Prev: 12_CodeExecution/07_DissectingSample]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/09_KnowledgeCheck →]
