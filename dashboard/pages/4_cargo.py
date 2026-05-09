import requests
import streamlit as st

BACKEND = "http://backend:8000"

st.title("Kargo Takip")

tracking_id = st.text_input("Takip Numarası", placeholder="TRK-001")

if st.button("Sorgula") and tracking_id:
    response = requests.get(f"{BACKEND}/cargo/track/{tracking_id}")
    if response.ok:
        data = response.json()
        st.success(f"Durum: {data['status']}")
        st.json(data)
    else:
        st.error("Takip numarası bulunamadı.")

if __name__ == "__main__":
    print("smoke ok")
