from fastapi import FastAPI, HTTPException
import json
from openai import OpenAI
from pydantic import BaseModel
from transitmind.config import Settings
from transitmind.graph.routing import find_route
from transitmind.live.feed import get_live_postitions, get_service_alerts
from transitmind.resolver import parse_route_query

# Number of responses from the LLM to look at
NUM_RESPONSES = 0

tools_str_func = {
    "find_route": find_route,
    "get_live_positions": get_live_postitions,
    "get_service_alerts": get_service_alerts,
    "parse_route_query": parse_route_query
}

llm_tools = [
    {
        "type": "function",
        "function": {
            "name": "find_route",
            "description": "(graph/routing.py)Loads the station map and returns the shortest path between the stops as a list of station names",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_stop_id": {"type": "string", "description": "The stop ID of the start station"},
                    "end_stop_id": {"type": "string", "description": "The stop ID of the end station"}
                },
                "required": ["start_stop_id", "end_stop_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_live_positions",
            "description": "(live/feed.py) Given a line, return a list of dictionaries for every active train on that line",
            "parameters": {
                "type": "object",
                "properties": {
                    "line": {"type": "string", "description": "The subway line for which you need the active train positions"},
                },
                "required": ["line"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_service_alerts",
            "description": "(live/feed.py) Given a line, return a list of dictionaries for every service alert on that line",
            "parameters": {
                "type": "object",
                "properties": {
                    "line": {"type": "string", "description": "The subway line for which you need the service alerts for"},
                },
                "required": ["line"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "parse_route_query",
            "description": "(resolver.py) Splits a natural language question, 'X' to 'Y' and returns a tuple of start and end stop IDs",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The natural language question 'X' to 'Y'"},
                },
                "required": ["query"]
            }
        }
    },
]   


# Instantiate settings
settings = Settings()

# Create LLM Client
client = OpenAI(api_key=settings.openai_api_key)

def agent_loop(query: str):

    messages = [
        {"role": "system", "content": "You are a personal assistant to help navigate the NYC MTA subway."},
        {"role": "user", "content": query}
    ]

    # Keep count of the agent iterations
    agent_iter = 0 

    while (agent_iter < settings.agent_max_iterations):
        llm_response = client.chat.completions.create(model=settings.llm_model, 
                                                messages=messages,
                                                tools=llm_tools)

        response_choice = llm_response.choices[NUM_RESPONSES]

        # LLM has a final answer
        if response_choice.finish_reason == "stop":
            break

        messages.append(response_choice.message.model_dump())
            
        # Using index as n = 1 and expect only one response
        for tool in response_choice.message.tool_calls:
            # tool.function.name - Function name as a string
            # tool.function.arguments - JSON string. Requires json.loads
            try:
                func = tools_str_func[tool.function.name]
                args = json.loads(tool.function.arguments)
                output = func(**args)
                messages.append({"role": "tool", "content": json.dumps(output), "tool_call_id": tool.id})
                #print(output)
            except KeyError:
                print(f"The tool: {tool.function.name} is not available")

        agent_iter += 1


    print(f"It took {agent_iter} iterations to come to a conclusion")
    print(response_choice.message.content)

    return response_choice.message.content



class AskRequest(BaseModel):
    question: str

# uvicorn is the webserver listening on the given port for HTTP requests
# It validates the content and sends that as a readable format to FastAPI
# FastAPI is built on ASGI (Asynchronous Server Gateway Interface) implementation
app = FastAPI()

@app.post("/ask")
def ask(request: AskRequest):
    try:
        answer = agent_loop(request.question)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"answer": answer}


#"How do i go from 169 St to Sheepshead Bay ?"