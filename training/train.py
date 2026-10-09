from sklearn.datasets import fetch_california_housing
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

FEATURES = ["MedInc", "HouseAge", "AveRooms", "Latitude", "Longitude"]

df = fetch_california_housing(as_frame=True).frame
X, y = df[FEATURES], df["MedHouseVal"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestRegressor(
    n_estimators=100, max_depth=10, n_jobs=-1, random_state=42
)
model.fit(X_train, y_train)

pred = model.predict(X_test)
print(f"MAE: {mean_absolute_error(y_test, pred):.3f}")
print(f"R2:  {r2_score(y_test, pred):.3f}")

joblib.dump({"model": model, "features": FEATURES}, "api/model.joblib", compress=3)
print("Model saved to api/model.joblib")