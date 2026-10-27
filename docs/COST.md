# TransitMind — Cost

All numbers come from `results/evals_output.json`: one eval run of 130 questions, using the token counts and costs that `run_eval.py` records through `compute_cost`. The same function feeds the `api_metrics` log line on `/ask`, so production logging uses the same arithmetic.

## Pricing used

| Role | Model | Input / 1M tokens | Output / 1M tokens |
|---|---|---|---|
| Agent | `gpt-4o-mini` | $0.15 | $0.60 |
| Eval judge | `claude-sonnet-5-5` | $2.00 | $10.00 |

Prices are the values in `.env.example`. If the provider changes its prices, update them there and recompute.

## Cost per query (agent)

| | Tokens | Cost |
|---|---|---|
| Input | 100,442 total, 773 mean per query | $0.0151 total |
| Output | 21,648 total, 167 mean per query | $0.0130 total |
| **Total (130 queries)** | 122,090 | **$0.0281** |
| **Mean per query** | 940 | **$0.000216** |

- Median query: 739 input and 97 output tokens. Max query: 2,325 input and 624 output tokens.
- p95 cost per query is $0.00049 and the max is $0.00064, so the worst case is about 3x the mean.
- Input is 82% of tokens but only 54% of cost, because output tokens cost 4x as much.
- Mean tool calls per query is 1.05, and no query hit the iteration limit.

### By category

| Category | Queries | Mean cost | Mean input tokens |
|---|---|---|---|
| no_tools | 15 | $0.00007 | 321 |
| messy_input | 15 | $0.00015 | 602 |
| service_alerts | 25 | $0.00015 | 728 |
| routing | 30 | $0.00018 | 756 |
| routing_service_alerts | 5 | $0.00025 | 866 |
| train_position | 25 | $0.00035 | 1,031 |
| routing_service_alerts_train_position | 5 | $0.00038 | 1,029 |
| service_alerts_train_position | 5 | $0.00038 | 1,043 |
| routing_train_position | 5 | $0.00040 | 1,053 |

`no_tools` queries show the fixed floor. About 320 input tokens of system prompt and tool schemas are sent on every request. Anything that returns live train positions costs about 2x a routing query, because the position payload is large.

## Breakdown

| Component | Cost per query |
|---|---|
| LLM input | $0.000116 |
| LLM output | $0.000100 |
| Embeddings (station lookup) | $0 |

Station lookup uses `all-MiniLM-L6-v2` and BM25 (`Qdrant/bm25`), both run locally, so there's no per-query embedding API charge. Their cost is compute (CPU time in the container) and a memory footprint, not tokens. Qdrant runs as a sidecar, and the MTA GTFS-RT feeds are free. These are infrastructure costs and are not included in the per-query figure.

## Scale estimates

At the mean of $0.000216 per query, with the eval mix as the traffic assumption:

| Volume | Per day | Per month (30 d) |
|---|---|---|
| 1,000 queries/day | $0.22 | $6.5 |
| 100,000 queries/day | $21.6 | $648 |

Treat these as an estimate with a band. At the p95 cost ($0.00049) per query, 100k/day is about $49/day. The eval mix is 130 hand-written questions, with about 31% (40 of 130) involving live train positions. Real traffic could skew toward positions, which would push the mean toward $0.00035. A position-heavy mix puts 100k/day near $35/day.

At this volume the LLM bill is small. Fixed infrastructure (hosting the app, Qdrant, Redis) is likely to be larger than the token cost at 1k/day.

## Eval cost (not part of serving)

| | Tokens (in / out) | Cost |
|---|---|---|
| Agent, 130 questions | 100,442 / 21,648 | $0.028 |
| Judge, 109 questions (21 not judged: 15 `no_tools` plus 6 others I haven't traced) | 93,620 / 4,209 | $0.229 |
| **Full run** | | **$0.257** |

The judge costs about 8x the agent, at $0.0021 per judged answer. This is because a judge call sees the question, tool responses and answer, and it runs on a pricier model. A full eval run is cheap enough to run on every change.

## Optimization levers

Ordered by expected payoff, using the numbers above.

1. **Trim the position tool payload.** Position queries cost about 2x others, and their input is about 300 tokens heavier. Returning only the fields the answer needs (line, direction, next stop) cuts input for the most expensive category without changing the model.
2. **Shrink the fixed prompt.** About 320 input tokens go out on every request. Tighter tool descriptions and system prompt reduce every query, but the floor is small, so expect savings of a few percent.
3. **Prompt caching.** OpenAI caches automatically only for prompts of 1,024 tokens or more, and the mean prompt here is 773. Most queries would not qualify, so this helps only the heaviest position queries unless the fixed prefix grows. Anthropic's caching is explicit and has a minimum size of its own, so check it before counting on savings.
4. **Cache common queries.** The Redis instance is configured but unused. Alert and position data change within minutes, so only a short TTL is safe (tens of seconds). Routing answers depend only on static data and could be cached for much longer.
5. **Reduce agent iterations.** The agent already averages 1.05 tool calls per query, so there's little left to remove.
6. **Cheaper model for tool-call turns.** The agent is already on a small model. Moving the final answer-writing turn to something cheaper is possible, but it risks the faithfulness score (currently 98 of 109), so measure it with the eval before adopting it.

## Caveats

- One run, one model, one question set. Cost per query isn't averaged across runs.
- The eval questions are hand-written, so real traffic may differ.
- The per-query cost counts model tokens only. It leaves out hosting, Qdrant, Redis, bandwidth and developer time.
- These figures were not checked against the provider's billing dashboard, only against the token counts the API returned.
