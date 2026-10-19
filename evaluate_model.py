
import pandas as pd
import joblib
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.metrics import mean_absolute_error, r2_score

df = pd.read_csv("data/bahrain_lap_times.csv")

def to_seconds(lap_time):
    minutes, seconds = lap_time.split(":")
    return int(minutes) * 60 + float(seconds)

df["LapTimeSeconds"] = df["LapTime"].apply(to_seconds)
df = df.sort_values(["Driver", "Lap"])

df["PreviousLapTime"] = (
    df.groupby("Driver")["LapTimeSeconds"].shift(1)
)

df["Previous3LapAverage"] = (
    df.groupby("Driver")["LapTimeSeconds"]
    .transform(lambda s: s.shift(1).rolling(3, min_periods=3).mean())
)

df = df.dropna(
    subset=["PreviousLapTime", "Previous3LapAverage"]
).copy()

split_lap = int(df["Lap"].max() * 0.7)
test = df[df["Lap"] > split_lap].copy()

features = ["Lap", "PreviousLapTime", "Previous3LapAverage"]
model = joblib.load("models/lap_time_model.pkl")

test["PredictedLapTime"] = model.predict(test[features])
test["ErrorSeconds"] = (
    test["LapTimeSeconds"] - test["PredictedLapTime"]
).abs()

print("MAE:", round(mean_absolute_error(
    test["LapTimeSeconds"], test["PredictedLapTime"]
), 3), "seconds")

print("R² Score:", round(r2_score(
    test["LapTimeSeconds"], test["PredictedLapTime"]
), 3))

Path("charts").mkdir(exist_ok=True)

sample = test[test["Driver"] == "max_verstappen"].sort_values("Lap")

plt.figure(figsize=(12, 6))
plt.plot(sample["Lap"], sample["LapTimeSeconds"], marker="o", label="Actual")
plt.plot(sample["Lap"], sample["PredictedLapTime"], marker="o", label="Predicted")

plt.title("Max Verstappen - Actual vs Predicted Lap Times")
plt.xlabel("Lap Number")
plt.ylabel("Lap Time (seconds)")
plt.legend()
plt.tight_layout()
plt.savefig("charts/prediction_vs_actual.png", dpi=300)
plt.show()

print("Chart saved: charts/prediction_vs_actual.png")
