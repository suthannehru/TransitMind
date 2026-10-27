# TransitMind

A natural-language assistant for the NYC subway system. It answers questions about routes, live train positions and service alerts by calling tools backed by the MTA GTFS and GTFS-realtime feeds.

## Tools

| Tool | Purpose |
|---|---|
| `find_route` | Resolves the two station names to stops and finds the route between them |
| `get_service_alerts` | Lists service alerts for a line |
| `get_live_positions` | Describes where the active trains on a line are, as readable sentences |

The Staten Island Railway is referenced as `SI`.

## Station lookup

`find_route` turns a station name into a stop ID with hybrid retrieval over a Qdrant collection called `stations`. Each station is stored as one point with two named vectors:

- `dense`: a 384-dimension `all-MiniLM-L6-v2` embedding, compared with cosine distance. It matches meaning.
- `sparse`: BM25 weights from fastembed (`Qdrant/bm25`), with Qdrant's IDF modifier enabled. It matches exact tokens such as `63` or `Flushing`.

At query time `query_stop` in `graph/routing.py` searches both vectors (top 20 each) and merges the two rankings with reciprocal rank fusion (RRF). The top 3 fused results are returned and the first one is used. The collection is built by `python -m transitmind.static_kb.loader`, which runs as the `loader` service in `docker-compose.yml`. If the collection already exists the loader skips creating it, so delete the `qdrant_data` volume after changing the vector config.

Both embedding models are downloaded at image build time.

## Evaluation

The eval runs every question in `src/transitmind/eval/test_questions.py` through the assistant and scores it on tool selection and answer faithfulness. Raw results are written to `results/evals_output.json`. The `results/` folder is git-ignored.

```
python -m transitmind.eval.run_eval
```

### Metrics

Latest run: 130 questions, with hybrid station lookup.

| Metric | Result |
|---|---|
| Passed | 121 / 130 (93.1%) |
| Faithful | 102 / 109 judged (93.6%) |
| Average tool precision | 0.946 |
| Average tool recall | 0.958 |
| Hit tool-call limit | 0 |

- Precision is the share of called tools that were expected. Recall is the share of expected tools that were called.
- 21 questions were not judged for faithfulness, including all 15 `no_tools` questions. They are left out of the faithful denominator.
- Averages cover all 130 questions. The `no_tools` questions score 1.0 on both, which lifts the averages slightly.
- LLM output varies between runs, so a difference of a question or two is not meaningful.

### Dense-only vs hybrid

The same 130 questions run with dense-only station lookup and with hybrid lookup:

| Metric | Dense only | Hybrid |
|---|---|---|
| Passed | 109 / 130 (83.8%) | 121 / 130 (93.1%) |
| Faithful | 98 / 113 judged (86.7%) | 102 / 109 judged (93.6%) |
| Average tool precision | 0.924 | 0.946 |
| Average tool recall | 0.978 | 0.958 |

Hybrid fixed 17 questions and broke 5. Most of the fixes were station-resolution failures, such as the Kew Gardens to Sheepshead Bay, St George to Tottenville and Great Kills questions. Four of the five regressions are the Bedford Av and 8 Av pair (see Known issues). The faithful counts are not strictly comparable because a different set of questions was judged in each run.

### Results by category

| Category | Passed | Faithful | Avg precision | Avg recall |
|---|---|---|---|---|
| train_position | 24 / 25 | 21 / 25 | 0.98 | 1.00 |
| service_alerts_train_position | 5 / 5 | 5 / 5 | 1.00 | 1.00 |
| no_tools | 15 / 15 | not judged | 1.00 | 1.00 |
| service_alerts | 23 / 25 | 23 / 25 | 0.96 | 1.00 |
| routing | 26 / 30 | 29 / 30 | 0.87 | 0.87 |
| messy_input | 14 / 15 | 9 / 9 | 0.93 | 0.93 |
| routing_train_position | 4 / 5 | 5 / 5 | 0.90 | 0.90 |
| routing_service_alerts | 5 / 5 | 5 / 5 | 1.00 | 1.00 |
| routing_service_alerts_train_position | 5 / 5 | 5 / 5 | 1.00 | 1.00 |

### Failures (9)

**Wrong station resolved (6)**
- Four questions about Bedford Av and 8 Av (route, reversed route, messy phrasing, and combined with the L train positions). `find_route` resolved "Bedford Av" to Bedford-Nostrand Avs on the G, so the route went G then L instead of the direct L trip.
- "Lexington Av/63 St to 72 St on the Q" and "Brighton Beach to 72 St" scored 0 on precision and recall. Two different stations are named "72 St" (on the B/C and on the Q).

**Called a tool that wasn't expected (3)**
- "How's the 3 running this morning?" and "What's going on with the R right now?" also called `get_live_positions`.
- "Show me the current locations of the 2 trains" called `get_live_positions` twice, and the answer was judged unfaithful.

## Known issues

- Exact-name matches can lose to near matches. For "Bedford Av", `Bedford-Nostrand Avs` and `Bedford Av` are close to tied after fusion, and the order can flip between runs. An exact-name boost before or after fusion would likely fix it.
- Stations that share a name, such as the two "72 St" stations, are resolved by taking the first result. The code does not ask which line is meant.
- Faithfulness failures are now mostly in `train_position`: 4 of the 7 unfaithful answers, with 2 in `service_alerts` and 1 in `routing`.
