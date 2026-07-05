# TrackWise — Build Plan

## Context

You have `docs/PROJECT_SPEC.md` describing TrackWise, an agentic RAG assistant for the NYC subway, and no code yet. You've never built something like this before, but you want to implement every feature in the spec: agentic tool-calling, eval harness, MCP server, deployment-ready Docker, observability, safety.

The plan is **MVP-first**: get a working end-to-end answer in phase 1, then layer features. That way you always have something demoable, you learn the pieces incrementally, and each phase's "verification" step tells you the previous phase actually works.

**Stack decisions (locked in):**
- **Language:** Python 3.11+, FastAPI, Pydantic v2
- **LLM providers:** Anthropic Claude *and* OpenAI, behind a swappable interface
- **Vector DB:** Qdrant in a docker-compose sidecar (real client/server, ports cleanly to AWS later)
- **Cache:** Redis in docker-compose (ports 1:1 to ElastiCache)
- **Deploy:** Local Docker now, AWS path documented and designed-for (env-var config, structured JSON logs to stdout, no filesystem coupling in app code)
- **Testing/eval:** pytest + RAGAS + LLM-as-judge

---

## Repo layout (target)

```
TransitMind/
├── docs/PROJECT_SPEC.md          # exists
├── docs/PLAN.md                  # this file
├── docs/ARCHITECTURE.md          # phase 10
├── docs/COST.md                  # phase 9
├── docs/FAILURE_MODES.md         # phase 8
├── src/trackwise/
│   ├── config.py                 # pydantic-settings, all env vars
│   ├── logging.py                # structlog → JSON stdout
│   ├── api/main.py               # FastAPI app, POST /ask
│   ├── llm/                      # provider interface + Anthropic + OpenAI impls
│   ├── static_kb/                # GTFS parser, embedder, Qdrant loader
│   ├── live/                     # GTFS-RT fetcher + Redis cache
│   ├── graph/                    # networkx station graph + shortest_path
│   ├── tools/                    # the 4 agent tools + shared schemas
│   ├── agent/                    # agent loop (tool dispatch, bounds, retries)
│   ├── mcp_server/               # MCP entry point
│   └── eval/                     # eval runner + question set
├── data/                         # gitignored: raw GTFS zip, qdrant volume
├── tests/
├── docker-compose.yml            # app + qdrant + redis
├── Dockerfile
├── pyproject.toml
├── .env.example
└── README.md
```

---

## Phase 0 — Scaffold (half a day)

- Init git repo, `.gitignore` (include `.env`, `data/`, `__pycache__`, `.venv`)
- `pyproject.toml` with deps: `fastapi`, `uvicorn`, `pydantic-settings`, `structlog`, `httpx`, `redis`, `qdrant-client`, `sentence-transformers`, `gtfs-realtime-bindings`, `networkx`, `anthropic`, `openai`, `mcp`, `pytest`, `ragas`
- `docker-compose.yml` with three services: `app`, `qdrant:latest`, `redis:7-alpine` (with named volumes)
- `.env.example` listing every var: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `LLM_PROVIDER`, `LLM_MODEL`, `QDRANT_URL`, `REDIS_URL`, `MTA_FEED_BASE_URL`, `LOG_LEVEL`, `AGENT_MAX_ITERATIONS`
- `src/trackwise/config.py` — one `Settings` class, all env vars
- `src/trackwise/logging.py` — structlog configured for JSON output
- `README.md` skeleton

**Verify:** `docker compose up` brings up Qdrant + Redis. `python -c "from trackwise.config import settings; print(settings)"` works.

---

## Phase 1 — MVP slice (1–2 days)

**Goal:** one question, one grounded answer, end-to-end. Not agentic yet — fixed retrieve→generate. This is the "look, it works" moment.

- Download MTA static GTFS zip (one-time script into `data/gtfs/`)
- `static_kb/loader.py`: parse `stops.txt` → for ~20 stations, build docs of form: `"{stop_name}. Lines: {routes}. Transfers to: {nearby stops}."`
- Embed with `sentence-transformers/all-MiniLM-L6-v2` (local, fast, free) → upsert to Qdrant collection `stations`
- `live/fetcher.py`: fetch **one** GTFS-RT feed URL, parse alerts with `gtfs-realtime-bindings`, print them
- `api/main.py`: `POST /ask {question: str}` → embed question → Qdrant top-3 → stuff into prompt with system message → call Claude → return answer
- Hardcode Anthropic for this phase; you'll abstract in phase 5

**Verify:** `curl -X POST localhost:8000/ask -d '{"question":"Where is Bedford Ave?"}'` returns a grounded answer that names the L line.

---

## Phase 2 — Full static knowledge base (1 day)

- Extend loader to all ~472 stations
- Chunking strategy: one chunk per station containing name, lines, transfers, and adjacent stations (this is what you retrieve on)
- Build `graph/station_graph.py`: parse `stop_times.txt` to derive station adjacency by route → `networkx.Graph`, pickle to `data/graph.pkl`
- Persist Qdrant to a Docker volume so restarts don't re-embed

**Verify:** `python -m trackwise.static_kb.loader` completes in reasonable time. Query "L train stations in Brooklyn" retrieves relevant stops. `nx.shortest_path(g, "Bedford Av", "Times Sq-42 St")` returns a plausible path.

---

## Phase 3 — Live feed system (1 day)

- `live/fetcher.py`: async loop, poll each GTFS-RT feed (positions + alerts, one per line group) every 30s
- Store parsed results in Redis with 60s TTL and clear keys: `mta:positions:{line_group}`, `mta:alerts:{line_group}`
- Start the fetcher as a FastAPI startup background task
- `live/reader.py`: read-through functions that fetch from Redis, mark data as stale if TTL missed
- Handle feed-down: return `{"status": "stale", "last_seen": ...}` — never raise into the agent

**Verify:** After `docker compose up`, `redis-cli KEYS 'mta:*'` shows populated keys that update every ~30s. Kill the fetcher; readers return `stale` cleanly.

---

## Phase 4 — Tools (1 day)

Each tool is a plain Python function with a Pydantic input model and a structured return dict. LLM tool schemas are generated from the Pydantic models.

- `tools/vector_search.py` — semantic station search over Qdrant
- `tools/get_live_positions.py` — reads from `live/reader.py`
- `tools/get_service_alerts.py` — reads from `live/reader.py`
- `tools/find_route.py` — `nx.shortest_path` over the pickled graph, returns stops + line changes
- `tools/registry.py` — dict of `{name: (fn, input_model, description)}` used by both the agent and the MCP server

**Verify:** `pytest tests/tools/` — unit test each tool with mocked upstream (Qdrant / Redis). No LLM involved yet.

---

## Phase 5 — Agentic loop (2 days)

This is the heart of the project — where you replace the fixed pipeline with an LLM that chooses tools.

- `llm/base.py` — abstract interface: `chat_with_tools(messages, tools) -> LLMResponse` (response can be either final text or a list of tool calls)
- `llm/anthropic_provider.py` — uses Claude's native tool-use API
- `llm/openai_provider.py` — uses OpenAI function calling
- Provider chosen via `LLM_PROVIDER` env var
- `agent/loop.py`:
  1. System prompt: describes TrackWise, lists available tools
  2. Loop up to `AGENT_MAX_ITERATIONS` (default 5): call LLM → if tool_use, dispatch via `tools/registry.py`, append result, continue → if text, return
  3. On tool exception: append error message as tool result (don't crash)
- Replace phase-1 fixed pipeline in `POST /ask` with the agent loop

**Verify:** `curl -X POST /ask -d '{"question":"Fastest way from Bedford Ave to Times Square, and is anything delayed?"}'` — inspect logs to confirm the LLM called `find_route` and `get_service_alerts` (not just `vector_search`).

---

## Phase 6 — Eval harness (2 days)

The spec calls this out as *the* signal of real LLM experience. Do it well.

- `eval/questions.yaml` — 30–50 questions, each with: `question`, `expected_stations` (list), `expected_tools` (list, order-agnostic), `gold_answer` (reference text)
- `eval/retrieval.py` — for each question, run the agent, log which stations were retrieved, which tools were called → precision/recall vs expected
- `eval/faithfulness.py` — RAGAS `faithfulness` metric, or LLM-as-judge using Claude Haiku 4.5 (cheap) that scores agent answer against gold answer + retrieved context
- `eval/runner.py` — CLI: `python -m trackwise.eval` → prints per-question results + summary table, saves `eval/results/{timestamp}.json`
- Track numbers in README: "Retrieval precision: X%, faithfulness: Y%"

**Verify:** Runner completes on the full question set, prints numbers, saves JSON. Deliberately break a tool → numbers drop → you can point to which questions regressed. That's the story you tell interviewers.

---

## Phase 7 — MCP server (1 day)

- `mcp_server/server.py` — use Anthropic's `mcp` Python SDK
- Register the same tools from `tools/registry.py` — one code path, two surfaces (HTTP API + MCP)
- Entry point: `python -m trackwise.mcp_server`
- README section: how to connect from Claude Desktop (config JSON snippet)

**Verify:** Add TrackWise to Claude Desktop's MCP config, ask Claude "What subway lines run through Bedford Ave?" — it calls your `vector_search` tool.

---

## Phase 8 — Observability + safety (1 day)

- FastAPI middleware: log per-request latency, tool calls made, LLM tokens in/out (from provider response objects), estimated cost
- Structured log fields go to stdout as JSON — CloudWatch will pick these up unchanged when you deploy
- Hard bounds already in `agent/loop.py` (max iterations); add per-tool timeout via `asyncio.wait_for`
- `docs/FAILURE_MODES.md` — short doc listing: feed-down, malformed protobuf, LLM refuses to stop calling tools, tool exception, embedding drift. One paragraph each, with what you did about it.

**Verify:** Hit `/ask` a few times; logs show `latency_ms`, `input_tokens`, `output_tokens`, `estimated_cost_usd`, `tools_called`. Kill Qdrant → agent still returns something coherent (fallback message) instead of 500.

---

## Phase 9 — Cost writeup (half a day)

- Pull real numbers from your observability logs across the eval run
- `docs/COST.md`: current $/query, breakdown (embedding + LLM input + LLM output), estimated cost at 1k/day and 100k/day
- Optimization levers to discuss: prompt caching, Haiku for tool-call turns, cheaper embedding model, reducing agent iterations, caching common queries
- This document is what you show interviewers when they ask "how would this scale?"

**Verify:** Numbers in `COST.md` match what your logs actually reported.

---

## Phase 10 — Docker finalize + AWS design doc (1 day)

- Multi-stage `Dockerfile`: build stage installs deps, runtime stage is slim
- Confirm `docker compose up` starts everything cleanly on a fresh checkout
- `docs/ARCHITECTURE.md` — the AWS design you'd deploy tomorrow if asked:
  - ECR for the image
  - ECS Fargate task (app container)
  - ElastiCache Redis (replace `REDIS_URL`)
  - Qdrant sidecar container in the same task OR Qdrant Cloud (name your tradeoff)
  - ALB → task
  - Secrets Manager for API keys
  - CloudWatch for logs (already-JSON stdout picks up)
  - Diagram in the doc
- Optional: actually deploy (Fly.io or Railway is a shortcut if you want a real URL without AWS billing setup)

**Verify:** Fresh clone → `cp .env.example .env` → fill in API keys → `docker compose up` → `/ask` works. That's the "portfolio-ready" state.

---

## What to reuse rather than build

- **Don't write a GTFS-RT parser** — `gtfs-realtime-bindings` (official Google package) or `nyct-gtfs` handles the protobuf
- **Don't write an agent framework** — write the loop yourself in ~50 lines using each provider's native tool-use API. LangChain/LangGraph will hide too much for a first build
- **Don't build a custom eval framework** — RAGAS gives you `faithfulness`, `answer_relevancy`, `context_precision` out of the box
- **Don't roll your own MCP protocol** — use Anthropic's `mcp` Python SDK

---

## Rough timeline

If you work at ~4–6 focused hours a day and you're new to most of this: **3–4 weeks calendar time**, roughly. The eval harness (phase 6) and agent loop (phase 5) will be the hardest and most educational; budget extra there. Deploy and docs are the easy wins at the end.

---

## Overall verification (end state)

You should be able to walk an interviewer through:

1. `docker compose up` → curl `/ask` with a realistic transit question → grounded, correct-ish answer
2. Show the agent trace: LLM called `find_route` and `get_service_alerts`, fused both
3. `python -m trackwise.eval` → numbers → "here's a question class where retrieval was weak, here's what I changed"
4. Open `docs/COST.md` → real $/query → optimization plan
5. Point at `docs/FAILURE_MODES.md` → one specific failure you found and fixed
6. Connect Claude Desktop to your MCP server, ask a question live
