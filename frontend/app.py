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
    "¡Cállate Kyle!",
    "¡Voy a demandarte!",
    "¡Screw you guys, I'm going home!",
    "¡Respeten mi autoridad!",
    "¡Malditos hippies!",
]

CARTMAN_BUBBLE_PHRASES = [
    "¡RESPETEN MI AUTORIDAD!",
    "¡CÁLLATE KYLE!",
    "¡VOY A DEMANDARTE!",
    "¡MALDITOS HIPPIES!",
    "¡SCREW YOU GUYS!",
    "¡SOY EL JEFE!",
    "¡TE VOY A DAR UNA PALIZA!",
    "¡ESO ES DE PERDEDORES!",
    "¡CREE QUE ES MEJOR QUE YO!",
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

st.markdown(f"""
<style>
    .stApp {{
        background: linear-gradient(180deg, #e8f0fe 0%, #d4e4f7 100%);
    }}

    .header-card {{
        background: linear-gradient(135deg, #1a5276 0%, #2e86c1 50%, #1a5276 100%);
        border-radius: 20px;
        padding: 20px 25px;
        margin-bottom: 20px;
        box-shadow: 0 6px 25px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}

    .side-card {{
        flex: 0 0 auto;
        width: 175px;
        text-align: center;
        position: relative;
    }}
    .side-card img {{
        display: block;
        margin: 0 auto;
        border-radius: 10px;
    }}

    .speech-bubble {{
        position: relative;
        background: white;
        color: #c0392b;
        font-weight: 900;
        font-size: 13px;
        padding: 10px 12px;
        border-radius: 12px;
        margin-top: 10px;
        min-height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        line-height: 1.3;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }}
    .speech-bubble::after {{
        content: '';
        position: absolute;
        top: -10px;
        left: 50%;
        transform: translateX(-50%);
        border-left: 10px solid transparent;
        border-right: 10px solid transparent;
        border-bottom: 10px solid white;
    }}

    @keyframes kenny-die {{
        0% {{ transform: rotate(0deg) scaleX(1); opacity: 1; }}
        55% {{ transform: rotate(0deg) scaleX(1); opacity: 1; }}
        65% {{ transform: rotate(90deg) scaleX(1); opacity: 0.8; }}
        75% {{ transform: rotate(180deg) scaleX(0.5); opacity: 0; }}
        80% {{ transform: rotate(180deg) scaleX(0.5); opacity: 0; }}
        85% {{ transform: rotate(0deg) scaleX(0); opacity: 0; }}
        95% {{ transform: rotate(0deg) scaleX(1.1); opacity: 0.7; }}
        100% {{ transform: rotate(0deg) scaleX(1); opacity: 1; }}
    }}
    .kenny-anim {{
        animation: kenny-die 5s ease-in-out infinite;
    }}

    .title-text {{
        color: white;
        text-align: center;
        flex: 1;
        padding: 0 15px;
    }}
    .title-text h1 {{
        font-size: 1.8rem;
        margin: 0;
        text-shadow: 0 2px 8px rgba(0,0,0,0.3);
        line-height: 1.2;
    }}
    .title-text p {{
        margin: 8px 0 0 0;
        opacity: 0.9;
        font-size: 0.95rem;
    }}

    .stChatMessage {{
        border-radius: 12px !important;
        margin-bottom: 8px !important;
    }}
    .stButton button {{
        background: #2e86c1 !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        border: none !important;
    }}
    .stButton button:hover {{
        background: #1a5276 !important;
    }}
</style>

<div class="header-card">
    <div class="side-card">
        <img src="data:image/png;base64,{kenny_b64}" width="140" class="kenny-anim">
    </div>
    <div class="title-text">
        <h1>🚇 Agente Inteligente<br>del Metro de Santiago</h1>
        <p>Consulta tarifas, rutas, impedimentos y planifica tus viajes.</p>
    </div>
    <div class="side-card">
        <img src="data:image/png;base64,{cartman_b64}" width="150">
        <div class="speech-bubble" id="cartman-bubble">¡RESPETEN MI AUTORIDAD!</div>
    </div>
</div>

<script>
var phrases = {json.dumps(CARTMAN_BUBBLE_PHRASES)};
var i = 0;
setInterval(function() {{
    var el = document.getElementById('cartman-bubble');
    if (el) {{
        i = (i + 1) % phrases.length;
        el.textContent = phrases[i];
    }}
}}, 3000);
</script>
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
