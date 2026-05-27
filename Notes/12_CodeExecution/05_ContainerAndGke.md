---
module: 12_CodeExecution
page: 05_ContainerAndGke
title: ContainerCodeExecutor and GkeCodeExecutor
estimated_minutes: 20
prereqs: [12_CodeExecution/04]
concepts: [ContainerCodeExecutor, GkeCodeExecutor, BYO sandbox, image control]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 12_CodeExecution/04_VertexAiCodeExecutor]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/06_AgentEngineSandbox →]

You are here: 🗺 Runtime Track ▸ 12 Code Execution ▸ 05 Container & GKE

# 🚀 Bring your own sandbox

When the Google-managed sandboxes don't fit (regulated environment, custom binaries, on-prem), ADK ships two executors that delegate to *your* container runtime.

## `ContainerCodeExecutor`

Runs each code execution inside a Docker container you specify.

```python
from google.adk.agents import LlmAgent
from google.adk.code_executors import ContainerCodeExecutor

agent = LlmAgent(
    model="gemini-2.5-flash",
    name="analyst",
    code_executor=ContainerCodeExecutor(
        image="my-org/python-sandbox:3.12-slim",
        # Other ctor kwargs (per container_code_executor.py):
        #   base_url=None       — point at a remote Docker daemon
        #   docker_path=None    — build from a Dockerfile dir instead of `image`
    ),
)
```

The constructor only accepts `base_url`, `image`, and `docker_path`. **Network isolation, timeouts, and memory caps are not executor kwargs** — they're properties of the Docker daemon / image / container runtime config. Bake them into the image (or the `docker run` defaults for your daemon); the executor itself doesn't expose knobs for them.

You control:

- The base image (so the package set is yours).
- Resource limits and network policy — at the **Docker layer**, not via the executor.
- Volume mounts (data files made available to the sandbox) — same: configured on the Docker side.

Cost: container startup per execution adds latency. Worth it when you need real isolation on your own host.

## `GkeCodeExecutor`

Same shape as `ContainerCodeExecutor` but the container runs as a pod in your **GKE cluster** instead of via local Docker.

```python
from google.adk.code_executors import GkeCodeExecutor

agent = LlmAgent(
    ...,
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

Use when:

- You already run on GKE and want the sandbox to share node policy / IAM.
- You need horizontal scale: 100 concurrent agent turns → 100 pods, not 100 local containers.

## Comparing them

| | `Container` | `Gke` |
|--|--|--|
| Runs where | local Docker daemon (or one you point at) | k8s pod |
| Scale | single host bound | cluster-wide |
| Setup cost | Docker installed | GKE cluster, SA, image registry |
| Best for | dev that mirrors prod; single-node deploy | full prod with autoscale |

## The image is now part of your security perimeter

You inherit responsibility for everything in the container: package CVEs, syscall surface, network egress policy, secrets-not-leaked. The executor *isolates*; it doesn't *harden*. Two practical asks:

- Pin the base image digest, not the tag.
- Set egress to deny-by-default. Allow only what your tools/queries need.

> ⚠️ **Gotcha.** A misconfigured Docker daemon ( `--privileged`, host network mount) collapses the isolation completely. `ContainerCodeExecutor` is only as safe as the Docker config it runs against.

> ❓ **Ask the student:** "You run 200 agent turns/minute. Container or GKE?" *(Expected: GKE — local Docker can't keep up with autoscale and per-pod isolation matters at that volume.)*

> **🚀 In Production**
>
> If you're already on GKE, use `GkeCodeExecutor` with per-execution pods, deny-egress NetworkPolicy, and pinned image digests. If you're self-hosting on a small fleet of VMs, `ContainerCodeExecutor` is fine — but treat the Docker config as part of the security audit.

---

[← Prev: 12_CodeExecution/04_VertexAiCodeExecutor]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/06_AgentEngineSandbox →]
