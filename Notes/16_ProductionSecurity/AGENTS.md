# AGENTS.md — Module 16 Production & Security (teaching notes for the AI tutor)

## What the student should walk away knowing

- A named threat model for agents (8 classes from page 01).
- The prompt-injection taxonomy (direct / indirect / jailbreak / exfiltration) and a defense for each.
- Why authorization belongs at the tool, not the prompt.
- Secret-handling discipline: never in prompts, never in repos, never in spans.
- Seven concrete callback/plugin recipes they can copy into any agent.
- **The agent-vs-user identity split (page 06)**: SA-with-authz, user-asserted token, impersonation/token-exchange. They can name the right pattern for a given resource type.
- **When and how to wire `LlmAsAJudge` (page 07)**: which `JudgeOn` hooks default-on, cost per turn, how it composes with the rest of defense-in-depth.
- The six layers of defense-in-depth, and that they need at least three live.
- The session-poisoning bug and how `safety-plugins/` solves it.
- The split between LLM (fuzziness) and code (enforcement) shown by `policy-as-code/`.

## Pacing

- **Easy if:** student has shipped a security-conscious web service before. Skim pages 01-02; spend most time on the cookbook (05) and dissections (06-07).
- **Hard if:** student has only built proof-of-concept agents. Slow down at page 01 (let the threat model sink in) and at page 06 (read the LlmAsAJudge code line by line).

## Watch for these mistakes

- **"I'll put it in the system instruction."** This is the prompt-as-gatekeeper anti-pattern. Push them to a callback every time.
- **Filtering the response only, not the request.** PII leaks to the model. The model may then store / repeat / leak it.
- **Forgetting indirect injection.** The student assumes "I trust my RAG corpus." They shouldn't.
- **One layer thinking.** "I added a regex, am I safe?" No — page 10 § 1.
- **Same model for the judge.** Cost + injection-prone. The judge should be a cheaper, single-purpose model.
- **Persisting filtered content.** The most common subtle bug. Always set the state flag and short-circuit in `before_run_callback` — the pattern in `safety-plugins/`.
- **Conflating agent and user identity (page 06).** Student treats the SA as "the user" and ships an IDOR. Catch it before they get past Pattern A.
- **Cargo-culting all four `JudgeOn` hooks (page 07).** Quadruples cost. Make them justify each hook against a named threat.

## When to suggest a detour

- Student asks "what's a real example of indirect injection?" → suggest [[PromptInjection]] detour.
- Student asks about Pydantic for structured outputs → [[PY_pydantic]].
- Student asks about per-user state prefixes → [[04_SessionsState/02_StateScopes]].

## Mini-drill grading

- **Pass** = PII shows up redacted in the model-input span, and toxic output is replaced with a canned message. Decision log exists.
- **Stretch** = student added a third recipe (rate limit, cost cap, or tool-arg whitelist) and demonstrates it firing.
- **Common stumble** = student rate-limits the judge LLM itself by accident. Coach them to scope the rate limit to the *user-facing* model calls.

## Cross-link reminders

- 07 Callbacks — mechanics of `before_*` / `after_*` hooks.
- 13 Plugins — `BasePlugin` shape; runner-level wiring.
- 14 Evaluation — red-team eval cases.
- 15 Observability — guardrail decisions are observability data.
- 12 CodeExecution — sandbox layers referenced by Recipe 6.
- 10C BigQueryAgents — scan-byte cap (Recipe 7).
- 04 SessionsState — `user:` prefix used by Recipe 4 and by page 06.
- 02 FirstAgent — structured outputs defense referenced by page 02.
- 22 DeploymentModels § AuthAndIAM — platform side of the page-06 identity split.
- Detours/Cloud_Run, Detours/AgentEngine — where the SA actually gets attached.
