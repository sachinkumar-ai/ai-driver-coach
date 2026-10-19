
import requests
import pandas as pd
from pathlib import Path

all_results = []

print("Downloading 2024 F1 race results...")

for round_no in range(1, 25):
    url = (
        "https://api.jolpi.ca/ergast/f1/2024/"
        f"{round_no}/results.json?limit=100"
    )

    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()

        races = response.json()["MRData"]["RaceTable"]["Races"]

        if not races:
            continue

        race = races[0]

        for result in race["Results"]:
            all_results.append({
                "Season": 2024,
                "Round": round_no,
                "Race": race["raceName"],
                "Date": race["date"],
                "Position": int(result["position"]),
                "Driver": (
                    result["Driver"]["givenName"]
                    + " "
                    + result["Driver"]["familyName"]
                ),
                "Team": result["Constructor"]["name"],
                "Grid": int(result["grid"]),
                "Points": float(result["points"]),
                "Laps": int(result["laps"]),
                "Status": result["status"]
            })

        print(f"Round {round_no}: {race['raceName']}")

    except requests.RequestException as error:
        print(f"Round {round_no} failed: {error}")

df = pd.DataFrame(all_results)

Path("data").mkdir(exist_ok=True)

df.to_csv("data/f1_2024_season.csv", index=False)

print("\nSeason data downloaded!")
print("Total records:", len(df))
print("Total races:", df["Round"].nunique())
print("Saved: data/f1_2024_season.csv")
