from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

bundle = joblib.load(Path(__file__).parent / "model.joblib")
model, FEATURES = bundle["model"], bundle["features"]

app = FastAPI(title="California House Price API")


class HouseInput(BaseModel):
    MedInc: float = Field(..., gt=0, description="Median income (x $10k)")
    HouseAge: float = Field(..., ge=0)
    AveRooms: float = Field(..., gt=0)
    Latitude: float = Field(..., ge=32, le=42)
    Longitude: float = Field(..., ge=-125, le=-114)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(data: HouseInput):
    df = pd.DataFrame([data.model_dump()])[FEATURES]
    value = float(model.predict(df)[0])
    return {"predicted_value_usd": round(value * 100_000, 2)}