---
module: 12_CodeExecution
page: 05A_GkeCodeExecutor
title: GkeCodeExecutor — pods on your cluster
estimated_minutes: 25
prereqs: [12_CodeExecution/05]
concepts: [GkeCodeExecutor, k8s job, gVisor, NetworkPolicy, hardened defaults, Workload Identity]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 12_CodeExecution/05_ContainerCodeExecutor]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/06_AgentEngineSandbox →]

You are here: 🗺 Runtime Track ▸ 12 Code Execution ▸ 05A GKE

# 🚀 GkeCodeExecutor — code execution at cluster scale

Same shape as `ContainerCodeExecutor` but the container runs as a pod in your **GKE cluster** instead of via local Docker. The two big operational differences: each execution is its own pod (no state leakage like Container suffers), and the framework writes a hardened pod spec for you (you don't get to forget the security context).

```python
from google.adk.agents import LlmAgent
from google.adk.code_executors import GkeCodeExecutor

agent = LlmAgent(
    model="gemini-2.5-flash",
    name="analyst",
    code_executor=GkeCodeExecutor(
        image="us-central1-docker.pkg.dev/proj/repo/sandbox:1.0",
        namespace="agent-sandbox",
        executor_type="job",   # "job" (default) or "sandbox"
        cpu_limit="500m",      # other real fields: timeout_seconds, mem_limit, cpu_requested,
                               # mem_requested, kubeconfig_path, kubeconfig_context, etc.
    ),
)

# Service-account binding is NOT a constructor kwarg — there is no `service_account`
# field on GkeCodeExecutor, and passing one raises a Pydantic ValidationError.
# Bind identity at the cluster level via Workload Identity:
#
#   gcloud iam service-accounts add-iam-policy-binding \
#     SANDBOX_GSA@PROJECT.iam.gserviceaccount.com \
#     --role roles/iam.workloadIdentityUser \
#     --member "serviceAccount:PROJECT.svc.id.goog[agent-sandbox/sandbox-ksa]"
#
#   kubectl annotate serviceaccount sandbox-ksa \
#     -n agent-sandbox \
#     iam.gke.io/gcp-service-account=SANDBOX_GSA@PROJECT.iam.gserviceaccount.com
#
# The pods the executor creates will run under whatever KSA the namespace
# defaults to (or the one the controlling pod template specifies).
```

## The hardened pod spec — read it once

`gke_code_executor.py` is 429 lines; the security-critical chunk is `_create_job_manifest` at `:265-336`. The framework writes this manifest for you — you don't have to remember the flags. But you should know what it ships, because if you ever override it (or wrap this executor), these are the defenses you must preserve.

From `_create_job_manifest` (`:281-307`):

| Field | Value | Why |
|---|---|---|
| `run_as_non_root` | `True` | Don't let LLM code call APIs that require root inside the container. |
| `run_as_user` | `1001` | Pin a non-zero UID; defense in depth if the image doesn't already do this. |
| `allow_privilege_escalation` | `False` | Block `setuid` binaries and `sudo` escapes. |
| `read_only_root_filesystem` | `True` | LLM code can't write to `/` — no persistent state inside the pod. |
| `capabilities=drop(["ALL"])` | dropped | No `CAP_NET_RAW`, no `CAP_SYS_ADMIN`, etc. The container starts with zero kernel capabilities. |
| `runtime_class_name` | `"gvisor"` | Pod scheduled on a gVisor sandbox node — kernel syscalls go through a userspace interpreter, not directly to the host kernel. Major bar against kernel-CVE escapes. |
| `resources.requests/limits` | from constructor (`cpu_requested`, `mem_requested`, `cpu_limit`, `mem_limit`) | Hard caps; the pod gets OOMkilled at the memory limit rather than degrading the node. |

Plus from `_create_job_manifest` job-level spec (`:318-323`):

- `backoff_limit=0` — failed pod does NOT auto-retry. (Combined with `error_retry_attempts=2` on the executor itself, the runtime retries by submitting *new* code, not by re-running the same pod.)
- `ttl_seconds_after_finished=600` — failed/completed jobs stick around for 10 minutes for log inspection, then the k8s TTL controller cleans them up. Useful for audit/observability: you have a window to fetch logs without manual cleanup later.

Compare to `ContainerCodeExecutor`, which sets **none** of these by default. Same code, different posture: GKE-job ships hardened; Container ships open.

## `executor_type="job"` vs `"sandbox"`

Two execution modes, picked at construction:

- **`job` (default)** — every `execute_code()` call creates a fresh k8s Job + ConfigMap (the code is mounted at `/app/code.py`, run via `command=["python3", "/app/code.py"]`). Pod runs once, hits the security context above, gets cleaned up by the TTL controller. **Per-execution isolation: yes** (each pod is fresh). **Per-execution latency: pod startup** (typically seconds).
- **`sandbox`** — long-lived pods managed by the `k8s-agent-sandbox` controller (`_check_sandbox_dependency` at `:166-175` verifies the controller is installed and raises a clear error if not). Lower per-execution latency at the cost of cross-execution state leakage (same trade-off as `ContainerCodeExecutor`). Requires extra cluster-side setup; surface this with your platform team before picking it.

If you don't know which one to pick: `job`. It's the default for a reason.

## When to use it

- You already run on GKE and want the sandbox to share node policy / IAM.
- You need horizontal scale: 100 concurrent agent turns → 100 pods, not 100 local containers.
- You want hardened defaults out of the box and aren't willing to maintain the equivalent Docker config by hand.

## Comparing to `ContainerCodeExecutor`

| | `Container` | `Gke` |
|--|--|--|
| Runs where | local Docker daemon (or one you point at) | k8s pod |
| Per-execution isolation | NO (state leaks in the container) | YES (job mode) / NO (sandbox mode) |
| Hardened defaults | none (you configure) | yes (security context built in) |
| Scale | single host bound | cluster-wide |
| Setup cost | Docker installed | GKE cluster, namespace, SA, image registry |
| Best for | dev that mirrors prod; small fleet | full prod with autoscale |

## Sandbox-bypass posture

Per the `02A` matrix: GKE-job scores **YES** on filesystem isolation, env isolation, and privilege-escalation defense — directly from the security-context block above. Network egress is **◐ DEPENDS**: the framework does NOT apply a `NetworkPolicy`. Without one, every pod can talk to anything reachable from the node. Apply a `default-deny` NetworkPolicy in the sandbox namespace, then explicitly allow only what your tooling needs.

> ⚠️ **Gotcha #1.** `executor_type="sandbox"` requires the `k8s-agent-sandbox` package AND a cluster-side controller. If you set the flag and the controller isn't installed, `_check_sandbox_dependency` raises with a specific error message — read it, install the controller (or switch back to `job` mode), and try again.

> ⚠️ **Gotcha #2.** "GKE means it's secure" is wrong. The framework hardens the *pod*. You still need a `NetworkPolicy` for egress, a `ResourceQuota` for the namespace, image-pull permissions scoped tightly, and Workload Identity for the KSA. The pod-level defaults give you a long head start, not a finish line.

> ❓ **Ask the student:** "You run 200 agent turns/minute. Container or GKE?" *(Expected: GKE — local Docker can't keep up with autoscale and per-pod isolation matters at that volume.)*

> ❓ **Ask the student:** "Your security review asks 'what's the blast radius if the LLM emits code that exploits a Python sandbox CVE in our base image?' Answer for `executor_type="job"`." *(Expected: blast radius is one Job's pod. gVisor blocks most kernel-syscall escapes; the pod's KSA scopes IAM; the namespace-level `NetworkPolicy` scopes egress; the TTL cleans up the failed job after 10 min. The radius is small, not zero — naming "small" is the right answer; naming "zero" is overclaiming.)*

> 🚀 **In Production**
>
> If you're already on GKE, use `GkeCodeExecutor` with `executor_type="job"`,
> a deny-by-default `NetworkPolicy`, pinned image digests, and Workload-Identity-
> bound KSA scoped to the minimum IAM needed by the tools the sandbox calls.
> Set `timeout_seconds=` explicitly (default at `:94` is 300s — fine for analytics,
> too long for a calculator). Use the `ttl_seconds_after_finished=600` window
> to ship failed-job logs to your audit store before they're GC'd.

---

[← Prev: 12_CodeExecution/05_ContainerCodeExecutor]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/06_AgentEngineSandbox →]
