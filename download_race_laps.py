

import requests
import pandas as pd
from pathlib import Path
import time

year = 2024
round_number = 2
race_name = "Saudi Arabian Grand Prix"
all_laps = []

for lap_number in range(1, 51):
    url = (
        f"https://api.jolpi.ca/ergast/f1/{year}/"
        f"{round_number}/laps/{lap_number}.json?limit=100"
    )

    for attempt in range(3):
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            data = response.json()

            races = data["MRData"]["RaceTable"]["Races"]

            if races and races[0].get("Laps"):
                for item in races[0]["Laps"][0]["Timings"]:
                    all_laps.append({
                        "Race": race_name,
                        "Lap": lap_number,
                        "Driver": item["driverId"],
                        "LapTime": item["time"],
                        "Position": int(item["position"])
                    })

            break

        except Exception as error:
            print(f"Lap {lap_number}, attempt {attempt + 1}: {error}")
            time.sleep(2)

    if lap_number % 10 == 0:
        print(f"Checked through lap {lap_number}")

    time.sleep(0.2)

df = pd.DataFrame(all_laps)
Path("data").mkdir(exist_ok=True)
df.to_csv("data/saudi_lap_times.csv", index=False)

print("\nDownload complete!")
print("Records:", len(df))
print("Unique laps:", df["Lap"].nunique() if not df.empty else 0)
print("Last lap:", df["Lap"].max() if not df.empty else "No data")
