---
module: 18_StreamingLive
page: 09_InProduction
title: Streaming in production — costs, safety, session caps, telemetry
estimated_minutes: 25
prereqs: [18_StreamingLive/08]
concepts: [token-cost, guardrails-front-loaded, session-caps, resume-token, telemetry-sampling]
icon: 🚀
in_production: true
---

[← Prev: 18_StreamingLive/08_DissectingLiveSample]  [↑ Map](../../MAP.md)  [Next: 18_StreamingLive/10_KnowledgeCheck →]

You are here: 🗺 Production Track ▸ 18 Streaming & Live ▸ 09 In Production

## Token cost over a stream

You pay per chunk **emitted**, not per chunk shown. If the user barge-ins after the model has already streamed 400 tokens, you paid for 400 tokens of output. Native-audio models also charge per second of audio in/out — typically several times more than text.

Mitigations:
1. **Cap response length** in `RunConfig.speech_config` and/or system instruction ("Answer in 2-3 sentences").
2. **Tear down idle sessions** aggressively. A Live session that's been silent for 60 s is probably abandoned.
3. **Track tokens-per-session** as a primary metric. Alert on the 99th percentile, not the average.

## Partial-output safety — the gotcha that bites everyone

You **cannot** filter what you've already streamed. Once a sentence is on the user's screen, it's there. Post-hoc redaction is theater. Your guardrails MUST run **before** the bytes leave your server.

Two strategies:

1. **Front-load** (cheap, fast): system prompt + tool-call filtering done by `before_model_callback`. Catches the easy 80%.
2. **In-line** (expensive, slow): for high-stakes outputs (legal, medical), don't stream at all. Use `run_async` non-streaming, run a safety classifier on the full response, then yield. You lose live-typing UX in exchange for the ability to suppress.

For most use cases, front-load + a small post-stream "I have to redact the last paragraph" UX is the practical compromise.

> 🚀 **In Production**
>
> If you stream, accept that *some* unsafe outputs will reach the user. Plan the user-facing recovery (a "report this" button, a corrected follow-up) instead of pretending you can prevent it 100%.

## Session limits — Live has caps

- **Connection duration**: typically 10-15 min for half-cascade models, longer for some configurations. Plan a summarize-and-reset at ~80%.
- **Turn count**: soft cap; not usually the binding constraint.
- **Idle timeout**: a session with no activity for a few minutes is killed by the server.

Design pattern: keep a `last_activity` timestamp per session. At 80% of the cap, asynchronously summarize the conversation, store the summary in your session service, then on disconnect/reconnect bootstrap the new Live session with that summary in the system instruction.

## Reconnection strategy

See page 07 for `session_resumption`. The three layers:

1. **Server-side resume token** (`transparent=True` does this).
2. **Client-side audio replay buffer** — keep the last 2-3 s of model audio; on reconnect, replay so the user doesn't lose context.
3. **Application-level summary fallback** — if resume tokens have expired (a few minutes), pull a summary from your session store and restart the Live session with that context.

## Telemetry sampling — don't log every chunk

A 10-min audio session emits hundreds of events. Logging every one to Cloud Logging costs more than the inference. The pattern:

- **Aggregate** per session: total events, total tokens in/out, TTFA, P99 chunk latency, interruptions count.
- **Sample** detailed event traces at 1-5%. Tag with session ID so on-demand drill-down works.
- **Stream live** only the metrics that drive paging alerts (P99 latency, error rate).

```python
# pattern: lightweight per-chunk counter, heavy per-session flush
class StreamMetrics:
    def __init__(self):
        self.chunks = 0
        self.tokens_out = 0
        self.first_chunk_ts = None
        self.interruptions = 0

    def on_chunk(self, event, t):
        self.chunks += 1
        if self.first_chunk_ts is None:
            self.first_chunk_ts = t
        if event.interrupted:
            self.interruptions += 1
        # tokens estimate from event...

    def flush(self):
        logging.info("session_metrics", extra=self.__dict__)
```

## Checklist for shipping a Live feature

- [ ] `session_resumption` enabled
- [ ] Per-session token + cost meter wired to billing
- [ ] Interrupt handling tested end-to-end (cannot defer)
- [ ] Hard cap on response length in system instruction
- [ ] Idle session teardown < 60 s
- [ ] P50 + P99 TTFA tracked, alerted on
- [ ] Pre-stream guardrails (`before_model_callback`)
- [ ] Logging sampled at 1-5%, aggregated metrics always on
- [ ] Graceful fallback if Live API is unavailable (e.g. fall back to `run_async`)
- [ ] Microphone permission errors handled in the client UI

> ❓ **Ask the student:** "If you needed to add a profanity filter to a Live voice agent, where would you put it?" (Pre-model in a `before_model_callback` and as instruction in the system prompt. NOT in a post-stream filter — too late.)

[← Prev: 18_StreamingLive/08_DissectingLiveSample]  [↑ Map](../../MAP.md)  [Next: 18_StreamingLive/10_KnowledgeCheck →]
