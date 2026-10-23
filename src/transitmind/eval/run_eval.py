from anthropic import Anthropic
from collections import defaultdict
import json
import random
import structlog
from transitmind.agent.graph import build_graph
from transitmind.agent.loop import agent_loop
from transitmind.agent.prompt import initial_params
from transitmind.config import settings
from transitmind.eval.test_questions import test_questions
from transitmind.graph.routing import G
import networkx as nx

logger = structlog.get_logger(__name__)

graph = build_graph()

def build_station_keys() -> dict[str, str]:
    """Maps each stop ID to one canonical ID shared by the stops in the same complex with the exact same name"""

    transfers = nx.Graph([(u, v) for u, v, d in G.edges(data=True) if d.get("transfer")])
    keys = {}

    for complex_stops in nx.connected_components(transfers):
        stops_by_name = defaultdict(list)
        for stop in complex_stops:
            stops_by_name[G.nodes[stop].get("name")].append(stop)
        for stops in stops_by_name.values():
            for stop in stops:
                keys[stop] = min(stops)

    return keys

station_keys = build_station_keys()

def canonical_args(args: dict) -> frozenset:
    """Treats stop IDs of the same station as equal, so the expected and called args are compared by station"""

    return frozenset((k, station_keys.get(v, v) if k.endswith("stop_id") else v) for k, v in args.items())

# Create the client for the LLM-Judge
client = Anthropic(api_key=settings.anthropic_api_key)

def judge_faithfulness(question: str, tool_responses: list[dict], answer: str) -> tuple[bool, list[str]]:
    
    # Use the LLM to score the answer

    system_prompt = """You are a strict fact-checker that determines if the answer's factual claims are supported by the tool_responses.
        If not, determine which claims aren't backed by tool_responses. Please don't add the usual fence of ```json in the beginning of the response and the ``` towards the end.
        The entire response must be a JSON object. Don't add any sort of reasonings before or after the JSON object. The keys are 'faithful' and 'unsupported_claims'. The value of 'faithful' is a boolean where true indicates faithful.
        The value of 'unsupported_claims' is a list of strings. Each string is a reason to explain the deviation between the answer and the tools response. The list is empty if faithful.
        """

    user_message = f"Question: {question}\n\nTools and responses: {json.dumps(tool_responses)}\n\nAnswer: {answer}"
    messages = [{"role": "user", "content": user_message}]

    response = client.messages.create(model="claude-sonnet-5-5",
                           system=system_prompt,
                           max_tokens=2500,
                           messages=messages
                           )
    # Use generator to pull the next text block. Returns None if iteration is done
    response_text = next((res.text for res in response.content if res.type == "text"), None)

    if not response_text:
        return (False, ["No response from LLM-Judge"])

    try:
        data = json.loads(response_text)
    except json.JSONDecodeError:
        logger.error("evals_response_error", output=response_text)
        return (False, ["Unparseable judge output"])

    return (data.get("faithful", False), data.get("unsupported_claims", []))
    

def run_test_questions(limit: int, use_graph: bool=True) -> None:
    outputs = []
    passes_category = defaultdict(lambda: defaultdict(int))

    num_q = min(limit, len(test_questions))
    shuffled_tq = random.sample(test_questions, num_q)

    # Iterate through the tools call to compute precision, recall, and pass
    for tq in shuffled_tq:

        if use_graph:
            response = graph.invoke(initial_params(tq["question"]))
            content = response["messages"][-1]["content"]
        else:
            response = agent_loop(tq["question"])
            content = response["content"]

        #LLM-Judge
        if response["tool_calls"]:
            faithful, unsupported_claims = judge_faithfulness(tq["question"], response["tool_calls"], content)
            if not faithful:
                logger.warning("llm-judge-faithful-check", response=response, faithful=faithful, unsupported_claims=unsupported_claims)
            passes_category[tq["category"]]["judged"] += 1
            passes_category[tq["category"]]["faithful"] += 1 if faithful else 0
        else:
            faithful, unsupported_claims = None, []

        output = tq.copy()

        expected_tools_len = 0
        agent_tool_calls_len = 0

        agent_tool_calls = defaultdict(set)
        excepted_tool_calls = dict()

        # Add all expected tools as a key
        for etc in tq["expected_tools"]:
            excepted_tool_calls[etc] = set()

        # Add the args as a frozenset
        for f, args in tq["expected_args"].items():
            if f not in excepted_tool_calls:
                raise KeyError("Expected args for a function that is not in the expected tool calls")

            if len(args):
                excepted_tool_calls[f].add(canonical_args(args))

        # Assumption is that a function is not called twice with the same params
        for t in response["tool_calls"]:
            agent_tool_calls_len += 1
            agent_tool_calls[t["function"]].add(canonical_args(t["args"]))


        for v in excepted_tool_calls.values():
            expected_tools_len += len(v) if len(v) > 0 else 1

        correct_calls = 0

        # Loop through each function and args pair
        # If they match remove from expected_tool_calls and increment correct_calls
        # args is the set of frozensets
        for f, args_set in agent_tool_calls.items():
            # Check if function call is expected
            if f in excepted_tool_calls:
                # Check if the set has any frozensets of arguments
                if len(excepted_tool_calls[f]):
                    # For each unique frozensets, iterate and see if there's a match
                    for args in args_set:
                        if f in excepted_tool_calls and args in excepted_tool_calls[f]:
                            correct_calls += 1
                            excepted_tool_calls[f].remove(args)
                            if len(excepted_tool_calls[f]) == 0:
                                del excepted_tool_calls[f]
                else:
                    correct_calls +=1
                    del excepted_tool_calls[f]



        # Metrics Computation
        # Precision: Total Correct Calls / Total Calls
        # Recalll Total Correct Calls / Total Calls it should've made
        precision = 1 if correct_calls == 0 and agent_tool_calls_len == 0 else 0 if agent_tool_calls_len == 0 else correct_calls / agent_tool_calls_len 
        recall = 1 if correct_calls == 0 and expected_tools_len == 0 else 0 if expected_tools_len == 0 else correct_calls / expected_tools_len 
        passed = False
        if len(excepted_tool_calls) == 0 and correct_calls == agent_tool_calls_len:
            passes_category[tq["category"]]["passes"] += 1
            passed = True

        passes_category[tq["category"]]["total"] += 1
        output.update({
            "precision": precision,
            "recall": recall,
            "hit_limit": response["hit_limit"],
            "called": response["tool_calls"],
            "answer": content,
            "faithful": faithful,
            "unsupported_claims": unsupported_claims,
            "passed": passed
        })
        outputs.append(output)

        with open("results/evals_output.json", "w") as f:
            json.dump(outputs, f, indent=2)

    for category, count in passes_category.items():
        logger.warning("eval_pass_category", category=category, passes=count["passes"], faithful=count["faithful"], judged=count["judged"], total=count["total"])

if __name__ == "__main__":
    question_limit = 130
    run_test_questions(question_limit, use_graph=settings.use_graph)