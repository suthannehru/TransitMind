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

        agent_tool_calls = set()
        excepted_tool_calls = set(tq["expected_tools"])
        
        for t in response["tools"]:
            agent_tool_calls.add(t["function"])

        # Metrics Computation
        # Precision: Total Correct Calls / Total Calls
        # Recalll Total Correct Calls / Total Calls it should've made
        correct_calls = len(agent_tool_calls.intersection(excepted_tool_calls))
        precision = correct_calls / len(agent_tool_calls) if len(agent_tool_calls) != 0 else 0
        recall = correct_calls / len(excepted_tool_calls) if len(excepted_tool_calls) != 0 else 0
        passed = False
        if agent_tool_calls == excepted_tool_calls:
            passes_category[tq["category"]]["passes"] += 1
            passed = True

        passes_category[tq["category"]]["total"] += 1
        output.update({
            "precision": precision,
            "recall": recall,
            "hit_limit": response["hit_limit"],
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