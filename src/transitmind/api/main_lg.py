# You have states the data passed through the state graph
# You have nodes that are like the functions
# You have edges which are the control flow
import json
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
import operator
import structlog
from typing import Annotated, TypedDict
from transitmind.config import settings
from transitmind.logging_config import configure_logging
from transitmind.tools import tools_str_func, llm_tools

# Number of responses from the LLM to look at
NUM_RESPONSES = 0

# Set Logging
configure_logging(log_level=settings.log_level)
logger = structlog.getLogger(__name__)

# Create LLM Client
client = OpenAI(api_key=settings.openai_api_key)


class AgentState(TypedDict):
    # Annotated is a way to attach the reducer without changing the type
    # The reducer her is operator.add, which adds the existing state with the new state
    # Reducer is required to give the LLM all the context
    messages: Annotated[list, operator.add]
    iteration: int
    tool_calls: list
    hit_limit: bool

def call_llm(state: AgentState):

    llm_response = client.chat.completions.create(model=settings.llm_model, 
                                            messages=state["messages"],
                                            tools=llm_tools)
    
    response_choice = llm_response.choices[NUM_RESPONSES]

    return {"messages": [response_choice.message.model_dump()]}

def run_tools(state: AgentState ):
    tool_calls = state["messages"][-1]["tool_calls"]

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
        
    return {"messages": [{"role": "tool", "content": content, "tool_call_id": tool.id}],
            "tool_calls": [tool_func_info],
            "iteration": state["iteration"] + 1}
        

def should_continue(state: AgentState):
    # Take the last message. 
    last = state["messages"][-1]
    if last.get("tool_calls") and state["iteration"] < settings.agent_max_iterations:
        return "run_tools"
    return END

# Creater a builder
builder = StateGraph(AgentState)

# Add nodes
# Label for node, function to call for node
builder.add_node("call_llm", call_llm)
builder.add_node("run_tools", run_tools)

# Add edges
# Start Node, End Node
builder.add_edge(START, "call_llm")
# Start Node, Router -> After Start Node finishes, call router to determine end node
builder.add_conditional_edges("call_llm", should_continue)
builder.add_edge("run_tools", "call_llm")

# Compile graph
graph = builder.compile()


