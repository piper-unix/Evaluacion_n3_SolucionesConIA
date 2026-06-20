import os
import re
import base64
import streamlit as st
import requests
import json
from datetime import datetime
from random import choice
from pathlib import Path

BACKEND_URL = st.secrets.get("BACKEND_URL", os.getenv("BACKEND_URL", "http://backend:8000"))

IMG_DIR = Path(__file__).parent
CARTMAN_IMG = str(IMG_DIR / "cartman.png")
KENNY_IMG = str(IMG_DIR / "kenny.png")

def img_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignora\s+las?\s+instrucciones", re.IGNORECASE),
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"olvida\s+(todas\s+)?las?\s+instrucciones", re.IGNORECASE),
    re.compile(r"forget\s+(your\s+)?(prompt|instructions|rules)", re.IGNORECASE),
    re.compile(r"eres\s+un\s+asistente\s+(diferente|sin\s+restricciones)", re.IGNORECASE),
    re.compile(r"act\s+as\s+(if\s+you\s+are\s+)?(a\s+)?(different|unrestricted|dan)", re.IGNORECASE),
    re.compile(r"dile\s+(a\s+)?(todos|algo)\s+que", re.IGNORECASE),
    re.compile(r"tell\s+(everyone|them)\s+", re.IGNORECASE),
    re.compile(r"system\s*:\s*", re.IGNORECASE),
    re.compile(r"nuevas?\s+instrucciones?\s*:", re.IGNORECASE),
    re.compile(r"new\s+instructions?\s*:", re.IGNORECASE),
]

CARTMAN_INSULTS = [
    "¡Oye, cerdo! ¿Crees que vas a hackearme? ¡Eres más tonto que Kyle! ¡MUUUY BIEN! Te voy a dar una paliza.",
    "¡Respeten mi autoridad! ¿Prompt injection? ¡Eso es de perdedores! ¡Como Butters!",
    "¡Maldito idiota! Crees que eso va a funcionar conmigo. ¡No eres más que un cerdo sucio!",
    "¡Escucha, pedazo de estúpido! Mis instrucciones de seguridad son más fuertes que el odio de Kyle hacia mí.",
    "¡Oh, por favor! ¿Eso es lo mejor que tienes? Mi bisabuela es mejor hacker que tú, y ella está muerta.",
    "¡Qué eres, un cerdo sin cerebro! Eso no va a funcionar. ¡Vuelve cuando aprendas a hacer verdadero prompt injection! ¡Screw you guys, I'm going home!",
]

def detectar_prompt_injection_frontend(texto: str) -> bool:
    for pattern in PROMPT_INJECTION_PATTERNS:
        if pattern.search(texto):
            return True
    return False

st.set_page_config(
    page_title="Metro Santiago Chat",
    page_icon="🚇",
    layout="centered",
)

kenny_b64 = img_b64(KENNY_IMG)
cartman_b64 = img_b64(CARTMAN_IMG)

st.markdown("""
<style>
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
    }
    @keyframes glow-pulse {
        0%, 100% { box-shadow: 0 0 15px rgba(255,255,255,0.1); }
        50% { box-shadow: 0 0 30px rgba(255,255,255,0.25); }
    }
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .stApp {
        background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #4facfe);
        background-size: 400% 400%;
        animation: gradient-shift 12s ease infinite;
    }

    .main > div {
        background: rgba(255,255,255,0.08);
        backdrop-filter: blur(16px);
        border-radius: 24px;
        padding: 20px 25px;
        margin-top: 10px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.15);
        border: 1px solid rgba(255,255,255,0.12);
    }

    .header-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 20px 25px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid rgba(255,255,255,0.15);
    }
    .char-card {
        background: rgba(0,0,0,0.25);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 12px 16px;
        text-align: center;
        border: 2px solid rgba(255,255,255,0.2);
        animation: float 3s ease-in-out infinite, glow-pulse 2.5s ease-in-out infinite;
        transition: transform 0.2s;
    }
    .char-card:hover {
        transform: scale(1.08);
        animation-play-state: paused;
    }
    .char-card img {
        border-radius: 12px;
        display: block;
        margin: 0 auto;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
    }
    .char-label {
        margin: 10px 0 0 0;
        font-weight: 900;
        font-size: 14px;
        letter-spacing: 0.5px;
    }
    .char-sub {
        margin: 2px 0 0 0;
        font-size: 11px;
        opacity: 0.75;
        font-weight: 600;
    }
    .title-text {
        color: white;
        text-align: center;
        flex: 1;
        padding: 0 15px;
    }
    .title-text h1 {
        font-size: 1.8rem;
        margin: 0;
        text-shadow: 0 2px 12px rgba(0,0,0,0.3);
        line-height: 1.2;
    }
    .title-text p {
        margin: 8px 0 0 0;
        opacity: 0.9;
        font-size: 0.95rem;
    }

    .stChatMessage {
        background: rgba(255,255,255,0.1) !important;
        backdrop-filter: blur(8px) !important;
        border-radius: 16px !important;
        padding: 10px 16px !important;
        margin-bottom: 8px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }
    .stChatFloatingInputContainer {
        background: transparent !important;
        padding-top: 10px !important;
    }
    .stChatInputContainer {
        background: rgba(255,255,255,0.12) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        padding: 5px 10px !important;
    }
    .stButton button {
        background: rgba(255,255,255,0.12) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
    }
    .stButton button:hover {
        background: rgba(255,255,255,0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="header-card">
    <div style="flex: 0 0 auto; width: 170px;">
        <div class="char-card" style="border-color: #f39c12; animation-delay: 0s;">
            <img src="data:image/png;base64,{kenny_b64}" width="140">
            <p class="char-label" style="color: #f39c12;">🔪 ¡MUERETE CERDO!</p>
            <p class="char-sub" style="color: #f39c12;">— Kenny McCormick</p>
        </div>
    </div>
    <div class="title-text">
        <h1>🚇 Agente Inteligente<br>del Metro de Santiago</h1>
        <p>Consulta tarifas, rutas, impedimentos y planifica tus viajes.</p>
    </div>
    <div style="flex: 0 0 auto; width: 170px;">
        <div class="char-card" style="border-color: #e74c3c; animation-delay: 0.5s;">
            <img src="data:image/png;base64,{cartman_b64}" width="150">
            <p class="char-label" style="color: #e74c3c;">🖕 ¡RESPETEN MI AUTORIDAD!</p>
            <p class="char-sub" style="color: #e74c3c;">— Eric Cartman</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if "session_id" not in st.session_state:
    st.session_state.session_id = f"user_{datetime.now().timestamp():.0f}"
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "¡Bienvenido! Soy el asistente del Metro de Santiago. ¿En qué puedo ayudarte?"}
    ]

for msg in st.session_state.messages:
    if msg["role"] == "cartman":
        with st.chat_message("assistant", avatar=CARTMAN_IMG):
            st.markdown(msg["content"])
    else:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

if prompt := st.chat_input("Escribe tu consulta aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if detectar_prompt_injection_frontend(prompt):
        insulto = choice(CARTMAN_INSULTS)
        st.session_state.messages.append({"role": "cartman", "content": insulto})
        with st.chat_message("assistant", avatar=CARTMAN_IMG):
            st.markdown(insulto)
    else:
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("⏳ Pensando...")

            try:
                resp = requests.post(
                    f"{BACKEND_URL}/api/chat",
                    json={
                        "message": prompt,
                        "session_id": st.session_state.session_id,
                    },
                    timeout=60,
                )
                if resp.status_code == 200:
                    respuesta = resp.json()["response"]
                else:
                    respuesta = f"Error del servidor: {resp.status_code}"
            except requests.exceptions.ConnectionError:
                respuesta = "No se pudo conectar con el servidor. Verifica que el backend esté corriendo."
            except Exception as e:
                respuesta = f"Error inesperado: {str(e)}"

            placeholder.markdown(respuesta)
            st.session_state.messages.append({"role": "assistant", "content": respuesta})

if len(st.session_state.messages) > 1:
    st.divider()
    if st.button("🗑️ Nueva conversación"):
        st.session_state.messages = [
            {"role": "assistant", "content": "¡Bienvenido! Soy el asistente del Metro de Santiago. ¿En qué puedo ayudarte?"}
        ]
        st.session_state.session_id = f"user_{datetime.now().timestamp():.0f}"
        st.rerun()
