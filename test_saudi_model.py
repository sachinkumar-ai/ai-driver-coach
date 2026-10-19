
import pandas as pd
import joblib
from sklearn.metrics import mean_absolute_error, r2_score

# Load Saudi GP data
df = pd.read_csv("data/saudi_lap_times.csv")

# Convert lap times into seconds
def to_seconds(t):
    parts = str(t).split(":")
    if len(parts) == 2:
        return float(parts[0]) * 60 + float(parts[1])
    return float(parts[0])

df["LapTime"] = df["LapTime"].apply(to_seconds)
# Remove unusually slow laps (e.g. pit stops or incidents)
df = df[df["LapTime"].between(70, 110)].copy()
df = df.sort_values(["Driver", "Lap"])

# Create previous-lap features
df["PreviousLapTime"] = df.groupby("Driver")["LapTime"].shift(1)
df["Previous3LapAverage"] = (
    df.groupby("Driver")["LapTime"]
    .transform(lambda s: s.shift(1).rolling(3, min_periods=1).mean())
)

df = df.dropna(subset=["PreviousLapTime", "Previous3LapAverage"])

# Load the existing trained model
model = joblib.load("models/lap_time_model.pkl")

features = ["Lap", "PreviousLapTime", "Previous3LapAverage"]
X = df[features]
y = df["LapTime"]

predictions = model.predict(X)

df["PredictedLapTime"] = predictions
df["Error"] = abs(df["LapTime"] - df["PredictedLapTime"])

print("\nLargest prediction errors:")
print(
    df[["Lap", "Driver", "LapTime", "PredictedLapTime", "Error"]]
    .sort_values("Error", ascending=False)
    .head(10)
    .round(3)
    .to_string(index=False)
)

print("Saudi GP Model Test")
print("-------------------")
print("Test records:", len(df))
print("Rows after filtering:", len(df))
print("Actual lap-time range:", y.min(), "to", y.max())
print("Mean actual lap time:", round(y.mean(), 3))
print("Mean predicted lap time:", round(predictions.mean(), 3))
print("MAE:", round(mean_absolute_error(y, predictions), 3), "seconds")
print("R2 Score:", round(r2_score(y, predictions), 3))

print("\nDriver-wise MAE:")
print(
    df.assign(Error=abs(y - predictions))
    .groupby("Driver")["Error"]
    .mean()
    .sort_values()
    .round(3)
    .to_string()
)

print("\nLargest prediction errors:")
print(
    df[["Lap", "Driver", "LapTime", "PredictedLapTime", "Error"]]
    .sort_values("Error", ascending=False)
    .head(10)
    .round(3)
    .to_string(index=False)
)