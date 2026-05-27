# AGENTS.md — Module 99 Capstone (teaching notes for the AI tutor)

## What the student should walk away with
- A working, deployable agent repo that integrates 20 modules of surface area.
- A self-review they can defend (in the README, in conversation).
- Honest understanding of where ADK fit their problem and where it didn't.
- A 6-month tickle to revisit and re-eval the capstone.

## Pacing
- Day 1 is the danger zone. Students often:
  - Spec-shop between tracks for hours. **Force a commit by end of hour 1.**
  - Skip the README "architecture first" step. **Insist on it.**
- Day 4 is when integration breaks. Multi-agent + A2A + observability stress the design. Be ready to suggest architectural backtracks.
- Day 5 is when polish-paralysis hits. **Time-box ruthlessly.** Eval-fix > prompt-polish.

## Watch for these mistakes
- **Scope creep.** Each track's spec is rich. The student must cut. If they're still adding features on Day 4, they're failing.
- **InMemorySessionService in "production" code.** Forbidden — call it out.
- **UnsafeLocalCodeExecutor in Track B.** Forbidden — the whole track is about safety.
- **Evals as an afterthought.** The 5 cases should be written on Day 4, not Day 5 at midnight.
- **Self-review that says "ADK is just better."** Reject. Push for a real concession to a competitor.
- **A2A configured but never called from a client.** Half the requirement. Force the student to demo the round-trip.

## When to suggest a detour
- Stuck on workflow graph mechanics → re-read `06_GraphWorkflows/`.
- Stuck on MCP server setup → re-read `08_MCP/`.
- Stuck on A2A handshake → re-read `10_A2A/`.
- Stuck on a stack trace inside ADK → open `19_Internals/`.
- Spinning on framework anxiety → `20_FrameworkComparison/09` decision flowchart.

## Grading the drill
- Use the rubric in `09_MiniDrill.yml`. Score honestly.
- Don't penalize cuts that were thoughtful. Do penalize cuts that were avoidant.
- Probe with the post-submit questions in the YAML. The student passes if they can answer ≥3 coherently.

## Track-specific notes

### Track A (Research)
- The critic loop runs away if uncapped. **Always cap.**
- MCP filesystem server works locally without GCP — good for offline dev.

### Track B (Code Reviewer)
- The diff-safety callback is the most-skipped requirement. **Catch it.**
- The sandbox MUST be Vertex or Container. Reject UnsafeLocal.

### Track C (Personal Knowledge Hub)
- The PII scrubber is the most-faked requirement (regex that doesn't actually fire). Have the student demo it firing on a real PII string.
- BOTH memory services are required for Track C. If they only used one, send them back.

## After they pass
- Celebrate. They finished the course.
- Push toward option A (ship it) from `07_InProduction`.
- Make them set the 6-month tickle out loud.
