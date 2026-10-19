
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Load 2024 F1 season data
df = pd.read_csv("data/f1_2024_season.csv")

# Keep valid finishing positions
df["Position"] = pd.to_numeric(df["Position"], errors="coerce")
df["Grid"] = pd.to_numeric(df["Grid"], errors="coerce")

df = df.dropna(subset=["Position", "Grid"])

# Calculate position gain in each race
df["Positions_Gained"] = df["Grid"] - df["Position"]

# Calculate average gain for each driver
driver_analysis = (
    df.groupby("Driver")["Positions_Gained"]
    .mean()
    .sort_values()
)

Path("charts").mkdir(exist_ok=True)

# Create chart
plt.figure(figsize=(12, 8))
driver_analysis.plot(kind="barh")

plt.axvline(0, linestyle="--")
plt.title("2024 F1 Season - Average Positions Gained")
plt.xlabel("Average Positions Gained per Race")
plt.ylabel("Driver")
plt.tight_layout()

plt.savefig("charts/driver_position_analysis.png", dpi=300)
plt.show()

print("\nTOP 5 DRIVERS BY AVERAGE POSITIONS GAINED")
print(driver_analysis.sort_values(ascending=False).head(5).round(2))

print("\nLOWEST 5 AVERAGES")
print(driver_analysis.head(5).round(2))
