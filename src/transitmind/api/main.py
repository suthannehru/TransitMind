from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transitmind.graph.routing import find_route
from transitmind.resolver import parse_route_query

class AskRequest(BaseModel):
    question: str

# uvicorn is the webserver listening on the given port for HTTP requests
# It validates the content and sends that as a readable format to FastAPI
# FastAPI is built on ASGI (Asynchronous Server Gateway Interface) implementation
app = FastAPI()

@app.post("/ask")
def ask(request: AskRequest):
    try:
        start_stop_id, end_stop_id = parse_route_query(request.question)
        route = find_route(start_stop_id, end_stop_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"route": route}