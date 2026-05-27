---
module: 12_CodeExecution
page: 08_InProduction
title: Code execution in production
estimated_minutes: 20
prereqs: [12_CodeExecution/07]
concepts: [executor choice, package allowlist, audit log, resource limits]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 12_CodeExecution/07_DissectingSample]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/09_KnowledgeCheck →]

You are here: 🗺 Runtime Track ▸ 12 Code Execution ▸ 08 In Production

# 🚀 The five non-negotiables

## 1. UnsafeLocal never reaches prod

The single sharpest rule in this module. `UnsafeLocalCodeExecutor` runs in your process. Prompt injection one turn from a user → owned. There is no "but I trust this input" exception when the inputs include LLM outputs.

The standard swap:

- Vertex deploy → `VertexAiCodeExecutor` (or `AgentEngineSandboxCodeExecutor` for Agent Engine).
- Self-hosted → `ContainerCodeExecutor` or `GkeCodeExecutor`.
- Pure-computational (math, plots) only → `BuiltInCodeExecutor`.

Detour: `16_ProductionSecurity/02_CodeExecSafety.md` covers prompt-injection scenarios in depth.

## 2. Sandbox is not the same as safety

Even with a real sandbox: an unbounded loop ties up a runner thread, a huge allocation blows your memory, a wide-open network can exfiltrate via your sandbox's egress. Set:

- **CPU + memory limits** (`mem_limit`, `cpu_quota`, k8s `resources.limits`).
- **Wall-clock timeout** per execution.
- **Egress policy** — deny-by-default; whitelist explicit destinations if needed.
- **Filesystem boundaries** — read-only mounts where possible.

## 3. Audit-log all executed code

Every executed snippet is, effectively, a privileged operation. Log:

- The full code body (with PII scrubbed if user data leaks into it).
- The execution result (stdout/stderr/return).
- The agent + session + user identity that triggered it.

Hook this up via `15_Observability` — the `BigQueryAgentAnalyticsPlugin` from module 13 captures this naturally.

## 4. The LLM will try to install packages

`!pip install requests` or `subprocess.run(["pip", "install", ...])` is exactly the kind of thing an LLM will reach for. Decide explicitly:

- **Deny.** Pin the image / sandbox package set. Reject `pip install` calls at the sandbox layer.
- **Allow with allowlist.** Pre-vet a list of safe packages and have the sandbox enforce it.
- **Open** is acceptable in a heavy-data-science setup where ops controls the network, but make it a *decision*, not a default.

## 5. Choose by deploy target, not by familiarity

Many teams reach for `UnsafeLocal` because it's two lines and "we'll fix it later." Then "later" is the post-launch incident review. The cost of doing `VertexAiCodeExecutor` from day one is one config block.

## Quick checklist before launch

- [ ] No `UnsafeLocalCodeExecutor` anywhere in the deploy artifact.
- [ ] CPU + memory + timeout limits set explicitly.
- [ ] Egress policy on the sandbox documented (and denied by default).
- [ ] Executed code is logged to a queryable store.
- [ ] Package-install policy decided (deny / allowlist / open) and enforced at sandbox layer.
- [ ] An incident playbook exists: "what to do when a sandbox runs unexpected code."

> 🤖 **Tutor:** The package-install question catches almost every team off guard. Have the student think through what happens when the model writes `import scikit_learn` and the sandbox doesn't have it.

---

[← Prev: 12_CodeExecution/07_DissectingSample]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/09_KnowledgeCheck →]
