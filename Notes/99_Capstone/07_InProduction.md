---
module: 99_Capstone
page: 07_InProduction
title: What to do with the capstone after the course
estimated_minutes: 15
prereqs: [99_Capstone/06]
concepts: [post-course, deployment, iteration]
icon: 🚀
in_production: true
---

[← Prev: 99_Capstone/06_SelfReviewChecklist]  [↑ Map](../../MAP.md)  [Next: 99_Capstone/08_KnowledgeCheck →]

You are here: 🗺 Production Track ▸ 99 Capstone ▸ 07 In Production

# 🚀 After the course — what to do with this artifact

You have a working agent. Now what?

## Option A — Ship it (recommended)

Deploy the capstone as a real internal tool — for yourself, your team, or a friend. Real usage surfaces issues no eval ever will.

- **Track A** (Research): point it at a real question source — your Slack #questions channel, your bug tracker. Have it suggest answers humans can vote on.
- **Track B** (Code Reviewer): wire it to one PR's worth of test traffic. Have it post advisory comments (not blocking). Measure: agree rate vs human reviewer.
- **Track C** (PKH): use it daily. Log every recall miss as a bug.

Deploy targets:

- **Cloud Run** — simplest. `gcloud run deploy` from your repo; A2A endpoint becomes the service URL.
- **Vertex Agent Engine** — most managed. Targets ADK directly.
- **GKE** — most control. Containerize, write a Helm chart, wire HPA.

## Option B — Iterate weekly

Run the evals weekly. Add a case for every bug you find. Your `EvalSet` becomes a living regression suite.

Cadence:

- **Weekly**: `adk eval`; review any regressions; add cases for new failure modes.
- **Monthly**: review traces in Cloud Trace; identify slow spans; optimize.
- **Quarterly**: bump ADK version; re-run evals; fix anything that broke.

## Option C — Write a postmortem

Even if you don't deploy: write 1-2 pages on what you'd do differently. Topics:

- The hardest integration (probably memory or A2A).
- The thing that took longest (probably evals).
- The framework decision you'd revisit (be honest).
- The feature you cut and regret cutting.

A postmortem of a project no one shipped is **still valuable**. It's how you turn "I built a thing" into "I learned how to build things."

## Option D — Open-source it

Strip credentials, write a real README, push to GitHub. The agent-framework space is hungry for working examples. Yours might be the one that helps someone else's onboarding.

Things to do before pushing:

- `git secrets --scan` for accidentally committed keys.
- Pin all dependencies in `requirements.txt`.
- Add a LICENSE.
- Write a `CONTRIBUTING.md` with "what would help."

## The 6-month tickle

Set a calendar reminder for **6 months from today**. Open the capstone. Run the evals. See what's broken.

- The ADK version has moved.
- An LLM has been deprecated.
- A tool's auth has changed.

Patching the 6-month decay is a different skill than the original build. **Do this once.** It's the most realistic preview of production agent ownership you'll get.

## Anti-patterns

- **Letting it bit-rot.** A capstone that doesn't run in 3 months is a tombstone, not an artifact.
- **Over-investing.** This isn't your day job. 5 days build + occasional maintenance is plenty.
- **Treating it as a portfolio piece without using it.** Hiring managers ask about the production reality. "I ran the eval suite weekly for 4 months" is a story; "I built it once and never touched it" is not.

> 🚀 **In Production**
>
> The capstone is **a beginning**, not an end. The course taught you the surface; the capstone integrated it; production is where you learn what nobody can teach.

> ❓ **Ask the student:** "Which option (A/B/C/D) do you commit to in the next 30 days?" *(Get a verbal commitment. Have them write it in the README's 'next steps' section.)*

[← Prev: 99_Capstone/06_SelfReviewChecklist]  [↑ Map](../../MAP.md)  [Next: 99_Capstone/08_KnowledgeCheck →]
