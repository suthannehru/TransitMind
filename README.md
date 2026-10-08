# TransitMind

A natural-language assistant for the NYC subway system. It answers questions about routes, live train positions and service alerts by calling tools backed by the MTA GTFS and GTFS-realtime feeds.

## Tools

| Tool | Purpose |
|---|---|
| `parse_route_query` | Resolves the stations named in a question to stop IDs |
| `find_route` | Finds the route between two stops |
| `get_service_alerts` | Lists service alerts for a line |
| `get_live_positions` | Describes where the active trains on a line are, as readable sentences |

The Staten Island Railway is referenced as `SI`.

## Evaluation

The eval runs every question in `src/transitmind/eval/test_questions.py` through the assistant and scores it on tool selection and answer faithfulness. Raw results are written to `results/evals_output.json`.

```
python -m transitmind.eval.run_eval
```

### Metrics

Latest run: 130 questions.

| Metric | Result |
|---|---|
| Passed | 116 / 130 (89.2%) |
| Faithful | 78 / 111 judged (70.3%) |
| Average tool precision | 0.953 |
| Average tool recall | 0.974 |
| Hit tool-call limit | 0 |

- Precision is the share of called tools that were expected. Recall is the share of expected tools that were called.
- 19 questions were not judged for faithfulness, including all 15 `no_tools` questions. They are left out of the faithful denominator.
- Averages cover all 130 questions. The `no_tools` questions score 1.0 on both, which lifts the averages slightly.

### Results by category

| Category | Passed | Faithful | Avg precision | Avg recall |
|---|---|---|---|---|
| train_position | 25 / 25 | 18 | 1.00 | 1.00 |
| service_alerts_train_position | 5 / 5 | 3 | 1.00 | 1.00 |
| no_tools | 15 / 15 | not judged | 1.00 | 1.00 |
| service_alerts | 22 / 25 | 20 | 0.94 | 1.00 |
| routing | 26 / 30 | 19 | 0.93 | 0.93 |
| messy_input | 13 / 15 | 9 | 0.87 | 1.00 |
| routing_train_position | 4 / 5 | 3 | 0.93 | 0.93 |
| routing_service_alerts | 4 / 5 | 3 | 0.93 | 0.93 |
| routing_service_alerts_train_position | 2 / 5 | 3 | 1.00 | 0.85 |

### Failures (14)

**Called a tool that wasn't expected (5)**
- "How's the 3 running this morning?", "How's the Staten Island Railway running today?" and "What's going on with the R right now?" also called `get_live_positions`.
- "How do I get to Sheepshead Bay?" and "Need a route to World Trade Center" expected no tools but called the routing tools.

**Skipped `find_route` (3)**
- Three `routing_service_alerts_train_position` questions never called `find_route`. These are the St George to Tottenville, Bedford Av to 8 Av and Flushing-Main St to Mets-Willets Point questions.

**Wrong or incomplete route results (5)**
- Astoria-Ditmars Blvd to Union Square, Sheepshead Bay to Lexington Av/63 St, Lexington Av/63 St to 72 St on the Q, and Brighton Beach to 72 St called the expected tools but scored 0.5 on precision and recall, and four were judged unfaithful.
- St George to Great Kills scored 0.67 on both, and the answer was judged unfaithful.

**Tool order (1)**
- Astoria-Ditmars Blvd to Union Square plus an N service check called `get_service_alerts` before `find_route`.

## Known issues

- Faithfulness is the weak point. 33 of 111 judged answers were marked unfaithful, mostly routing answers that over-interpret the bare station list from `find_route`.
- Several routing failures trace back to `parse_route_query` picking the wrong station.
