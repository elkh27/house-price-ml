import os

import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="House Price Predictor", page_icon="🏠")
st.title("🏠 California House Price Predictor")
st.write("Choose a location and house details, then click **Predict**.")

with st.sidebar:
    st.header("Location")
    lat = st.slider("Latitude", 32.5, 42.0, 34.05)
    lon = st.slider("Longitude", -124.4, -114.3, -118.24)

    st.header("House details")
    med_inc = st.number_input("Median income (x $10k)", 0.5, 15.0, 4.0)
    age = st.number_input("House age (years)", 1, 52, 25)
    rooms = st.number_input("Average rooms", 1.0, 10.0, 5.0)

st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}), zoom=6)

if st.button("Predict", type="primary"):
    payload = {
        "MedInc": med_inc,
        "HouseAge": age,
        "AveRooms": rooms,
        "Latitude": lat,
        "Longitude": lon,
    }
    with st.spinner("Getting prediction... (the free server may take up to a minute to wake up)"):
        try:
            response = requests.post(f"{API_URL}/predict", json=payload, timeout=90)
            response.raise_for_status()
            price = response.json()["predicted_value_usd"]
            st.success(f"Predicted median house value: **${price:,.0f}**")
        except requests.RequestException as e:
            st.error(f"Could not reach the API: {e}")