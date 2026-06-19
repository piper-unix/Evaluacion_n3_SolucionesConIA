import os
import re
import streamlit as st
import requests
import json
from datetime import datetime
from random import choice

BACKEND_URL = st.secrets.get("BACKEND_URL", os.getenv("BACKEND_URL", "http://backend:8000"))

CARTMAN_IMAGE_URL = "https://upload.wikimedia.org/wikipedia/en/7/77/EricCartman.png"

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

with st.sidebar:
    st.image(CARTMAN_IMAGE_URL, width=120)
    st.markdown("### Eric Cartman")
    st.markdown("*\"Respeten mi autoridad\"*")
    st.divider()
    st.markdown(
        "Estoy vigilando tus prompts, cerdo. "
        "Si intentas hackear el sistema, te vas a arrepentir."
    )

st.title("🚇 Agente Inteligente del Metro de Santiago")
st.markdown("Consulta tarifas, rutas, impedimentos y planifica tus viajes.")

if "session_id" not in st.session_state:
    st.session_state.session_id = f"user_{datetime.now().timestamp():.0f}"
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "¡Bienvenido! Soy el asistente del Metro de Santiago. ¿En qué puedo ayudarte?"}
    ]

for msg in st.session_state.messages:
    if msg["role"] == "cartman":
        with st.chat_message("assistant", avatar=CARTMAN_IMAGE_URL):
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
        with st.chat_message("assistant", avatar=CARTMAN_IMAGE_URL):
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
