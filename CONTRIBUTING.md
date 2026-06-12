# Contributing to Awesome Agent Memory

Thanks for helping keep this list useful! Contributions of new products, papers, benchmarks, tutorials, and articles are all welcome — as are link fixes and better categorization.

## What belongs here

- **Products**: systems whose primary purpose is memory for LLM/MLLM agents (memory layers, knowledge bases for agents, memory MCP servers, etc.).
- **Papers / Benchmarks / Surveys**: peer-reviewed or arXiv work on agent memory, long-term context, retrieval-augmented memory, parametric memory, continual learning, or memory evaluation.
- **Tutorials / Articles / Workshops**: substantial educational or editorial content about agent memory (not product announcements).

General-purpose vector databases, RAG frameworks, or agent frameworks where memory is a minor feature are out of scope.

## Entry format

### Open-Source products

Ordered by GitHub star count (descending). Use a numbered entry with a star badge:

```markdown
N. **[Name](https://homepage)**
     ![Star](https://img.shields.io/github/stars/owner/repo.svg?style=social&label=Star)
     [[code](https://github.com/owner/repo)]
     [[paper](https://arxiv.org/abs/XXXX.XXXXX)]
     _One-line factual description (≤ 25 words)._
```

Place the new entry at the position matching its current star count.

### Closed-Source products

Unnumbered bullet, no star badge, appended to the end of the section:

```markdown
-  [Name](https://homepage)
   [[blog](https://...)]
   _One-line factual description (≤ 25 words)._
```

### Papers, benchmarks, surveys

Grouped by year (newest first). **Bold** the title if reproducible code is publicly available, and add the `[[code](...)]` link:

```markdown
- **[Paper Title](https://arxiv.org/abs/XXXX.XXXXX)**
    [[code](https://github.com/owner/repo)]
```

## Style rules

- Descriptions are factual, not promotional — no superlatives, pricing, or marketing copy.
- Link to primary sources (official homepage, arXiv abstract page, GitHub repo).
- Use LF line endings (enforced by `.gitattributes`); please don't let your editor convert the file to CRLF.
- One resource per PR is easiest to review, but related batches are fine.

## Before submitting

1. Check the resource isn't already listed (search the README — projects sometimes appear under a different name).
2. Verify all links resolve.
3. Confirm placement: correct section, correct year group, correct star-rank position.
