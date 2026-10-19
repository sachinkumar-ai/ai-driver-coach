import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

df = pd.read_csv("data/bahrain_lap_times.csv")

def to_seconds(lap_time):
    minutes, seconds = lap_time.split(":")
    return int(minutes) * 60 + float(seconds)

df["LapTimeSeconds"] = df["LapTime"].apply(to_seconds)

# Calculate lap-time variation for each driver
consistency = df.groupby("Driver")["LapTimeSeconds"].std()
consistency = consistency.sort_values()

Path("charts").mkdir(exist_ok=True)

plt.figure(figsize=(12, 7))
consistency.plot(kind="barh")

plt.title("2024 Bahrain GP - Driver Lap-Time Consistency")
plt.xlabel("Lap-Time Variation (seconds)")
plt.ylabel("Driver")
plt.tight_layout()

plt.savefig("charts/driver_consistency.png", dpi=300)
plt.show()

print("Consistency chart saved!")
print(consistency.round(3))