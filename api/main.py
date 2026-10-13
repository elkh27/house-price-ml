from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sklearn.neighbors import BallTree

EARTH_RADIUS_KM = 6371.0
MAX_DISTANCE_KM = 5.0

bundle = joblib.load(Path(__file__).parent / "model.joblib")
model, FEATURES = bundle["model"], bundle["features"]

# Spatial index of training locations, used to reject points outside data coverage
tree = BallTree(np.radians(bundle["coords"]), metric="haversine")

app = FastAPI(title="California House Price API")


class HouseInput(BaseModel):
    MedInc: float = Field(..., gt=0, description="Median income (x $10k)")
    HouseAge: float = Field(..., ge=0)
    AveRooms: float = Field(..., gt=0)
    Latitude: float = Field(..., ge=32, le=42)
    Longitude: float = Field(..., ge=-125, le=-114)


def distance_to_nearest_km(lat: float, lon: float) -> float:
    dist, _ = tree.query(np.radians([[lat, lon]]), k=1)
    return float(dist[0][0] * EARTH_RADIUS_KM)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(data: HouseInput):
    distance = distance_to_nearest_km(data.Latitude, data.Longitude)
    if distance > MAX_DISTANCE_KM:
        raise HTTPException(
            status_code=422,
            detail=(
                f"This location is {distance:.0f} km from the nearest area in the "
                "training data (for example ocean or uninhabited land), so the model "
                "can't make a reliable prediction here."
            ),
        )

    df = pd.DataFrame([data.model_dump()])[FEATURES]
    value = float(model.predict(df)[0])
    return {
        "predicted_value_usd": round(value * 100_000, 2),
        "distance_to_nearest_data_km": round(distance, 2),
    }