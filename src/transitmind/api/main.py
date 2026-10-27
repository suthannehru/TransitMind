from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from qdrant_client.http.exceptions import ResponseHandlingException
import structlog
import time
from transitmind.agent.run import compute_cost, run_agent
from transitmind.config import settings

logger = structlog.getLogger(__name__)

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
        _, answer, prompt_tokens, completion_tokens, total_tokens = run_agent(request.question)
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ResponseHandlingException as rhe:
        raise HTTPException(status_code=503, detail=str(rhe))
    finally:
        request_latency = round((time.perf_counter() - start_request) * 1000)
        agent = "graph" if settings.use_graph else "loop"

        input_cost, output_cost = compute_cost(input_tokens=prompt_tokens, output_tokens=completion_tokens)

        logger.info("api_metrics", 
                    agent=agent,
                    latency_ms=request_latency,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    input_cost_usd=input_cost,
                    output_cost_usd=output_cost)
    
    return {"answer": answer}