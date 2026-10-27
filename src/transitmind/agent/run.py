from transitmind.agent.loop import agent_loop
from transitmind.agent.prompt import initial_params
from transitmind.agent.graph import build_graph
from transitmind.config import settings
from typing import Any

graph = build_graph()

def run_agent(query: str) -> tuple[dict, str, int, int, int]:
    input_tokens = 0; output_tokens = 0; total_tokens = 0;
    if settings.use_graph:
        response = graph.invoke(initial_params(query))
        answer = response["messages"][-1]["content"]

        # Tokens Usage
        input_tokens = response["prompt_tokens"]
        output_tokens = response["completion_tokens"]
        total_tokens = response["total_tokens"]

    else:
        response = agent_loop(query)
        answer = response["content"]

        # Tokens Usage
        tokens = response["tokens"]
        input_tokens = tokens["prompt_tokens"]
        output_tokens = tokens["completion_tokens"]
        total_tokens = tokens["total_tokens"]

    return (response, answer, input_tokens, output_tokens, total_tokens)

def compute_cost(input_tokens: int, output_tokens: int, agent:bool = True) -> tuple[float, float]:

    if agent:
        in_price = settings.input_price_per_million
        out_price = settings.output_price_per_million
    else:
        in_price = settings.llm_judge_input_price_per_million
        out_price = settings.llm_judge_output_price_per_million
    
    # Compute cost
    input_cost = round((input_tokens / 1e6) * in_price, 6)
    output_cost = round((output_tokens / 1e6) * out_price, 6)

    return input_cost, output_cost