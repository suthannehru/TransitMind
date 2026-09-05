# TransitMind — NYC Transit Agentic RAG Assistant

## What this is

A natural-language assistant for the NYC subway system that answers questions like *"What's the fastest way from Bedford Ave to Times Square right now, and is anything delayed?"* by combining:

- **Static knowledge** (station topology, transfers, line relationships) — embedded in a vector DB, retrieved via RAG
- **Live data** (train positions, service alerts) — pulled in real time from MTA's free GTFS-Realtime feeds
- **Agentic reasoning** — an LLM agent that decides which tool to call (vector search, live feed, route-graph pathfinder) rather than a fixed retrieve-then-generate pipeline

The core engineering problem is **fusing a static knowledge base with a live, fast-changing data source inside a single agent loop** — a pattern that maps directly to real production RAG/agent systems, not a tutorial demo.

---

## Why this project (the core insight)

Most RAG portfolio projects fail on one of two axes:

- **Value** — does a real person actually want this, or does it just wrap a dataset that a normal search UI already handles fine?
- **Complexity** — does it force you past "embed → vector search → stuff into prompt," or is it ETL with an embedding step bolted on?

TransitMind clears both:

- **Value:** every NYC commuter has asked "is my train messed up right now" — a real, personal, frequent question that isn't well served by existing tools.
- **Complexity:** static-vs-live data fusion, protobuf parsing, graph pathfinding, and tool-selection logic are all genuinely hard problems — not busywork.

---

## Data sources (all free, no billing account required)

| Source | What it provides | Access |
|---|---|---|
| MTA GTFS-Realtime (subway) | Live train positions, updated ~every 30s | Free, no API key required (as of `nyct-gtfs` v2.0.0) |
| MTA GTFS-Realtime (alerts) | Live service alerts/disruptions | Free |
| MTA static GTFS | Station list, line topology, transfers, schedules | Free download, no key |

---

## Baseline architecture (the "sufficient" version)

```
POST /ask
  → LLM parses intent
  → retrieves static context (stations, transfers, line topology) from vector DB
  → fetches live feed (positions, alerts) from cache
  → fuses both into prompt
  → returns grounded natural-language answer
```

This alone is a legitimate, working RAG project. But per current 2026 AI/agentic hiring research, **basic RAG is now baseline, not a differentiator** — the "LangChain + Pinecone" project no longer signals readiness on its own. The features below are what move it from "sufficient" to "more than sufficient."

---

## Features required for "more than sufficient"

### 1. Agentic tool-calling (not fixed-pipeline RAG)
Replace the fixed retrieve→generate flow with an agent that **chooses** among tools each turn:
- `vector_search(query)` — static station/topology knowledge
- `get_live_positions(line)` — current GTFS-RT feed
- `get_service_alerts(line)` — current disruptions
- `find_route(origin, destination)` — graph pathfinding over the station network

This is what separates "agentic AI" (the fastest-growing hiring category) from a plain RAG pipeline.

### 2. Eval harness
The single most-cited signal of real (vs. tutorial) LLM experience in current hiring research. Build:
- A test set of ~30–50 transit questions with known-correct answers
- Automated scoring of retrieval quality (did it fetch the right stations/alerts?) and answer faithfulness (RAGAS or an LLM-judge)
- Results tracked and reported in the README with actual numbers

### 3. MCP server exposure
Wrap the tools (`vector_search`, `get_live_positions`, `find_route`, etc.) as an **MCP server** so any MCP-compatible client (including Claude) can use them. MCP fluency is now a named requirement in a large share of current listings.

### 4. Production deployment + observability
- Dockerized service
- Deployed on real infrastructure (AWS preferred — closes a cloud-platform gap alongside the AI-specific gaps)
- Logging for latency and token usage per request
- A short cost writeup: $ per query, estimated cost at scale — "cost modeling" is explicitly called out as an underrated but heavily-weighted interview signal

### 5. Safety/guardrails basics
- Handle tool-call failures gracefully (feed down, malformed response)
- Bound agent actions (no unbounded tool-call loops)
- Brief note on failure modes considered — mirrors "excessive agency" mitigation questions asked in interviews

---

## What "done" looks like

A deployed, observable, evaluated agentic system — not a notebook — where you can walk an interviewer through:
1. The static/live data fusion design
2. A specific eval result and what it told you
3. One failure mode you found and fixed
4. The cost-per-query number and how you'd optimize it at scale

That combination — not the RAG pipeline alone — is what the current hiring bar is actually asking for.
