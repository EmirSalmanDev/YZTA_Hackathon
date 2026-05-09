import requests
import streamlit as st

BACKEND = "http://backend:8000"

st.title("Stok Durumu")


def load_stock() -> list:
    response = requests.get(f"{BACKEND}/stock")
    return response.json() if response.ok else []


def load_critical() -> list:
    response = requests.get(f"{BACKEND}/stock/critical")
    return response.json() if response.ok else []


stock = load_stock()
critical_skus = {p["sku"] for p in load_critical()}

if stock:
    st.dataframe(stock, use_container_width=True)
    if critical_skus:
        st.warning(f"Kritik stok uyarısı: {', '.join(critical_skus)}")
else:
    st.info("Stok verisi yok.")

if __name__ == "__main__":
    print("smoke ok")
