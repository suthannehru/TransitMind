# You have states the data passed through the state graph
# You have nodes that are like the functions
# You have edges which are the control flow
import json
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
import operator
import structlog
from typing import Annotated, TypedDict, Any
from transitmind.config import settings
from transitmind.logging_config import configure_logging
from transitmind.tools import tools_str_func, llm_tools
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Number of responses from the LLM to look at
NUM_RESPONSES = 0

# Set Logging
configure_logging(log_level=settings.log_level)
logger = structlog.getLogger(__name__)

# Create LLM Client
client = OpenAI(api_key=settings.openai_api_key)

class AskRequest(BaseModel):
    question: str

def initial_params(query: AskRequest) -> dict[str, Any]:
    return {
        "messages": [
            {"role": "system", "content": "You are a personal assistant to help navigate the NYC MTA subway. Please provide all content provided by the tools in the exact same order. Use only information the tools returned: do not add transfers, lines, stations, directions, walking steps or advice that are not in the tool responses. If a tool returns an error or says no route exists, say so."},
            {"role": "user", "content": query.question}
        ],
        "iteration": 0,
        "tool_calls": [],
        "hit_limit": False
    }

class AgentState(TypedDict):
    # Annotated is a way to attach the reducer without changing the type
    # The reducer her is operator.add, which adds the existing state with the new state
    # Reducer is required to give the LLM all the context
    messages: Annotated[list, operator.add]
    iteration: int
    tool_calls: Annotated[list, operator.add]
    hit_limit: bool

def call_llm(state: AgentState):
    llm_response = client.chat.completions.create(model=settings.llm_model, 
                                            messages=state["messages"],
                                            tools=llm_tools)
    
    response_choice = llm_response.choices[NUM_RESPONSES]

    return {"messages": [response_choice.message.model_dump()]}

def run_tools(state: AgentState ):
    tool_calls = state["messages"][-1]["tool_calls"]
    tool_messages = []
    calls = []

    for tool in tool_calls:
        tool_func = tool["function"]["name"]

        try:
            args = json.loads(tool["function"]["arguments"])
        # json.loads fails and args cannot be used                
        except json.JSONDecodeError:
            args = {}
        
        tool_func_info = {"function": tool_func, "args": args}

        try:
            func = tools_str_func[tool_func]
            output = func(**args)
            content = json.dumps(output)
            logger.info("tool_output", iteration=state["iteration"], output=output)
        # Not an available tool
        # Log both the invalid function name and arguments
        except KeyError as k:
            content = str(k)
            logger.error("tool_output_err", function=tool_func)
        # 1. No shortest path exists between start and end stop id (find_route)
        # 2. Invalid start or/and end stop ID (find_route)
        except ValueError as v:
            content = str(v)
            logger.error("tool_output_err", err=content)
        except Exception as e:
            content = str(e)
            logger.error("tool_output_err", function=tool_func, err=content)
        
        tool_func_info["tool_response"] = content
        calls.append(tool_func_info)
        tool_messages.append({"role": "tool", "content": content, "tool_call_id": tool["id"]})
        
    return {"messages": tool_messages,
            "tool_calls": calls,
            "iteration": state["iteration"] + 1}

def limit_reached(state: AgentState):
    return {
        "hit_limit": True,
        "messages": [{"role": "assistant",
                      "content": f"Failed to generate an answer due to hitting the maximum agent iterations of {settings.agent_max_iterations}"}]
    }

def should_continue(state: AgentState):
    # Take the last message. 
    last = state["messages"][-1]
    if last.get("tool_calls"):
        if state["iteration"] < settings.agent_max_iterations:
            return "run_tools"
        return "limit_reached"
    return END

# Creater a builder
builder = StateGraph(AgentState)

# Add nodes
# Label for node, function to call for node
builder.add_node("call_llm", call_llm)
builder.add_node("run_tools", run_tools)
builder.add_node("limit_reached", limit_reached)

# Add edges
# Start Node, End Node
builder.add_edge(START, "call_llm")
# Start Node, Router -> After Start Node finishes, call router to determine end node
builder.add_conditional_edges("call_llm", should_continue)
builder.add_edge("run_tools", "call_llm")
builder.add_edge("limit_reached", END)

# Compile graph
graph = builder.compile()

app = FastAPI()

@app.post("/ask")
def ask(request: AskRequest):
    try:
        final_state = graph.invoke(initial_params(request))
        answer = final_state["messages"][-1]["content"]
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"answer": answer}

if __name__ == "__main__":
    print(graph.invoke(initial_params(AskRequest(question="How do you go from 169 St to Prospect Park ?"))))

