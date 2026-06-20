import os
import re
import base64
import streamlit as st
import requests
import json
from datetime import datetime
from random import choice
from pathlib import Path
from streamlit.components.v1 import html as st_html

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

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a0000 30%, #2a0000 60%, #0a0a0a 100%);
    }
    .stChatMessage {
        border-radius: 12px !important;
        margin-bottom: 8px !important;
        background: rgba(30, 0, 0, 0.4) !important;
        border: 1px solid rgba(180, 0, 0, 0.2) !important;
    }
    .stButton button {
        background: #8b0000 !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        border: 1px solid #cc0000 !important;
    }
    .stButton button:hover {
        background: #cc0000 !important;
        border-color: #ff2222 !important;
    }
    .stChatInputContainer {
        background: rgba(30, 0, 0, 0.4) !important;
        border: 1px solid rgba(180, 0, 0, 0.3) !important;
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

st_html(f"""
<style>
    @keyframes float {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-5px); }}
    }}
    @keyframes bus-crash {{
        0% {{ transform: translateX(250px); opacity: 0; }}
        8% {{ opacity: 1; }}
        28% {{ transform: translateX(10px); opacity: 1; }}
        33% {{ transform: translateX(-15px); opacity: 0.9; }}
        40% {{ transform: translateX(-120px); opacity: 0.8; }}
        48% {{ transform: translateX(-280px); opacity: 0; }}
        100% {{ transform: translateX(250px); opacity: 0; }}
    }}
    @keyframes kenny-hit {{
        0%, 26% {{ transform: translate(0, 0) rotate(0deg) scaleX(1); opacity: 1; }}
        30% {{ transform: translate(0, 0) rotate(0deg) scaleX(1); opacity: 1; }}
        34% {{ transform: translate(25px, -20px) rotate(15deg) scaleX(0.9); opacity: 0.9; }}
        40% {{ transform: translate(70px, -80px) rotate(70deg) scaleX(0.5); opacity: 0.5; }}
        46% {{ transform: translate(120px, -150px) rotate(120deg) scaleX(0.3); opacity: 0; }}
        50%, 85% {{ transform: translate(120px, -150px) rotate(120deg); opacity: 0; }}
        90% {{ transform: translate(0, 20px) rotate(0deg) scaleX(0.5); opacity: 0; }}
        96% {{ transform: translate(0, -5px) rotate(0deg) scaleX(1.1); opacity: 0.7; }}
        100% {{ transform: translate(0, 0) rotate(0deg) scaleX(1); opacity: 1; }}
    }}
    @keyframes pulse-red {{
        0%, 100% {{ box-shadow: 0 0 10px rgba(200,0,0,0.2), 0 6px 30px rgba(0,0,0,0.3); }}
        50% {{ box-shadow: 0 0 35px rgba(200,0,0,0.5), 0 6px 30px rgba(0,0,0,0.3); }}
    }}
    @keyframes blood-drip {{
        0%, 80% {{ background-position: 0% 50%; opacity: 0.3; }}
        50% {{ background-position: 100% 50%; opacity: 0.6; }}
    }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        background: transparent;
        font-family: 'Source Sans Pro', sans-serif;
    }}
    .header-card {{
        background: linear-gradient(135deg, #1a0000 0%, #4a0000 50%, #1a0000 100%);
        border-radius: 20px;
        padding: 18px 22px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid rgba(200,0,0,0.25);
        animation: pulse-red 3s ease-in-out infinite;
        position: relative;
        overflow: hidden;
    }}
    .header-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(200,0,0,0.05), transparent);
        background-size: 200% 100%;
        animation: blood-drip 4s ease-in-out infinite;
        pointer-events: none;
    }}
    .side-card {{
        flex: 0 0 auto;
        width: 175px;
        text-align: center;
        position: relative;
        z-index: 1;
    }}
    .kenny-scene {{
        position: relative;
        width: 140px;
        height: 180px;
        margin: 0 auto;
        overflow: hidden;
    }}
    .kenny-scene img {{
        position: absolute;
        top: 10px;
        left: 0;
        width: 140px;
        animation: kenny-hit 5s ease-in-out infinite;
    }}
    .bus-emoji {{
        position: absolute;
        top: 40px;
        left: 0;
        font-size: 60px;
        line-height: 1;
        z-index: 2;
        animation: bus-crash 5s ease-in-out infinite;
        filter: drop-shadow(0 0 8px rgba(255,0,0,0.4));
    }}
    .impact {{
        position: absolute;
        top: 15px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 50px;
        opacity: 0;
        z-index: 3;
        animation: impact-flash 5s ease-in-out infinite;
    }}
    @keyframes impact-flash {{
        0%, 30% {{ opacity: 0; transform: translateX(-50%) scale(0.5); }}
        32% {{ opacity: 1; transform: translateX(-50%) scale(1.5); }}
        36% {{ opacity: 0; transform: translateX(-50%) scale(0.5); }}
        100% {{ opacity: 0; transform: translateX(-50%) scale(0.5); }}
    }}
    .speech-bubble {{
        position: relative;
        background: #1a0000;
        color: #ff3333;
        font-weight: 900;
        font-size: 12px;
        padding: 10px 12px;
        border-radius: 12px;
        margin-top: 8px;
        min-height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        line-height: 1.3;
        border: 1px solid rgba(200,0,0,0.3);
        box-shadow: 0 3px 15px rgba(200,0,0,0.15);
        animation: float 2.5s ease-in-out infinite;
    }}
    .speech-bubble::after {{
        content: '';
        position: absolute;
        top: -10px;
        left: 50%;
        transform: translateX(-50%);
        border-left: 10px solid transparent;
        border-right: 10px solid transparent;
        border-bottom: 10px solid #1a0000;
    }}
    .title-text {{
        color: #ffcccc;
        text-align: center;
        flex: 1;
        padding: 0 12px;
        z-index: 1;
        position: relative;
        animation: float 3.5s ease-in-out infinite;
    }}
    .title-text h1 {{
        font-size: 1.7rem;
        margin: 0;
        text-shadow: 0 2px 15px rgba(200,0,0,0.3);
        line-height: 1.2;
    }}
    .title-text p {{
        margin: 7px 0 0 0;
        opacity: 0.8;
        font-size: 0.9rem;
    }}
    .cartman-floater {{
        animation: float 3s ease-in-out infinite;
    }}
</style>

<div class="header-card">
    <div class="side-card">
        <div class="kenny-scene">
            <img src="data:image/png;base64,{kenny_b64}" width="140" style="position: absolute; top: 10px; left: 0; width: 140px; animation: kenny-hit 5s ease-in-out infinite;">
            <div class="bus-emoji">🚌</div>
            <div class="impact">💥</div>
        </div>
    </div>
    <div class="title-text">
        <h1>🚇 Metro de Santiago</h1>
        <p>Agente Inteligente — Tarifas, rutas, impedimentos y viajes.</p>
    </div>
    <div class="side-card">
        <img src="data:image/png;base64,{cartman_b64}" width="150" class="cartman-floater">
        <div class="speech-bubble" id="cartman-bubble">¡RESPETEN MI AUTORIDAD!</div>
    </div>
</div>

<script>
var phrases = {json.dumps(CARTMAN_BUBBLE_PHRASES)};
var i = Math.floor(Math.random() * phrases.length);
setInterval(function() {{
    var el = document.getElementById('cartman-bubble');
    if (el) {{
        i = (i + 1) % phrases.length;
        el.textContent = phrases[i];
        el.style.transform = 'scale(0.92)';
        el.style.borderColor = '#ff0000';
        setTimeout(function() {{ el.style.transform = 'scale(1)'; el.style.borderColor = 'rgba(200,0,0,0.3)'; }}, 150);
    }}
}}, 2500);
</script>
""", height=300)

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
