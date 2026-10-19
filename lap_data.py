
import requests
import pandas as pd
from pathlib import Path

all_laps = []

print("Downloading Bahrain GP 2024 lap times...")

for lap_number in range(1, 58):
    url = (
        "https://api.jolpi.ca/ergast/f1/2024/1/"
        f"laps/{lap_number}.json?limit=100"
    )

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()["MRData"]
    races = data["RaceTable"]["Races"]

    if not races or not races[0].get("Laps"):
        continue

    lap = races[0]["Laps"][0]

    for timing in lap["Timings"]:
        all_laps.append({
            "Race": races[0]["raceName"],
            "Lap": int(lap["number"]),
            "Driver": timing["driverId"],
            "LapTime": timing["time"],
            "Position": int(timing["position"])
        })

    if lap_number % 10 == 0:
        print(f"Processed lap {lap_number}")

df = pd.DataFrame(all_laps)

Path("data").mkdir(exist_ok=True)
df.to_csv("data/bahrain_lap_times.csv", index=False)

print("\nLap-time data saved successfully!")
print("Total records:", len(df))
print(df.head(10).to_string(index=False))
print("\nFile: data/bahrain_lap_times.csv")
