from fastapi import FastAPI, HTTPException
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

# uvicorn is the webserver listening on the given port for HTTP requests
# It validates the content and sends that as a readable format to FastAPI
# FastAPI is built on ASGI (Asynchronous Server Gateway Interface) implementation
app = FastAPI()

@app.post("/ask")
def ask(request: AskRequest):
    start_request = time.perf_counter()
    prompt_tokens = 0; completion_tokens = 0; total_tokens = 0;
    try:
        if settings.use_graph:
            final_state = graph.invoke(initial_params(request.question))
            answer = final_state["messages"][-1]["content"]

            # Tokens Usage
            prompt_tokens = final_state["prompt_tokens"]
            completion_tokens = final_state["completion_tokens"]
            total_tokens = final_state["total_tokens"]

        else:
            response = agent_loop(request.question)
            answer = response["content"]

            # Tokens Usage
            tokens = response["tokens"]
            prompt_tokens = tokens["prompt_tokens"]
            completion_tokens = tokens["completion_tokens"]
            total_tokens = tokens["total_tokens"]

    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        request_latency = round((time.perf_counter() - start_request) * 1000)
        logger.info("api_metrics", 
                    latency_ms=request_latency,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens)
    
    return {"answer": answer}