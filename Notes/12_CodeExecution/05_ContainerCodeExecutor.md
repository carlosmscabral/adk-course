---
module: 12_CodeExecution
page: 05_ContainerCodeExecutor
title: ContainerCodeExecutor — your Docker daemon as the sandbox
estimated_minutes: 20
prereqs: [12_CodeExecution/04]
concepts: [ContainerCodeExecutor, BYO sandbox, image control, long-lived container]
icon: 🚀
in_production: true
detours_suggested: []
---

[← Prev: 12_CodeExecution/04_VertexAiCodeExecutor]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/05A_GkeCodeExecutor →]

You are here: 🗺 Runtime Track ▸ 12 Code Execution ▸ 05 Container

# 🚀 ContainerCodeExecutor — bring your own Docker

When the Google-managed sandboxes don't fit (regulated environment, custom binaries, on-prem, no Vertex), ADK ships `ContainerCodeExecutor` that delegates to *your* Docker daemon. GKE is the sibling (see 05A).

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

## Mechanics: long-lived container, exec-per-snippet

`container_code_executor.py` is 200 lines. The model matters for understanding the security implications.

- **Container lifecycle**: created ONCE at executor init via `containers.run(image=..., detach=True, tty=True)` (`:182-186`) and registered with `atexit.register(self.__cleanup_container)` (`:120`). The container is **long-lived for the executor's lifetime** (typically your process lifetime).
- **Per-execution**: each `execute_code()` call invokes `self._container.exec_run(['python3', '-c', code], demux=True)` (`:130-133`). Code is *literally* `python3 -c "..."` inside the running container — no file write, no script staging.
- **Stdout/stderr split**: `demux=True` gives you a tuple `(stdout_bytes, stderr_bytes)` (`:136-143`); both get decoded to UTF-8 and returned in the `CodeExecutionResult`.

The critical security implication: **state leaks between executions inside one `ContainerCodeExecutor`**. Snippet 1 can `open("/tmp/secret", "w").write("...")`; snippet 2 reads it back. Writable `/tmp`, leftover Python globals (well — actually `python3 -c` runs in a fresh interpreter each time, so the globals reset, but the filesystem doesn't), background processes the model spawned… all persist. This is the major operational difference from `GkeCodeExecutor` in its `job` mode (where each execution is a fresh pod with a fresh root filesystem).

If you need per-execution isolation with `ContainerCodeExecutor`, your only options are (a) restart the container between calls (extremely slow), (b) accept the leakage, or (c) move to GKE.

## You control

- The base image (so the package set is yours).
- Resource limits and network policy — at the **Docker layer**, not via the executor.
- Volume mounts (data files made available to the sandbox) — same: configured on the Docker side.

Cost: container startup per executor-init adds latency (one-time, not per-call). Per-call latency is roughly `exec_run` overhead — fast.

## When to use it

- Self-hosted on a small fleet of VMs where you control the Docker daemon.
- Dev environment that mirrors prod (same image as your GKE deploy).
- Air-gapped or on-prem environment where Vertex isn't an option.

## The image is now part of your security perimeter

You inherit responsibility for everything in the container: package CVEs, syscall surface, network egress policy, secrets-not-leaked, what's writable. The executor *isolates*; it doesn't *harden*. Two practical asks:

- Pin the base image digest, not the tag.
- Set egress to deny-by-default. Allow only what your tools/queries need.

The framework gives you the seam (a container boundary). You configure the rest. Per the `02A` bypass matrix, every cell for `Container` reads `◐ DEPENDS` — meaning the framework hands you the dimension to defend, but the verdict is determined by your image and your daemon config, not by the executor class.

> ⚠️ **Gotcha #1.** A misconfigured Docker daemon (`--privileged`, `--net=host`, bind-mounting `/`) collapses the isolation completely. `ContainerCodeExecutor` is only as safe as the Docker config it runs against. The single most dangerous flag is `--privileged` — it disables namespacing, capability drops, and seccomp in one move. Audit your daemon flags.

> ⚠️ **Gotcha #2.** State leaks across executions. If you assumed each snippet runs in a fresh sandbox, you assumed wrong — that's the GKE-job model, not the Container model. Plan accordingly: don't put secrets in the container's writable filesystem between user turns; assume the next snippet can read them.

> ❓ **Ask the student:** "The model writes `subprocess.run(['nc', '-l', '4444'], ...)` in turn 5 and then `open('/proc/net/tcp').read()` in turn 6. Why does this work in `ContainerCodeExecutor` even though each snippet is a fresh `python3 -c`?" *(Expected: each `exec_run` is a fresh process tree, but the container's network namespace and filesystem persist across calls — the listener from turn 5 is still running when turn 6 inspects `/proc/net/tcp`.)*

> 🚀 **In Production**
>
> If you're self-hosting on a small fleet of VMs, `ContainerCodeExecutor` is fine —
> but treat the Docker config as part of the security audit. Pin image digests,
> deny-by-default egress at the daemon (or via host iptables), set tight resource
> limits via the image. Assume state leaks across executions in the same
> container; design the agent's prompt and the surrounding callbacks so the
> next snippet can't read what the previous one wrote. If you can't keep that
> contract, use `GkeCodeExecutor` (job mode) instead — see 05A.

---

[← Prev: 12_CodeExecution/04_VertexAiCodeExecutor]  [↑ Map](../../MAP.md)  [Next: 12_CodeExecution/05A_GkeCodeExecutor →]
