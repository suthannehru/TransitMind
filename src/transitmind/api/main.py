from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import structlog
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
    try:
        if settings.use_graph:
            final_state = graph.invoke(initial_params(request.question))
            answer = final_state["messages"][-1]["content"]
        else:
            response = agent_loop(request.question)
            answer = response["content"]
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"answer": answer}