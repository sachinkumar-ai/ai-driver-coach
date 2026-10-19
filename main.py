


import requests
import pandas as pd
from pathlib import Path

url = "https://api.jolpi.ca/ergast/f1/2024/1/results.json"

print("Loading real F1 race data...")

response = requests.get(url, timeout=30)
response.raise_for_status()

data = response.json()
races = data["MRData"]["RaceTable"]["Races"]
results = races[0]["Results"]

rows = []

for result in results:
    rows.append({
        "Season": 2024,
        "Race": races[0]["raceName"],
        "Position": result["position"],
        "Driver": result["Driver"]["givenName"] + " " + result["Driver"]["familyName"],
        "Team": result["Constructor"]["name"],
        "Grid": result["grid"],
        "Points": result["points"],
        "Laps": result["laps"],
        "Status": result["status"]
    })

df = pd.DataFrame(rows)

Path("data").mkdir(exist_ok=True)
df.to_csv("data/f1_race_results.csv", index=False)

print("\nF1 data loaded successfully!")
print(df.head(10).to_string(index=False))
print("\nTotal drivers:", len(df))
print("Saved to: data/f1_race_results.csv")


import matplotlib.pyplot as plt
from pathlib import Path

# Load race results
df = pd.read_csv("data/f1_race_results.csv")

# Sort drivers by points
df = df.sort_values("Points", ascending=True)

# Create charts folder
Path("charts").mkdir(exist_ok=True)

# Create bar chart
plt.figure(figsize=(10, 6))
plt.barh(df["Driver"], df["Points"])
plt.xlabel("Points")
plt.ylabel("Driver")
plt.title("2024 Bahrain GP - Driver Performance")
plt.tight_layout()

# Save chart
plt.savefig("charts/driver_performance.png", dpi=300)
plt.show()

print("Chart saved: charts/driver_performance.png")


# AI Driver Coach - Basic Performance Analysis

print("\n" + "=" * 40)
print("       AI DRIVER COACH")
print("=" * 40)

df = pd.read_csv("data/f1_race_results.csv")

winner = df.loc[df["Position"].idxmin()]
best_grid = df.loc[df["Grid"].idxmin()]

print(f"\nRace: {df['Race'].iloc[0]}")
print(f"Winner: {winner['Driver']}")
print(f"Winning Team: {winner['Team']}")
print(f"Points Scored: {winner['Points']}")

print("\n--- Driver Performance Insights ---")

for _, driver in df.iterrows():
    position = int(driver["Position"])
    grid = int(driver["Grid"])
    points = float(driver["Points"])

    if position < grid:
        print(
            f"{driver['Driver']}: Improved "
            f"{grid - position} position(s) during the race."
        )
    elif position > grid:
        print(
            f"{driver['Driver']}: Lost "
            f"{position - grid} position(s) during the race."
        )
    else:
        print(
            f"{driver['Driver']}: Finished in the starting position."
        )

print("\n--- Coach Summary ---")
print(
    f"{winner['Driver']} won the race and scored "
    f"{winner['Points']} points."
)

