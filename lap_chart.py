
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

df = pd.read_csv("data/bahrain_lap_times.csv")

# Convert lap times into seconds
def to_seconds(lap_time):
    minutes, seconds = lap_time.split(":")
    return int(minutes) * 60 + float(seconds)

df["LapTimeSeconds"] = df["LapTime"].apply(to_seconds)

# Calculate each driver's average lap time
average_times = (
    df.groupby("Driver")["LapTimeSeconds"]
    .mean()
    .sort_values(ascending=True)
)

Path("charts").mkdir(exist_ok=True)

plt.figure(figsize=(12, 7))
average_times.plot(kind="barh")

plt.title("2024 Bahrain GP - Average Lap Time by Driver")
plt.xlabel("Average Lap Time (seconds)")
plt.ylabel("Driver")
plt.tight_layout()

plt.savefig("charts/average_lap_times.png", dpi=300)
plt.show()

print("Chart saved: charts/average_lap_times.png")
print("\nAverage lap times:")
print(average_times.round(3))
