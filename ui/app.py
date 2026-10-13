import os

import folium
import requests
import streamlit as st
from streamlit_folium import st_folium

API_URL = os.getenv("API_URL", "http://localhost:8000")

BASEMAP_URL = (
    "https://server.arcgisonline.com/ArcGIS/rest/services/"
    "Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}"
)

st.set_page_config(page_title="House Price Predictor", page_icon="🏠", layout="wide")
st.title("🏠 California House Price Predictor")
st.write("Click anywhere on the map to choose a location, set the house details, then click **Predict**.")

# Default location: Los Angeles
if "lat" not in st.session_state:
    st.session_state.lat = 34.05
    st.session_state.lon = -118.24

with st.sidebar:
    st.header("House details")
    med_inc = st.number_input("Median income (x $10k)", 0.5, 15.0, 4.0)
    age = st.number_input("House age (years)", 1, 52, 25)
    rooms = st.number_input("Average rooms", 1.0, 10.0, 5.0)

map_col, result_col = st.columns([2, 1])

with map_col:
    m = folium.Map(
        location=[37.2, -119.5],
        zoom_start=6,
        tiles=BASEMAP_URL,
        attr="Tiles &copy; Esri",
    )
    folium.Marker(
        [st.session_state.lat, st.session_state.lon],
        tooltip="Selected location",
        icon=folium.Icon(color="red", icon="home"),
    ).add_to(m)

    map_data = st_folium(m, height=550, use_container_width=True, key="map")

    clicked = map_data.get("last_clicked") if map_data else None
    if clicked:
        new_point = (round(clicked["lat"], 4), round(clicked["lng"], 4))
        if new_point != (st.session_state.lat, st.session_state.lon):
            st.session_state.lat, st.session_state.lon = new_point
            st.rerun()

with result_col:
    st.subheader("Selected location")
    st.write(f"Latitude: **{st.session_state.lat}**")
    st.write(f"Longitude: **{st.session_state.lon}**")

    if st.button("Predict", type="primary", use_container_width=True):
        payload = {
            "MedInc": med_inc,
            "HouseAge": age,
            "AveRooms": rooms,
            "Latitude": st.session_state.lat,
            "Longitude": st.session_state.lon,
        }
        with st.spinner("Getting prediction... (the free server may take up to a minute to wake up)"):
            try:
                response = requests.post(f"{API_URL}/predict", json=payload, timeout=90)
                if response.status_code == 422:
                    detail = response.json().get("detail")
                    if isinstance(detail, str):
                        st.warning(detail)
                    else:
                        st.warning("Please choose a location inside California.")
                else:
                    response.raise_for_status()
                    price = response.json()["predicted_value_usd"]
                    st.metric("Predicted median house value", f"${price:,.0f}")
            except requests.RequestException as e:
                st.error(f"Could not reach the API: {e}")