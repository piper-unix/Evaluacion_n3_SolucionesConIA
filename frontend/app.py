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
    .header-card {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        border-radius: 20px;
        padding: 25px 30px;
        margin-bottom: 25px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .char-card {
        background: rgba(255,255,255,0.08);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 15px 20px;
        text-align: center;
        border: 2px solid rgba(255,255,255,0.15);
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        transition: transform 0.2s;
    }
    .char-card:hover {
        transform: scale(1.03);
    }
    .char-card img {
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        display: block;
        margin: 0 auto;
    }
    .char-label {
        margin: 12px 0 0 0;
        font-weight: 900;
        font-size: 15px;
        letter-spacing: 0.5px;
    }
    .char-sub {
        margin: 2px 0 0 0;
        font-size: 12px;
        opacity: 0.7;
        font-weight: 500;
    }
    .title-text {
        color: white;
        text-align: center;
        flex: 1;
        padding: 0 15px;
    }
    .title-text h1 {
        font-size: 1.9rem;
        margin: 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
        line-height: 1.2;
    }
    .title-text p {
        margin: 10px 0 0 0;
        opacity: 0.85;
        font-size: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="header-card">
    <div style="flex: 0 0 auto; width: 170px;">
        <div class="char-card" style="border-color: #e67e22;">
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
        <div class="char-card" style="border-color: #c0392b;">
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
