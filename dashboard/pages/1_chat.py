import requests
import streamlit as st

BACKEND = "http://backend:8000"

st.title("Asistan ile Sohbet")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Mesajınızı yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # TODO: call POST /chat and display reply
    with st.chat_message("assistant"):
        st.write("...")

if __name__ == "__main__":
    print("smoke ok")
