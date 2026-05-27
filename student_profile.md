---
last_updated: 2026-05-27
cursor: 00_Setup/00_Overview
total_hours: 0
total_minutes_logged: 0
speed_ratio: TBD
mode: on-pace
---

# 👤 Student Profile

**The adaptive-memory snapshot for the AI tutor.** The tutor reads this at session start to calibrate pacing, and writes back at session end with new datapoints. Initial state is empty — the first 2–3 sessions populate it; from there it drives compression / drill / detour decisions.

> 🤖 **Tutor:** see the *Adaptation rules* table in [AGENTS.md](AGENTS.md). Update this file every session-end. If a pattern emerges (a recurring gap, a consistent strength), write an auto-memory and reference it here with `[[name]]`.

---

## Calibration

- **Speed**: TBD (need ≥1 completed module to compute `speed_ratio = actual_minutes / sum(estimated_minutes)`)
- **Mode**: on-pace (default until calibrated)
- **Strong concepts**: TBD
- **Recurring gaps**: TBD
- **Style**: engine-first ([[user-learning-approach]]) — types low-level primitives by hand before trusting abstractions; teach engine-first.
- **Detours taken**: _(none yet)_
- **Detours suggested but declined**: _(none yet)_
- **External calibration carried in**: ([[user-python-calibration]]) — sort/class/nested-loops landed first try; search-loop control flow (break + no-match branch) needs reps. Watch for this in 02 First Agent's `async for event in runner.run_async(...)` loop.

## Environment

- **Python version**: TBD (tutor verifies in 00 Setup)
- **ADK version**: TBD (target: 2.0 GA — `pip show google-adk` to confirm)
- **GCP project id**: TBD (required for the Data & GCP track starting at 10A)
- **GCP region**: TBD
- **Has microphone**: TBD (required for Module 18 voice drill; SSE drill stands in if not)
- **Editor / shell**: TBD

## Working hypotheses (tutor maintains)

Short bulleted observations the tutor jots after each session. Promote to `Strong concepts` / `Recurring gaps` once confirmed across 2+ sessions.

- _(none yet)_

## Detour ledger

Track which detours have been *suggested*, *taken*, or *declined-twice* (stop suggesting). The tutor populates this as the course unfolds.

| Detour | Suggested at | Taken? | Helpful? | Notes |
|---|---|---|---|---|
| _(none yet)_ | | | | |

---

## Per-module log

The tutor appends one row per completed module. Estimated minutes come from each page's frontmatter; actual minutes is the tutor's tally for the session(s) on that module.

| Module | Started | Completed | Est min | Actual min | KC score | Drill | Notes |
|---|---|---|---|---|---|---|---|
| _(none yet)_ | | | | | | | |

---

## Auto-memory cross-references

When a pattern is stable enough to outlive this course, the tutor writes a dedicated memory file (e.g., `user_adk_calibration.md`) and links it here. These survive beyond the course and feed cross-project signals.

- _(none yet — first one will land mid Module 02)_
