
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

df = pd.read_csv("data/bahrain_lap_times.csv")

def to_seconds(lap_time):
    minutes, seconds = lap_time.split(":")
    return int(minutes) * 60 + float(seconds)

df["LapTimeSeconds"] = df["LapTime"].apply(to_seconds)
df = df.dropna(subset=["Lap", "Driver", "LapTimeSeconds"])
df = df.sort_values(["Driver", "Lap"])

# Previous lap time for each driver
df["PreviousLapTime"] = (
    df.groupby("Driver")["LapTimeSeconds"].shift(1)
)

# Average of the previous 3 laps, excluding current lap
df["Previous3LapAverage"] = (
    df.groupby("Driver")["LapTimeSeconds"]
    .transform(lambda s: s.shift(1).rolling(3, min_periods=3).mean())
)

df = df.dropna(
    subset=["PreviousLapTime", "Previous3LapAverage"]
).copy()

features = ["Lap", "PreviousLapTime", "Previous3LapAverage"]
X = df[features]
y = df["LapTimeSeconds"]

# Test on later laps instead of randomly mixing laps
split_lap = int(df["Lap"].max() * 0.7)
train = df[df["Lap"] <= split_lap]
test = df[df["Lap"] > split_lap]

X_train = train[features]
y_train = train["LapTimeSeconds"]
X_test = test[features]
y_test = test["LapTimeSeconds"]

model = RandomForestRegressor(
    n_estimators=200,
    min_samples_leaf=5,
    random_state=42
)
model.fit(X_train, y_train)

predictions = model.predict(X_test)

print("MAE:", round(mean_absolute_error(y_test, predictions), 3), "seconds")
print("R² Score:", round(r2_score(y_test, predictions), 3))

Path("models").mkdir(exist_ok=True)
joblib.dump(model, "models/lap_time_model.pkl")
print("Improved model saved successfully!")
