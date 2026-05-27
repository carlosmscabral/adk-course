---
module: 10A_EmbeddingsVectorSearch
page: 01_WhatIsAnEmbedding
title: What is an embedding?
estimated_minutes: 20
prereqs: [10A_EmbeddingsVectorSearch/00]
concepts: [dense-vector, cosine, euclidean, semantic-similarity]
icon: 🧠
in_production: false
detours_suggested: []
---

[← Prev: 10A_EmbeddingsVectorSearch/00_Overview] [↑ Map](../../MAP.md) [Next: 10A_EmbeddingsVectorSearch/02_VertexAITextEmbeddings →]

You are here: 🗺 Data & GCP Track ▸ 10A Embeddings & Vector Search ▸ 01 What is an embedding?

---

## 🧠 The one-line definition

> An **embedding** is a fixed-length vector of floats that represents meaning.
> Two texts with similar meaning have vectors that point in similar directions.

That's it. The rest of this page is just sharpening what "similar direction" means.

## 📐 Cosine vs Euclidean

Two ways to measure "close":

```
cosine(u, v) = (u · v) / (||u|| · ||v||)        # angle between vectors, ignores length
euclidean(u, v) = sqrt(sum((u_i - v_i)^2))      # straight-line distance, length matters
```

For text embeddings, **cosine is the default** because length carries no semantic signal (embedding norms are typically already ~1). Vertex AI Vector Search defaults to cosine for text models.

## 🔎 A 2D intuition

```
_figures/embedding_2d.txt
```

```
         ^
         |    king *
         |   queen *
         |  monarch
         |
         |              pizza *
         |             burger *
         +--------------------->

cos(king, queen) ≈ 0.94    cos(king, pizza) ≈ 0.11
```

Royalty clusters in one direction, food in another. The model never sees the labels "royalty" or "food" — those clusters fall out of training on enough text.

## 🛠 By hand — cosine in 6 lines

```python
>>> import math
>>> def cos(u, v):
...     dot = sum(a*b for a, b in zip(u, v))
...     nu  = math.sqrt(sum(a*a for a in u))
...     nv  = math.sqrt(sum(b*b for b in v))
...     return dot / (nu * nv)
...
>>> cos([1, 0, 0], [1, 0, 0])
1.0
>>> cos([1, 0, 0], [0, 1, 0])
0.0
>>> cos([1, 0, 0], [-1, 0, 0])
-1.0
```

Range is `[-1, 1]`. For text-embedding-005, values you'll see in practice land in `[0.0, 1.0]` — negative cosines are rare for natural language.

> 🛠 **Have the student run:** the snippet above, then compute `cos([1,1], [2,2])` — should be `1.0`. Same direction, different magnitude. That's why we ignore magnitude.

## ⚠️ Dimensionality matters less than you think

`text-embedding-005` outputs **768** floats. `text-embedding-large-exp-03-07` outputs **3072**. More dims = more capacity, more storage, more index cost. **You usually want 768.** Only bump if eval scores demand it.

## ❓ Quick check

> ❓ **Ask the student:** "If embedding A is `[3, 0]` and embedding B is `[0, 3]`, what's their cosine similarity? Their Euclidean distance?"
>
> Expected: cosine = 0 (perpendicular, no semantic overlap). Euclidean ≈ 4.24.

## 🧭 If the student looks stuck

The "vector pointing in a direction = meaning" leap is the conceptual hump. Have them play with the cosine snippet for 5 min before moving on.

## 🤖 Tutor

> Don't dwell on the math. The reason embeddings work is empirical — the model learns the space. The student just needs the *what*, not the *why*. Move to 02 once they can run the cosine snippet.

---

[← Prev: 10A_EmbeddingsVectorSearch/00_Overview] [↑ Map](../../MAP.md) [Next: 10A_EmbeddingsVectorSearch/02_VertexAITextEmbeddings →]
