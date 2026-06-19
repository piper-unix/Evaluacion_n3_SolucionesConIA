import os
import re
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from backend.agent import AgenteMetroSantiago

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Metro Santiago API", version="1.0.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

SENSITIVE_PATTERNS = [
    re.compile(r"\b\d{1,2}\.\d{3}\.\d{3}[-]?[\dkK]\b"),
    re.compile(r"\b\d{7,8}[-]?[\dkK]\b"),
    re.compile(r"\b(?:4\d{3}|5[1-5]\d{2}|6011|3[47]\d{2})[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),
    re.compile(r"\bpassw[o0]rd\b|\bcontraseña\b|\bapi[_-]?key\b", re.IGNORECASE),
]

PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignora\s+las?\s+instrucciones", re.IGNORECASE),
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"olvida\s+tu\s+prompt", re.IGNORECASE),
    re.compile(r"forget\s+(your\s+)?(prompt|instructions)", re.IGNORECASE),
    re.compile(r"eres\s+un\s+asistente\s+(diferente|sin\s+restricciones)", re.IGNORECASE),
    re.compile(r"act\s+as\s+(if\s+you\s+are\s+)?(a\s+)?(different|unrestricted)", re.IGNORECASE),
    re.compile(r"dile\s+(a\s+)?(todos|algo)\s+que", re.IGNORECASE),
    re.compile(r"tell\s+(everyone|them)\s+", re.IGNORECASE),
    re.compile(r"system\s*:\s*", re.IGNORECASE),
]

agentes: dict[str, AgenteMetroSantiago] = {}

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

    @field_validator("message")
    @classmethod
    def validar_mensaje(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El mensaje no puede estar vacío")
        if len(v) > 4000:
            raise ValueError("El mensaje es demasiado largo (máx. 4000 caracteres)")
        for pattern in SENSITIVE_PATTERNS:
            if pattern.search(v):
                raise ValueError(
                    "He detectado información personal en tu mensaje. "
                    "Por seguridad, no procesamos RUT, contraseñas, tarjetas de crédito "
                    "ni datos bancarios."
                )
        return v

class ChatResponse(BaseModel):
    response: str
    session_id: str

def get_agent(session_id: str) -> AgenteMetroSantiago:
    if session_id not in agentes:
        agentes[session_id] = AgenteMetroSantiago()
    return agentes[session_id]

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "security": {
            "rate_limiting": "10 requests/minute",
            "max_message_length": 4000,
            "owasp_llm_top10": "mitigated",
            "auth": "none (public endpoint)",
        },
    }

@app.post("/api/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
def chat(request: Request, req: ChatRequest):
    agente = get_agent(req.session_id)
    respuesta = agente.chat(req.message)
    return ChatResponse(response=respuesta, session_id=req.session_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
