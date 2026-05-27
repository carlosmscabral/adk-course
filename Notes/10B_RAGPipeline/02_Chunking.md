---
module: 10B_RAGPipeline
page: 02_Chunking
title: Chunking — three strategies
estimated_minutes: 25
prereqs: [10B_RAGPipeline/01]
concepts: [fixed-size-chunking, sentence-aware, semantic-chunking, overlap, stride]
icon: 🧠
in_production: true
detours_suggested: []
---

[← Prev: 10B_RAGPipeline/01_RAGConcepts] [↑ Map](../../MAP.md) [Next: 10B_RAGPipeline/03_HandRolledRAG →]

You are here: 🗺 Data & GCP Track ▸ 10B RAG Pipeline ▸ 02 Chunking

---

## 🧠 The fundamental trade-off

```
small chunks                                          large chunks
   ────────────────────────────────────────────────────────────►
   high precision                                  high context
   more vectors ($$$)                              fewer vectors
   may miss surrounding context                    may bury the answer
```

You're picking a point on this slider. The right point depends on the *query distribution*. Short Q&A → small. Long-form synthesis → larger.

## 🛠 Strategy 1: fixed-size

Split every N tokens (or N characters). Easiest. Worst quality.

```python
>>> def chunk_fixed(text: str, size: int = 500, stride: int = 100) -> list[str]:
...     chunks = []
...     i = 0
...     while i < len(text):
...         chunks.append(text[i : i + size])
...         i += size - stride
...     return chunks
...
>>> para = "Python is a language. Created in 1991. Used widely. Object-oriented. ..."
>>> chunks = chunk_fixed(para, size=30, stride=10)
>>> chunks
['Python is a language. Created', 'ge. Created in 1991. Used wide', 'd. Used widely. Object-oriente', ...]
```

`stride` = overlap. Why overlap? A sentence cut at chunk boundary loses meaning. Overlap by ~20% of chunk size to give the cut sentence a second chance in the next chunk.

## 🛠 Strategy 2: sentence-aware

Chunk on sentence boundaries, pack until you hit a budget.

```python
>>> import re
>>> def chunk_sentences(text: str, max_chars: int = 1000) -> list[str]:
...     sentences = re.split(r'(?<=[.!?])\s+', text)
...     chunks, buf = [], ""
...     for s in sentences:
...         if len(buf) + len(s) > max_chars and buf:
...             chunks.append(buf.strip())
...             buf = s
...         else:
...             buf += " " + s
...     if buf:
...         chunks.append(buf.strip())
...     return chunks
```

Better quality than fixed: sentences aren't cut. Cheap to implement. Still naive about *topic* boundaries.

## 🛠 Strategy 3: semantic chunking

Embed sentences, find where the embedding drift is large, split there. Better quality. Slower + more expensive (embed cost during chunking).

```python
def chunk_semantic(text: str, threshold: float = 0.15) -> list[str]:
    sentences = split_into_sentences(text)
    embs = embed_documents(sentences)             # from 10A/02
    chunks, current = [], [sentences[0]]
    for i in range(1, len(sentences)):
        sim = cos(embs[i - 1], embs[i])           # from 10A/01
        if sim < (1 - threshold):                  # big drift = topic change
            chunks.append(" ".join(current))
            current = []
        current.append(sentences[i])
    if current:
        chunks.append(" ".join(current))
    return chunks
```

Use semantic chunking when ingest is rare + quality matters. For volume / cheap pipelines, sentence-aware is the sweet spot.

## ⚠️ The "answer split across chunks" failure

If the answer to a question spans 3 sentences and your chunker cuts between sentence 2 and 3 — neither chunk has the full answer. Retrieval finds one chunk, the LLM gives an incomplete answer.

**Mitigations:**

1. Larger chunks (trade precision for safety).
2. Overlap / stride (the next chunk has sentence 3).
3. Retrieve top-k > 1 and trust the LLM to stitch.
4. Add **parent-doc retrieval** (retrieve small for matching, return larger window for context).

## 🛠 Have the student run

> 🛠 Take this paragraph:
>
> > "Python lists are mutable sequences. They support index access, slicing, and many in-place operations. Lists differ from tuples in that tuples are immutable. Tuples are often used for fixed records like coordinates. Both lists and tuples are iterable."
>
> Chunk it three ways: `chunk_fixed(size=80, stride=20)`, `chunk_sentences(max_chars=120)`, and manually-by-topic. Compare. Discuss: which would best answer "what's the difference between a list and a tuple?"

## 🚀 In Production

> **🚀 In Production**
> Chunk size is an **eval-driven decision**, not a guess. Build a tiny eval set of 20-30 representative questions, run with 256/512/1024 token chunks, measure `recall@5`. Pick the smallest size that hits your recall bar. Cheaper at index size, faster at retrieval, better LLM context.

## ❓ Check

> ❓ **Ask the student:** "Your retrieval consistently misses questions where the answer needs context from two adjacent paragraphs. What's the cheapest fix to try first?"
>
> Expected: increase chunk size or increase overlap (stride). Both buy more "context bridging" without changing the architecture.

## 🤖 Tutor

> Chunking feels boring but it's the single biggest lever on retrieval quality. Push the student to actually *try* the three strategies on a real doc. Don't let them just read about it.

---

[← Prev: 10B_RAGPipeline/01_RAGConcepts] [↑ Map](../../MAP.md) [Next: 10B_RAGPipeline/03_HandRolledRAG →]
