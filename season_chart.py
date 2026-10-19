
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

df = pd.read_csv("data/f1_2024_season.csv")

# Calculate total points for each driver
driver_points = (
    df.groupby("Driver")["Points"]
    .sum()
    .sort_values(ascending=True)
)

# Create charts folder
Path("charts").mkdir(exist_ok=True)

# Draw chart
plt.figure(figsize=(12, 8))
driver_points.plot(kind="barh")

plt.title("2024 F1 Season - Driver Championship Points")
plt.xlabel("Total Points")
plt.ylabel("Driver")
plt.tight_layout()

plt.savefig("charts/season_driver_points.png", dpi=300)
plt.show()

print("Chart saved: charts/season_driver_points.png")
print("\nTop 5 Drivers:")
print(driver_points.sort_values(ascending=False).head(5))
