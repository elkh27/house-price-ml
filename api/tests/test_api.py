from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

VALID_HOUSE = {
    "MedInc": 4.0,
    "HouseAge": 25,
    "AveRooms": 5.0,
    "Latitude": 34.05,
    "Longitude": -118.24,
}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_returns_positive_price():
    response = client.post("/predict", json=VALID_HOUSE)
    assert response.status_code == 200
    assert response.json()["predicted_value_usd"] > 0


def test_invalid_latitude_is_rejected():
    bad_house = {**VALID_HOUSE, "Latitude": 80}
    response = client.post("/predict", json=bad_house)
    assert response.status_code == 422


def test_missing_fields_are_rejected():
    response = client.post("/predict", json={"MedInc": 4.0})
    assert response.status_code == 422