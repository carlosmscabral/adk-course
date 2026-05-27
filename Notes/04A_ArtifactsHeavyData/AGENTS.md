# 🤖 AGENTS.md — Module 04A Artifacts & Heavy Data (teaching notes for the AI tutor)

> 🤖 **Tutor:** read this file after the global [AGENTS.md](../../AGENTS.md) and before opening 00_Overview. The module-specific pacing here does not fit in page frontmatter.

## What the student should walk away knowing

- **The state-vs-artifact split**: small + structured → state, large or binary → artifact. The decision tree on page 01 is the contract.
- **`BaseArtifactService` interface** and the three implementations (`InMemoryArtifactService`, `FileArtifactService`, `GcsArtifactService`); when to use each.
- **`tool_context.save_artifact(filename, part)` returns an int version**; `load_artifact(filename, version=None)` returns the latest (or pinned) Part or None.
- **`Part(inline_data=Blob(...))` vs `Part(file_data=FileData(file_uri=...))`** — the ~10 MB rule.
- **`artifact_delta` on EventActions** is the audit trail. The Runner persists `{filename: version}`; the bytes live in the artifact service.
- **Cross-sub-agent handoff** = filename in state (via `output_key=` or explicit state write), bytes in artifact service. Sequential or graph topology required — never Parallel for this.
- **GCS production setup**: bucket creation flags, IAM least-privilege, lifecycle policy. The fallback pattern from `brand-aligned-presentations`.
- **Signed URLs for cross-process handoffs** (A2A, frontend, webhooks). Short TTL, never logged.

## Pacing

- **Easy if** the student is comfortable with Module 04's state-delta model and has wired a `FunctionTool` with `ToolContext` before. → Cruise pages 01-04; spend the time on 05 (multimodal Parts), 09 (handoff), 10 (dissection).
- **Hard if** the student conflates state and artifacts. Linger on page 01's decision tree; reuse it whenever they ask "where does X go?". The whole module collapses if they cannot place a value in the right store.
- **Hard if** the student has no GCP project. Pages 03 / 06 / 07 are ☁️-tagged for a reason — walk the code and the patterns but skip live runs. The local Work/ scripts on `InMemoryArtifactService` (pages 02, 04, 08, 09) all run without GCP.
- Expected total time for an on-pace student: **~3 hours** (sum of `estimated_minutes` across the module).

## Watch for these mistakes

- **Returning bytes from a tool.** Students raised on REPL print habits will return the artifact content. Push them to return short status strings (`"saved as report.md v0"`). The drill rubric catches this.
- **Forgetting to wire `artifact_service=` to the Runner.** Symptom: `ValueError: Artifact service is not initialized.` Mentioned on page 02; will reappear in the drill.
- **`output_key` set on the consumer instead of the producer.** Pattern: `output_key=` belongs on the agent whose REPLY should land in state; in the uploader→summariser drill, that is the uploader.
- **Inlining a large file.** If a `Part(inline_data=Blob(data=...))` carries > ~10 MB, the request fails. Push them to `file_data` with a GCS URI.
- **Storing bytes in state.** Anti-pattern that the module exists to prevent. If they reach for `state["pdf"] = bytes`, stop them and walk the page 01 decision tree.
- **Mutating an artifact in place.** Artifacts are versioned and immutable per version. To "update" an artifact, save a new version. Reading and modifying bytes locally is fine; pushing them back overwrites only if you `save_artifact` with the same name (which creates v+1, not a mutation).
- **No lifecycle policy on the GCS bucket.** Easy to skip in dev; catastrophic in prod. Page 03's recipe is a one-liner; insist on it before they call the GCS work done.

## When to suggest a detour

| Student says / shows | Suggest |
|---|---|
| "Wait, what's `gs://` and how do I auth?" | [[Cloud_Run]] (deployment context) or [[SignedUrls_GCS]] for the URL deep-dive — both cover GCS basics. |
| "What's a signed URL for, really?" | [[SignedUrls_GCS]] — covers V4 signing, browser-direct uploads, audience-restricted URLs in ~20 min. |
| "Why is artifact_delta on the event and not a callback?" | Skip the detour, point at [Module 19 / Internals](../19_Internals/) — the framework-source trace lives there. |
| "How does Agent Engine handle artifacts?" | [22 Deployment Models / 03 Agent Engine](../22_DeploymentModels/03_AgentEngine.md) — Agent Engine provides a GCS bucket automatically. |

If the same detour is suggested and declined twice (check `student_profile.md`), stop offering it.

## Mini-drill grading

- **Clean pass** = stdout contains all three expected substrings on the first run; bonus second turn produces no new `artifact_delta`; final reply is a coherent one-sentence summary.
- **Pass with hint** = student forgot `tool_context` parameter or wired `output_key` to the wrong agent, tutor pointed it out, student fixed and re-ran successfully.
- **Fail** = `artifact_delta` never appears (tool never called `save_artifact`); or `load_artifact` returns None and the summariser produces garbage; or the runner errors with "Artifact service is not initialized." Re-drill: have them rebuild from `Work/09_handoff.py`.

### Edge case to probe (after the basic drill passes)

- Ask them to **swap `SequentialAgent` for `ParallelAgent`** and re-run. The summariser will fail (`load_artifact` returns None because the uploader hasn't saved yet). They should explain why — temporal ordering is required for artifact handoffs. The fix is either Sequential, or a graph workflow with an explicit dependency edge (Module 06). This drives home that **artifacts are not magic — they are bytes in a store, and a downstream reader must run AFTER the upstream writer**.

## Cross-module hooks

- **This module is referenced from**: [04B Human-in-the-Loop](../4B_HumanInTheLoop/) (HITL flows often pass artifacts back and forth with the human); [05 Multi-Agent](../05_MultiAgent/) (cross-agent handoffs); [06 Graph Workflows](../06_GraphWorkflows/) (artifact dependencies become explicit edges); [10 A2A](../10_A2A/) (remote agents need signed URLs, not artifact-service references); [16 Production & Security](../16_ProductionSecurity/) (PII in artifacts, safety scanning); [22 Deployment Models](../22_DeploymentModels/) (which bucket per deployment shape); [23 Frontend Integration](../23_FrontendIntegration/) (browser-direct uploads via signed PUT URLs).
- **This module references**: [04 Sessions & State](../04_SessionsState/) (state-delta and event-actions model, `user:` prefix); [03 Tools](../03_Tools/) (`FunctionTool` + `ToolContext`); [05 Multi-Agent](../05_MultiAgent/05_SharingStateAcrossAgents.md) (shared session); the [SignedUrls_GCS detour](../Detours/SignedUrls_GCS.md).
- If the student forgets a prerequisite concept (state prefixes, ToolContext injection), the tutor should NOT re-teach inline — back up to the prereq page briefly, then return to where they were.
