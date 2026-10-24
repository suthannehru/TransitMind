import json
import structlog
from transitmind.agent.client import NUM_RESPONSES, client
from transitmind.agent.prompt import build_messages
from transitmind.config import settings
from transitmind.tools import llm_tools, tools_str_func

logger = structlog.getLogger(__name__)

def agent_loop(query: str):

    res = {}
    tool_calls = [] # Store tool_calls for evals

    messages = build_messages(query)

    # Keep count of the agent iterations
    agent_iter = 0 

    # Log tokens usage
    res["tokens"] = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    while (agent_iter < settings.agent_max_iterations):
        llm_response = client.chat.completions.create(model=settings.llm_model, 
                                                messages=messages,
                                                tools=llm_tools)

        res["tokens"]["prompt_tokens"] += llm_response.usage.prompt_tokens
        res["tokens"]["completion_tokens"] += llm_response.usage.completion_tokens
        res["tokens"]["total_tokens"] += llm_response.usage.total_tokens

        response_choice = llm_response.choices[NUM_RESPONSES]

        # LLM has a final answer or there's no more tool calls
        if response_choice.finish_reason == "stop" or \
            not response_choice.message.tool_calls:
            break

        messages.append(response_choice.message.model_dump())
        # Using index as n = 1 and expect only one response
        for tool in response_choice.message.tool_calls:
            # tool.function.name - Function name as a string
            # tool.function.arguments - JSON string. Requires json.loads
            
            tool_func = tool.function.name
            try:
                args = json.loads(tool.function.arguments)
            # json.loads fails and args cannot be used                
            except json.JSONDecodeError:
                args = {}
            
            tool_func_info = {"function": tool_func, "args": args}

            try:
                func = tools_str_func[tool.function.name]
                output = func(**args)
                content = json.dumps(output)
                logger.info("tool_output", iteration=agent_iter, output=output)
            # Not an available tool
            # Log both the invalid function name and arguments
            except KeyError as k:
                content = str(k)
                logger.error("tool_output_err", function=tool.function.name)
            # 1. No shortest path exists between start and end stop id (find_route)
            # 2. Invalid start or/and end stop ID (find_route)
            except ValueError as v:
                content = str(v)
                logger.error("tool_output_err", err=content)
            except Exception as e:
                content = str(e)
                logger.error("tool_output_err", function=tool.function.name, err=content)

            tool_func_info["tool_response"] = content
            tool_calls.append(tool_func_info)
            messages.append({"role": "tool", "content": content, "tool_call_id": tool.id})

        agent_iter += 1

    # If max iterations is hit, there is no final answer
    if agent_iter >= settings.agent_max_iterations:
        res["content"] = "Hit the iteration limit. Failed to generate an answer"
        res["hit_limit"] = True
        logger.error("agent_max_iterations", iteration=agent_iter, output="")
    else:
        res["content"] = response_choice.message.content
        res["hit_limit"] = False
        logger.info("final_tool_output", iteration=agent_iter, output=response_choice.message.content)

    res["tool_calls"] = tool_calls

    return res
