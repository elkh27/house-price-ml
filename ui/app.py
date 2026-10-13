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