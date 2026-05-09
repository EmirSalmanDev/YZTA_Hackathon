import requests
import streamlit as st

BACKEND = "http://backend:8000"

st.title("Siparişler")


def load_orders() -> list:
    # TODO: handle connection errors
    response = requests.get(f"{BACKEND}/orders")
    return response.json() if response.ok else []


orders = load_orders()

if orders:
    st.dataframe(orders, use_container_width=True)
else:
    st.info("Henüz sipariş yok.")

if __name__ == "__main__":
    print("smoke ok")
