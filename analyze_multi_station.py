
import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = "air_quality_multi_station_clean.csv"

# Load the validated dataset.
df = pd.read_csv(INPUT_FILE)

# Convert timestamps into datetime values.
df["datetime_utc"] = pd.to_datetime(
    df["datetime_utc"], utc=True
)

# Keep PM2.5 records for the main pollution analysis.
pm25 = df[df["parameter"] == "pm25"].copy()

if pm25.empty:
    raise ValueError("No PM2.5 records found in the dataset.")

# Calculate descriptive statistics for each station.
summary = pm25.groupby("location_name")["value"].agg(
    ["count", "mean", "median", "min", "max"]
).round(2)

print("\nPM2.5 Summary by Station (µg/m³):")
print(summary.to_string())

# Calculate the average PM2.5 level at each station.
averages = pm25.groupby("location_name")["value"].mean().sort_values()

print("\nAverage PM2.5 by Station (µg/m³):")
print(averages.round(2).to_string())

# Graph 1: Compare average PM2.5 between stations.
averages.plot(kind="bar", figsize=(9, 5))
plt.title("Average PM2.5 by Lahore Monitoring Station")
plt.xlabel("Monitoring Station")
plt.ylabel("Average PM2.5 (µg/m³)")
plt.xticks(rotation=25, ha="right")
plt.tight_layout()
plt.savefig("pm25_station_comparison.png", dpi=150)
plt.close()

# Graph 2: Show PM2.5 trends over time.
for station, station_data in pm25.groupby("location_name"):
    station_data = station_data.sort_values("datetime_utc")
    plt.plot(
        station_data["datetime_utc"],
        station_data["value"],
        marker=".",
        label=station,
    )

plt.title("PM2.5 Measurements Over Time")
plt.xlabel("Time (UTC)")
plt.ylabel("PM2.5 (µg/m³)")
plt.legend()
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig("pm25_multi_station_trends.png", dpi=150)
plt.close()

print("\nAnalysis completed.")
print("Created: pm25_station_comparison.png")
print("Created: pm25_multi_station_trends.png")
