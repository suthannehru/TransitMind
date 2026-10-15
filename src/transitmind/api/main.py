from fastapi import FastAPI, HTTPException
import json
import logging
from openai import OpenAI
from pydantic import BaseModel
import structlog
from transitmind.config import settings
from transitmind.graph.routing import find_route
from transitmind.live.feed import get_live_positions, get_service_alerts
from transitmind.logging_config import configure_logging
from transitmind.resolver import parse_route_query
from transitmind.tools import tools_str_func, llm_tools

# Number of responses from the LLM to look at
NUM_RESPONSES = 0

# Set Logging
configure_logging(log_level=settings.log_level)
logger = structlog.getLogger(__name__)

# Create LLM Client
client = OpenAI(api_key=settings.openai_api_key)

def agent_loop(query: str):

    res = {}
    tool_calls = [] # Store tool_calls for evals

    messages = [
        {"role": "system", "content": "You are a personal assistant to help navigate the NYC MTA subway. Please provide all content provided by the tools in the exact same order. Use only information the tools returned: do not add transfers, lines, stations, directions, walking steps or advice that are not in the tool responses. If a tool returns an error or says no route exists, say so."},
        {"role": "user", "content": query}
    ]

    # Keep count of the agent iterations
    agent_iter = 0 

    while (agent_iter < settings.agent_max_iterations):
        llm_response = client.chat.completions.create(model=settings.llm_model, 
                                                messages=messages,
                                                tools=llm_tools)

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

    res["tools"] = tool_calls

    return res



class AskRequest(BaseModel):
    question: str

# uvicorn is the webserver listening on the given port for HTTP requests
# It validates the content and sends that as a readable format to FastAPI
# FastAPI is built on ASGI (Asynchronous Server Gateway Interface) implementation
app = FastAPI()

@app.post("/ask")
def ask(request: AskRequest):
    try:
        response = agent_loop(request.question)
        answer = response["content"]
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"answer": answer}