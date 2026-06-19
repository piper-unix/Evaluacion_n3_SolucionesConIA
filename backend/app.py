import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.agent import AgenteMetroSantiago

app = FastAPI(title="Metro Santiago API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agentes: dict[str, AgenteMetroSantiago] = {}

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str

def get_agent(session_id: str) -> AgenteMetroSantiago:
    if session_id not in agentes:
        agentes[session_id] = AgenteMetroSantiago()
    return agentes[session_id]

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío")
    agente = get_agent(req.session_id)
    respuesta = agente.chat(req.message)
    return ChatResponse(response=respuesta, session_id=req.session_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
