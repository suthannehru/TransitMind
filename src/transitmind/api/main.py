from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel
import structlog
import time
from transitmind.agent.graph import build_graph
from transitmind.agent.loop import agent_loop
from transitmind.agent.prompt import initial_params
from transitmind.config import settings

logger = structlog.getLogger(__name__)

graph = build_graph()

class AskRequest(BaseModel):
    question: str
    # Earlier turns from the UI; not used by the agents yet
    history: list[dict[str, str]] = []

# uvicorn is the webserver listening on the given port for HTTP requests
# It validates the content and sends that as a readable format to FastAPI
# FastAPI is built on ASGI (Asynchronous Server Gateway Interface) implementation
app = FastAPI()

@app.post("/ask")
def ask(request: AskRequest):
    start_request = time.perf_counter()
    prompt_tokens = 0; completion_tokens = 0; total_tokens = 0;
    tool_calls = []
    try:
        if settings.use_graph:
            final_state = graph.invoke(initial_params(request.question))
            answer = final_state["messages"][-1]["content"]

            # Tokens Usage
            prompt_tokens = final_state["prompt_tokens"]
            completion_tokens = final_state["completion_tokens"]
            total_tokens = final_state["total_tokens"]
            tool_calls = final_state["tool_calls"]

        else:
            response = agent_loop(request.question)
            answer = response["content"]

            # Tokens Usage
            tokens = response["tokens"]
            prompt_tokens = tokens["prompt_tokens"]
            completion_tokens = tokens["completion_tokens"]
            total_tokens = tokens["total_tokens"]
            tool_calls = response["tool_calls"]

    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        request_latency = round((time.perf_counter() - start_request) * 1000)
        agent = "graph" if settings.use_graph else "loop"

        # Compute cost
        input_cost = round((prompt_tokens / 1e6) * settings.input_price_per_million, 6)
        output_cost = round((completion_tokens / 1e6) * settings.output_price_per_million, 6)

        logger.info("api_metrics", 
                    agent=agent,
                    latency_ms=request_latency,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    input_cost_usd=input_cost,
                    output_cost_usd=output_cost)
    
    return {"answer": answer,
            "agent": agent,
            "latency_ms": request_latency,
            "total_tokens": total_tokens,
            "cost_usd": input_cost + output_cost,
            "tool_calls": tool_calls}


# Mounted last so it doesn't shadow the API routes
app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="static")