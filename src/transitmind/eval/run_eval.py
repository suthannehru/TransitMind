from collections import defaultdict
import json
import random
import structlog
from transitmind.api.main import agent_loop
from transitmind.eval.test_questions import test_questions

logger = structlog.get_logger(__name__)


def run_test_questions(limit: int) -> None:
    outputs = []
    passes_category = defaultdict(lambda: defaultdict(int))

    num_q = min(limit, len(test_questions))
    shuffled_tq = random.sample(test_questions, num_q)

    # Iterate through the tools call to compute precision, recall, and pass
    for tq in shuffled_tq:
        response = agent_loop(tq["question"])
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
                excepted_tool_calls[f].add(frozenset(args.items()))

        # Assumption is that a function is not called twice with the same params
        for t in response["tools"]:
            agent_tool_calls_len += 1
            agent_tool_calls[t["function"]].add(frozenset(t["args"].items()))


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
            "called": response["tools"],
            "answer": response["content"],
            "passed": passed
        })
        outputs.append(output)

        with open("data/evals_output.json", "w") as f:
            json.dump(outputs, f, indent=2)

    for category, count in passes_category.items():
        logger.info("eval_pass_category", category=category, passes=count["passes"], total=count["total"])

if __name__ == "__main__":
    question_limit = 10
    run_test_questions(question_limit)