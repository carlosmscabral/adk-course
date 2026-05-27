---
module: 03_Tools
page: 09_LongRunningTool
title: LongRunningFunctionTool — for slow tools (mention)
estimated_minutes: 10
prereqs: [03_Tools/08]
concepts: [LongRunningFunctionTool, progress-event, generator]
icon: 🧠
in_production: false
detours_suggested: []
---

[← Prev: 03_Tools/08_AgentToolPreview](08_AgentToolPreview.md)  [↑ Map](../../MAP.md)  [Next: 03_Tools/10_DissectingSample →]

You are here: 🗺 Foundation Track ▸ 03 Tools ▸ 09 LongRunningFunctionTool

# 🧠 `LongRunningFunctionTool` — mention only

For Foundation Track, a one-page heads-up. Module 12 (Code Execution) and Module 18 (Streaming) deepen this.

## 🧠 The problem

A `FunctionTool` returns once. The whole tool call blocks the agent loop until the function returns. That's fine for `add(3, 4)` — terrible for `train_model()` or `transcode_video()` which take minutes and have meaningful intermediate progress.

## 🧠 The fix

A `LongRunningFunctionTool` is a **generator** — it `yield`s progress events along the way and the agent loop forwards them as ADK events. The tool can stream "20%... 40%... 60%..." back to the agent (and to the user, via the streaming UI) instead of going silent for 5 minutes.

```python
from google.adk.tools import LongRunningFunctionTool
from typing import Generator


def transcode(input_path: str) -> Generator[dict, None, dict]:
    """Transcode a video file. Yields progress as a percentage."""
    for pct in range(0, 100, 10):
        # ... do real work ...
        yield {"progress_pct": pct}
    return {"status": "complete", "output_path": "out.mp4"}


agent = LlmAgent(
    ...,
    tools=[LongRunningFunctionTool(transcode)],
)
```

The `yield`ed dicts become tool-progress events; the final `return` value is the tool result the LLM sees.

## 🧠 When to use

* Anything > ~30 seconds.
* Anything with meaningful intermediate progress.
* Background jobs you want to surface to the user.

For **truly async** work (kick off a job, poll for completion later), see Module 12's pattern for resumability.

## ❓ Sniff test

> ❓ **Ask the student:** would `get_weather(city)` (HTTP call to a weather API, typically <500ms) be a `LongRunningFunctionTool`?
> *(Expected: no — way too short to be worth the complexity. Plain `FunctionTool`.)*

> 🛠 **Have the student do this:** scan `adk-samples/python/agents/` for any file that imports `LongRunningFunctionTool`. (Hint: it's used in `agent-skills-tutorial`, among others.) Just notice the shape — they don't need to read the implementation yet.

> 🤖 **Tutor:** if the student is itching to build one, hold them off — there's a more natural place to do this in Module 12 (Code Execution). Foundation Track stays on short, synchronous tools.

---

[← Prev: 03_Tools/08_AgentToolPreview](08_AgentToolPreview.md)  [↑ Map](../../MAP.md)  [Next: 03_Tools/10_DissectingSample →]
