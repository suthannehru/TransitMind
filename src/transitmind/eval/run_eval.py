from anthropic import Anthropic
from collections import defaultdict
import json
import random
import structlog
from transitmind.api.main import agent_loop
from transitmind.config import settings
from transitmind.eval.test_questions import test_questions

logger = structlog.get_logger(__name__)

# Create the client for the LLM-Judge
client = Anthropic(api_key=settings.anthropic_api_key)

def judge_faithfulness(question: str, tool_responses: list[dict], answer: str) -> tuple[bool, list[str]]:
    
    # Use the LLM to score the answer

    system_prompt = """You are a strict fact-checker that determines if the answer's factual claims are supported by the tool_responses.
        If not, determine which claims aren't backed by tool_responses 
        Respond only with a JSON object. The JSON has two keys which are 'faithful' and 'unsupported_claims' 
        faithful is mapped to a boolean. True if its faithful. unsupported_claims is a list of strings. 
        Each string is a reference to a unsupported claim. If the answer is faithful, the list is empty.
        Please don't add the usual fence of ```json in the beginning of the response and the ``` towards the end."""

    user_message = f"Question: {question}\n\nTools and responses: {json.dumps(tool_responses)}\n\nAnswer: {answer}"
    messages = [{"role": "user", "content": user_message}]

    response = client.messages.create(model="claude-sonnet-5-5",
                           system=system_prompt,
                           max_tokens=1000,
                           messages=messages
                           )
    # Use generator to pull the next text block. Returns None if iteration is done
    response_text = next((res.text for res in response.content if res.type == "text"), None)

    if not response_text:
        return (False, ["No response from LLM-Judge"])

    try:
        data = json.loads(response_text)
    except json.JSONDecodeError:
        return (False, ["Unparseable judge output"])

    return (data.get("faithful", False), data.get("unsupported_claims", []))
    

def run_test_questions(limit: int) -> None:
    outputs = []
    passes_category = defaultdict(lambda: defaultdict(int))

    num_q = min(limit, len(test_questions))
    shuffled_tq = random.sample(test_questions, num_q)

    # Iterate through the tools call to compute precision, recall, and pass
    for tq in shuffled_tq:

        response = agent_loop(tq["question"])

        #LLM-Judge
        faithful, unsupported_claims = judge_faithfulness(tq["question"], response["tools"], response["content"])
        passes_category[tq["category"]]["faithful"] += 1 if faithful else 0
        logger.warning("llm-judge-faithful-check", faithful=faithful, unsupported_claims=unsupported_claims)

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
            "faithful": faithful,
            "unsupported_claims": unsupported_claims,
            "passed": passed
        })
        outputs.append(output)

        with open("data/evals_output.json", "w") as f:
            json.dump(outputs, f, indent=2)

    for category, count in passes_category.items():
        logger.warning("eval_pass_category", category=category, passes=count["passes"], faithful=count["faithful"], total=count["total"])

if __name__ == "__main__":
    question_limit = 3
    run_test_questions(question_limit)