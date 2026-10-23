from typing import Any

SYSTEM_PROMPT = "You are a personal assistant to help navigate the NYC MTA subway. Please provide all content provided by the tools in the exact same order. Use only information the tools returned: do not add transfers, lines, stations, directions, walking steps or advice that are not in the tool responses. If a tool returns an error or says no route exists, say so."

def build_messages(query: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query}
    ]    


def initial_params(query: str) -> dict[str, Any]:
    return {
        "messages": build_messages(query),
        "iteration": 0,
        "tool_calls": [],
        "hit_limit": False
    }