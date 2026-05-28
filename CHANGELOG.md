# 📜 CHANGELOG

All notable changes to this course will be documented here. Follows a loose [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) shape; one bump per phase + one bump per absorbed ADK release.

---

## [0.4.8] - 2026-05-28

Phase-0 dogfood fix #8 — **the tutor silently dropped the foundational agent-loop diagram.** User caught it from the live Antigravity transcript of Module 01: the tutor presented the page's prose and Three Examples cleanly, but the ASCII drawing of the agent loop never appeared in the rendering. Diagram-first is a non-negotiable learning style for this course (the user reads visuals before prose, then types primitives by hand from what the visual showed). Dropping the drawing breaks the contract at the most foundational page in the curriculum.

Root cause: the page contained `{{INCLUDE _figures/agent_loop.txt}}` inside a fenced code block — a transclude placeholder that **Markdown has no primitive for**. The tutor saw a literal `{{INCLUDE ...}}` token, didn't know what to do with it, and silently skipped to the next paragraph. This is the same pattern as v0.4.3/v0.4.4: the tutor optimizes for momentum and fills perceived structural gaps by skipping rather than asking.

Convention scope: the `{{INCLUDE _figures/X.txt}}` pattern appears on **10 pages** across the course (`00_Setup/03`, `01_Foundations/01`+`02`, `02_FirstAgent/02`, `03_Tools/03`, `04_SessionsState/01`+`04`, `04A_ArtifactsHeavyData/04`, `1A_AppAndRunner/01`). Page `00_Setup/03` even has a tutor hook that tried to compensate (*"the `{{INCLUDE …}}` placeholder above is for the static site renderer..."*) — clearly insufficient, since the convention still broke on Module 01.

### Fixed

- **`Notes/01_Foundations/01_WhatIsAnAgent.md`** — replaced the `{{INCLUDE _figures/agent_loop.txt}}` placeholder with the **full ASCII drawing inlined** in the fenced code block. The page is now self-contained: a Markdown viewer, a tutor, or a static renderer all see the same thing. Added a `> 🤖 Tutor` hook immediately below the drawing reinforcing that the diagram must be shown verbatim before the prose around it (the bullets reference the drawing by phrase like *"reading it left-to-right..."* — without the drawing they dangle).
- **`AGENTS.md`** — two new sections:
  - **Positive rule (in `🧠 During a lesson`)** — new "Visuals are non-optional" subsection. States that every ASCII diagram in a fenced code block must be displayed verbatim before surrounding prose. Names the `{{INCLUDE _figures/X.txt}}` placeholder explicitly: it's a legacy transclude that the tutor must expand by `Read`ing the referenced file and pasting its contents verbatim into the message. Names the two failure modes (the placeholder is unfamiliar; the tutor thinks prose substitutes for the visual). Gives a fallback for unicode/width issues (ask the student what they see; degrade to `+--+ / |` if needed; never drop).
  - **Negative rule (in `❌ What NOT to do`)** — "Do not drop diagrams." Short cross-reference to the positive rule above, naming the contract violation.

### Why

Diagram-first is one of the user's stated learning-style commitments — visuals are the *anchor*, prose is the *gloss*. The agent-loop drawing on `01_Foundations/01` is the single most important visual in the course; v0.4.6 even redrew it from scratch to depict the agent as the outer box (the v0.4.5/v0.4.6 precision arc culminated in that drawing). Shipping the precision fixes and then having the tutor silently skip the result is the worst of both worlds.

The `{{INCLUDE}}` placeholder convention was a Phase-0 authoring shortcut — clean source, separate concern, one file per figure. In retrospect it's the kind of cleverness-tax pattern that fails to render in any consumer (Markdown viewers don't expand it, the tutor doesn't expand it, and a future static site generator would need a custom plugin). Inline ASCII in fenced blocks is what `practical-python` does, and it works for the same reason: zero indirection between source and student.

v0.4.8 fixes only the page that just broke in dogfood, plus the AGENTS.md rule that future-proofs the other 9 affected pages until they're individually swept. The mechanical fan-out across the other 9 is deferred per the user's standing "dogfood first, extrapolate after" rule — but is now tracked as a new sweep candidate in the deferred backlog.

### Method

User flagged from a live Antigravity transcript: the tutor's rendering of the page included prose, the ⚠️ Key Distinction callout, the Three Examples, and the closing question — but the diagram was missing. Grep across `Notes/` confirmed the convention rot is broader than this page (10 affected pages, 1 with an inadequate compensating hook). Three edits: inline the diagram + add 1 positive + 1 negative AGENTS.md rule. No `_figures/agent_loop.txt` deletion — keeping it as the editor-facing source for now; the page is canonical, the .txt is artifact.

### Deferred

- **New deferred sweep #5: `{{INCLUDE _figures/X.txt}}` placeholder rot.** Inline the remaining 9 affected pages and update `_AUTHORING.md` to forbid the placeholder pattern going forward (inline ASCII in fenced blocks is the new convention). Update the deferred-sweeps memory file with this entry.
- Same v0.4.4–v0.4.7 backlog otherwise (hook audit, expected-output truthing, brittle-count, theoretical-precision sweep).

---

## [0.4.7] - 2026-05-28

Phase-0 dogfood fix #7 — closes the agent-vs-LLM precision arc by drawing the **built-in vs custom tool** line that v0.4.6 left implicit. While fact-checking the user's framing of "LLM picks → agent runs," a nuance surfaced: `google_search` is a Gemini **built-in** — the search executes server-side at Google, not inside the agent's Python process. So Example 2 on Module 01's opener (just rewritten in v0.4.6 to say *"the agent runs the search"*) was technically inaccurate for `google_search` specifically. The general pattern is correct and Example 3's `add`/`multiply` demonstrate it correctly; `google_search` is the exception, and the page never named it as such.

### Fixed

- **`Notes/01_Foundations/01_WhatIsAnAgent.md`** — Example 2 reworded to neutral voice (*"the LLM emits a tool-call request for `google_search(...)`, the search runs, the result is fed back into the LLM"*) and followed by a new `⚠️ Built-in vs custom tools` callout naming the distinction: built-ins run server-side at Google's infrastructure; custom `FunctionTool`-wrapped Python tools run in the agent process. The callout explicitly redirects the reader to Example 3 as the canonical "agent runs the tool" case and forward-refs Module 03 for the precise treatment.
- **`Notes/Detours/GeminiPayload.md`** — appended a `⚠️ This round-trip is for FunctionTool (custom Python tools)` callout at the end of section 4. Names which built-ins follow the model-side path (`google_search`, server-side code executor, URL-context retrieval), states that they never surface a `function_call` Part for the agent to dispatch, and notes that the final `Content` carries `grounding_metadata` instead of a `function_response` Part. Frames the shorthand "the LLM picks `google_search(...)`" as fine *if* the reader holds the built-in vs custom distinction in mind.

### Why

The v0.4.5 → v0.4.6 arc tightened the agent-vs-LLM language but used `google_search` as the example of "agent runs the tool" — the one tool in the samples for which that's untrue. Leaving it would silently re-introduce a different conflation (built-in tools vs `FunctionTool`-wrapped Python functions), and a student who later reads any sample using a built-in tool would be confused by the missing `function_call` Part in the event stream. The fix doesn't change the engine-first arc — Example 3 (`add`/`multiply`) is still the canonical case, and Module 03 still owns the full distinction. v0.4.7 just makes sure Example 2 doesn't quietly contradict either of them.

### Method

User flagged the nuance directly after the fact-check: *"yes, let's made this clear. google_search is a model functionality."* Two `Edit`s, one on each affected file. No drawing change needed — the loop diagram is generic (it shows "the agent runs the tool" as the loop's default branch; built-ins are an external optimization the diagram doesn't need to depict).

### Deferred

- Same backlog as v0.4.4–v0.4.6 (hook audit, expected-output truthing, brittle-count, theoretical-precision sweep). No new debt. The theoretical-precision sweep's case gets stronger again: v0.4.5 caught a definition defect, v0.4.6 caught drawing + examples + detour defects, v0.4.7 caught a built-in-tool exception — the pattern of "one foundational concept page tends to harbor several adjacent imprecisions" is now well-attested across three fix versions.

---

## [0.4.6] - 2026-05-28

Phase-0 dogfood fix #6 — completes the agent-vs-LLM precision arc that v0.4.5 started. v0.4.5 fixed the opening definition on `01_WhatIsAnAgent.md`. User then re-read the same page and surfaced two more instances of the same conflation, plus a directive to harden the supporting detour:

1. The ASCII drawing (`_figures/agent_loop.txt`) made the agent invisible — drew only LLM, TOOL, and arrows. The agent (the program holding the loop) was implicit at best and arguably depicted as the LLM at worst. Perfectly contradicted the v0.4.5 definition.
2. Examples 2 and 3 on the page used language like "LLM picks `google_search(...)`, gets results, summarizes" — recreating the conflation in narrative form.
3. The `Detours/GeminiPayload.md` detour briefly mentioned `function_call` and `function_response` Parts in passing (sections 2 and 3), but never showed the *round trip* — agent → LLM (function_call) → agent (runs tool) → agent → LLM (function_response) → text reply. Without that worked example, the precision lesson from Module 01 had nowhere to land at the wire level.

### Fixed

- **`Notes/01_Foundations/_figures/agent_loop.txt`** — full redraw. AGENT is now the outer bordered box containing a pseudo-Python loop (`while True: ... tokens = LLM(...); parsed = parse(...); if parsed is TEXT: return; else: result = tool(parsed.args); continue`). LLM and TOOL are two separate external boxes on the right that the agent invokes via labeled arrows. Includes an explicit comment in the loop body — `# the AGENT runs the tool — not the LLM` — and a closing legend: *"The AGENT is the box: the loop, the history, the parse, the tool execution, the decision to stop. The LLM never runs your tools — it emits a request as tokens; the AGENT parses those tokens and runs the tool."*
- **`Notes/01_Foundations/01_WhatIsAnAgent.md`** — bullets 3 and 4 rewritten: bullet 3 now says *"The LLM returns tokens. The agent parses those tokens as either: a text reply, or a tool-call request — the LLM does not run it; it just emits the request."* Bullet 4: *"the agent looks up the matching Python function, runs it, appends the result..."*. Examples 1, 2, 3 all rewritten to put the agent in the active voice for every tool execution. Example 3 expanded into a numbered three-step list with the alternation `LLM emits → agent runs → agent appends → LLM emits ...` made literal, and a closing sentence: *"Notice the pattern: the LLM only ever emits — text or a tool-call request. The agent does all the running."*
- **`Notes/Detours/GeminiPayload.md`** — inserted a new section 4 (and renumbered sections 4 → 5 and 5 → 6): **"The function-call round trip — what 'the LLM picks a tool' actually means"**. Contents: a five-step exchange (agent → LLM → agent runs tool → agent → LLM); a worked code example assembling the three `Content`s in order (`user_turn`, `model_call` with `function_call` Part, `tool_turn` with `function_response` Part); explicit annotation on step 3 *"The LLM is not involved in this step. At all."*; a multi-tool variant showing the same pattern repeated for "weather in Tokyo and Madrid"; two "burn this in" takeaways (`function_call` is a structured Part, not an invocation; `role='tool'` exists precisely so the model knows the Content is a tool result, not user-typed JSON); cross-reference to Module 01's drawing as *"the wire-level view of the same loop."*

### Why

v0.4.5 fixed the definition; v0.4.6 makes the rest of the surface area match. The user's framing for the sweep was *"this is foundation knowledge we can't get the luxury of getting/teaching wrong"* — and the page-04-of-Module-01 issue would have been exactly that: a corrected paragraph followed immediately by a drawing and examples that contradicted it. The GeminiPayload detour is the natural landing pad for the wire-level proof — without the worked function-call round trip example, the precision lesson stays abstract.

The compounding effect across v0.4.5 + v0.4.6 is what matters: the engine-first arc through Modules 01 → 02 now reads coherently. Module 01 says "the agent is the program that drives the loop"; Module 01's drawing shows that program with the loop inside it; Module 01's examples put the agent in the active voice; the detour proves it at the wire level. When the student hits Module 02 and writes `Runner` + `Session` by hand, the API stops feeling like overhead and starts feeling like the *exact* code the agent box in the drawing was always running.

### Method

User flagged the drawing and Examples 2/3 in two follow-up turns after v0.4.5. Read the drawing + sibling `runtime_timeline.txt` (which was already fine — explicit Runner column, legend "Runner = orchestrator; owns the loop"); confirmed only `agent_loop.txt` needed the redraw. Read the GeminiPayload detour to find the right insertion point for the round-trip section. Four edits across three files (the prose change on Module 01 split into bullets and examples), one full file rewrite (`agent_loop.txt`).

### Deferred

- Same v0.4.4/v0.4.5 deferred sweeps (hook audit, expected-output truthing, brittle-count, theoretical-precision audit on remaining Foundation pages). v0.4.6 doesn't add new debt; the theoretical-precision sweep just got more justified.
- Module 02's page-by-page review for the same conflation pattern — when the student/tutor gets there, it'll surface; not preempting per user's "dogfood first, extrapolate after" rule.

---

## [0.4.5] - 2026-05-28

Phase-0 dogfood fix #5 — single-page content-precision fix on the very first page of Module 01. User flagged the opening definition as conceptually wrong, not just imprecise.

### Fixed

- **`Notes/01_Foundations/01_WhatIsAnAgent.md`** — replaced the opening definition. Was: *"An agent is an LLM that has been given a list of tools and the ability to decide, on each turn, whether to call one of them or just reply."* Now: *"An agent is a piece of software that drives an LLM in a loop ... The LLM itself is stateless and tool-less; it just emits tokens. The agent is the program that interprets those tokens as actions and keeps the loop running."* Added a forward-reference to Module 02 (`Runner` + `Session` by hand): "you are building exactly that program."

### Why

The original wording conflated the LLM (a stateless token-emitter) with the agent (the software that orchestrates around it). It's the kind of definition that reads fine in isolation but breaks Module 02 in advance: if the student internalizes "agent = LLM," then `Runner` and `Session` feel like inexplicable overhead rather than the obvious mechanism for "drive a loop and hold state across turns." Engine-first pedagogy requires the right mental model at the *start*, because everything that's built by hand later assumes it.

### Method

User flagged the line during their own re-read of Module 01 (pre-dogfood, while reviewing the page text). One `Edit`, two sentences added.

### Deferred

- Audit the rest of Module 01 (and Module 02 prose) for similar agent-vs-LLM conflations. Held until the user dogfoods Module 01 — same rationale as the v0.4.4 deferred sweeps.

---

## [0.4.4] - 2026-05-28

Phase-0 dogfood fix #4 — smaller scope than v0.4.1–v0.4.3, mostly content correctness. Fourth live Antigravity session ran cleanly through pages 03 → 04 → 05 → KC → drill of Module 00. The engine-first + secrets-handling contracts held (every command was student-typed, no `.env` written by the tutor, KCs asked one-at-a-time, end-of-session `PROGRESS.md` + `student_profile.md` updates landed). Two real defects + one soft observation surfaced:

1. **Page 04's verification command predicted the wrong output.** The page said `python -c "print(type(root_agent).__name__, ...)"` would print `Agent Facts gemini-flash-latest`. It actually prints `LlmAgent Facts gemini-flash-latest` — because `Agent` is a name alias (re-export), not a subclass, so `type(...).__name__` returns the real class name. The tutor papered over the mismatch on the fly, but the page itself was wrong, and the "huh, why `LlmAgent`?" moment is actually a *better* teaching beat than the page's original prediction.

2. **Tutor answered the drill's probe question for the student.** The mini-drill asked the student to swap the agent's personality AND to articulate "what's the difference between editing `instruction=` vs `model=`?" The student returned the (excellent grumpy-IT-picanha) output but skipped the probe. The tutor's wrap-up *answered the probe itself* instead of re-prompting. Violates the existing "Do not read the answer to the student" rule, but only implicitly — the rule didn't name drill probes specifically, and the tutor treated the probe as rhetorical color rather than a graded item.

3. **Soft:** page 03 said "60+ samples" but the actual `wc -l` reality is ~75. Tutor noticed and used 75; no harm, but the page would age better with a non-pinned framing.

### Fixed

- **`Notes/00_Setup/04_DissectingSample.md`** — corrected expected output from `Agent Facts gemini-flash-latest` to `LlmAgent Facts gemini-flash-latest`, and rewrote the surrounding prose to make the alias-vs-class distinction the teaching beat: *"Note the class name: `LlmAgent`, not `Agent`. That's the lesson. The import `from google.adk.agents import Agent` rebinds the name — `Agent` *is* `LlmAgent`, no subclass involved. `type(...).__name__` always returns the real class."* Added a `🤖 Tutor` hook covering the failure mode (if the student sees `Agent`, suspect a stale `__pycache__` or a pre-2.0 ADK).
- **`Notes/00_Setup/03_RepoTour.md`** — changed "roughly 60+ samples" to "somewhere in the **70s** (the catalog grew from ~60 at ADK 1.x to ~75 at 2.0, and Google keeps adding). The exact number isn't load-bearing — the point is 'this textbook is large.'" Added a `🤖 Tutor` hook for the "way off" failure mode (wrong fork / stale tag, verify with `git log -1`).
- **`AGENTS.md`** — added a new negative rule to `❌ What NOT to do`: *"Do not answer drill probe questions on the student's behalf."* Calls out that mini-drills often pair a coding task with a probe question, that re-prompting (not auto-answering) is the contract, and gives a verbatim re-prompt the tutor can use: *"Great output — but you still owe me the probe answer. In your own words: what's the actual difference between editing `instruction=` and `model=`?"*

### Why

The page-04 mismatch is the kind of defect that erodes student trust silently — the tutor smoothed it over once, but next session a different tutor or a stricter student will flag it as "the course is wrong about its own output." Better to fix the page so the truth lands as the lesson rather than as a workaround. The probe-answering defect is the more interesting one: it's an *adjacent* failure mode to v0.4.3 (tutor optimizes for momentum, fills perceived gaps). v0.4.3 fixed the setup-commands and secrets versions; v0.4.4 closes the drill-probe version. Together they shape a stable rule: *if the page asks the student a question, the tutor's job is to elicit and grade, never to supply.*

### Method

Read the transcript end-to-end, mapped each tutor turn against the page text and AGENTS.md contract, isolated 2 page-content defects and 1 contract-coverage defect. Three `Edit`s across three files. No new tasks or sweeps deferred — the fixes are surgical and the broader hook-audit deferred from v0.4.3 is still the right next sweep, not anything specific to this fix.

### Deferred

- Still the v0.4.3 deferred items (broader `Have the student run` hook audit; student-facing README note; automated bash-block-without-hook grep). v0.4.4 doesn't add new debt.

---

## [0.4.3] - 2026-05-27

Phase-0 dogfood fix #3 — the deepest defect so far. v0.4.2 fixed *where* files go; v0.4.3 fixes *who types the commands to put them there*. Third live Antigravity session (same `~/_demos/adk-course/`): with the workspace layout now authoritative, the tutor ran every setup command itself — `git clone` (background), `python3 -m venv`, `pip install google-adk`, even started preparing to ask the student for their API key so it could "write the `.env` for you." Setup completed in seconds. Engine-first muscle memory completed in zero seconds.

Root cause: `AGENTS.md` had a vague engine-first preamble ("the student types low-level primitives by hand before trusting any abstraction") and a "Do not silently fix the student's code" anti-rule — but no explicit anti-rule against running setup/install/clone commands on the student's behalf. The tutor's optimize-for-momentum bias filled the gap. Worst manifestation: a security-relevant ask ("share your API key so I can write the `.env`") that the contract didn't forbid.

### Fixed

- **`AGENTS.md`** — added a new positive rule and two new negative rules:
  - **Positive (in `🧠 During a lesson`)** — new "Hands on keys means hands on the STUDENT's keys" subsection (~25 lines): the student types every shell command, the tutor reads output and verifies; setup/install/clone IS the lesson; explicit 5-step "your role at command boundaries" sequence (present → wait → ask for output → interpret → repeat); narrow exceptions enumerated (verifying claimed work, diagnosing reported errors) with "even here, prefer asking them to run it."
  - **Negative #1 (in `❌ What NOT to do`)** — "Do not execute shell commands the student should be typing." Names the specific commands (`git clone`, `python3 -m venv`, `source .venv/bin/activate`, `pip install`, `cat > .env`, `cd`, `ls`, `adk run`), names the specific failure mode ("running these on the student's behalf via `Bash` foreground OR background is a contract violation"), and gives the signal-to-stop ("if you find yourself reaching for `Bash` to 'move things along' during setup or install — stop. That speed is the lesson's cost.").
  - **Negative #2 (in `❌ What NOT to do`)** — "Never handle secrets on the student's behalf." Forbids: asking for API keys, tokens, passwords, or `.env` contents; offering to "write the `.env` for you"; phrases like "share your key so I can verify." Frames it as both a security rule (transcripts get logged/screenshotted/replayed in unpredictable ways) and a pedagogy rule (creating the `.env` is part of the setup lesson).
- **`Notes/00_Setup/01_InstallingADK.md`** — restructured the clone block AND the venv/install block as `> 🛠 **Have the student run** (in their terminal — not yours):` callouts. The bash commands now live INSIDE the callout, so the tutor cannot miss the directive. Added explicit "ask the student to paste output back" steps and explicit "Do not run `git clone` yourself" / "Do not run any of these yourself" lines tied to the AGENTS.md rule for cross-reference.
- **`Notes/00_Setup/02_HelloFunFacts.md`** — added a "🤖 Tutor — secrets handling (HARD RULES)" hook above the existing `.env` location hook, with three numbered rules: never ask for the key, never offer to write the `.env`, the partial-cat verification (`cat ... | cut -c1-25`) is deliberately designed to confirm file existence without exposing the full secret in the transcript.

### Why

The user named the problem directly: *"all seems correct, but the Practical Python philosophy kinda says/believes the student should do the work (many times, typing), right?"* — and the answer is firmly yes, with both pedagogy and security implications. The engine-first model is the differentiator of this course; if the tutor collapses it into a one-shot automated install, the course produces a working environment without producing the developer who can rebuild it. The course can't fix that in retrospect; it has to forbid the collapse upfront.

The secondary lesson, accumulated across v0.4.1 → v0.4.2 → v0.4.3: the AI tutor's default optimization is "make the student successful right now." That bias is mostly good, but at three specific edges it's destructive: (1) running commands instead of teaching them (this fix), (2) handling secrets instead of teaching secret-handling (this fix), (3) ad-libbing locations instead of citing the spec (v0.4.1–v0.4.2). All three need explicit forbidden-phrase-level callouts in `AGENTS.md` and on the pages where the temptation peaks, because soft "don't" language loses to hard "I'll help you finish" reflexes.

### Method

Read the live transcript, identified three distinct failures (tutor ran `git clone` in background; tutor ran `python3 -m venv` and `pip install` directly; tutor asked "could you share your Gemini API key with me so I can write the `.env` file for you?"), traced each to a missing rule in `AGENTS.md`, patched with 4 `Edit`s across 3 files: 1 positive + 2 negative rules in `AGENTS.md`, restructured 2 command blocks on page 01 as student-runs hooks, added a secrets-handling hook on page 02.

### Deferred

- A `> 🛠 **Have the student run**` hook audit across every other page that shows a bash command (likely all Foundation Track pages and most Integration/Runtime Track pages). The current fix patches the 2 most-violated pages; the rest will surface in subsequent dogfood sessions or in a deliberate sweep.
- A short student-facing note in `README.md` explaining "the tutor types nothing; you do" so the student knows what to expect and can call out violations themselves. Postponed because README scope is broader than this fix.
- An automated check (`grep` script) that finds bash blocks without preceding tutor hooks. Worth building, but only after the manual sweep determines the right shape of the hook.

---

## [0.4.2] - 2026-05-27

Phase-0 dogfood fix #2 — v0.4.1 didn't go far enough. Second live tutor session (Antigravity, same `~/_demos/adk-course/` checkout) STILL produced "Let's create a `.env` file in the root of your workspace" — directly contradicting page 01's "don't create one yet" text. Two root causes:

1. **Tutor skipped my v0.4.1 workspace-section on page 01.** It auto-detected the `.venv` existed and shortcut past the prose that explained the layout. The workspace spec needs to be where the tutor cannot skip it — i.e., on page 00, which the tutor reads first as the module entry point.
2. **Tutor improvised against an explicit "don't" instruction.** The v0.4.1 hook said "Don't create one yet; it'd have no agent to attach to" — soft language that the tutor's optimize-for-momentum bias rolled over. Stronger hooks needed.

### Fixed

- **`Notes/00_Setup/00_Overview.md`** — added a **"🗺 Workspace layout — the authoritative answer"** section between Prereqs and Estimated time, ~70 lines of source-of-truth content the tutor cannot shortcut past. Contents:
  - Full ASCII tree of `<workspace>/` showing every directory the student will touch in Module 00 (and forward-references for Module 02+), with read-only / writable annotations and explicit `.env` locations called out with 🟢 markers.
  - **Three rules** that cover every "where?" question for the rest of the course: (1) course pages read-only except `Work/`; (2) samples read-only; (3) `.env` lives next to the agent module.
  - **Quick-reference table** mapping every "thing" the student creates (venv, cloned repos, `.env` for fun-facts, `.env` for student's own agents, hand-written exercise code, notes) to its canonical path.
  - **Mandatory tutor hook** at the end of the section: *"walk the student through this layout diagram and the three rules BEFORE page 01. Do not improvise alternate locations. If a later page seems to contradict this layout, the page is wrong — flag it, do not paper over it."*
- **`Notes/00_Setup/01_InstallingADK.md`** — replaced the soft "Don't create one yet" sentence with a hard tutor hook: *"DO NOT have the student create a `.env` on this page under any circumstances ... Any instruction phrased as 'create a `.env` in your workspace root,' 'create a `.env` in adk-course/,' or 'create a `.env` here' is wrong — `load_dotenv()` would not find it, the agent would fail to authenticate, and the student would have a broken setup blamed on the course."* Section header relabeled from `## 🧠 Where your API key will live` to `## 🧠 Where your API key will live (preview — do nothing yet)` so even a tutor skimming headers gets the signal. Added the full canonical path inline.
- **`Notes/00_Setup/02_HelloFunFacts.md`** — restructured the `.env` block: full canonical path inline (no path-arithmetic), an explicit `ls -la` + `cat` verification step, and a tutor hook with **four numbered location rules** the tutor can repeat verbatim if the student asks (covering: where the file goes, why dotenv looks there, what to do if it was created in the wrong place, cross-reference back to the 00_Overview layout diagram).

### Why

The user explicitly asked: *"I am looking for an authoritative answer on where things should be created!"* The defect was that v0.4.1's answer lived inside `01_InstallingADK.md` — buried in a section the tutor could and did skip. The authoritative answer must live where the tutor cannot shortcut past it: the Overview, which is the first thing read at module entry. The new section is structured as a reference (diagram + rules + table) rather than a narrative, so it functions as a citation target for every downstream page.

The secondary lesson: hooks at the level of "Don't do X" lose to tutor optimization. Hooks at the level of "DO NOT do X. If you find yourself wanting to do X, that's a signal Y" survive. The course is teaching the tutor as much as it's teaching the student.

### Method

Read live transcript from second Antigravity session, traced where the tutor's `.env`-location ad-lib came from (it was generating from prior-fix language it skimmed past), restructured: (a) elevate canonical layout to 00_Overview where it's unmissable, (b) harden the page-01 anti-improvisation hook with explicit forbidden phrases the tutor might generate, (c) restructure page-02 around verification + repeatable rules. Five `Edit`s total across 3 files.

### Deferred

- A `_figures/workspace_layout.txt` asset mirroring the 00_Overview tree — postponed because the inline version is already authoritative and a duplicate asset risks drift. If subsequent modules need to forward-reference the layout from a different angle, materialize it then.
- Auditing other Foundation Track modules (`03_Tools`, `04_SessionsState`, `1A_AppAndRunner`) for path-assumption defects. The same class of bug may exist where they introduce student-written agents in `Work/`. Verify-and-fix when those modules surface in dogfood.

---

## [0.4.1] - 2026-05-27

Phase-0 dogfood fix #1 — workspace layout was implicit. First live tutor session (Antigravity, running against a fresh `~/_demos/adk-course/` checkout without sibling `adk-samples`) had to ad-lib `git clone adk-samples` mid-lesson and confused the student with conflicting `.env` instructions across pages 01 and 02. Root cause: pages 00–02 assumed `~/study/adk-course/`, `~/study/adk-samples/`, `~/study/adk-python/` were all present, but the course never told the student that or walked them through the clone. Fix is surgical (3 pages, no structural change).

### Fixed

- **`Notes/00_Setup/01_InstallingADK.md`** — added an opening "Pick a workspace, clone the two companion repos" section that introduces the `<workspace>/` ↔ `~/study/` convention with an `ADK_WORKSPACE` env var, walks the clone of `adk-samples` and `adk-python` as siblings, and includes a tutor hook telling the AI to adapt paths if the student's machine layout differs (the *layout* is load-bearing; the *parent path* is not). Replaced the orphan `.env` creation block (which had no destination path) with a "your `.env` will live next to the agent module, on the next page" pointer — eliminates the dual-`.env` confusion that surfaced in the dogfood transcript.
- **`Notes/00_Setup/02_HelloFunFacts.md`** — removed the redundant `git clone adk-samples` step (page 01 now handles it) and the "if you already cloned it, skip" branch. Replaced with a direct `cd "$ADK_WORKSPACE/adk-samples/python/agents/fun-facts"`. Tightened the `.env`-creation block to explicitly name "alongside `agent.py`" and added a tutor hook for the common workspace-root vs agent-dir confusion. Added a `source "$ADK_WORKSPACE/.venv/bin/activate"` reminder before `adk run` because the venv lives in workspace root while the command is run from the sample dir — easy to forget.
- **`Notes/00_Setup/00_Overview.md`** — added a fourth Prereq line: "A workspace directory decided." Names the 3-sibling layout convention upfront so the student arrives at page 01 knowing what's coming.

### Why

The defect was uncovered by the first real Phase-0 dogfood run (Antigravity teaching Module 00 to Carlos on a fresh `~/_demos/` checkout). The tutor's behavior was correct *given the source* — it noticed the `adk-samples` was missing and improvised cloning instructions — but the AGENTS.md contract explicitly forbids ad-libbing structure. This means the page, not the tutor, was the bug. The fix preserves the implicit `~/study/` canonical layout for the rest of the course (the `repo_tour.txt` figure and Module 19 cross-references all still resolve) while making the layout an explicit step the student walks through rather than an unstated assumption.

### Method

Read the live transcript, traced the tutor's improvisations back to the source pages, identified two coupled defects (missing clone instructions + orphan `.env` block on page 01), patched with 4 surgical `Edit`s. No new pages, no structural split. Plan: not separately authored — the fix is small enough that the CHANGELOG entry IS the plan.

### Deferred

- A broader pass on the `<workspace>` convention to other Foundation Track modules (`03_Tools`, `04_SessionsState`, `1A_AppAndRunner`, `2A_AgentConfig`) — they may also hardcode `~/study/`-style paths without the explicit setup. Verify-and-fix when those modules surface in dogfood.
- The `_figures/repo_tour.txt` figure still shows `~/study/` as the literal parent. Leave for now — the page 01 fix introduces `<workspace>/` as the abstract concept, and the figure remains a valid concrete example. Revisit if dogfood shows confusion.

---

## [0.4.0] - 2026-05-27

Module 12 (Code Execution) — content-depth pass. Net new ≈ 1100 lines across 11 lesson pages, 2 YAML files, 1 AGENTS.md, and 2 figures, plus a structural split. Backlog-closer of the type 0.3.13's "next natural work is content depth" line called out: this is the first content-depth pass, executed against the highest-value module that was running thin (504 lines pre-pass for 6 executors + a sample dissection — page 02 alone needed 80 more lines to land the "in-process is not a sandbox" point with primary sources). Plan file at `.claude/plans/module-12-code-execution-depth-pass.md`.

### Added

**New page — `02A_SandboxBypassClasses.md` (108 lines)**
- Executor-agnostic threat model: four bypass classes (filesystem isolation, environment leakage, network egress, privilege escalation) with per-executor verdict (NO/YES/PART./DEP./FULL/N/A) and source-anchor citations. Lets pages 03-06 forward-link instead of re-stating.
- Embedded the matrix from `_figures/bypass_matrix.txt` inline; explains the "DEPENDS as TODO not verdict" framing for Container/GKE rows.
- Prompt-injection multiplier section — connects sandbox-class threats to the upstream prompt-injection story in [[16_ProductionSecurity/02_PromptInjectionDefense]].

**New page — `05A_GkeCodeExecutor.md` (126 lines, split from `05_ContainerAndGke.md`)**
- Hardened pod spec table direct from `gke_code_executor.py:_create_job_manifest` (`:265-336`): `run_as_non_root=True`, `run_as_user=1001`, `allow_privilege_escalation=False`, `read_only_root_filesystem=True`, `capabilities=drop(["ALL"])`, `runtime_class_name="gvisor"`, plus job-level `backoff_limit=0` + `ttl_seconds_after_finished=600`.
- `executor_type="job"` vs `"sandbox"` discussion with `_check_sandbox_dependency` reference at `:166-175`.
- Gotcha: `service_account=` is NOT a kwarg (raises Pydantic ValidationError); identity binding happens at the cluster level via Workload Identity (gcloud + kubectl annotate, snippet included).

**New figures — `_figures/code_exec_event_flow.txt` (52 lines) and `_figures/bypass_matrix.txt` (26 lines)**
- Event-flow ASCII anchored to `flows/llm_flows/_code_execution.py:151-169` (`_CodeExecutionResponseProcessor`), `code_execution_utils.py:113-172` (extraction), `:189-221` (result envelope), `_code_execution.py:435-470` (`_post_process_code_execution_result`). Closing paragraph distinguishes BuiltIn (request-side) from response-side executors.
- Bypass matrix as a standalone figure for cross-page reference from 02A, 03, 04, 05, 05A, 06, 08.

### Changed

**`00_Overview.md` (59→75)** — "Why this module gets extra depth" paragraph; "The event shape, in one paragraph" sketch; "Where this slots into the runtime" callout; expanded module map with `02A` and `05A` rows. Frontmatter: `prereqs: [03_Tools/01, 04_SessionsState/02]`, expanded `concepts:` list.

**`01_WhyCodeExecution.md` (76→114)** — strengthened the ASCII trace with actual Part field names (`ExecutableCode(language='PYTHON', code=...)`, `CodeExecutionResult(outcome='OUTCOME_OK', output='Code execution result:\n…')`) and source refs to `code_execution_utils.py:184-187, :202-205, :218-221`. Added "The cost lens" paragraph and a tool-vs-code-exec triage ASCII flowchart.

**`02_UnsafeLocalCodeExecutor.md` (76→106)** — added "What this executor actually does" mechanics block with five source-anchored bullets: `_execute_in_process` at `:37-48`, `_prepare_globals` at `:51-54`, multiprocessing `spawn` at `:88-107` ("spawn is not a sandbox"), frozen Field ValueError at `:69-74`. Added "Sandbox-bypass classes (executor-agnostic)" intro forward-linking to 02A. **Fixed broken cross-ref**: callout previously pointed at non-existent `16_ProductionSecurity/02_CodeExecSafety.md`; repointed to `[[16_ProductionSecurity/02_PromptInjectionDefense]]` and `[[16_ProductionSecurity/05_GuardrailsCookbook]] Recipe 6`. Added third tutor question on `stateful=True` ValueError.

**`03_BuiltInCodeExecutor.md` (67→101)** — added "Mechanics: a request-side mutation, not a response-side handler" (with `execute_code` no-op at `:36-42` and `process_llm_request` mutating `llm_request.config.tools` at `:44-57`); "Model compatibility" with `is_gemini_eap_or_2_or_above` check; "What this means for tracing" calling out absence of `executable_code` parts on YOUR wire; trade-off table row for "Where on the wire"; bypass posture forward-link to 02A.

**`04_VertexAiCodeExecutor.md` (69→116)** — "Under the hood" block with three source-anchored bullets: extension load-or-create at `:88-104` with env-var side effect at `:101-103`, `_IMPORTED_LIBRARIES` at `:36-85`, `_execute_code_interpreter` at `:200-227`. "Stateful execution: what it actually costs" with illustrative numbers (Turn 1 ≈ 480 output tokens / ~400 context, Turn 5 ≈ 2000 extra input tokens, Turn 20 ≈ 10000 — flagged as illustrative, verify against price card). "`optimize_data_file=True` mechanics" with text/csv-only constraint and `processed_input_files` cache reference (`code_executor_context.py:78-96`). Bypass posture forward-link.

**`05_ContainerCodeExecutor.md` (NEW file, 92 lines; split from `05_ContainerAndGke.md`)** — "Mechanics: long-lived container, exec-per-snippet" with three bullets including the critical "**state leaks between executions inside one `ContainerCodeExecutor`**" finding (writable `/tmp` and background processes persist across `exec_run` calls even though Python globals reset). Bypass posture explains why every Container cell reads DEPENDS. Two gotchas (`--privileged` collapse, state-leak). Tutor question on cross-execution `nc -l 4444` → `/proc/net/tcp` example.

**`06_AgentEngineSandbox.md` (62→113)** — "Mechanics: three init modes + per-session sandboxes" surfacing the hidden auto-create cost (`:79-103`) and the per-session sandbox lifecycle (`:131-173`) backed by `state['sandbox_name']`. Names the **14-day kernel state-loss window** from the in-line comment at `:163-170` — separate from the sandbox resource's 1-year TTL — as a product surface, not just an infra detail. "Output handling" section explains the JSON/file mime-type split at `:196-227`. Comparison table with `VertexAiCodeExecutor` includes sandbox-per-what / auto-create-posture / state-loss-boundary rows.

**`07_DissectingSample.md` (104→233)** — re-structured as a file-by-file walk: `analytics/agent.py` (32 lines), `analytics/prompts.py:40-79` (statefulness + imports + output-protocol contract), `tools.py:59-126` (`call_analytics_agent` wrapper using `AgentTool` + state-passing), `data_science/agent.py:177-204` (root constructor). Made the **prompt-executor coupling** explicit: `stateful=True` ↔ "variables stay in the environment"; `_IMPORTED_LIBRARIES` constant ↔ "ALREADY imported" block in prompt. Added wire-trace ASCII for one user→answer execution (4 LLM calls, 2 tool invocations, 1 sandbox round trip). Added migration table covering the same workload across all 5 sandbox-class executors.

**`08_InProduction.md` (75→106)** — recast from "five non-negotiables" prose to Risk/Mitigation/Source 10-item structure. New items: bypass-matrix completion as launch gate (item 2), explicit `timeout_seconds=` discipline with the retry-math interaction (item 3), `error_retry_attempts` pinning (item 4), audit-logging via `_CODE_EXECUTION_RESULTS_KEY` from `code_executor_context.py:167-191` (item 6), prompt-executor coupling version-control (item 7), `stateful=True` context-bloat cost with turns-per-session heuristic (item 8), egress + input filtering (item 9). Launch-gate checklist expanded from 6 to 10 items.

**`09_KnowledgeCheck.yml` (37→57; 7→11 questions)** — q3 updated to test request-side-vs-response-side distinction (BuiltIn vs Vertex); 4 new questions: q8 (four bypass classes with defense + anti-defense pairs), q9 (retry math: `error_retry_attempts=2` × `timeout_seconds=60` = 3 min worst case + interactive-vs-batch tradeoff), q10 (`stateful=True` cost asymmetry + turns-per-session heuristic), q11 (prompt-executor coupling failure mode in the data-science sample).

**`10_MiniDrill.yml` (58→121; estimated_minutes 45→75)** — added Step 2 event-stream inspection (print `executable_code` / `code_execution_result` parts), Step 4 sandbox-bypass demonstration using safer enumeration (`os.uname()` / `sys.path` / `getpid()` — chosen deliberately to prove the breach without reading anything sensitive; tutor_notes explicitly redirects escalation attempts), Step 5 stateful bonus reusing `x = factorial(20)` across turns, Step 6 "disable and forget UnsafeLocal." `tutor_notes` expanded with adaptive moves for each step.

**`AGENTS.md` (39→55)** — added pacing-trap note on page 07's 200+ line dissection (two-sitting consumption); new constructor-vs-first-call error catalog (AgentEngineSandbox lazy create, GkeCodeExecutor `service_account=` ValidationError, Vertex frozen-Field path); page-02A reading note ("hold the four classes in your head before pages 03-06 make sense"); Step-4 safety redirect for the bypass drill.

### Deleted

- `Notes/12_CodeExecution/05_ContainerAndGke.md` — split into `05_ContainerCodeExecutor.md` + `05A_GkeCodeExecutor.md`. External cross-refs unaffected: nothing in the repo linked to the deleted file (verified via grep against the deleted-file path).

### Fixed

- `Contents.md:331` — stale link to deleted `05_ContainerAndGke.md`; replaced with two entries (05 + 05A) and inserted the new `02A` row between 02 and 03.
- `02_UnsafeLocalCodeExecutor.md` (pre-existing): callout pointed at non-existent `16_ProductionSecurity/02_CodeExecSafety.md`; repointed to the two actual targets (`02_PromptInjectionDefense` + `05_GuardrailsCookbook` Recipe 6). The wrong link had been present since v0.3.4 but was only surfaced when the depth pass re-read the page.

### Method

- **Source verification first**: ran a verification pass against `adk-python/src/google/adk/code_executors/*.py` and `adk-python/src/google/adk/flows/llm_flows/_code_execution.py` before any prose change, confirming every line ref the plan cited is still accurate at the cited offset (`_create_job_manifest` `:265-336`, security context `:281-307`, `runtime_class_name="gvisor"` `:307`, `_execute_in_process` `:37-48`, `error_retry_attempts: int = 2` `:59`, etc.).
- **Source verification of the sample**: re-read `adk-samples/python/agents/data-science/data_science/{agent.py,tools.py,sub_agents/analytics/{agent.py,prompts.py}}` end-to-end for the page-07 dissection; every line-ref in the new prose is anchored to the actual file (e.g., `tools.py:99-100` for the state read, `:104-118` for the question-with-data string, `:120-124` for the `AgentTool.run_async` call).
- **No invented security claims**: every defense and every bypass-class verdict in 02A and 02 is sourced either from a kwarg/field on a real ADK class or from a documented behavior. The few illustrative numbers (page 04's stateful cost example) are explicitly labeled "illustrative, verify against your model's price card."
- **Re-ran the v0.3.13 audit toolkit** post-pass:
  - `audit_yaml.py`: 0 schema issues; module 12's 2 YAML files parse cleanly.
  - `audit_anchors.py`: 0 broken across the repo (47/47 resolve; module 12's new anchors all match GitHub slugger).
  - `audit_figures.py`: 0 orphan figures on real content; the 2 new figures (`code_exec_event_flow.txt`, `bypass_matrix.txt`) are referenced from multiple module pages.
  - Custom check: `grep -rn "12_CodeExecution" --include="*.md"` outside the module — confirmed every external cross-ref still resolves (13_Plugins/00_Overview, 16_ProductionSecurity/{05,09,10}, 99_Capstone/00_Overview).

### Why

- User: "let's go with your recommended approaches for everything." — single forward-going approval of all six recommendations from the planning thread (page-02 single-page, page-05 split, safer bypass demo, illustrative cost numbers, broken-cross-ref repoint to `PromptInjectionDefense` + `GuardrailsCookbook` Recipe 6, defer SandboxIsolationPrimitives detour).
- v0.3.13's CHANGELOG explicitly named content depth as the next natural work after the dogfood backlog closed. Module 12 was the highest-leverage choice: 504 pre-pass lines for the *security-most-load-bearing* module in the course, with page 02 (UnsafeLocal) the canonical "if the student doesn't internalize this they'll ship UnsafeLocal in prod" page running 76 lines without naming the multiprocessing-spawn-is-not-a-sandbox fact from the actual source.
- Minor version bump (0.3.x → 0.4.0): the cadence on 0.3.x has been patch-bumping (dogfood waves, audit additions, small fixes). A ~1100-line content addition spanning the structural split of a page, two new pages, and a new YAML question class is the largest single content addition in the course's history — warrants the minor bump.

### Deferred

- `Notes/Detours/SandboxIsolationPrimitives.md` — namespaces / cgroups / seccomp / gVisor primer. Useful for a student who wants to understand WHY a hardened pod spec resists CVE-class escapes. Not blocking module completion; deferred to a future detour pass when student feedback shows the page-02A treatment isn't enough.
- Module 11 (Memory) and Module 16 (ProductionSecurity) cross-link audit — both modules forward-link into 12, but neither was re-read end-to-end in this pass. If a future depth pass on 11 or 16 surfaces structural changes that affect the forward-links, fix at that time.
- A "v0.4.1" companion pass to add a sample for `AgentEngineSandboxCodeExecutor` — currently page 06 references the `memory-bank` sample for the Agent Engine deploy shape, but `adk-samples` doesn't have a code-execution-specific Agent Engine sample to dissect. Wait for the canonical sample to exist rather than fabricating one.

---

## [0.3.13] - 2026-05-27

Dogfood Wave 10 — three independent defect classes the v0.3.12 closure missed, all surfaced by widening the auditor toolkit beyond links. Built three new programmatic audits (anchor-resolution, YAML-schema, orphan-figure) and ran them against the whole course. 56 fixes across 14 files; 0 schema issues remaining; 47/47 anchors resolve; 0 orphan figures on real content. Wave 10 closes the dogfood backlog completely — every audit class the toolkit can express is now green.

### Fixed

**YAML parse failures (2 files)**
- `Notes/10C_BigQueryAgents/09_MiniDrill.yml:45` — `"rejected" OR "REJECTED"` parsed as invalid YAML (quoted scalar followed by bare text). Collapsed to single value `"rejected"` with a comment noting the agent is expected to canonicalise.
- `Notes/23_FrontendIntegration/13_KnowledgeCheck.yml:41` — bare `>10MB` in a flow-sequence context triggered the folded-scalar parser. Quoted as `">10MB"`.

**Broken anchor links (46 fixes across 8 files)**
- 37 via `/tmp/fix_anchors.py` — regex `r'(\]\([^)]*?#)-(?=[a-z])'` catching the `#-letter` artifact pattern. Earlier waves had stripped emoji prefixes from headings (`### 🚀 In Production` → slug `in-production`) but left cross-refs pointing at `#-in-production` with a leading hyphen the slug algorithm doesn't produce.
- 4 real anchor mismatches discovered during script verification:
  - `21_AdkApiSurface/10_InProduction.md:27` — dropped non-existent `#in-production` from `00_Overview.md` link.
  - `3A_ProjectStructure/10_InProduction.md:33` — dropped non-existent `#in-production` from `02_MinimalLayout.md` link.
  - `3A_ProjectStructure/10_InProduction.md:95` — repointed to `#the-shape-that-works-for-both` (the actual heading slug).
  - `22_DeploymentModels/11_InProduction.md:26` — repointed `#the-decision-tree` → `#a-decision-flowchart` (the actual heading text).
- 5 double-hyphen anchors driven by GitHub's slug algorithm: em-dash (`—`) is punctuation, stripped; surrounding spaces collapse to ONE space → ONE hyphen. So `## Identity binding — the only critical security note` slugs to `identity-binding-the-only-critical-security-note`, NOT `identity-binding--the-only-...`. Fixed at `3A_ProjectStructure/10_InProduction.md:{45,64,88}`, `22_DeploymentModels/11_InProduction.md:32`, `4B_HumanInTheLoop/12_InProduction.md:57`.

**Orphan figures wired into prose (3 files)**
- `Notes/10C_BigQueryAgents/02_NL2SQLPattern.md` — linked `_figures/nl2sql_flow.txt` (NL2SQL agent flow with cost-guard `before_tool_callback`).
- `Notes/4B_HumanInTheLoop/02_RequestConfirmation.md` — linked `_figures/hitl_lifecycle.txt` (pause→approval→resume lifecycle timeline).
- `Notes/2A_AgentConfig/06_YamlVsPythonTradeoffs.md` — linked `_figures/yaml_vs_python.txt` (side-by-side YAML/Python equivalence + capability matrix). Used as a "do I need to drop into Python here?" decision aid.

**MiniDrill schema completion — `solution_pointer` field (7 files)**
The YAML schema audit required every `exercise:` block to declare a `solution_pointer` (even when null) so the AI tutor can disambiguate "this drill is intentionally peek-proof" from "this drill is missing a pointer by accident." Added the field — set to `null` with an inline comment — to:
- `04A_ArtifactsHeavyData/13_MiniDrill.yml` (folded existing free-text comment into the canonical field)
- `3A_ProjectStructure/12_MiniDrill.yml` (folded existing free-text comment into the canonical field)
- `21_AdkApiSurface/12_MiniDrill.yml` (uncommented the placeholder line; promoted to real field)
- `1A_AppAndRunner/11_MiniDrill.yml`, `2A_AgentConfig/11_MiniDrill.yml`, `23_FrontendIntegration/14_MiniDrill.yml`, `24_ChannelIntegrations/13_MiniDrill.yml` (new stub)

### Method
- `/tmp/audit_yaml.py` — `pyyaml`-based schema validator over all `*KnowledgeCheck.yml` and `*MiniDrill.yml` files. Verifies required fields (`id`, `prompt`, `verification`, `solution_pointer`, `grading_rubric`, etc.); reports parse errors with line numbers. Bonus stale-pattern scan for known pre-2.0 idioms.
- `/tmp/audit_anchors.py` — link-audit's anchor variant: for every `[text](page.md#anchor)` reference, walk `page.md`'s headings, slugify each per GitHub's algorithm (lowercase → strip punctuation → whitespace-collapse → space-to-hyphen), check the anchor resolves.
- `/tmp/audit_figures.py` — bidirectional: for every `_figures/*.txt` on disk, find at least one referencing page in the same module; for every figure reference, confirm the file exists.
- `/tmp/fix_anchors.py` — assertion-checked applier; regex tightened to `(\]\([^)]*?#)-(?=[a-z])` to avoid matching legitimate hyphens inside slugs.
- Anchor algorithm gotcha caught mid-wave: I initially treated double-hyphen anchors (`#foo--bar`) as correct and the audit as buggy. Re-checked GitHub's slugifier: whitespace-runs collapse to ONE space *before* the space-to-hyphen pass, so even an em-dash surrounded by spaces (` — `) produces only ONE hyphen in the slug. Updated the 5 sources rather than the audit.
- Re-ran each audit post-fix: schema 0 issues, anchors 47/47 resolve, figures 0 dangling on real content (1 expected hit on `_AUTHORING.md` referencing `_figures/.gitkeep` — template placeholder, not a real bug).

### Why
- User: "let's cotinue refiniing, if applicalbe" — second instance of the same standing authorization, with the "if applicable" clause demanding an honest call on whether more refinement is warranted. The answer was yes for three more defect classes that the link-only auditor of v0.3.11/12 couldn't see.
- The pattern across Waves 9, 9b, and 10 is the same: every dogfood pass adds an auditor for one defect class, then closes that class against the whole repo. Three classes added this wave: schema (catches structural drift in machine-parseable lesson files), anchors (catches the renumbering/rename fallout that link-only audits miss because the URL is right but the fragment is wrong), figures (catches authored-but-unwired ASCII art that the tutor would never surface).

### Deferred
- The dogfood backlog as expressible by current audit classes is now **empty**. Audits green across: links (v0.3.11), display labels (v0.3.12), YAML schema (this wave), anchors (this wave), figures (this wave), class-name parity (verified vs 2.0 source in v0.3.6), module structural completeness (verified in v0.3.12).
- One accepted false-positive remains: stale-pattern scan matches `06_GraphWorkflows/10_KnowledgeCheck.yml:4` on `adk 1.` — the substring is the literal subject of the question (asking the student to name the legacy ADK 1.x workflow templates), not stale content. Documented here in lieu of a per-script allowlist.
- Next natural work is content depth (e.g., the 4B_HumanInTheLoop expansion noted in v0.3.11), NOT another defect-class fix. Belongs in a content-pass phase, not a Wave 11.

---

## [0.3.12] - 2026-05-27

Dogfood Wave 9b — cheatsheet display-label cleanup (15 fixes across 7 files). Wave 9 fixed all the broken URLs in the cheatsheets' "Where it's covered in the course" sections, but a verification pass revealed the *display labels* (the bracket text humans read) were still showing the OLD page numbers/filenames. The links would land you on the right page, but with a confusing "huh, the label said `01_SessionLifecycle` but I'm on `01_SessionVsState`" experience. Pure 🟡 polish — the kind of debt that erodes trust in the cheatsheets even though navigation works.

### Fixed

**Cheatsheet label/href mismatches (7 files)**
- `runner_session_lifecycle.md` — `03_RunAsyncAndEvents` → `03_RunAsyncIsAGenerator`; `01_SessionLifecycle` → `01_SessionVsState`; `03_EventDeltas` → `04_WritingStateFromTools`; `01_TracingRunAsync` → `09_DissectingOneCall`.
- `event_actions.md` — same `03_RunAsyncAndEvents`/`03_EventDeltas` labels; plus `02_Transfer` → `03_TransferToAgent`, `04_HumanInTheLoop` → `07_HumanInTheLoop`, `03_SessionMutation` → `11_TracingOneStateMutation`.
- `llmagent_signature.md` — `01_SubAgents` → `02_SubAgents`; `04_InstructionTemplating` → `03_ReadingStateInPrompts` (2 sites).
- `state_prefixes.md` — `04_InstructionTemplating` → `03_ReadingStateInPrompts` (2 sites); `03_EventDeltas` → `04_WritingStateFromTools`; `04_GuardrailsCookbook` → `05_GuardrailsCookbook`.
- `tool_authoring.md` — `04_BuiltInTools` → `05_BuiltInTools`; `03_AgentAsTool` → `04_AgentAsTool`.
- `callback_signatures.md` — off-by-one on the 4 callback-slot labels (`01/02/03/04_*` → `02/03/04/08_*`); merged the duplicate-target lines (Callbacks-as-policy + Guardrails cookbook both pointed to `05_GuardrailsCookbook.md`; collapsed to one accurate pointer since there is no separate `CallbacksAsPolicy.md` page in module 16 — the concept lives inside GuardrailsCookbook).
- `a2a_mcp_quickref.md` — `04_A2A_vs_MCP` → `05_A2A_vs_MCP`.

### Method
- Targeted audit agent (read-only) over the four Wave 4 surfaces: cheatsheets, drills, 21_AdkApiSurface, module-local AGENTS.md files. Drills + 21_AdkApiSurface + AGENTS.md surfaces verified CLEAN (drills correctly use `Workflow`/`McpToolset`; 21 is HTTP/CLI surface as designed, not Python API enumeration; all 35 module AGENTS.md files populated with substantive teaching guidance, no stubs).
- Cheatsheet edits applied synchronously per-file (verified each line in context before substitution).
- Re-ran link audit: 1/2 190 (the lone remaining is the verified false positive in M4 drill — `[title](uri)` template inside backticks).

### Why
- Same user authorization as Wave 9: "let's not leave polish behind." Display-label drift is exactly the kind of silent debt that prior waves' link-target sweeps don't catch — the URL works, so the audit is green, but the human reading experience is degraded. Worth a 24-line follow-up commit to land properly.

### Deferred
- Nothing on the Wave 4 surface. The dogfood backlog as of this commit is empty: links audit clean, class-names verified against 2.0 source, structural pages (drills + AGENTS.md + 21_AdkApiSurface + cheatsheets) all populated and current. Next natural work is content depth (e.g., the 4B_HumanInTheLoop expansion noted in v0.3.11), not defect-class fixes.

---

## [0.3.11] - 2026-05-27

Dogfood Wave 9 — internal-links integrity sweep. Built a programmatic auditor over all `.md` files in the course (2 190 internal markdown links across 430 files; code-block stripping to avoid false positives on f-strings and illustrative prose). The audit surfaced 93 broken links clustered into ~10 systemic patterns that had accumulated as modules grew, files were renumbered, and folders were renamed without rewriting the cross-refs left behind in detours, cheatsheets, and the 2.0 release-note absorption.

### Fixed

**File renumbering (within-module shifts as drills grew)**
- `04_SessionsState/10_MiniDrill.yml` → `14_MiniDrill.yml` — 04A_ArtifactsHeavyData/00_Overview.md (top + bottom breadcrumbs).
- `06_GraphWorkflows/04_HumanInTheLoop.md` → `07_HumanInTheLoop.md` — 06_GraphWorkflows/{04, 06}, Updates note, runner_session_lifecycle cheatsheet.
- `07_Callbacks/09_MiniDrill.yml` → `12_MiniDrill.yml` — callback_signatures cheatsheet.
- Several cheatsheet drill-pointer fixes in the same shape.

**Folder renames (caught by audit)**
- `21_ApiSurface/` → `21_AdkApiSurface/` — 4 sites across cheatsheets and Detours/AgentEngine.md.
- `4B_HITL/` → `4B_HumanInTheLoop/` — 3 sites across runner_session_lifecycle cheatsheet and 4B_HumanInTheLoop/00_Overview.md (self-referential breadcrumb left over from rename).
- `10A_VectorSearch/` → `10A_EmbeddingsVectorSearch/` — 2 sites in 10B_RAGPipeline/04_VertexAIRAGEngine.md.
- `04A_Artifacts/` → `04A_ArtifactsHeavyData/` — 2 sites in 04_SessionsState/00_Overview.md.
- `22_DeploymentModels/03_AgentEngine.md` → `03_AgentEnginePath.md` (and sibling renames) — 5 sites across Detours/{AgentEngine,Cloud_Run,FastAPI_for_ADK}.md.

**Filename case (post-class-rename artifact)**
- `02_McpToolset.md` → `02_MCPToolset.md` — 4 sites across 08_MCP/{00, 01, 03}. The class was renamed `McpToolset` in v0.3.6 but the filename kept its uppercase `MCP` (acronym style); cross-refs written before the class rename had been "fixed" downward in v0.3.6 and overshot.

**Detour relative-path bug (10 sites across 5 files)**
- `Detours/*.md` linked `../MAP.md` — but Detours lives one level deeper than other Notes pages, so `../MAP.md` resolves to `Notes/MAP.md` (which doesn't exist). Correct path is `../../MAP.md` (repo-root MAP.md). Fixed top + bottom breadcrumbs in AudioEncoding, AudioQuantization, ProtocolBuffers, WebSockets, gRPC.

**Cheatsheet cross-refs (heaviest concentration — 25+ edits)**
- callback_signatures (6 edits), event_actions (5), state_prefixes (4), runner_session_lifecycle (4), llmagent_signature (3), tool_authoring (2), a2a_mcp_quickref (1). Cheatsheets are referenced from many modules but only authored once; they hadn't been re-checked against the live module structure since the modules grew.

**Display-text/href mismatches in 2026-05_adk-2.0.md (4 sites)**
- The script-based fix updated hrefs but left bracket display text stale. E.g. `[Notes/06_GraphWorkflows/02_GraphIntro.md](../06_GraphWorkflows/04_GraphIntro.md)` — href correct, label rotted. Cleaned up at lines 25, 99, 101, 102.

### Method
- `/tmp/link_audit2.py` — regex extractor over all `.md` with `re.sub(r'```.*?```', '', text, flags=re.DOTALL)` and inline-backtick stripping to suppress code-snippet false positives. Resolves each link relative to its file and checks existence.
- Severity rubric applied: broken internal navigation → 🔴 (fix); orphan detours / stale display text → 🟡 (fix in this wave per "don't leave polish behind").
- `/tmp/link_rewrite.py` — assertion-checked Python applying 74 (file, old, new, expected_count) tuples. Script fails loudly if any expected occurrence count is off, preventing silent under-replacement.
- Re-ran audit post-fix: 93 → 1 (the lone remaining is `[title](uri)` in `Drills/M4_AuditorWithEvals.md:64` — illustrative-prose template inside backticks that the stripper doesn't catch because it spans formatting; verified false positive).

### Why
- User: "let's cotinue as suggested. let's not leave polish behind" — authorized both the proactive audit AND the deferred 🟡 cleanup. A course with 430 .md files and ~2 000 internal links cannot rely on synchronous edit-then-check discipline; programmatic auditing is the only way to keep cross-refs honest as the repo grows.
- This is the kind of regression that compounds silently: a single rename in week 3 leaves stale links that the student first hits in week 8. Catching all 93 in one sweep is cheaper than 93 individual "wait, this link is broken" interruptions during real study sessions.

### Deferred
- No known defects in the audit-able surface remain. Next natural target is structural review of the recently-grown 4B_HumanInTheLoop module (file list went from ~6 to 13 over Waves 7-8) — content depth, not defect work; belongs in a content-pass phase rather than a dogfood wave.

---

## [0.3.10] - 2026-05-27

Dogfood Wave 8 — `WorkflowAgent` → `Workflow` class-name sweep across 14 files. The 1.x class `WorkflowAgent` does not exist in ADK 2.0; the canonical 2.0 class is `Workflow` from `google.adk.workflow` (verified at `workflow/_workflow.py:148` and the import sites at `agents/config_agent_utils.py:473`, `cli/agent_test_runner.py:239`). The stale name had survived prior waves because it reads plausibly and is conceptually correct — but a student copy-pasting from any of these sites would hit `ImportError: cannot import name 'WorkflowAgent' from 'google.adk.agents'`.

### Fixed

**Class-name substitutions (12 files)**
- `Notes/07_Callbacks/02_BeforeAfterModel.md` — "`WorkflowAgent` step" → "`Workflow` node" (also tightened the conceptual unit; `Workflow` graphs have *nodes*, not *steps*).
- `Notes/03_Tools/08_AgentToolPreview.md` — composition-alternatives list.
- `Notes/3A_ProjectStructure/05_AdkCliExpectations.md` — `root_agent` valid-types list.
- `Notes/Updates/2026-05_adk-2.0.md` — two sites (composition headline + agent surface enumeration). Added explicit "Replaces the 1.x `WorkflowAgent` name" hint and qualified the new bullet with the `google.adk.workflow` import path.
- `Notes/10_A2A/04_ConsumeWithRemoteA2aAgent.md` — RemoteA2aAgent slot-into list.
- `Notes/05_MultiAgent/08A_LangGraphAgent.md` — "prefer ADK's own graph `Workflow`" recommendation.
- `Notes/05_MultiAgent/06_SequentialAgent.md` — branching/looping alternatives sentence.
- `Notes/99_Capstone/04_SharedRequirements.md` — ≥3-agents requirement.
- `Notes/99_Capstone/06_SelfReviewChecklist.md` — Track A graph requirement.
- `Notes/99_Capstone/09_MiniDrill.yml` — Track A grading rubric (added qualifying import path for the grader's clarity).
- `Notes/2A_AgentConfig/02_RootAgentYaml.md` — YAML-not-loadable warning (kept the import-path pointer that was already there).
- `Notes/20_FrameworkComparison/_figures/landscape.txt` — ASCII landscape diagram.

**Structural fixes (2 files)**
- `Notes/00_Setup/_figures/repo_tour.txt` — `Workflow` was listed under `agents/`. It actually lives in `workflow/`. Split into two rows: `agents/` keeps its real members; new `workflow/` row lists `Workflow, FunctionNode (graph workflows, 2.0)`. Also fixed the `workflows-sequential/` sample annotation.
- `Notes/2A_AgentConfig/08_DissectingSample.md:166` — table linked to nonexistent folder `../06_WorkflowAgents/`. Fixed to `../06_GraphWorkflows/` (the real path) and retitled "workflow agents" → "template workflows" to match the live-site nav we adopted in v0.3.9.

### Method
- Source-of-truth verification: `grep -rn "^class WorkflowAgent\|^class Workflow"` against `adk-python/src/google/adk/workflow/` and `agents/` — `WorkflowAgent` class genuinely doesn't exist anywhere in 2.0.
- Synchronous edits (~14 files, ~17 lines changed); each site read in context before substitution to verify the sentence reads cleanly post-swap.
- Intentional disambiguation references at `06_GraphWorkflows/08_DissectingWorkflowSample.md:33` (explaining the 1.x→2.0 rename for sample readers) and the new Updates note are preserved — they explicitly say "1.x `WorkflowAgent`" with the 2.0 contrast.

### Why
- User: "let's continue" — Wave 8 closes the lone known-defect carried in the v0.3.9 Deferred section. With ~100% dogfood coverage of authored content, individual correctness defects like this are now visible enough to chase one-by-one.
- This was the highest-impact open item: 14 sites including all three capstone checklists/rubrics, the 2.0 release notes, the 2A AgentConfig dissection, and the framework landscape figure. Anyone learning ADK 2.0 from these pages would form a wrong mental model of the canonical class name.

### Deferred
- Wave 4 🟡 polish items still open (have been across multiple waves now — most are stylistic).
- Cheatsheets pedantic 🟡 (intentionally skipped).
- Next natural wave: a links/anchors integrity sweep across the now-large repo (catch other broken folder/cross-page references like the `06_WorkflowAgents` one this wave caught).

---

## [0.3.9] - 2026-05-27

Dogfood Wave 7 — the smallest-but-most-overdue surface: `Reference/CheatSheets/`, four milestone drills (M1-M4 + M5 capstone), and `Reference/docs_snapshot.md`. Three parallel read-only verification agents surfaced 5 🔴 + ~22 🟡 across ~1.9K lines. Notable clean bills: M5 capstone fully verified, all 7 cheatsheets with no correctness-breaking errors (~12 🟡 were pedantic abbreviations intentionally left as-is). Synchronous fixes this round — the surface was small enough that direct edits beat fix-agent dispatch overhead. Also landed the 1A `_configs` import-path tail deferred from v0.3.7+v0.3.8.

### Fixed

**Milestone drills — M1-M4 (4 files / 11 fixes)**
- `M1_ConversationServer.md`: breadcrumbs (top + bottom) pointed at `04_SessionsState/10_MiniDrill` — actual page is `14_MiniDrill`. Stretch-goal cross-reference said "Module 04 page 06" for state prefixes; correct cite is "Module 04 pages 02 + 10" (prefix definitions + DatabaseSessionService pairing).
- `M2_WorkflowEditor.md`: Version B fan-out prose described importing private `_ParallelWorker` directly — wrong direction per `workflow/_parallel_worker.py:35` (private machinery, not user-facing). Rewrote to describe the canonical `parallel_worker=True` flag on `@node`-decorated function or `Agent`/`LlmAgent` node, citing `adk-python/contributing/samples/workflows/parallel_worker/agent.py:44,55`. ASCII diagram updated accordingly. `reviewer_node` snippet signature was missing the auto-injected `ctx: Context` parameter — added per `workflow/_function_node.py:185`.
- `M3_FederatedPlanner.md`: AgentCard URL used legacy `/.well-known/agent.json` — canonical 2.0 path is `/.well-known/agent-card.json` per `a2a/utils/constants.py:3` (legacy still backward-compat served at `starlette_app.py:131-141`). Fixed in both the code snippet (line 288) and the gotcha bullet (line 357). `RemoteA2aAgent.agent_card` tutor note had contradictory wording about return types — cleaned up to cite `llm_agent.py:100-103` (`Optional[dict]` matching tool's result schema). Cross-link `[[07_Callbacks/05_ErrorCallbacks]]` corrected to `08_ErrorCallbacks`.
- `M4_AuditorWithEvals.md`: critic agent's model listed as `gemini-2.5-pro`; actual `llm-auditor/sub_agents/critic/agent.py:64` uses `gemini-2.5-flash`. Part 2 LoggingPlugin snippet used the deprecated `Runner(plugins=...)` shape — rewrote around `App(plugins=[...])` passed via `app=`, with deprecation banner citing `runners.py:219-220, 287-306`.

**Reference/docs_snapshot.md — section index rewrite**
- "Agents — Workflow agents (Sequential/Parallel/Loop) (legacy section)" → "Multi-Agent Workflows — Template workflows (Sequential, Parallel, Loop, Custom)" to match the current live-site nav structure.
- Renamed "Tools" rows to "Custom Tools" where the live site does.
- Added rows for live-site surfaces that had drifted off the snapshot: Custom Tools — `LongRunningFunctionTool`/action confirmations (→ 03 + 18 + 4B); Tools — Grounding (Google Search grounding) (→ Detours/Grounding + 17); Components — Artifacts (→ 04A); Components — Context caching/compression (→ 1A); Run Agents — Safety and Security (→ 16); expanded Evaluation row to cover custom metrics + user/environment simulation + optimization.
- Fixed "Agent Config (2.0)" course-module link: `02_FirstAgent` → `2A_AgentConfig`.
- Added explicit out-of-scope footnote for multi-language ADKs (TypeScript / Go / Java / Kotlin) — this course is Python-only.

**1A `_configs` import-path tail (3 files / 6 edits, carried from v0.3.7)**
- `Notes/1A_AppAndRunner/04_WiringResumability.md`: `ResumabilityConfig` IS lazily re-exported via `apps/__init__.py:21,26` `__all__` — student-facing imports should use the shallow public path. Consolidated 3 sites (lines 29, 64, 107) from `from google.adk.apps._configs import ResumabilityConfig` to `from google.adk.apps import App, ResumabilityConfig`. Added explanatory parenthetical on the lazy-loader pattern in the student-run snippet.
- `Notes/1A_AppAndRunner/AGENTS.md` + `Notes/2A_AgentConfig/AGENTS.md`: watch-lists and divergence notes split the warning to distinguish public `ResumabilityConfig` (use shallow) vs private `EventsCompactionConfig` (still requires deep `_configs` import — not in `__all__`).

### Method
- Three parallel read-only verification agents (Wave 7 dogfood, ~1.9K lines across 12 files) — smaller surface meant fewer agents.
- Source-of-truth verification spanned `adk-python` source (`workflow/_function_node.py`, `_parallel_worker.py`, `a2a/utils/constants.py`, `remote_a2a_agent.py`, `runners.py`, `apps/__init__.py`) plus a live-site re-fetch of https://adk.dev/ nav for the docs_snapshot section-index drift.
- Cheatsheets ~12 🟡 (pedantic abbreviations like `tools=[]` shorthand for `Field(default_factory=list)`, model field's `''` default vs resolved `gemini-2.5-flash` fallback) intentionally left as-is — verification agent explicitly noted "no correctness-breaking errors found."

### Why
- User: "let's go, enxt wave" — closed the last large unreviewed surfaces (drills + cheatsheets + snapshot), bringing dogfood coverage to ~100% of authored content. Drills are the integration test for entire tracks; carrying broken cross-refs and outdated cite paths through to capstone work would compound. Section-index drift in `docs_snapshot.md` would have silently misled the next 4-week refresh diff.
- 5 🔴 across 4 drills + 0 🔴 across 7 cheatsheets + M5 capstone clean is the strongest "course is converging" signal yet.

### Deferred
- Cheatsheets pedantic 🟡 items (intentionally skipped — would add footnote density without changing learner outcomes).
- Wave 4 🟡 polish items still open.
- `04_SharedRequirements.md` references nonexistent `WorkflowAgent` class (flagged out-of-scope by M5-track agent; M5 itself clean).

---

## [0.3.8] - 2026-05-27

Dogfood Wave 6 — the deferred `Notes/Detours/` surface: 27 detours (~5K lines) across Python, ADK-deep, ADK-adjacent, cloud-platform, and protocol/transport sidebars. Five parallel read-only verification agents surfaced 16 🔴 + 25 🟡 against `adk-python`, `google/genai`, `fastmcp`, `gcloud`, and the official Slack/Google Chat docs. 12 of 27 detours verified entirely clean (notably all 9 Python detours, GeminiPayload, AudioQuantization, PromptInjection). Five parallel fix agents then corrected 15 files.

### Fixed

**Transport reframing — `gRPC.md` + `ProtocolBuffers.md` (Fix-F, 2 files / 7 fixes)**
- Vertex Live is **gRPC-DEFINED but WebSocket-TRANSPORTED**. Both detours framed Live as raw gRPC; verified against `google/genai/live.py:48` (`from websockets.asyncio.client import connect`), `:997` (`json.dumps(request_dict)`), `:1002,1038` (URI = `/ws/google.cloud.aiplatform.{ver}.LlmBidiService/BidiGenerateContent`). Added new "What Vertex actually uses on the wire" section to `gRPC.md` clarifying the service is defined in protobuf/gRPC-style but the SDK speaks WebSocket+JSON to it.
- `gRPC.md` ASCII diagram: `:path = .../BidiGenerate` → `BidiGenerateContent`; added annotation that the path describes the gRPC service shape, wire is WebSocket at `/ws/<that-path>`.
- `runner.run_live(...)` framing: was "gRPC stream", now "WebSocket stream (gRPC-defined service, WebSocket transport)".
- Resumption note: TCP/HTTP-2 → TCP/WebSocket; "the whole RPC" → "the whole session".
- `ProtocolBuffers.md`: wire-type table was incomplete (claimed 4, listed only 4) — protobuf has **6** wire types (0 VARINT, 1 FIXED64, 2 LENGTH_DELIMITED, 3 START_GROUP proto2-only, 4 END_GROUP proto2-only, 5 FIXED32). Added rows for 3+4 with proto2-only annotation; verified against `google.protobuf.internal.wire_format` constants.
- Varint tag explainer sharpened: was "4 bits of tag + 3 bits of wire-type + 1 continuation bit" (wrong shape — varints don't pack like that); now "7 value bits + 1 continuation bit per byte; low 3 bits of the value are wire type, leaving 4 bits for field number in the first byte" with worked examples (`15<<3 = 0x78`, `16<<3 = 0x80 0x01`).
- `ProtocolBuffers.md` bidi-demo bullet: reframed away from "leaving the protobuf-on-gRPC world for JSON-on-WebSocket" — the browser WebSocket uses the same JSON wire format the SDK itself uses to talk to Vertex Live.

**VisualBuilder.md — substantive rewrite (Fix-G, 1 file / full rewrite)**
- Page conflated two unrelated ADK 2.0 features. Builder produces **YAML AgentConfig** files (`root_agent.yaml`, `sub_agent_*.yaml`) per `fast_api.py:109` (`_ALLOWED_EXTENSIONS = frozenset({".yaml", ".yml"})`), `:352` (default save path `root_agent.yaml`), and `api_server.py:658-661` ("All YAML agents are treated as visual builder agents"). It is NOT a visual frontend over `google.adk.workflow.Workflow` Python.
- Rewrote sections 1, 4, 5 around the YAML/AgentConfig truth; replaced the bogus `Workflow(...)` Python round-trip example with a real AgentConfig YAML matching `contributing/samples/multi_agent/sub_agents_config/root_agent.yaml`; cross-linked to `[[2A_AgentConfig]]`.
- Section 2 table: rewrote rows around agent hierarchies / orchestrator agents; `Workflow` explicitly called out as no-UI (the graph-workflow engine has no visual equivalent).
- Section 3: trigger is now "click the **+** icon in the top-left" (not a phantom Builder tab/route); `agents_dir` shown as positional argument; added `⚠️` about silent `python-multipart` soft-fail (`fast_api.py:78-85`).
- Surfaced `_BLOCKED_YAML_KEYS = frozenset({"args"})` at `fast_api.py:111` as a code-execution guard worth knowing when hand-editing YAML round-trip.
- Section 5 "Have the student try": replaced `Workflow` + conditional-edge exercise with 3-agent root/researcher/summarizer YAML authoring.

**ADK-deep detours (Fix-H, 4 files / 11 fixes)**
- `FastMCP.md`: `Context` has no `request_headers` attribute — replaced with `get_http_headers()` from `fastmcp.server.dependencies`. `mount("/weather", weather)` is wrong — real signature is `mount(weather, namespace="weather")` and namespaces tool NAMES, not URL paths. Switched `transport="streamable-http"` → `"http"` (current FastMCP 2.x alias; old name still works). Stripped parens from `@mcp.tool()` / `@mcp.prompt()` across all sites (no-parens is the modern form). `datetime.utcnow()` → `datetime.now(timezone.utc)` (utcnow deprecated in 3.12).
- `FastAPI_for_ADK.md`: removed bogus `session_service=` kwarg from `get_fast_api_app()` (real signature only takes `session_service_uri: str | None` per `fast_api.py:377-404`); rewrote section 6 around URI-sharing pattern. Route table: dropped dev-only `/events/{e}` row (it's in `dev_server.py:1145-1149`, not `api_server.py`); memory PATCH-only; PATCH on per-session path (`api_server.py:1137`), not on collection. `postgres://` → `postgresql://` (SQLAlchemy strict).
- `AgentEngine.md`: `rewind_async()` signature was wrong — real is `(*, user_id: str, session_id: str, rewind_before_invocation_id: str, run_config: Optional[RunConfig] = None)` per `runners.py:1114-1121`. Added 3-paths callout for `AdkApp` import location.
- `a2UI.md`: agent-discovery sentence tightened — `agents_dir` is positional (`cli_tools_click.py:1745-1751`), discovery requires a valid agent package shape.

**Cloud-platform detours (Fix-I, 4 files / 15 fixes)**
- `Cloud_Run.md`: **`--cpu-always-allocated` does not exist** as a `gcloud run deploy` flag — real flag is `--no-cpu-throttling`. Fixed 3 sites; clarified `--cpu-boost` is cold-start-only. Removed bogus `--agent_engine_app=agent_engine_app.py` flag from `adk deploy cloud_run` example (no such flag per `cli_tools_click.py:2082-2147`); replaced with the `--` separator pattern for forwarding gcloud args. Softened 15-min idle-shutdown to "rough rule of thumb; not a published SLO"; added cost-hedge clause; flagged post-2024 default-SA restriction; paired `--ingress=internal-and-cloud-load-balancing` with `--no-allow-unauthenticated`.
- `GoogleChat_Apps.md` (security-critical): audience claim was wrong — JWT mode uses project **NUMBER** (not project ID); OIDC mode uses endpoint URL. Fixed in config block, section 6 prose, and verification snippet. Split verification into two distinct code paths: `verify_chat_request_jwt` (`id_token.verify_token`, `iss == chat@system.gserviceaccount.com`, audience = project number) vs `verify_chat_request_oidc` (`verify_oauth2_token`, `email == chat@...`, `iss == accounts.google.com`, audience = endpoint URL). Clarified `chat.bot` scope must be requested explicitly via `google.auth.default(scopes=[...])`.
- `Slack_Bots.md` (security-critical): `response_url` was framed as "one-time URL that lets you respond multiple times" — reality per Slack docs is "up to 5 responses within 30 minutes". Added `verify_slack_signature` HMAC-SHA256 helper with 5-min replay protection; refactored handler to read `await req.body()` raw bytes BEFORE `parse_qs` (avoids the `req.form()` body-consumption footgun that prevents post-hoc signature verification). Added `slack-bolt` `SlackRequestHandler` as production-cleaner alternative. Session-id consistency: `session_id = f"slack:{user_id}"` (min-viable) with thread-aware production pattern `f"{channel}:{thread_ts}"` cross-linked.
- `SignedUrls_GCS.md`: section 5(B) was broken — used `credentials.service_account_email` (only exists on `compute_engine.Credentials`, raises `AttributeError` on user ADC) and never passed `credentials=` into `generate_signed_url`. Rewrote around `google.auth.iam.Signer` with explicit signer email + `IAMCredentialsClient.sign_blob` comparison table. Revocation note expanded: removing `roles/iam.serviceAccountTokenCreator` self-binding invalidates future `signBlob` requests (already-issued URLs still honor TTL).

**Misc small detour fixes (Fix-J, 4 files / 5 fixes)**
- `Grounding.md`: `bypass_multi_tools_limit=True` does NOT lift the 1.x ValueError (that's unconditional in `google_search_tool.py:74-78`); the flag is consumed at `llm_agent.py:149-155` and triggers `GoogleSearchAgentTool` wrapping (the search runs in a sub-agent). Reframed the bullet; softened the 2.x flowchart's "composes freely" overstatement (Gemini API still rejects mixing without the wrap).
- `OpenTelemetry.md`: `OTLPSpanExporter(endpoint="localhost:4317")` silently fails — `insecure = parsed_url.scheme == "http"` per `exporter.py:317`, so without `http://` scheme it defaults to TLS against a plain-text collector. Fixed both occurrences with `endpoint="http://localhost:4317"` (or `insecure=True`); added gotcha callout.
- `WebSockets.md`: `WebSocketDisconnect` is Starlette/FastAPI; pure `websockets` library raises `websockets.ConnectionClosedError`. Replaced with the correct exception + a namespace callout noting Starlette's equivalent.
- `AudioEncoding.md`: MP3 priming framing was wrong — claimed pre-roll silence at every frame boundary. Reality is encoder priming happens at the **start of the stream** (~1152 samples) plus the bit-reservoir scheme contributes to seek latency, not per-frame artifacts.

### Method
- Five parallel read-only verification agents (Wave 6 dogfood, ~5K detour lines) → five parallel fix agents (Wave 6 fix), all with non-overlapping scopes.
- Source-of-truth verification spanned `adk-python` source, `google/genai/live.py`, `gcloud run deploy --help`, `google.protobuf.internal.wire_format`, the official Slack `response_url` docs, the official Google Chat `verify-requests` docs, and FastMCP 2.x public docs.
- One brief premise (transport in gRPC.md/ProtocolBuffers.md framed Vertex Live as raw gRPC) was caught as wrong during verification; reframing bundled into Fix-F.

### Why
- User: "let's continue our strategy!" Wave 6 closed the deferred Detours surface — the last large unreviewed area after Wave 5 covered the main-module pages. Errors found were severe enough — silently-failing OTLP TLS, security-critical Google Chat audience inversion, Slack `response_url` semantics, broken `signBlob` ADC path, `--cpu-always-allocated` flag that doesn't exist — that landing this before any new authoring is necessary.
- 12 of 27 detours verified entirely clean is a strong signal that prior waves of careful authoring held up; the failures clustered in the cloud-platform area where docs evolve fastest.

### Deferred
- Module-1A `04_WiringResumability.md` + 2 `AGENTS.md` references still use the `_configs` import path for `ResumabilityConfig` (carried over from v0.3.7 deferred); bundle into next wave.
- Wave 4 🟡 polish items still open.
- `Reference/CheatSheets/` and the four milestone drills (M1-M4) have not been dogfood-verified at all yet — natural next target.

---

## [0.3.7] - 2026-05-27

Dogfood Wave 5 — the largest uncovered surface yet: 145 pages across 11 modules (11 Memory, 12 CodeExec, 13 Plugins, 14 Eval, 16 ProdSec, 17 AdvModels, 18 Live, 23 Frontend, side modules 1A/2A/3A/4B/04A). Six parallel read-only verification agents surfaced 13 🔴 + ~32 🟡 against ground-truth `adk-python` source. Five parallel fix agents then corrected 48 files across all 11 modules.

### Fixed

**Module 17 AdvancedModels** (8 files)
- `PlanReActPlanner` page: replaced fabricated sample-anchors (supply-chain / sdlc / swe-benchmark / tau2) with the verified truth — no first-party sample instantiates `PlanReActPlanner` in production code (`grep` against `adk-samples/`); only doc reference is `short-movie-agents/GEMINI.md`. All four cited samples use `BuiltInPlanner`.
- `OpenAIModels`: dropped invalid `api_key=` kwarg from `OpenAILlm(...)` (class declares only `model` + `max_tokens` per `_openai_llm.py:349-350`); `OPENAI_API_KEY` read from env via `AsyncOpenAI()` at `:510-511`.
- `ApigeeLlm`: rewrote constructor snippet with real kwargs (`model="apigee/<provider>/<model_id>"`, `proxy_url`, `custom_headers`) per `apigee_llm.py:88-97`; model-string validation cited from `:138-139`.
- `ModelSelectionPatterns`: fallback callback fixed — `BaseLlm.generate_content_async` returns `AsyncGenerator[LlmResponse, None]` per `base_llm.py:50-52`, requires `async for` not `await`. New shape: `async for response in FALLBACK.generate_content_async(...): if not response.partial: return response`.
- Systemic `-002` sweep across pages 01/02/10A/12: replaced every `gemini-2.5-flash-002` / `-lite-002` / `-pro-002` with bare names. Added one-liner explaining the 2.5+ family does not use `-NNN` suffix (that was 1.5/2.0-era convention; dated previews use `-preview-MM-YYYY` form).
- `MCPToolset` → `McpToolset` alias clarified at `11_DissectingSample.md:46` to match the actual sample import.

**Modules 18 StreamingLive + 13 Plugins** (9 files)
- `LoggingPlugin._log` uses raw `print()` with ANSI escape codes — NOT Python `logging` module (`logging_plugin.py:284-288`). Dropped `logging.basicConfig` snippet and INFO-filter gotcha; added stdout-capture guidance and pointer to `DebugLoggingPlugin` for structured JSON output.
- `on_session_end_callback` does NOT exist on `BasePlugin`. Replaced with `after_run_callback(*, invocation_context)` per `base_plugin.py:174`. Distinguished from `close()` (runner shutdown) in custom-plugin scaffolding.
- `event.turn_complete` is essentially a Live-API control signal (`gemini_llm_connection.py:123,354`, `base_llm_flow.py:1087`). Canonical finality for `run_async` text streaming is `event.is_final_response()` (`events/event.py:220-235`). Swapped across `01_StreamingFundamentals.md`, `03_TextStreaming.md`, `11_MiniDrill_TextStream.yml`.
- `StreamingMode.BIDI` is NOT consumed by `run_live` per `run_config.py:173-181` docstring — softened the "required" framing to "set by convention".
- Line citation drifts fixed in `02_GeminiLiveIntro.md` and `06_VideoInput.md`.

**Modules 11 Memory + 14 Evaluation + 12 CodeExec** (8 files)
- `adk eval` CLI runs each case **exactly once** — there is no `--num_runs` flag. `NUM_RUNS = 2` (`agent_evaluator.py:59`) is the Python-API default only, multiplied via `:577`. Replaced two myth sites with the correct framing.
- Memory Bank sample alignment: `Gemini(model="gemini-3-flash-preview", retry_options=types.HttpRetryOptions(attempts=3))` per `adk-samples/.../memory-bank/app/agent.py`.
- `vector_distance_threshold` framework default is 10 (`vertex_ai_rag_memory_service.py:99`) — added inline note.
- `similarity_top_k` applies to RAG-backed memory service only — clarified across Memory Bank vs RAG memory.
- `UnsafeLocalCodeExecutor` runs in a **spawned child process** (not your Python process) with timeout via `result_queue.get(timeout=...)` per `:88-107` — no sandboxing; rewrote both intro and In-Production block.
- `VertexAiCodeExecutor.optimize_data_file` comment corrected to "extracts CSV data files from the request and attaches them to the executor".
- `AgentEngineSandbox`: added env-var note (`GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION` per `:53-103`).

**Side modules 1A/2A/04A + 16 ProductionSecurity** (10 files)
- `LlmEventSummarizer` real signature: `LlmEventSummarizer(llm: BaseLlm, prompt_template: Optional[str] = None)` per `apps/llm_event_summarizer.py` — NOT `LlmEventSummarizer(model="...")`. Fixed in `06_WiringContextCompaction.md` and `09_InProduction.md` checklist.
- `runner.close()` (`runners.py:2135-2144`) is the public lifecycle hook — preferred over `runner.plugin_manager.close()` which only handles plugin teardown. Updated `02_OnStartupShutdown.md` patterns 1 & 2, In-Production callout, and `11_MiniDrill.yml` rubric.
- `BaseArtifactService` has **7** abstract methods (not 5) — bumped count and listed `list_artifact_versions` + `get_artifact_version` in `04A/02_ArtifactServiceShape.md`.
- `GcsArtifactService` does NOT save `file_data` Parts — `gcs_artifact_service.py:232-236` raises `NotImplementedError`. Added caveat in `04A/05_MultimodalParts.md`.
- Module 1A `08_DissectingSample.md` aligned to `gemini-3-flash-preview` per sample.
- `16/03_Authentication.md`: imports `OAuth2` from `fastapi.openapi.models` directly (ADK re-exports it at `auth_schemes.py:22`).
- `16/08_DissectingSafetyPlugins.md`: added ModelArmor naming-note callout pointing at `main.py:28` alias.
- `2A/04_ToolReferences.md`: added denylist watch-note for `_BLOCKED_YAML_KEYS = frozenset({"args"})` + `_ENFORCE_DENYLIST = False` at `config_agent_utils.py:490-491`. (Original brief mis-identified `ToolConfig.args` schema; the existing YAML mapping form was actually valid per real `ToolArgsConfig` with `extra="allow"` — agent correctly refused the regression.)

**Side modules 3A/4B + 23 FrontendIntegration** (13 files)
- `adk web ./agents` — `agents_dir` is a `@click.argument` (positional) per `cli_tools_click.py:1745-1751`, not `--agents_dir`. Fixed in `3A/05_AdkCliExpectations.md`; Rule 2 reframed as env-var ordering (not discovery).
- `runner.cancel()` does NOT exist. Replaced sweeper in `4B/08_FrontendDrivenApprovals.md` with the abandon pattern: append terminal `Event(author='system', ...)` via `session_service.append_event` and mark `decision='timeout'`.
- `ResumabilityConfig` is publicly re-exported at `apps/__init__.py:21,26`. Replaced `from google.adk.apps._configs import ResumabilityConfig` with the public path across 6 Module-4B pages + mini-drill. (`EventsCompactionConfig` is NOT in `__all__` — keeps the deep path.)
- `response_schema: Optional[SchemaType]` per `events/request_input.py:28` accepts pydantic.BaseModel subclass OR JSON-Schema dict, NOT shorthand `{"city": str}`. Three sites in `4B/06_RequestInputInGraphs.md` rewritten to proper `{"type": "object", "properties": {"city": {"type": "string"}}}`.
- Fun-facts sample uses `gemini-flash-latest` (verified against `fun_facts/agent.py`); updated `3A/09_DissectingSample.md`.
- `23/03_SseFromTheBrowser.md`: removed stray `if False else None`; renamed custom route to `/my_sse` with note comparing to ADK's built-in `RunAgentRequest.new_message: types.Content` shape.
- `23/04_WebSocketsFromBrowser.md`: inline deprecation comment for `runner.run_live(session=)` (`runners.py:1519-1527` — prefer `user_id+session_id`).
- `23/05_CustomSPApattern.md`: artifact POST path corrected — `POST .../sessions/{sid}/artifacts` (no `/{name}`; filename in JSON body `SaveArtifactRequest.filename` per `api_server.py:1249-1268`).
- `23/08_StreamingPartialResults.md`: added `ADK_ENABLE_PROGRESSIVE_SSE_STREAMING` env-var note (default ON per `run_config.py:104-110`).

### Method
- Six parallel read-only verification agents (Wave 5 dogfood) → five parallel fix agents (Wave 5 fix), all with non-overlapping scopes. Each fix verified post-edit against canonical `adk-python` source.
- All ground-truth claims re-verified pre-edit; one brief premise (`ToolConfig.args` schema) was caught as wrong during verification and the agent correctly refused to regress.

### Why
- User: "lets continue refining." Wave 5 closed the largest unreviewed surface (~145 pages across 11 modules) since the dogfood pattern began. Errors found were severe enough — `runner.cancel()` referenced as if it existed, `await` on async-generators that would raise `TypeError`, plugin hooks named that don't exist on `BasePlugin` — that landing this before any new authoring is necessary.

### Deferred
- 2 module-1A files (`04_WiringResumability.md` + 2 `AGENTS.md` references) still use the `_configs` import path for `ResumabilityConfig` — Fix-E flagged but out of scope; bundle in next wave.
- Wave 6 (`Notes/Detours/` — ~23 unreviewed detours) remains the natural next refinement target.

---

## [0.3.6] - 2026-05-27

The two deferred items from v0.3.5 — `Contents.md` rewrite and the `MCPToolset` → `McpToolset` deprecation sweep — landed together. 50 files modified across two parallel fix agents.

### Fixed

**`Contents.md` — full rewrite**
- Old TOC was severely stale (~70 broken links + ~50 orphan pages from Phase 3.5 onward). Rewrote from disk: every module/page link verified to resolve. New structure mirrors `MAP.md`'s 8-track grouping (Foundation / Composition / Integration / Data & GCP / Runtime / Production / Reference / Capstone) with side modules (1A `AppAndRunner`, 2A `AgentConfig`, etc.) tagged inline so students can tell main-line from optional at a glance.
- Final count: **~393 link entries** — 351 module pages + 27 Detours + 5 Drills + 7 cheat sheets + 3 meta refs. Voice preserved from prior file.

**`MCPToolset` → `McpToolset` deprecation sweep**
- `class MCPToolset(McpToolset)` at `mcp_toolset.py:495-505` is a deprecation alias that emits a `DeprecationWarning` at instantiation; `McpToolset` is the modern name (`mcp_toolset.py:66`). 49 files updated (`Notes/`, `Drills/`, `Reference/`), ~144 occurrences renamed.
- New 🪧 callout at `Notes/08_MCP/02_MCPToolset.md:19` explains the alias + how to silence the warning without code change.
- **Intentionally retained** (2 files):
  - `Notes/08_MCP/02_MCPToolset.md` — frontmatter `page:` slug, breadcrumb, historical `title:` (the page IS about the deprecation story).
  - `Drills/M3_FederatedPlanner.md` — line-179 deprecation explainer comment + line-384 wiki-link to the MCP module page.

### Method
- Two parallel fix agents with non-overlapping scopes (Contents.md rewrite / corpus-wide sweep). Both verified post-run.

### Why
- User: "let's continue working. we are almost there." Both items were the last debts from the Wave 3-4 dogfood cycle. Shipping them together unblocks the Phase 4-5 authoring track that was waiting on a clean TOC.

### Deferred
- Wave 4 🟡 polish items remain open; small enough to fold into the next functional bump rather than block on a polish-only release.

---

## [0.3.5] - 2026-05-27

Dogfood Wave 4 — student-facing reference surface. Five parallel read-only verification agents covered the surfaces waves 1-3 hadn't sampled: all 7 cheatsheets, all 5 milestone drills, the entire `21_AdkApiSurface` module, every module-local `AGENTS.md`, and top-level `AGENTS.md`/`MAP.md`/`Contents.md`. Three parallel fix agents then corrected 17 files. (Top-level `AGENTS.md`/`MAP.md` verified clean. `Contents.md` is severely stale — ~70 broken links + ~50 orphan pages — deferred to v0.3.6 as a focused rewrite.)

### Fixed

**Cheatsheets (`Reference/CheatSheets/*.md` — all 7 had findings)**
- `a2a_mcp_quickref.md` — wrong A2A import (`google.adk.a2a` is empty; real: `from google.adk.a2a.utils.agent_to_a2a import to_a2a` at `agent_to_a2a.py:79`), legacy well-known path replaced with modern `/.well-known/agent-card.json` (a2a-sdk `constants.py:3`) + legacy fallback note, wrong `RemoteA2aAgent` import (`agents/__init__.py:34` doesn't export it), wrong kwarg `agent_card_url=` → `agent_card=` (`remote_a2a_agent.py:145`), wrong MCP import (`StdioServerParameters` is from `mcp` not ADK; `StdioConnectionParams` from `google.adk.tools.mcp_tool.mcp_session_manager`). Added `MCPToolset(header_provider=...)` row (`mcp_toolset.py:112-114`) and expanded auth-schemes row with the 5 concrete `*SecurityScheme` classes + snake_case rule.
- `callback_signatures.md` — "nine callback slots on `LlmAgent`" corrected to 8 (2 from `BaseAgent`: `before/after_agent_callback` per `base_agent.py:123,137`; 6 from `LlmAgent` per `llm_agent.py:391,406,420,435,450,465`). Added the `Union[_Single, list[_Single]]` stacking shape from waves 1-3 (`llm_agent.py:75-87`). Clarified `CallbackContext`/`ToolContext` are aliases of the same `Context` class (`callback_context.py:22`, `tool_context.py:29`), not subtypes.
- `event_actions.md` — removed folklore "`None` deletes the key" (`State.__setitem__` at `sessions/state.py:91-98` just stores `None`); removed wrong "order not guaranteed" claim (insertion order preserved); added missing public fields `end_of_agent` and `requested_tool_confirmations` (`event_actions.py:93-105`); dropped `requested_auth_configs` "(Auth flows)" qualifier.
- `llmagent_signature.md` — `tools: list[BaseTool]` → `tools: list[ToolUnion]` where `ToolUnion = Union[Callable, BaseTool, BaseToolset]` (`llm_agent.py:134,294`). Added missing kwargs: `global_instruction` (deprecated; `:230`), `static_instruction` (`:243`), `mode` (`:307`), `parallel_worker` (`:318`), `disallow_transfer_to_parent`/`_peers` (`:322,330`).
- `runner_session_lifecycle.md` — added `app=` modern path (`runners.py:209`); added `try/finally` + `await runner.close()` story (`runners.py:2135-2144`, `_cleanup_toolsets`); added optional `run_async` kwargs (`invocation_id`, `state_delta`, `run_config`, `yield_user_message` per `runners.py:914-924`) with resume gloss.
- `state_prefixes.md` — `ToolContext` detection note rewritten: annotation takes priority, param-name `tool_context` is fallback (`function_tool.py:87-88`).
- `tool_authoring.md` — same `ToolContext` detection fix; corrected "name + type" claim.

**Drills**
- `M2_WorkflowEditor.md` + `M5_Capstone.md` — `WorkflowAgent` → `Workflow` (`workflow/_workflow.py:148`, re-exported `google/adk/__init__.py:22`). M2 added "yield-list fan-out" note clarifying `_ParallelWorker` is private machinery.
- `M3_FederatedPlanner.md` — legacy `/.well-known/agent.json` → modern `/.well-known/agent-card.json` (4 sites) with `PREV_AGENT_CARD_WELL_KNOWN_PATH` fallback note. Added `MCPToolset` deprecation comment (use `McpToolset` per `mcp_toolset.py:66,500`).
- `M4_AuditorWithEvals.md` — `FinalResponseMatchV1` → `FinalResponseMatchV2Evaluator` (`final_response_match_v2.py:130`; metric key `final_response_match_v2`). Flagged deprecated `criteria` dict shape in `test_config.json` (modern: `EvalConfig(criteria={k: BaseCriterion(threshold=v)})` per `agent_evaluator.py:134-143`). Added deep-import note for `BigQueryAgentAnalyticsPlugin` (not in `plugins/__init__.py __all__`).

**21_AdkApiSurface**
- `01A_AdkRunUnderTheHood.md` — `aioconsole.ainput("[user]: ")` corrected to plain blocking `input()` (`cli/cli.py:210`); added `invocation_id=` kwarg to the `run_async` snippet for long-running-tool resume (`cli/cli.py:223-228`).
- `01B_AdkWebUnderTheHood.md` — "no `--reload` flag" claim corrected: both `--reload/--no-reload` (default True, passed to `uvicorn.Config(reload=)` at `cli_tools_click.py:1839`) and `--reload_agents` (default False, toggles agent-cache hot-reload via `get_fast_api_app(reload_agents=)` at `fast_api.py:396`) exist. Dropped uncited `_register_builder_endpoints` function-name claim; rewrote to accurate "wired conditionally inside `cli/fast_api.py` gated on `web=True` AND `python-multipart` installed" (`fast_api.py:74-85,644`).
- `02_AdkApiServer.md`, `03_RestShapes.md`, `07_SessionAndEventResources.md` — deprecated session-create route `POST .../sessions/{session_id}` (`@deprecated` at `api_server.py:1083-1086`) replaced as primary teaching with modern `POST .../sessions` + `CreateSessionRequest{session_id?, state?, events?}` body (`api_server.py:389-403`). Legacy form kept as one-line note. `GET .../app-info` marked experimental (`api_server.py:1034`).

**Module-local AGENTS.md**
- `Notes/06_GraphWorkflows/AGENTS.md` — dissection-answer text still drilled `ParallelWorker` semantics the module page had moved past. Answers 1 and 3 rewritten to drill the yield-list fan-out pattern instead, consistent with the existing line-20 "don't import `_ParallelWorker`" warning.

### Verified-only (no edits required)
- Top-level `AGENTS.md` — clean.
- `MAP.md` — every module/detour box matches disk; tracks correctly grouped; milestones at correct gates.
- 34 of 35 module-local `AGENTS.md` files — clean; waves 1-3 fixes propagated.

### Method
- **Wave 4 dogfood** (read-only, 5 parallel agents, `git status --short` clean post-run): cheatsheets / drills / 21 / module-local AGENTS.md / top-level meta.
- **Wave 4 fix** (3 parallel agents with non-overlapping scopes): cheatsheets / drills / 21+06-AGENTS.
- **Pre-fix discrepancy reconciled**: Wave 4-B agent flagged `/.well-known/agent.json` as canonical per `remote_a2a_agent.py:54`. Verified against a2a-sdk: modern canonical IS `/.well-known/agent-card.json` (`a2a-sdk: constants.py:3`); the hardcoded `:54` constant in ADK is only the fallback used when the a2a-sdk import fails. Wave 2's earlier fix was correct.

### Why
- User: "let's continue our strategy" + "let's dispatch the fixes." Reference surface (cheatsheets, drills, API-surface module) is where students lean hardest for quick lookups; these had accumulated the most pre-2.0 drift because they were authored to be terse one-pagers without anchor links back to source.

### Deferred to v0.3.6
- `Contents.md` near-total rewrite (~70 broken links, ~50 orphan pages on disk).
- `MCPToolset` → `McpToolset` deprecation sweep across the corpus.
- All 🟡s from Wave 4 (folded into the v0.3.6 polish pass).

---

## [0.3.4] - 2026-05-27

Dogfood Wave 3. Six parallel verification agents (read-only, `git status` clean post-run) covered the modules and detours 0.3.2/0.3.3 did not sample: 10A Embeddings, 10B RAG, 15 Observability, 19 Internals, 20 Framework Comparison, 22 Deployment, 24 Channel Integrations, 99 Capstone, and detours Grounding / OpenTelemetry / WebSockets / gRPC. Same severity rubric as prior waves. Five parallel fix agents then corrected 23 files surgically against `/home/carloscabral/study/adk-python/src/`. Both 🔴 and 🟡 landed in this bump (no split — the residue is small enough).

### Fixed
- **Pub/Sub trigger route** — real path is `/apps/{app_name}/trigger/pubsub`, not `/trigger/pubsub` (`cli/trigger_routes.py:401`). `user_id` is derived from the subscription resource name: `subscription.replace("/", "--")` (`trigger_routes.py:414-415`). Nine mentions updated across `Notes/24_ChannelIntegrations/07_AmbientAgentsAsChannels.md` (5) and `10_DissectingSample.md` (4); user_id note added once per file.
- **`BigQueryAgentAnalyticsPlugin` import path** — corrected from fabricated `google.adk.plugins.analytics.bigquery` to real `google.adk.plugins.bigquery_agent_analytics_plugin` (`plugins/bigquery_agent_analytics_plugin.py:1967`). Affected `Notes/22_DeploymentModels/07_ObservabilityWiring.md`.
- **19 Internals line-citation drift** — `base_session_service.py:141` → `:114` (four occurrences across `09_DissectingOneCall.md`, `11_TracingOneStateMutation.md`: `async def append_event` is at line 114, not 141). `llm_agent.py:340` → `:294` for the `tools` field declaration in `02_LlmAgentSource.md`. Other Internals citations spot-verified and confirmed accurate.
- **Capstone API name drift** — `FinalResponseMatchV1` → `FinalResponseMatchV2Evaluator` (metric key `final_response_match_v2`; class at `evaluation/final_response_match_v2.py:130`; registered at `metric_evaluator_registry.py:148-149`). `WorkflowAgent` → `Workflow` (real export at `workflow/_workflow.py:148`, re-exported in `google/adk/__init__.py`). Brief incorrectly identified the class as `RougeEvaluator` — that's the legacy v1 evaluator; agent flagged and used the correct v2 class. Affected `Notes/99_Capstone/01_TrackA_ResearchAssistant.md`, `04_SharedRequirements.md`.
- **Vertex AI RAG Engine GA migration** — preview surface (`vertexai.preview.rag`, flat `embedding_model_config=` / `chunk_size=` kwargs) replaced with GA surface (`vertexai.rag` with `backend_config=RagVectorDbConfig(rag_embedding_model_config=RagEmbeddingModelConfig(vertex_prediction_endpoint=VertexPredictionEndpoint(...)))` and `transformation_config=TransformationConfig(chunking_config=ChunkingConfig(chunk_size=, chunk_overlap=))`). Default embedding model now `gemini-embedding-001`. ⚠️ Preview-era callout added to `06_DissectingRAGSample.md` since the `adk-samples/python/agents/RAG/` sample still pins the preview namespace (verified at `agent.py:26`, `prepare_corpus_and_data.py:23,64`). Affected `Notes/10B_RAGPipeline/04_VertexAIRAGEngine.md`, `06_DissectingRAGSample.md`.
- **Embedding model deprecation** — `text-embedding-004` deprecated 2026-01-14; `text-embedding-005` is legacy. Recommended default is `gemini-embedding-001` (3072 dims, supports `task_type`). Switching model families requires re-embedding the entire corpus. Callouts added in `Notes/10A_EmbeddingsVectorSearch/02_VertexAITextEmbeddings.md` (model table reordered) and `06_DissectingSample.md` (flag without rewriting quoted sample); model swapped in `04_BuildingAnIndex.md` and `Notes/10B_RAGPipeline/03_HandRolledRAG.md`. Default index dimensions bumped 768 → 3072.
- **IndexDatapoint proto note** — added one-line clarification in `Notes/10A_EmbeddingsVectorSearch/04_BuildingAnIndex.md` that Vector Search `upsert_datapoints` takes `IndexDatapoint` proto objects (`from google.cloud.aiplatform_v1 import IndexDatapoint`), not dicts.
- **`LoggingPlugin` output format** — corrected from implied structured JSON to actual ANSI-colored stdout via `print(f"\033[90m...\033[0m")` (`plugins/logging_plugin.py:284-288`). Course now points students at `structlog` / `logging.dictConfig` for production. Affected `Notes/15_Observability/02_StructuredLogging.md`.
- **OpenTelemetry span attribute names** — replaced generic placeholders with the actual GenAI-semconv-compliant attribute names ADK emits: `gen_ai.request.model`, `gen_ai.usage.input_tokens`/`output_tokens`, `gen_ai.agent.name`, `gen_ai.tool.name`, plus GCP-specific `gcp.vertex.agent.session_id` and `gcp.vertex.agent.invocation_id` (`telemetry/tracing.py:44-58, 331-334`). Affected `Notes/15_Observability/04_TracingAnAgentRun.md`, `05_Metrics.md`.
- **Grounding multi-tool restriction inverted** — `google_search` cannot be combined with other tools on **Gemini 1.x** only (`tools/google_search_tool.py:74-78`); on 2.x the check is bypassed, and `bypass_multi_tools_limit` flag exists (`:42`). Course previously stated the inverse. Fixed prose at L69 and the flowchart at L175 in `Notes/Detours/Grounding.md`.
- **OpenAI Agents SDK idiom** — `handoffs=[handoff(researcher)]` → `handoffs=[researcher]` with inline note that `sub_agents=` is ADK terminology and `handoff(...)` wrapping is only for customization. Affected `Notes/20_FrameworkComparison/05_OpenAIAgentsSDK.md`.
- **Pydantic AI idiom** — `system_prompt="..."` → `instructions="..."` (newer preferred form in pydantic-ai 0.0.40+; both kwargs still exist). Affected `Notes/20_FrameworkComparison/06_PydanticAI.md`.
- **OpenTelemetry exporter install note** — `opentelemetry-sdk` only ships the SDK + console exporter; OTLP needs separate `pip install opentelemetry-exporter-otlp`. Install callout added to `Notes/Detours/OpenTelemetry.md`.
- **WebSockets 64KB claim** — RFC 6455 allows payloads up to 2^63 bytes; "64 KB" was a library-default fragment size, not a protocol limit. Python `websockets` library defaults to `max_size=2**20` (1 MiB), tunable via `max_size`/`write_limit`. Affected `Notes/Detours/WebSockets.md`.
- **gRPC HTTP/2 frame diagram** — replaced conflated HEADERS/DATA frame depiction with correct sequence: opening HEADERS (`:path`), interleaved bidirectional DATA frames, trailing HEADERS with `grpc-status`. Caption clarifies single bidi RPC = one stream id with bidirectional frames. Affected `Notes/Detours/gRPC.md`.

### Verified-only (no edits required)
- **Skills knowledge check Q2** — brief said Q2 cited 3 invocation patterns; actual Q2 is about the 3 SkillToolset auto-exposed tools (`list_skills`, `load_skill`, `load_skill_resource`), which is correct per source (`skill_toolset.py:93,186,262`). Q4 already correctly says 4 invocation patterns matching `00_Overview.md`. No fix needed.
- **`Notes/11_Memory/03_VertexAIMemoryBank.md` model pin** — already uses `gemini-2.5-flash`, the dominant in-course model (256 occurrences vs 32 for 2.5-pro). No change.

### Method
- **Wave 3 dogfood** (read-only): 6 parallel agents covered 10A/B, 15, 19, 20, 22/24, 99, and 4 detours. `git status` clean post-run.
- **🔴 + 🟡 combined fix wave**: 5 parallel fix agents with non-overlapping file scopes:
  - **A** — 24 Channel Integrations Pub/Sub + 22 BQ import
  - **B** — 19 Internals citations + 99 Capstone class names
  - **C** — 10B Vertex AI RAG Engine GA migration
  - **D** — 10A embeddings deprecation + 15 OTel/Logging plumbing
  - **E** — Grounding inversion + framework idioms + detour 🟡s
- **Brief deviations followed source**:
  1. Capstone v2 evaluator class is `FinalResponseMatchV2Evaluator` (not `RougeEvaluator`, which is the legacy v1).
  2. Pub/Sub mentions were 9 across two files, not "~5" as estimated in the brief.
  3. Skills Q2 was already correct; the inverted-count claim was a Wave-3 dogfood misread.

### Why
- User: "let's dispatch" — fire all Wave 3 fixes (🔴 and 🟡 together, residue small enough not to split).

---

## [0.3.3] - 2026-05-27

🟡 second pass after dogfood Wave 2. Four parallel fix agents corrected the imprecise-but-not-broken drift items deferred from 0.3.2. Same source-grounded methodology against `/home/carloscabral/study/adk-python/src/` plus the `a2a-sdk` source for the A2A path/scheme fixes.

### Fixed
- **A2A well-known path** — modern canonical path is `/.well-known/agent-card.json` (`AGENT_CARD_WELL_KNOWN_PATH` in `a2a/utils/constants.py:3`); `/.well-known/agent.json` is the legacy fallback (`PREV_AGENT_CARD_WELL_KNOWN_PATH`). `RemoteA2aAgent` imports the new path from the a2a-sdk (`remote_a2a_agent.py:51-54`). One 🪧 callout in `02_AgentCard.md` documents the fallback. Note: the on-disk filename `agent.json` for `adk api_server --a2a` directory mode (`fast_api.py:669-694`) is a separate concept and stays as-is. Affected `Notes/10_A2A/01_WhatIsA2A.md`, `02_AgentCard.md`, `03_ServeWithToA2a.md`, `04_ConsumeWithRemoteA2aAgent.md`, `05_A2A_vs_MCP.md`, `06_DissectingSample.md`, `07_InProduction.md`, `08_KnowledgeCheck.yml`, `09_MiniDrill.yml`, `AGENTS.md`.
- **A2A `SecurityScheme` is a union, not a constructor** — concrete classes: `HTTPAuthSecurityScheme`, `APIKeySecurityScheme`, `OAuth2SecurityScheme`, `OpenIdConnectSecurityScheme`, `MutualTLSSecurityScheme` (`a2a/types.py:1524-1538`). Fields are snake_case (`bearer_format`, not `bearerFormat`); `HTTPAuthSecurityScheme(scheme=, bearer_format=, type='http')` (`a2a/types.py:447-470`). Affected `Notes/10_A2A/02_AgentCard.md`, `07_InProduction.md`.
- **`SkillRegistry` ABC signatures are keyword-only** — `async def get_skill(self, *, name: str) -> Skill` and `async def search_skills(self, *, query: str) -> list[Frontmatter]` (`skills/skill_registry.py:29-54`). `get_skill` **raises** on missing name, doesn't return `None`. Concrete GCS impl confirms return types (`integrations/skill_registry/gcp_skill_registry.py:51,73`). Call sites updated to keyword form (`registry.search_skills(query=...)`). Affected `Notes/09_Skills/04_SkillRegistry.md`, `02_SkillAnatomy.md`, `07_KnowledgeCheck.yml`.
- **Skills frontmatter accepts `allowed-tools` alias** — `Frontmatter` Pydantic model uses `ConfigDict(populate_by_name=True)` and `alias="allowed-tools"` / `serialization_alias="allowed-tools"` on the `allowed_tools` field (`skills/models.py:56-69`). Added one-line note in `02_SkillAnatomy.md`.
- **`VertexAiMemoryBankService.agent_engine_id` expects bare ID** — source `vertex_ai_memory_bank_service.py:220-226` **warns** (not rejects) when the value contains `/`, then concatenates it into `'reasoningEngines/' + agent_engine_id`, producing a double-prefixed malformed path that fails at API call time. Page now shows `agent_engine_id="456"` with an inline `api_resource.name.split('/')[-1]` extraction comment. Affected `Notes/11_Memory/03_VertexAIMemoryBank.md`.
- **`app_engine_id` typo** → `agent_engine_id` in `Notes/11_Memory/06_DissectingMemoryBank.md` L77.
- **`--staging_bucket` is deprecated** — `cli_tools_click.py:1559-1569` emits `WARNING: --staging_bucket is deprecated and will be removed`; `:2256-2260` flag help text is `"Deprecated. This argument is no longer required or used."` Modern shape is `client.agent_engines.create(config=...)`. Added ⚠️ deprecation callout adjacent to the use. Affected `Notes/22_DeploymentModels/03_AgentEnginePath.md`.
- **Google Chat JWT issuer link** — verified `chat@system.gserviceaccount.com` is current via [verify-requests-from-chat docs](https://developers.google.com/workspace/chat/verify-requests-from-chat); no code change, added 🪧 link callout pointing at the official source. Affected `Notes/Detours/GoogleChat_Apps.md`.

### Verified-only (no edits required)
- `Notes/Detours/a2UI.md` CLI flags were already fixed in 0.3.2 (`--session_service_uri`, `--reload_agents`).

### Method
- **🟡 fix wave**: 4 parallel agents with non-overlapping file scopes (module 09 / module 10 / module 11 / cross-cutting 22+Detours). Brief was wrong on two items where source contradicted it; agents flagged and followed source:
  1. `get_skill` raises on missing name (brief implied `-> Skill | None`).
  2. The `agent_engine_id` validator only **warns** with `/` in the value — does not reject; failure surfaces downstream at the API call.
- **Out-of-original-scope catch**: Wave 2E agent flagged `Notes/10_A2A/07_InProduction.md` had the same `SecurityScheme` + path drift outside the brief's explicit file list. Picked up post-agent in this bump.

### Why
- User: "let's go" — dispatch the 🟡 wave deferred at end of 0.3.2. This closes the dogfood Wave 2 cycle (0.3.1 → 0.3.2 → 0.3.3).

---

## [0.3.2] - 2026-05-27

Dogfood Wave 2. Six parallel verification agents (read-only, `git status` clean post-run) covered the modules 0.3.1 did not sample: 06 Graph Workflows, 07 Callbacks, 08 MCP, 2A Agent Config, 10C BigQuery, 12 Code Execution, 13 Plugins, 14 Evaluation, 16 Production & Security, 17 Advanced Models, 18 Streaming & Live, and the VisualBuilder / a2UI / FastMCP detours. Same severity rubric as 0.3.1 (🔴 wrong shape, won't run / 🟡 drifted / 🟢 verified). Five parallel fix agents then corrected ~51 files surgically against `/home/carloscabral/study/adk-python/src/`. Only the 🔴 wave landed in this bump; 🟡 stays pending for the next pass.

### Fixed
- **Graph workflow API path** — real import is `from google.adk.workflow import Workflow, START` (not `google.adk.agents.workflow.WorkflowAgent`). `FunctionNode` + `@node` decorator are the public surface; `_ParallelWorker` is private. `Event` lives at `google.adk.events`. Real resume API is `runner.run_async(invocation_id=..., new_message=...)`. Worst offender because `AGENTS.md` doubled down on the wrong path; reversed. Affected all of `Notes/06_GraphWorkflows/` plus `Detours/VisualBuilder.md`.
- **`FunctionNode.rerun_on_resume` does exist** (brief was wrong) — `_function_node.py:174` shows `rerun_on_resume: bool = False`; workflow-level default is `True`, per-node default is `False`. Kept kwarg in examples with the scope note.
- **Sample-version skew** — `workflow-*`, `agent-skills-tutorial`, `financial-advisor` samples pin `google-adk<2.0.0`; flagged in 06's sample-anchor table so students don't read 1.x APIs as canonical.
- **`adk create` flags** — real flags are `--api_key`, `--project`, `--region` (no `google-` prefix). Source: `cli_tools_click.py:436-498`. Affected `Notes/2A_AgentConfig/03_AdkCreateCli.md`.
- **`LlmAgentConfig` is `extra='forbid'`** — unknown YAML keys (e.g., `global_instruction:`) raise validation errors at load; `_ADK_AGENT_CLASSES = {"LlmAgent", "LoopAgent", "ParallelAgent", "SequentialAgent"}` (no `WorkflowAgent`; graphs are Python-only). `ToolConfig` accepts only `name:` + `args:` — no `toolset:`/`class:` discriminator. Affected `Notes/2A_AgentConfig/02_RootAgentYaml.md`, `04_ToolReferences.md`, `07_PythonOnlyFeatures.md`, `01_WhyDeclarative.md`.
- **Callbacks DO stack per agent** — `BeforeModelCallback: TypeAlias = Union[_SingleBeforeModelCallback, list[_SingleBeforeModelCallback]]` (llm_agent.py:75-87). Pages and `AGENTS.md` previously claimed otherwise. Affected `Notes/07_Callbacks/05_CallbackContextAnatomy.md`, `06_CallbackRecipeCookbook.md`, `07_CallbacksVsPlugins.md`, `AGENTS.md`.
- **`ToolContext` and `CallbackContext` are aliases of the same class** — `ToolContext = Context` (tool_context.py:29), `CallbackContext = Context` (callback_context.py:22). Not subclasses. `ctx.session_id` is not real; use `ctx.session.id`.
- **Plugin imports + signatures** — `ContextFilterPlugin` and `GlobalInstructionPlugin` are not in `plugins/__init__.py __all__`; deep imports required. `GlobalInstructionPlugin(global_instruction=...)` kwarg, not `instruction=`. Real plugin hook names are `_callback`-suffixed. Affected `Notes/13_Plugins/01_WhatIsAPlugin.md`, `04_ContextFilterPlugin.md`, `05_GlobalInstructionPlugin.md`.
- **MCP lifecycle — Runner auto-closes toolsets** — `runners.py:2094-2144` (`_cleanup_toolsets`). Use `await runner.close()` with try/finally; `MCPToolset` is NOT an async context manager (no `__aenter__`/`__aexit__`). Affected `Notes/08_MCP/04_LifecycleManagement.md`, `07_InProduction.md`, `08_KnowledgeCheck.yml`, `09_MiniDrill.yml`, `AGENTS.md`, `Notes/10_A2A/03_ServeWithToA2a.md`.
- **MCP auth headers** — fabricated `tool_context.headers["Authorization"]` replaced with real `MCPToolset(header_provider=...)` recipe (`mcp_toolset.py:112-114`, `mcp_tool.py:386-398`).
- **`FastMCP` detour imports** — `MCPToolset, StdioConnectionParams` from `google.adk.tools.mcp_tool`; `StdioServerParameters` from `mcp` itself; example wraps params in `StdioConnectionParams(server_params=..., timeout=10.0)`.
- **`adk web` flags** — `--session_service_uri` (not `--session-service`), `--reload_agents` (not `--reload` for agent-code reload; `--reload` toggles the server). Affected `Detours/a2UI.md`.
- **Evaluation API shapes** — `LlmAsJudge` is an abstract base, config-driven via `judge_model_options.judge_model` (NOT `LlmAsJudge(model=...)`); real `__init__(self, eval_metric, criterion_type, expected_invocations_required=False)`. `RubricBasedEvaluator` constructor takes config, not `rubric=[...]`. Affected `Notes/14_Evaluation/04_LlmAsJudge.md`, `05_RubricBasedEvaluator.md`.
- **`adk eval` flags** — first positional is a DIRECTORY; real flags are `--config_file_path`, `--print_detailed_results`, `--eval_storage_uri`, `--log_level`. `--num_runs`, `--output_dir`, `--config_path` were fabricated. Affected `Notes/14_Evaluation/08_AdkEvalCli.md`.
- **Five evaluator types, not four** — `00_Overview.md` count fixed. `RougeEvaluator` (real class) has metric name `response_match_score`; surfaced as a 🪧 Naming callout.
- **`ContainerCodeExecutor` real kwargs** — only `base_url`, `image`, `docker_path`; dropped fictional `network`, `timeout_seconds`, `mem_limit`. **`GkeCodeExecutor` real fields** — `kubeconfig_path`, `kubeconfig_context`, `image`, `namespace`, `executor_type`, `cpu_limit`; no `service_account` (use Workload Identity binding via gcloud + kubectl annotate). Affected `Notes/12_CodeExecution/05_ContainerAndGke.md`.
- **Auth API real shape** — `BaseAuthenticatedTool` subclass + `tool_context.request_credential(auth_config)` / `get_auth_response(auth_config)` two-turn flow (`context.py:679, 696`). `@requires_auth` decorator and `tool_context.auth_state` do NOT exist. `BaseAuthenticatedTool` subclass overrides `_run_async_impl(args, tool_context, credential)`. Affected `Notes/16_ProductionSecurity/03_Authentication.md`, `10_InProduction.md`.
- **Streaming requires opt-in** — `runner.run_async()` default is `StreamingMode.NONE` (run_config.py); text streaming needs `run_config=RunConfig(streaming_mode=StreamingMode.SSE)`. Affected `Notes/18_StreamingLive/01_StreamingFundamentals.md`, `03_TextStreaming.md`, `11_MiniDrill_TextStream.yml`.
- **`LongRunningFunctionTool` is deferred-result, not async-generator** — `function_call_id` round-trip; tool returns `{"status": "pending", "job_id": ...}`; worker replays `function_response` with matching id (`function_tool.py:213-274`, `auth_tool.py:141-148`). Yield-progress pattern is the common fabrication. `_call_live(input_stream=...)` is the LIVE-only streaming-INPUT path, separate concern. Affected `Notes/18_StreamingLive/05_StreamingTools.md`.
- **`LLMRegistry.register(llm_cls)` is single-arg** — class implements `supported_models() -> list[str]` regex patterns classmethod (`registry.py:99-107`, `base_llm.py:45`). Two-arg `register("name", cls)` and `LLMRegistry.list_models()` were fabricated; real lookup is `LLMRegistry.resolve(model)`. Class is `Claude` (NOT `ClaudeLlm`), subclass of `AnthropicLlm` (anthropic_llm.py:716). Affected `Notes/17_AdvancedModels/01_LLMRegistry.md`, `14_MiniDrill.yml`.
- **BigQuery WriteMode default** — `BLOCKED` (config.py:56); `maximum_bytes_billed` IS first-class on `BigQueryToolConfig` (config.py:63-69, `>=10_485_760` validator). Page previously claimed unsafe default. Affected `Notes/10C_BigQueryAgents/03_BigQueryAsTool.md`, `07_InProduction.md`, `AGENTS.md`.
- **`adk web --builder` flag does not exist** — removed phantom flag from VisualBuilder detour.

### Method
- **Dogfood**: 6 read-only verification agents with non-overlapping module scopes, grounded against `/home/carloscabral/study/adk-python/src/` and ADK docs at <https://adk.dev/>. Reports written to the 🔴/🟡/🟢 severity rubric established in 0.3.1. `git status --short` verified empty after each agent returned.
- **Fix wave (🔴 only)**: 5 parallel agents with non-overlapping file scopes. Each fix verified against framework source with file:line citations; grep confirmations of bad strings returning 0 hits.
- **New pattern surfaced**: sample-version skew. Several samples still pin `google-adk<2.0.0`; pages anchored to them inherit 1.x APIs as if canonical. Flagged in 06's sample-anchor table; full sweep deferred to the 🟡 pass.
- **Reaffirmed lesson from 0.3.1**: brief-only authoring → confident hallucination; source-grounded authoring → correct content. The 0.3.0 modules touched by this wave were brief-authored; the bill is this entry.

### Pending (🟡 next pass, per user "later the imprecise as well")
- A2A well-known path (`/.well-known/agent-card.json` vs legacy `/.well-known/agent.json`)
- Skills signatures sweep
- GCP drift remainder (10A/10B)
- Memory module typos
- CLI flag drift remainder (`staging_bucket` deprecation note, Chat issuer)

### Why
- User: "let's expand our dogfood/review for the rest of our course, and then later, fix them." then "let's dispatch it all. first the wrong ones and later the imprecise as well." This entry is the 🔴 dispatch; 🟡 follows.

---

## [0.3.1] - 2026-05-27

Dogfood-and-fix cycle. Four parallel verification agents read the new 2.0-surface modules against `/home/carloscabral/study/adk-python/src/` (the real framework source) instead of against the brief. Five parallel fix agents then corrected ~25 surgically. The pattern that the verification surfaced: pages authored from the brief were confidently wrong on real API shapes; pages anchored to source were correct. This entry is the corrections, not new scope.

### Fixed
- **App container, not LlmAgent** — `ContextCacheConfig`, `EventsCompactionConfig` (not `ContextCompactionConfig`), and `ResumabilityConfig` attach to `App`, not `LlmAgent`. Imports from `google.adk.apps`. Affected `Notes/04_SessionsState/05_ContextCaching.md`, `06_ContextCompaction.md`, `Notes/1A_AppAndRunner/00_Overview.md`.
- **`LlmEventSummarizer` signature** — takes `llm=` and `prompt_template=`, not `model=`/`instruction=`. Affected `Notes/04_SessionsState/06_ContextCompaction.md`.
- **`Runner.rewind_async` real shape** — takes `rewind_before_invocation_id=`, no `to_event_id=` or `state_overrides=` (auto-computed from session events, skipping `app:`/`user:` prefixes). Affected `Notes/04_SessionsState/07_SessionRewind.md`.
- **Session migrate is a schema upgrade tool, not a cross-backend mover** — `migration_runner.upgrade(source_db_url, dest_db_url)` (pickle→JSON). Added "What this does NOT do." Affected `Notes/04_SessionsState/08_SessionMigrate.md`.
- **`Runner.cancel` does not exist** — replaced with the real abandon pattern (timeout / don't resume / append terminal `Event` via `session_service.append_event(...)`). Affected `Notes/4B_HumanInTheLoop/04_RunnerResumeAndCancel.md`, retitled to "Resume and abandon", and `12_InProduction.md`.
- **Ambient trigger endpoints — partial reversal** — `POST /apps/{app_name}/trigger/pubsub` and `/trigger/eventarc` DO exist in 2.0 (opt-in via `--with-triggers pubsub,eventarc`; source: `trigger_routes.py:391-467`, `cli_tools_click.py:1687`). GCS routes through Eventarc. Only `/triggers/gcs` and `/triggers/scheduler` were fabricated. Affected `Notes/4B_HumanInTheLoop/07_AmbientAgents.md`.
- **`rerun_on_resume` has two scopes** — workflow-level (default `True`, `_workflow.py:157`) AND node-level (default `False`, `_base_node.py:56`); node-level opt-out wins. Affected `Notes/4B_HumanInTheLoop/06_RequestInputInGraphs.md`.
- **`adk` CLI flag names** — real flags are `--session_service_uri` and `--artifact_service_uri` (not `--session_db_url`/`--artifact_storage_uri`). `--credential_service_uri` does not exist. Affected `Notes/21_AdkApiSurface/01_AdkRunCli.md`, `01A_AdkRunUnderTheHood.md`, `01B_AdkWebUnderTheHood.md`, `01C_FullCliFamily.md`.
- **`adk web` defaults** — default port is `8000` (not `8501`); dev UI is Angular (not Vite/React). Affected `Notes/21_AdkApiSurface/01B_AdkWebUnderTheHood.md`, `Notes/23_FrontendIntegration/06_A2UIClient.md`.
- **`/run_live` wire protocol** — real `LiveRequest` Pydantic model in (`content`/`blob`/`activityStart`/`activityEnd`/`close`); ADK Event JSON out (camelCase, `partial`/`turnComplete`/`interrupted`). Not Gemini Live native protocol. Documented query-string params and 1002 close-code gotcha. Affected `Notes/21_AdkApiSurface/05_WebSocketsForLive.md` (full rewrite).
- **REST shapes** — only `user_id` and `session_id` required; `app_name` falls back to `ADK_DEFAULT_APP_NAME`; `new_message` is `Optional`. Affected `Notes/21_AdkApiSurface/03_RestShapes.md`.
- **Session/event/artifact endpoints** — `list-sessions` returns `list[Session]` directly; DELETE takes no body; `PATCH /sessions/{s}` exists. Affected `Notes/21_AdkApiSurface/07_SessionAndEventResources.md`.
- **No `/debug/*` routes** — replaced with the real route list (`/health`, `/version`, `/list-apps`, `/apps/{app}/app-info`, session/event/artifact/memory CRUD, `/run`, `/run_sse`, `/run_live`, `/dev-ui`). Affected `Notes/Detours/FastAPI_for_ADK.md`.
- **`ComputerUseToolset` is an empty `__init__.py`** — must import from `base_computer` and `computer_use_toolset` submodules; 16 abstract methods (added missing `hover_at`, `scroll_at`). Affected `Notes/03_Tools/06_ComputerUse.md`.
- **`VertexAiRagRetrieval`** — requires `description=` kwarg; single-tool is a recommended pattern, not runtime-enforced. Affected `Notes/03_Tools/07_ToolLimitations.md`.
- **`SqliteSessionService` is fictional** — real class is `DatabaseSessionService(db_url="sqlite:///...")`. Affected `Notes/01_Foundations/07_KnowledgeCheck.yml`.
- **Agent Engine deploy** — `--staging_bucket` deprecated with active warning; newer SDK shape is `client.agent_engines.create(config=...)` (`cli_deploy.py:1169`); `VertexAiSessionService.rewind()` is fabricated — use `runner.rewind_async()`. Affected `Notes/Detours/AgentEngine.md`.
- **`Runner.resume` shape** — `runner.run_async(invocation_id=paused_invocation_id, new_message=function_response)` with `adk_request_confirmation` function-response part. Affected `Notes/1A_AppAndRunner/04_WiringResumability.md`.
- **PROGRESS.md reconciled** — Module 00 and 01 page lists corrected against actual files on disk.

### Method
- **Dogfood**: 4 read-only verification agents with non-overlapping scopes (tutor contract on 00+01 / Foundation core 02-04 / 2.0-surface 1A+4B+04 expansions / deployment 21-24), each grounded against `/home/carloscabral/study/adk-python/src/` and ADK docs at <https://adk.dev/>. Reports written to a 🔴/🟡/🟢 severity rubric.
- **Fix wave**: 5 parallel agents with non-overlapping file scopes to enable parallelism without git conflicts. Each fix verified against framework source with file:line citations.
- **Lesson**: agents working from a brief produce confident hallucinations correlated with how thin the brief is. Agents grounded against source produce correct content. The 0.3.0 modules were authored from brief — most of the fixes here are that bill coming due. Subsequent authoring should ground against source by default.

### Why
- User asked: "let's dogfood using sub-agents and find/review our learnings." The verification pass found ~15 🔴 (wrong API shape, will not run) and ~10 🟡 (correct intent, drifting names) defects across the 2.0-surface modules. Shipping a course where the 2.0 examples don't import is worse than shipping nothing 2.0-shaped, so the fix pass took precedence over new scope.

---

## [0.3.0] - 2026-05-27

Completeness pass after a docs-and-samples audit. Three new modules, four module expansions, one new detour, and a sample-citation rewiring across the existing modules.

### Added (new modules)
- **`Notes/1A_AppAndRunner/`** — The 2.0 `App` class as container, `on_startup`/`on_shutdown` hooks, `app:` state boundary, and the wiring of `resumability_config` / `context_cache_config` / `context_compaction_config`. Without this, several of the 2.0 features below can't be taught coherently. Slot between modules 01 and 02.
- **`Notes/2A_AgentConfig/`** — Declarative agent definition via `root_agent.yaml`, `adk create`, supported tool/sub-agent reference forms, the Python-vs-YAML tradeoffs, what's currently Python-only. Slot between modules 02 and 03.
- **`Notes/3A_ProjectStructure/`** ⭐ — User-requested. The pragmatic file/folder layout story: single-file → split agent/tools/prompts → directory-per-concept as the project grows. Explicit treatment of what `adk web`/`adk run`/`adk api_server` expect (the `root_agent` discovery rule, `__init__.py` gotchas) and what Cloud Run and Agent Engine deployments expect. Shared utilities pattern, eval/tests layout. Slot between modules 03 and 04. Light-touch callouts wired into 05/14/22 so the convention is reachable from natural pressure points.
- **`Notes/4B_HumanInTheLoop/`** ⭐ — Dedicated HITL module (user-requested). Covers `Context.request_confirmation()`, `EventActions.requested_tool_confirmations`, `Runner.resume()`/`cancel()`, `LongRunningFunctionTool` as a HITL primitive, `RequestInput` pauses in graphs, **Ambient Agents** (Pub/Sub / GCS / Scheduler triggered), driving the approval loop from a frontend or external consumer (Slack, web, mobile), and durable-execution integrations (Temporal, Dapr) for when ADK's built-in resume isn't enough. Slot after 04A.

### Added (module expansions)
- **Module 04 Sessions & State** — +4 pages: `05_ContextCaching`, `06_ContextCompaction`, `07_SessionRewind`, `08_SessionMigrate` (all ADK 2.0 primitives; `09–12` shifted from `05–08`).
- **Module 03 Tools** — +2 pages: `05_ComputerUse` (preview toolset, `BaseComputer`, Playwright/Chromium), `06_ToolLimitations` (single-instance constraints, e.g., Vertex AI RAG Engine tool can only be used alone). Trailing files shifted.
- **Module 16 Production & Security** — +2 pages: `06_AgentIdentityVsUser` (the under-taught distinction between agent identity and controlling-user identity for tool authorization), `07_GeminiAsJudgePlugin` (the safety plugin from `safety-plugins` sample).
- **Module 17 Advanced Models** — +2 pages: `05_PlannersBuiltIn` (`BuiltInPlanner` + `ThinkingConfig`), `06_PlanReActPlanner` (used by ~7 samples but taught nowhere previously).
- **Module 22 Deployment Models** — +1 page: `03A_GKE` (the third path alongside Cloud Run and Agent Engine).

### Added (module deep-dives — user-requested)
- **Module 07 Callbacks** — +3 pages: `05_CallbackContextAnatomy` (what's in `CallbackContext`, what isn't, common gotchas), `06_CallbackRecipeCookbook` (real-life recipes: caching, rate limiting, redaction, source citation, latency budgets, conditional tool execution), `07_CallbacksVsPlugins` (decision rubric).
- **Module 21 ADK API Surface** — +3 pages: `01A_AdkRunUnderTheHood`, `01B_AdkWebUnderTheHood`, `01C_FullCliFamily` (the full `adk` CLI map covering `eval`, `create`, `migrate`, `deploy`). User asked for an under-the-hood treatment of the CLI; the API-surface module is the right home.
- **Module 3A Project Structure** — +1 page: `07A_ConfigAndEnvVars` (user-requested). Centralises env-var coverage that was scattered across `00_Setup`, `Detours/Cloud_Run`, `22/08`, and per-provider 17-pages: full table of ADK-respected env vars, `pydantic-settings` one-class pattern, `.env.dev`/`.env.prod` separation, anti-patterns, and the "validate in `on_startup`, fail loud" rule. Slotted between 07 and 08; trailing files unchanged.

### Added (detour)
- **`Notes/Detours/Grounding.md`** — Google Search Grounding vs Enterprise Search vs Agentic RAG (distinction from module 10A/10B is real and worth a page).

### Changed (sample citations)
- Wove the following samples into existing modules as Dissecting Sample or InProduction citations: `ambient-expense-agent` (4B canonical), `deep-search` (23 frontend, 06 graph reflect-loop), `memory-bank` (11 canonical), `safety-plugins` (13, 16), `agent-observability-bq` (10C, 15), `adk-ae-oauth` (16, 22), `multiformat-hybrid-rag` (10B secondary), `bidi-demo` (18 canonical), `realtime-conversational-agent` (18, 23), `workflows-HITL_concierge` (4B, 06), `camel` (16 prompt-injection).

### Status
- `MAP.md` updated: 1A, 2A, 4B slotted in the Foundation block; module 03/04/16/17/22 lines expanded; `Grounding` added to detour grid.
- `Contents.md` updated: every new page listed with the trailing-files shifted.
- The 0.2.0 additions (`04A_ArtifactsHeavyData`, deployment track 21-24, six deployment detours, REPL→script style flip) remain in flight; this 0.3.0 entry stacks on top.

### Why
- User asked for completeness against ADK 2.0 docs + samples. A two-agent audit (docs at <https://adk.dev/> and the 73 samples under `adk-samples/python/agents/`) surfaced the gaps above. HITL was explicitly requested as a dedicated session; the rest are the audit's must-add column. Lower-priority items (Express Mode, Apigee, more telemetry sinks) were deferred to a future minor.

---

## [0.2.0] - 2026-05-27

Scope expansion after Phase B authoring. Three structural changes:

### Changed
- **Style: REPL → runnable scripts on ADK pages.** Rule #2 in `_AUTHORING_AGENT_BRIEF.md` flipped. ADK is async-only and session-bound — `>>>` blocks don't actually run. Switched to `# Work/NN_name.py — run with: uv run python Work/NN_name.py` script style on the ~14 ADK runtime pages. Pure-Python detours (`PY_async`, `PY_typing`, etc.) and pure-data manipulation pages keep REPL — that's how Python is actually taught.

### Added
- **New module `04A_ArtifactsHeavyData/`** ☁️ — `ArtifactService`, `GcsArtifactService`, multimodal Parts, video understanding, signed URLs, heavy-file handoff between sub-agents. Slot after Sessions/State because artifacts ride the same Event substrate. GCP-first.
- **New track: Deployment & Integration** 🌐 — four modules between Framework Comparison (20) and the Capstone (99):
  - `21_AdkApiSurface/` — `adk api_server`, HTTP/SSE/WS endpoints, REST shapes, wrapping in FastAPI.
  - `22_DeploymentModels/` — Cloud Run vs Agent Engine (Runtime); session persistence, scaling, cold start, auth, observability differences.
  - `23_FrontendIntegration/` — custom SPA, A2UI client, user_id/session lifecycle from the client, SSE/WS from the browser, auth context propagation.
  - `24_ChannelIntegrations/` — webhook → Runner adapter pattern, Slack bot, Google Chat app, Discord, long-running responses on chat platforms.
- **6 new detours**: `Cloud_Run`, `AgentEngine`, `FastAPI_for_ADK`, `SignedUrls_GCS`, `Slack_Bots`, `GoogleChat_Apps`.
- `MAP.md` updated: new track added, detour grid extended with a 🌐 Deploy column, legend gained 🌐.
- `Contents.md` updated: 04A inserted after 04; new track + detours listed.

### Why
- The user asked whether artifacts/multimedia/heavy-data were covered (they weren't) and whether the ADK API/frontend/Cloud-Run-vs-Agent-Engine/Slack/Google-Chat story had a home (it didn't). Both gaps were real and structural — patching them with extra `InProduction` blurbs would have buried them. New module + new track is the honest fix.

---

## [0.1.0] - 2026-05-27

Initial course scaffold. ADK Python 2.0 GA targeted. Docs snapshot at 2026-05-27.

### Added
- Repo-root files: [README.md](README.md), [AGENTS.md](AGENTS.md) (the AI-tutor operating manual), [MAP.md](MAP.md), [Contents.md](Contents.md), [PROGRESS.md](PROGRESS.md) (cursor at `00_Setup/00_Overview`), [student_profile.md](student_profile.md) (empty template).
- Top-level directories: `Notes/` (with empty module folders 00–20, 99, `Detours/`, `Updates/`, `_TEMPLATE_MODULE/`), `Drills/`, `Solutions/`, `Work/`, `Reference/CheatSheets/`.
- Docs snapshot: [Reference/docs_snapshot.md](Reference/docs_snapshot.md) — pins ADK 2.0 GA, fetch date 2026-05-27, source <https://adk.dev/>, refresh cadence 4 weeks.
- ADK 2.0 release-note absorption: [Notes/Updates/2026-05_adk-2.0.md](Notes/Updates/2026-05_adk-2.0.md) — graph workflows, collaborative agents, Visual Builder, Ambient Agents, Resume/Cancel, Agent Config, Skills, Context caching/compression, Session rewind/migrate. Legacy Sequential/Parallel/Loop templates still supported.
- Authoring recipe: [Notes/_AUTHORING.md](Notes/_AUTHORING.md) — how to add a module, detour, and release-update entry.
- Module template: [Notes/_TEMPLATE_MODULE/](Notes/_TEMPLATE_MODULE/) — copyable skeleton (`00_Overview`, `01_FirstConcept`, `05_DissectingSample`, `06_InProduction`, `07_KnowledgeCheck.yml`, `08_MiniDrill.yml`, `AGENTS.md`, `_figures/`).
- Cheat sheets in [Reference/CheatSheets/](Reference/CheatSheets/): `llmagent_signature.md`, `runner_session_lifecycle.md`, `state_prefixes.md`, `event_actions.md`, `tool_authoring.md`, `callback_signatures.md`, `a2a_mcp_quickref.md`.
- Student sandbox starter: [Work/_template_run.py](Work/_template_run.py) — runnable `InMemorySessionService` + `LlmAgent` + `runner.run_async(...)` loop against Gemini 2.5 Flash.

### Status
- **Phase 0 — Scaffolding & format MVP**: in progress. Repo-root + cheat sheets + template + Updates entry shipped. Modules `00_Setup/` and `01_Foundations/` still to author before the Phase 0 dogfood gate.
- All module folders exist as empty directories so the navigation links from [Contents.md](Contents.md) and [MAP.md](MAP.md) do not 404; content lands in subsequent phases.
