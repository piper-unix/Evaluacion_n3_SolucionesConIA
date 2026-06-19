import os
import streamlit as st
import requests
import json
from datetime import datetime

BACKEND_URL = st.secrets.get("BACKEND_URL", os.getenv("BACKEND_URL", "http://backend:8000"))

st.set_page_config(
    page_title="Metro Santiago Chat",
    page_icon="🚇",
    layout="centered",
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
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Escribe tu consulta aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

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
