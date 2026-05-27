# 🛠 Authoring Recipe — how to add to this course

Welcome, author (likely an AI coding assistant). This file describes the three additive operations the course is designed to absorb without restructuring:

1. **Add a new module** (covering a new ADK feature, or a deeper take on an existing one).
2. **Add a new detour** (a side-bar deep-dive — Python, protocol, or framework topic).
3. **Absorb an ADK release** (new version drops; mark affected modules).

All three preserve the invariants in [`../AGENTS.md`](../AGENTS.md): the cursor in [`../PROGRESS.md`](../PROGRESS.md), the per-module skeleton, the frontmatter contract, the tutor hooks, and the `student_profile.md` schema.

If you find yourself wanting to break one of those invariants — stop. Open an issue (or surface it to the user) before authoring. The contract is what makes the course teachable.

---

## 1. Add a new module

### (a) Decide on a track + number

The tracks are: Foundation (00–04) · Composition (05–06) · Integration (07–10) · Data & GCP (10A–10C) · Runtime (11–14) · Production (15–20) · Capstone (99).

- A new module that *follows from* an existing one slots in by appending a letter (e.g., a new GCP module would be `10D_Topic`).
- A new module that *deserves its own track* gets the next free number block.
- Never renumber an existing module — it breaks every `prereqs:` reference, every `PROGRESS.md` line, and every breadcrumb. Insert with a letter suffix instead.

Update the track placement in [`../MAP.md`](../MAP.md) — that file is the social contract for where modules live.

### (b) Copy the template

```
cp -r Notes/_TEMPLATE_MODULE Notes/NN_Topic
```

The template gives you:
- `00_Overview.md` — fill in goals, prereqs, time, sample anchor.
- `01_FirstConcept.md` — rename and clone for each concept page. Frontmatter is pre-stubbed.
- `05_DissectingSample.md` — pick a real sample under `../../../adk-samples/python/agents/` and walk it file-by-file.
- `06_InProduction.md` — consolidate this module's inline `> 🚀 In Production` callouts.
- `07_KnowledgeCheck.yml` — 5–7 one-sentence-answerable questions.
- `08_MiniDrill.yml` — exercise with verification rubric.
- `AGENTS.md` — module-local tutor notes.
- `_figures/.gitkeep` — ASCII diagrams go here.

Remember: the **trailing four** (`DissectingSample`, `InProduction`, `KnowledgeCheck`, `MiniDrill`) always sit at the end in that order. If your module has 7 concept pages instead of 4, shift them — `09_DissectingSample`, `10_InProduction`, `11_KnowledgeCheck.yml`, `12_MiniDrill.yml`.

### (c) Author per the skeleton

Honor the pedagogical rules in [`../_AUTHORING_AGENT_BRIEF.md`](../_AUTHORING_AGENT_BRIEF.md) — terse prose, REPL-driven, one concept per file, breadcrumbs top + bottom, tutor hooks (`> ❓`, `> 🛠`, `> 🤖`, `> 🧭`) on every page, inline `> 🚀 In Production` callouts wherever a real-world gotcha appears.

The mantra: **pages are scripts the tutor performs, not essays the student reads.**

### (d) Update `MAP.md` + `Contents.md`

- [`../MAP.md`](../MAP.md): drop the module into its track's box, in numeric order.
- [`../Contents.md`](../Contents.md): add the module section with every page linked. Mark pages 🚧 if any are stubs.

If the module is gated by a milestone (M1–M5), make sure the milestone bar in `MAP.md` sits above it.

### (e) Cross-link from neighbouring modules

Find at least one earlier module whose page should reference yours ("we'll see this fully in Module NN") and at least one later module that builds on yours. Add the explicit cross-reference — vague references erode trust.

Use the link conventions from the brief:
- Same module: `[link](04_NextPage.md)`
- Other module: `[link](../05_MultiAgent/03_AgentAsTool.md)`
- Detour: `[[PY_async]]` (the tutor resolves)
- Cheat sheet: `[link](../../Reference/CheatSheets/state_prefixes.md)`

### (f) Bump `CHANGELOG.md`

Add a dated entry under a new version (`## [0.x.0] - YYYY-MM-DD`). Name the module, list its sample anchor, note any new detours it introduces. If the module's mini-drill changes the demo app trajectory of the spiral curriculum, call that out.

### (g) Update `PROGRESS.md`

Add the new module's page checklist in the right track. Set `last_updated:` (frontmatter) to today's date. **Do not move the `cursor:`** — the student is wherever they were.

---

## 2. Add a new detour

Detours are short, optional sidebars. They live as **single files** in `Notes/Detours/` (no folder), 60–200 lines, with the same frontmatter shape as concept pages (`module: Detours`, plus `concepts:`, `icon:`, etc.).

### Steps

1. **Name it.** Convention: `PY_topic.md` for Python deep-dives, `Topic.md` for everything else (protocol, GCP, framework).
2. **Author it.** Same pedagogy: terse, REPL-driven, tutor hooks. Optional 🧪 mini-exercise at the end.
3. **Link from at least one Notes page with a 🧭 callout.** This is mandatory — an orphan detour (never linked) is flagged in CI. Example:
   ```markdown
   > 🧭 **Detour:** if WebSocket frames feel hand-wavy here, take 20 min at
   > [[WebSockets]] — it covers frames, ping/pong, close codes, and how SSE
   > differs.
   ```
4. **Add to [`../Contents.md`](../Contents.md)** under the right detour group (🐍 / ☁️ / 📡 / 📦).
5. **Bump [`../CHANGELOG.md`](../CHANGELOG.md)**.

Detours are **never gating**. Phrase suggestions as "if X feels hand-wavy, take 20 min here." Honor opt-out: if the tutor suggests a detour and the student declines twice (`student_profile.md` ledger), stop suggesting it.

### On-demand detours from the student

If during a session the student asks "wait, what's X?" and X is genuinely tangential, the tutor scaffolds a stub at `Notes/Detours/StudentRequested_Topic.md` and links it from the page that triggered it. This captures the demand without losing the lesson flow. Convert it from stub to full content in a later session.

---

## 3. Absorb an ADK release

ADK ships features and changes; the course is built against a pinned snapshot (see [`../Reference/docs_snapshot.md`](../Reference/docs_snapshot.md)). Every ~4 weeks an automated refresh pulls release notes; deltas land here.

### Steps

1. **Create the update entry.** Add `Notes/Updates/YYYY-MM_release.md`. Header: ADK version, release date, fetch date, source URL. Body: bulleted list of changes grouped by surface area (Agents · Runtime · Tools · Sessions · Models · CLI · NEW).
2. **Identify affected modules.** For each change, list the module(s) whose pages are now stale.
3. **Banner the affected modules.** Add a banner to the top of the module's `00_Overview.md`:
   ```markdown
   > ⚠ **Updated YYYY-MM** — see [release notes absorption](../Updates/YYYY-MM_release.md).
   > Sections impacted: 03 `FunctionTool` schema rules.
   ```
4. **Patch the pages.** Either inline edits (preferred for small deltas) or a new dedicated page (for big features — likely a new module instead).
5. **Bump [`../Reference/docs_snapshot.md`](../Reference/docs_snapshot.md)** with the new fetch date and any new section URLs.
6. **Bump [`../CHANGELOG.md`](../CHANGELOG.md)** with a `### Updated` block listing the release version and affected modules.

If a release deprecates a primitive the course teaches, do not delete the teaching — annotate it as legacy (the way 06 Graph Workflows already teaches Sequential/Parallel/Loop as "still supported, but graph is the modern story"). The student should learn what was, what is, and why the change.

---

## Invariants — do not break

| Invariant | Why |
|---|---|
| Page frontmatter contract (`module`, `page`, `title`, `estimated_minutes`, `prereqs`, `concepts`, `icon`, `in_production`, `detours_suggested`) | The tutor parses this to pace |
| Breadcrumbs top **and** bottom | Navigation UX; matches practical-python |
| Trailing four (`DissectingSample`, `InProduction`, `KnowledgeCheck`, `MiniDrill`) in that order at the end | Tutor expects fixed positions |
| One concept per file, ~20–40 lines | Pacing block size — the tutor teaches one file in one beat |
| At least one tutor hook (`> ❓`, `> 🛠`, `> 🤖`, `> 🧭`) per concept page | Pages without hooks are essays, not scripts |
| Real sample anchor in every `05_DissectingSample.md` | No invented examples; live patterns only |
| `> 🚀 In Production` callout inline wherever a tool/API/pattern has a real-world gotcha | The course teaches the right way the first time |
| `PROGRESS.md` checkboxes match `Contents.md` | Tutor cross-references them |

Break one of these and the tutor will start ad-libbing — at which point the AI-tutor contract (Verification gate #11 in the plan) is broken and the course no longer adapts.
