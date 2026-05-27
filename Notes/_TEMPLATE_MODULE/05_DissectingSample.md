---
module: NN_Topic
page: 05_DissectingSample
title: Dissecting <sample-name>
estimated_minutes: 40
prereqs: [NN_Topic/<last_concept_page>]
concepts: [<sample_anchor>, <pattern_demonstrated>]
icon: 🔬
in_production: false
detours_suggested: []
---

[← Prev: <last concept page>]  [↑ Map](../../MAP.md)  [Next: 06_InProduction →](06_InProduction.md)

You are here: 🗺 <Track Name> ▸ NN <Topic> ▸ 05 Dissecting Sample

# 🔬 Dissecting `<sample-name>`

> 🤖 **Tutor:** this page is a **guided read of real code**. The student should have the sample directory open in their editor as you walk them through it. Do not paste the code into chat — point at file paths and ask the student to read along.

Sample anchor: `/home/carloscabral/study/adk-samples/python/agents/<sample-name>/`

## Why this sample

(One paragraph: what this sample does, why it's a good fit for *this module's* concepts, and one thing it does that the student will not have seen elsewhere yet.)

## What we will trace

By the end of this read-through the student should be able to:
- Point at the file/line where the agent is constructed.
- Point at the file/line where the tool is registered.
- Point at the file/line where state is mutated.
- (… one or two more module-specific milestones …)

> 🛠 **Have the student run:** `ls /home/carloscabral/study/adk-samples/python/agents/<sample-name>/` and confirm the layout before we walk it.

## File-by-file walkthrough

### `<sample>/agent.py` — the root agent

(Quote the line that constructs the root agent. Explain each kwarg in 1 sentence. Reference the module's earlier concept pages: *"This is the `instruction=` we covered in 02 FirstAgent."*)

> ❓ **Ask the student:** "Why does this agent set `description=` even though it's the root and never gets routed to?"

### `<sample>/tools.py` (or wherever the tools live)

(Walk one tool. Name the docstring-as-schema pattern from 03 Tools. Ask the student to predict what the LLM "sees" when deciding to call this tool.)

### `<sample>/<sub_agent_or_other_file>.py`

(Continue for whichever files are load-bearing for this module's concepts. Skip files that are not relevant — do not pad the dissection.)

## Trace one turn

End-to-end on paper:

```
user query
  → root agent receives it
  → root agent's instruction + state interpolated
  → LLM call (model: <model>)
  → LLM emits tool call <X>
  → tool runs, returns <Y>
  → tool result fed back to LLM
  → LLM emits final text
  → Event yielded, content extracted
```

> 🛠 **Have the student run:** the sample (`adk run <sample-name>`) with one input. Capture the output. Compare to the trace above — did the actual execution match?

## Module concepts present in this sample

| Module concept | Where in the sample |
|---|---|
| (concept from 01) | `<file>:<line>` |
| (concept from 02) | `<file>:<line>` |
| (… etc) | |

---

[← Prev: <last concept page>]  [↑ Map](../../MAP.md)  [Next: 06_InProduction →](06_InProduction.md)
