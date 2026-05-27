---
module: 4B_HumanInTheLoop
page: 09_ChatPlatformApprovals
title: Slack & Google Chat as approval surfaces — interactive messages, cards, callbacks
estimated_minutes: 25
prereqs: [4B_HumanInTheLoop/08]
concepts: [slack-interactivity, block-kit, google-chat-cards, action-callbacks, signing-secret]
icon: 🛠
in_production: true
detours_suggested: []
---

[← Prev: 08_FrontendDrivenApprovals](08_FrontendDrivenApprovals.md)  [↑ Map](../../MAP.md)  [Next: 10_DurableExecutionIntegrations →](10_DurableExecutionIntegrations.md)

You are here: 🗺 Foundation Track ▸ 4B HITL & Resume/Cancel ▸ 09 Chat Approvals

# 🛠 Slack & Google Chat as the approval surface

For internal-tooling agents, the right approval UI is often **the chat platform the team already lives in** — not a new web page. Slack and Google Chat both support **interactive messages** with buttons that POST back to your endpoint. They map cleanly onto the `requested_tool_confirmations` → resume contract.

This page sketches the back-end side. The full channel integration (auth, signing, message shapes, deploy) is in [24 Channel Integrations](../24_ChannelIntegrations/) — and the chat-app detours `[[Slack_Bots]]` and `[[GoogleChat_Apps]]` go deeper. This page focuses on the **HITL-specific glue.**

## Slack — the interactive message

When `requested_tool_confirmations` arrives, you post a Slack message with two buttons:

```python
# Block Kit JSON — the Slack message that fronts an approval
blocks = [
    {"type": "section", "text": {"type": "mrkdwn", "text": tc.hint}},
    {"type": "section", "text": {"type": "mrkdwn",
                                  "text": f"```{json.dumps(tc.payload)}```"}},
    {"type": "actions", "block_id": f"approve_{invocation_id}", "elements": [
        {"type": "button", "text": {"type": "plain_text", "text": "Approve"},
         "style": "primary",
         "value": json.dumps({"inv": invocation_id, "fc": fc_id, "decision": "y"})},
        {"type": "button", "text": {"type": "plain_text", "text": "Reject"},
         "style": "danger",
         "value": json.dumps({"inv": invocation_id, "fc": fc_id, "decision": "n"})},
    ]},
]
slack_client.chat_postMessage(channel=manager_id, blocks=blocks, text=tc.hint)
```

The user clicks **Approve** → Slack POSTs to your `/slack/interactivity` endpoint with the `value` blob. You parse it, build the resume payload, call `runner.run_async()`.

```python
# /slack/interactivity handler (FastAPI sketch)
@app.post("/slack/interactivity")
async def interactivity(req: Request):
    verify_slack_signature(req)                          # see [[Slack_Bots]]
    payload = json.loads((await req.form())["payload"])
    action = payload["actions"][0]
    blob = json.loads(action["value"])
    confirmed = blob["decision"] == "y"

    tc = ToolConfirmation(confirmed=confirmed, payload={})
    msg = Content(role="user", parts=[Part(function_response=FunctionResponse(
        id=blob["fc"], name="adk_request_confirmation",
        response=tc.model_dump(by_alias=True),
    ))])
    async for _ in runner.run_async(
        user_id=slack_user_to_app_user(payload["user"]["id"]),
        session_id=lookup_session(blob["inv"]),
        invocation_id=blob["inv"],
        new_message=msg,
    ):
        pass    # results stream back; you can post final text to Slack too
    return {"text": "Recorded."}
```

Three things doing work here:
- `verify_slack_signature` — *non-negotiable*; without it anyone can fake an approval. The Slack signing secret + HMAC dance is detoured in `[[Slack_Bots]]`.
- `slack_user_to_app_user` — your mapping from Slack user IDs to your app's users. Don't trust Slack's user blob; bind to your own identity.
- The `function_response.name` is the same `"adk_request_confirmation"` you've seen in pages 04 and 08 — the wire is identical.

## Google Chat — the same shape with Cards v2

Google Chat uses **Card v2** messages with `onClick.action.function` callbacks. The shape:

```python
card = {
    "header": {"title": "Expense approval needed"},
    "sections": [{"widgets": [
        {"textParagraph": {"text": tc.hint}},
        {"buttonList": {"buttons": [
            {"text": "Approve", "onClick": {"action": {
                "function": "approve", "parameters": [
                    {"key": "inv", "value": invocation_id},
                    {"key": "fc", "value": fc_id},
                ]}}},
            {"text": "Reject", "onClick": {"action": {
                "function": "reject", "parameters": [
                    {"key": "inv", "value": invocation_id},
                    {"key": "fc", "value": fc_id},
                ]}}},
        ]}},
    ]}],
}
```

Google Chat POSTs back to your bot endpoint with the action name and parameters. You build the same resume payload and call `runner.run_async()` — the runtime end is unchanged. Card grammar lives in `[[GoogleChat_Apps]]`.

## Identity binding — the only critical security note

Both Slack and Google Chat give you a **platform user ID** in the callback. **You must map that to your application's authenticated user** before honoring the resume. The threat:

1. Approver A's session id leaks (intern shares a debug log).
2. Attacker posts the "approve" button in their own Slack DM.
3. Slack POSTs to your endpoint with attacker's user id.
4. If you don't check that the user is *authorized to approve this specific pending action*, the attacker just approved A's $14k expense.

The fix is enforcement at the *handler*, not the *button*. The pending-approvals table from page 08 has an `approver_user_id` column; the handler verifies `slack_user_to_app_user(...) == approver_user_id` before calling `runner.run_async`. Anything less ships an exploit.

## Render the *outcome* back

After resume completes, post the agent's final reply back into the same channel (Slack: `chat.update` to replace the buttons with "Approved by @alice"; Google Chat: `messages.update` similarly). The audit story closes neatly: every approval lives in the channel where it was decided, alongside who clicked.

> ❓ **Ask the student:** "If Slack redelivers the interactivity POST (network flake), what protects you from double-resuming?" (The dedup token in the pending-approvals table. On the second POST, the row's `decided_at` is non-null — reject the duplicate.)

> 🛠 **Have the student:** sketch (on paper, no need to wire) the equivalent flow for their team's chat platform. The shape generalizes: button → callback → resume.

## 🚀 In Production

> **🚀 In Production**
>
> Chat-platform approvals are *delightful* until your bot's webhook URL leaks. Treat the webhook as a **security perimeter**: verify the platform signature on every request, dedupe on platform message id, require the user binding step above. Re-read [16 Production & Security](../16_ProductionSecurity/) before shipping a chat-driven approver.

---

[← Prev: 08_FrontendDrivenApprovals](08_FrontendDrivenApprovals.md)  [↑ Map](../../MAP.md)  [Next: 10_DurableExecutionIntegrations →](10_DurableExecutionIntegrations.md)
