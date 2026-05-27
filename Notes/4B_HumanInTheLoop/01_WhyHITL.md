---
module: 4B_HumanInTheLoop
page: 01_WhyHITL
title: Why HITL — the three canonical cases
estimated_minutes: 15
prereqs: [4B_HumanInTheLoop/00]
concepts: [HITL-irreversible, HITL-ambiguous, HITL-policy-gate]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 02_RequestConfirmation →](02_RequestConfirmation.md)

You are here: 🗺 Foundation Track ▸ 4B HITL & Resume/Cancel ▸ 01 Why HITL

# 🧠 Why HITL

> 🤖 **Tutor:** before any code, drive a one-minute conversation: "name an agent action you would NOT let a model take without asking." The student's answer almost always falls into one of the three cases below.

An agent that never pauses for a human is **either toy or dangerous.** Production agents pause for one of three reasons.

## Case 1 — Irreversible actions

Sending an email. Deleting a file. Charging a card. Closing a Jira ticket. Posting to a public channel. The agent might be right 99% of the time — the 1% is the news headline. The rule: **if the action cannot be undone in one human gesture, request confirmation.**

```
agent: "I will delete /home/user/2024_taxes.pdf because it looks like a duplicate."
                                      ↓
                          PAUSE — ask the human
                                      ↓
agent: rm /home/user/2024_taxes.pdf   ← runs only after explicit approve
```

## Case 2 — Ambiguous intent

The agent has narrowed a request to two plausible interpretations. Cheaper to ask than to guess wrong.

```
user:  "Cancel my reservation."
agent: "I see two: dinner at Roister 7pm Friday, and Lyft Saturday airport.
        Which one?"
                                      ↓
                          PAUSE — wait for human
                                      ↓
user:  "The Lyft."
agent: <cancels Lyft>
```

A pause is much cheaper than the recovery cost of guessing wrong.

## Case 3 — Policy / compliance gates

The action is fine in principle, but **policy requires a named human in the audit log.** Expense reports over $10k. Outbound emails to customers. PRs to a production branch. The model is competent — the regulation says a human must sign.

```
agent: prepares $14,200 expense reimbursement
              ↓
        policy gate fires
              ↓
   manager (named in audit log) approves
              ↓
        payment dispatched
```

> 🛠 **Have the student:** for the project they care about most, list every tool the agent can call. Mark each one with `R` (reversible), `A` (could be ambiguous), or `G` (policy gate). The tools with no marks need no confirmation; everything else needs HITL.

## The rule (now we have three examples)

**Wrap any tool that can do real-world damage, branch on ambiguity, or trip a compliance gate behind an HITL pause.** Page 02 shows how, in seven lines.

> ❓ **Ask the student:** "Is reading a file ever HITL-worthy?" (Usually no — but if the file contains PII and reading it constitutes a privacy event under GDPR/HIPAA, it can fall under case 3.)

## 🚀 In Production

> **🚀 In Production**
>
> The first HITL bug every team ships: a tool that **logs the intent before the human approves**. The model says "I will delete X," that string lands in logs, the human rejects — but a security scanner now flags a "deletion event." Audit logs should record *both* the request and the decision (approve / reject / timeout). Page 12 has the full audit-log template.

---

[← Prev: 00_Overview](00_Overview.md)  [↑ Map](../../MAP.md)  [Next: 02_RequestConfirmation →](02_RequestConfirmation.md)
