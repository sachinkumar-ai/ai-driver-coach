

import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

df = pd.read_csv("data/bahrain_lap_times.csv")

def to_seconds(lap_time):
    minutes, seconds = lap_time.split(":")
    return int(minutes) * 60 + float(seconds)

df["LapTimeSeconds"] = df["LapTime"].apply(to_seconds)
df = df.dropna(subset=["Lap", "Position", "Driver", "LapTimeSeconds"])

X = df[["Lap", "Position", "Driver"]]
y = df["LapTimeSeconds"]

preprocessor = ColumnTransformer(
    transformers=[
        ("driver", OneHotEncoder(handle_unknown="ignore"), ["Driver"]),
        ("numbers", "passthrough", ["Lap", "Position"])
    ]
)

model = Pipeline([
    ("preprocessor", preprocessor),
    ("regressor", RandomForestRegressor(
        n_estimators=200,
        min_samples_leaf=5,
        random_state=42
    ))
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model.fit(X_train, y_train)
predictions = model.predict(X_test)

print("MAE:", round(mean_absolute_error(y_test, predictions), 3), "seconds")
print("R² Score:", round(r2_score(y_test, predictions), 3))

Path("models").mkdir(exist_ok=True)
joblib.dump(model, "models/lap_time_model.pkl")

print("Updated model saved successfully!")
