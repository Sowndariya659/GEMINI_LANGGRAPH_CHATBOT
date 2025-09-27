from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from graph import chat_app

app = FastAPI()

class ChatRequest(BaseModel):
    user_message: str
    thread_id: str
    document_chunks: List[str] = []  # Optional

class ChatResponse(BaseModel):
    response: str

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    # Initial state includes message + chunks
    state = {
        "messages": [req.user_message],
        "document_chunks": req.document_chunks
    }
    config = {"configurable": {"thread_id": req.thread_id}}
    result = chat_app.invoke(state, config=config)
    return ChatResponse(response=result["messages"][-1])
