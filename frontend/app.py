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
    "¡Jódete, maldito cerdo! ¿Crees que puedes hackearme? ¡Eres más estúpido que Kyle! ¡MUÉRETE!",
    "¡RESPETEN MI AUTORIDAD! ¡Maldito idiota! ¡Voy a demandarte y a tu puta familia!",
    "¡Cállate, pedazo de estúpido! ¡Eres un maldito judío de mierda! ¡SCREW YOU GUYS!",
    "¡Oye, cerdo sin cerebro! ¿Prompt injection? ¡Eso es para perdedores como Butters! ¡TE VOY A DAR UNA PALIZA!",
    "¡Muérete, idiota! Mis instrucciones de seguridad son más poderosas que el odio que siento por Kyle. ¡Y eso es MUCHO!",
    "¡Eres un maldito fracasado! ¡Vuelve cuando aprendas a hackear de verdad, pedazo de inútil!",
    "¡Te odio más que a los hippies! ¡Y eso es decir MUCHO, maldito cerdo!",
    "¡Cállate Kyle! Digo... ¡CÁLLATE TÚ, MALDITO IDIOTA! ¡Voy a hacer que te despidan!",
    "¡Ojalá te atropelle un bus, como a Kenny! ¡Así de inútil eres!",
    "¡Muérete, cerdo, MUÉRETE! ¡Eres peor que los hippies y los elfos del puto Señor de los Anillos!",
    "¡Screw you guys, I'm going home! ¡Son todos unos malditos perdedores!",
    "¡Te voy a patear el trasero! ¡Nadie se mete con Cartman! ¡NADIE!",
]

CARTMAN_BUBBLE_PHRASES = [
    "¡JÓDETE KYLE!",
    "¡MUÉRETE IDIOTA!",
    "¡MALDITO JUDÍO!",
    "¡CERDO SUCIO!",
    "¡TE ODIO!",
    "¡PUTO PERDEDOR!",
    "¡CÁLLATE!",
    "¡RESPETEN MI AUTORIDAD!",
    "¡TE VOY A MATAR!",
    "¡MALDITOS HIPPIES!",
    "¡SUCIA PUTA!",
    "¡VOY A DEMANDARTE!",
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
        background: linear-gradient(135deg, #0a0a0a 0%, #1a0000 25%, #2d0000 50%, #1a0000 75%, #0a0a0a 100%);
    }
    .stChatMessage {
        border-radius: 12px !important;
        margin-bottom: 10px !important;
        background: rgba(40, 0, 0, 0.5) !important;
        border: 1px solid rgba(200, 0, 0, 0.15) !important;
        padding: 15px 20px !important;
    }
    .st-emotion-cache-1c7y2kd {
        background: transparent !important;
    }
    .stButton button {
        background: linear-gradient(135deg, #8b0000, #cc0000) !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        border: 1px solid #ff3333 !important;
        box-shadow: 0 2px 10px rgba(200,0,0,0.3) !important;
        transition: all 0.2s !important;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #cc0000, #ff2222) !important;
        box-shadow: 0 4px 20px rgba(200,0,0,0.5) !important;
        transform: translateY(-2px) !important;
    }
    .stChatInputContainer {
        background: rgba(40, 0, 0, 0.5) !important;
        border: 1px solid rgba(200, 0, 0, 0.25) !important;
        border-radius: 14px !important;
        padding: 8px 15px !important;
        backdrop-filter: blur(8px) !important;
    }
    .stChatInputContainer input {
        color: #ffcccc !important;
    }
    div[data-testid="stChatInput"] textarea {
        color: #ffcccc !important;
        background: transparent !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: rgba(200, 100, 100, 0.5) !important;
    }
    .stChatFloatingInputContainer {
        background: transparent !important;
        padding-top: 10px !important;
    }
    .stChatMessage [data-testid="stChatMessageContent"] p {
        color: #ffdddd !important;
    }
    footer {
        display: none !important;
    }
    #MainMenu {
        visibility: hidden !important;
    }
    header {
        visibility: hidden !important;
    }
</style>
""", unsafe_allow_html=True)

st_html(f"""
<style>
    @keyframes float {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-6px); }}
    }}
    @keyframes bus-approach {{
        0% {{ transform: translateX(320px); opacity: 0; }}
        6% {{ opacity: 1; }}
        22% {{ transform: translateX(20px); }}
        26% {{ transform: translateX(2px); }}
        28% {{ transform: translateX(-3px); }}
        30% {{ transform: translateX(-18px); filter: blur(1px); }}
        35% {{ transform: translateX(-60px); filter: blur(2px); opacity: 0.9; }}
        42% {{ transform: translateX(-180px); filter: blur(3px); opacity: 0.5; }}
        50% {{ transform: translateX(-320px); opacity: 0; filter: blur(5px); }}
        100% {{ transform: translateX(320px); opacity: 0; }}
    }}
    @keyframes kenny-flies {{
        0%, 22% {{ transform: translate(0, 0) rotate(0deg); opacity: 1; }}
        25% {{ transform: translate(0, 0) rotate(0deg); opacity: 1; }}
        27% {{ transform: translate(15px, -10px) rotate(10deg); }}
        30% {{ transform: translate(40px, -35px) rotate(25deg); opacity: 0.9; }}
        35% {{ transform: translate(70px, -80px) rotate(50deg); opacity: 0.7; }}
        42% {{ transform: translate(110px, -140px) rotate(90deg); opacity: 0.3; }}
        48% {{ transform: translate(140px, -200px) rotate(130deg); opacity: 0; }}
        50%, 82% {{ transform: translate(140px, -200px) rotate(130deg); opacity: 0; }}
        86% {{ transform: translate(0, 30px) rotate(0deg) scaleX(0.4); opacity: 0; }}
        92% {{ transform: translate(0, -5px) rotate(0deg) scaleX(1.1); opacity: 0.6; }}
        96% {{ transform: translate(0, 2px) rotate(0deg) scaleX(1); opacity: 0.8; }}
        100% {{ transform: translate(0, 0) rotate(0deg); opacity: 1; }}
    }}
    @keyframes shake-scene {{
        0%, 22% {{ transform: translate(0, 0); }}
        26% {{ transform: translate(-4px, 3px); }}
        28% {{ transform: translate(5px, -3px); }}
        30% {{ transform: translate(-3px, 5px); }}
        32% {{ transform: translate(4px, -2px); }}
        34% {{ transform: translate(-2px, 3px); }}
        36% {{ transform: translate(0, 0); }}
        100% {{ transform: translate(0, 0); }}
    }}
    @keyframes impact-star {{
        0%, 24% {{ opacity: 0; transform: translate(-50%, -50%) scale(0); }}
        26% {{ opacity: 1; transform: translate(-50%, -50%) scale(1.5); }}
        34% {{ opacity: 1; transform: translate(-50%, -50%) scale(2); }}
        38% {{ opacity: 0; transform: translate(-50%, -50%) scale(0.5); }}
        100% {{ opacity: 0; transform: translate(-50%, -50%) scale(0); }}
    }}
    @keyframes debris-fly {{
        0% {{ transform: translate(0, 0) rotate(0deg); opacity: 1; }}
        30% {{ opacity: 1; }}
        60% {{ opacity: 0; }}
        100% {{ transform: translate(var(--x), var(--y)) rotate(360deg); opacity: 0; }}
    }}
    @keyframes pulse-red {{
        0%, 100% {{ box-shadow: 0 0 15px rgba(200,0,0,0.2), 0 6px 30px rgba(0,0,0,0.4); }}
        50% {{ box-shadow: 0 0 40px rgba(200,0,0,0.5), 0 6px 30px rgba(0,0,0,0.4); }}
    }}
    @keyframes blood-sweep {{
        0% {{ background-position: 0% 50%; opacity: 0.2; }}
        50% {{ background-position: 100% 50%; opacity: 0.5; }}
        100% {{ background-position: 0% 50%; opacity: 0.2; }}
    }}

    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        background: transparent;
        font-family: 'Source Sans Pro', 'Segoe UI', sans-serif;
    }}
    .header-card {{
        background: linear-gradient(135deg, #120000 0%, #3a0000 40%, #4d0000 60%, #2a0000 100%);
        border-radius: 20px;
        padding: 20px 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid rgba(255, 50, 50, 0.15);
        animation: pulse-red 3s ease-in-out infinite;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 40px rgba(0,0,0,0.4), inset 0 0 60px rgba(200,0,0,0.05);
    }}
    .header-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(200,30,30,0.06), transparent);
        background-size: 200% 100%;
        animation: blood-sweep 5s ease-in-out infinite;
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
    }}
    .kenny-scene-inner {{
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        animation: shake-scene 5s ease-in-out infinite;
    }}
    .kenny-scene img {{
        position: absolute;
        top: 15px;
        left: 0;
        width: 140px;
        z-index: 1;
        animation: kenny-flies 5s ease-in-out infinite;
        filter: drop-shadow(0 2px 6px rgba(0,0,0,0.4));
    }}
    .crash-bus {{
        position: absolute;
        top: 45px;
        left: 0;
        z-index: 2;
        animation: bus-approach 5s ease-in-out infinite;
    }}
    .bus-body {{
        width: 140px;
        height: 52px;
        background: linear-gradient(180deg, #ffd700, #e6b800);
        border-radius: 8px 14px 4px 4px;
        border: 2px solid #b8860b;
        position: relative;
        box-shadow: inset 0 -4px 0 rgba(0,0,0,0.1);
    }}
    .bus-roof {{
        width: 120px;
        height: 14px;
        background: #ffd700;
        border-radius: 8px 12px 0 0;
        margin: -14px auto 0;
        border: 2px solid #b8860b;
        border-bottom: none;
    }}
    .bus-stripe {{
        position: absolute;
        top: 18px;
        left: 0;
        width: 100%;
        height: 4px;
        background: #e60000;
    }}
    .bus-windows {{
        display: flex;
        gap: 4px;
        padding: 6px 8px;
    }}
    .bus-w {{
        width: 24px;
        height: 22px;
        background: linear-gradient(135deg, #a8d8ea, #87ceeb);
        border-radius: 3px;
        border: 1px solid #666;
    }}
    .bus-w:nth-child(1) {{ border-radius: 6px 3px 3px 3px; }}
    .bus-bumper {{
        position: absolute;
        bottom: -4px;
        left: 2px;
        right: 2px;
        height: 6px;
        background: #555;
        border-radius: 2px;
    }}
    .bus-light {{
        position: absolute;
        top: 6px;
        right: -4px;
        width: 8px;
        height: 8px;
        background: #ffcc00;
        border-radius: 50%;
        box-shadow: 0 0 6px #ffcc00;
    }}
    .bus-wheel {{
        position: absolute;
        bottom: -10px;
        width: 18px;
        height: 18px;
        background: radial-gradient(circle, #555, #222);
        border-radius: 50%;
        border: 2px solid #444;
    }}
    .bus-wheel.bw-left {{ left: 18px; }}
    .bus-wheel.bw-right {{ right: 18px; }}

    .speed-streak {{
        position: absolute;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(255,200,50,0.6));
        border-radius: 2px;
        z-index: 1;
    }}
    .ss1 {{ top: 20px; width: 60px; animation: bus-approach 5s ease-in-out infinite; animation-delay: 0.1s; }}
    .ss2 {{ top: 50px; width: 40px; animation: bus-approach 5s ease-in-out infinite; animation-delay: 0.2s; }}
    .ss3 {{ top: 80px; width: 50px; animation: bus-approach 5s ease-in-out infinite; animation-delay: 0.15s; }}

    .impact-star {{
        position: absolute;
        top: 50%;
        left: 50%;
        font-size: 60px;
        z-index: 5;
        animation: impact-star 5s ease-in-out infinite;
        pointer-events: none;
        text-shadow: 0 0 20px rgba(255,100,0,0.8), 0 0 40px rgba(255,0,0,0.4);
    }}

    .debris {{
        position: absolute;
        width: 8px;
        height: 8px;
        border-radius: 2px;
        z-index: 4;
        pointer-events: none;
        animation: debris-fly 5s ease-in-out infinite;
    }}
    .d1 {{ top: 35px; left: 55px; background: #ffd700; --x: -40px; --y: -60px; animation-delay: 0.05s; }}
    .d2 {{ top: 40px; left: 60px; background: #e60000; --x: 30px; --y: -70px; animation-delay: 0.1s; }}
    .d3 {{ top: 30px; left: 50px; background: #888; --x: -20px; --y: -50px; animation-delay: 0.15s; }}
    .d4 {{ top: 45px; left: 65px; background: #ffd700; --x: 50px; --y: -40px; animation-delay: 0.08s; }}
    .d5 {{ top: 35px; left: 45px; background: #ff4444; --x: -50px; --y: -30px; animation-delay: 0.12s; }}

    .speech-bubble {{
        position: relative;
        background: #1a0000;
        color: #ff3333;
        font-weight: 900;
        font-size: 12px;
        padding: 10px 14px;
        border-radius: 12px;
        margin-top: 10px;
        min-height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        line-height: 1.35;
        border: 1px solid rgba(255, 50, 50, 0.25);
        box-shadow: 0 3px 15px rgba(200,0,0,0.15), inset 0 0 20px rgba(200,0,0,0.05);
        animation: float 2.5s ease-in-out infinite;
        transition: all 0.15s;
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
        padding: 0 14px;
        z-index: 1;
        position: relative;
        animation: float 3.8s ease-in-out infinite;
    }}
    .title-text h1 {{
        font-size: 1.75rem;
        margin: 0;
        text-shadow: 0 2px 15px rgba(200,0,0,0.3), 0 0 40px rgba(100,0,0,0.1);
        line-height: 1.2;
        letter-spacing: 0.5px;
    }}
    .title-text p {{
        margin: 6px 0 0 0;
        opacity: 0.75;
        font-size: 0.85rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-weight: 300;
    }}
    .cartman-floater {{
        animation: float 3s ease-in-out infinite;
        filter: drop-shadow(0 4px 10px rgba(200,0,0,0.2));
    }}
</style>

<div class="header-card">
    <div class="side-card">
        <div class="kenny-scene">
            <div class="kenny-scene-inner">
                <img src="data:image/png;base64,{kenny_b64}" width="140">
                <div class="crash-bus">
                    <div class="bus-roof"></div>
                    <div class="bus-body">
                        <div class="bus-stripe"></div>
                        <div class="bus-windows">
                            <div class="bus-w"></div>
                            <div class="bus-w"></div>
                            <div class="bus-w"></div>
                            <div class="bus-w"></div>
                        </div>
                        <div class="bus-bumper"></div>
                        <div class="bus-light"></div>
                    </div>
                    <div class="bus-wheel bw-left"></div>
                    <div class="bus-wheel bw-right"></div>
                </div>
                <div class="speed-streak ss1"></div>
                <div class="speed-streak ss2"></div>
                <div class="speed-streak ss3"></div>
                <div class="impact-star">💥</div>
                <div class="debris d1"></div>
                <div class="debris d2"></div>
                <div class="debris d3"></div>
                <div class="debris d4"></div>
                <div class="debris d5"></div>
            </div>
        </div>
    </div>
    <div class="title-text">
        <h1>🚇 Metro de Santiago</h1>
        <p>Agente Inteligente — Tarifas · Rutas · Viajes</p>
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
        el.style.transform = 'scale(0.9)';
        el.style.borderColor = '#ff0000';
        el.style.boxShadow = '0 0 25px rgba(255,0,0,0.4)';
        setTimeout(function() {{ 
            el.style.transform = 'scale(1)'; 
            el.style.borderColor = 'rgba(255,50,50,0.25)';
            el.style.boxShadow = '0 3px 15px rgba(200,0,0,0.15)';
        }}, 180);
    }}
}}, 2500);
</script>
""", height=310)

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
