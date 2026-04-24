import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from math import sqrt

RUN_DIR = Path("/home/pi/smart-stable/runs/2026-03-31_govee_validation")

pi_file = RUN_DIR / "pi_raw_log_overlap.csv"
govee_file = RUN_DIR / "govee_export.csv"

# Load CSVs
pi_df = pd.read_csv(pi_file)
govee_df = pd.read_csv(govee_file)

govee_df.columns = [c.replace("\xa0", " ").strip() for c in govee_df.columns]
# Parse timestamps
pi_df["iso_time"] = pd.to_datetime(pi_df["iso_time"])
govee_df["Timestamp for sample frequency every 1 min min"] = pd.to_datetime(
    govee_df["Timestamp for sample frequency every 1 min min"]
)

# Keep only needed columns
pi_df = pi_df[["iso_time", "tempC", "humPct"]].copy()
govee_df = govee_df[
    ["Timestamp for sample frequency every 1 min min", "Temperature_Celsius", "Relative_Humidity"]
].copy()

# Rename columns to common names
govee_df.columns = ["time", "govee_tempC", "govee_humPct"]
pi_df.columns = ["time", "pi_tempC", "pi_humPct"]

# Round Pi timestamps down to the minute and average within each minute
pi_df["time"] = pi_df["time"].dt.floor("min")
pi_minute = pi_df.groupby("time", as_index=False).mean()

# Merge on common minute timestamps
merged = pd.merge(pi_minute, govee_df, on="time", how="inner")

# Calculate errors
merged["temp_error"] = merged["pi_tempC"] - merged["govee_tempC"]
merged["hum_error"] = merged["pi_humPct"] - merged["govee_humPct"]

temp_mae = merged["temp_error"].abs().mean()
hum_mae = merged["hum_error"].abs().mean()

temp_rmse = sqrt((merged["temp_error"] ** 2).mean())
hum_rmse = sqrt((merged["hum_error"] ** 2).mean())

temp_bias = merged["temp_error"].mean()
hum_bias = merged["hum_error"].mean()

print("Rows merged:", len(merged))
print(f"Temperature MAE:  {temp_mae:.3f} °C")
print(f"Temperature RMSE: {temp_rmse:.3f} °C")
print(f"Temperature Bias: {temp_bias:.3f} °C")
print()
print(f"Humidity MAE:  {hum_mae:.3f} %")
print(f"Humidity RMSE: {hum_rmse:.3f} %")
print(f"Humidity Bias: {hum_bias:.3f} %")

# Save merged data
merged.to_csv(RUN_DIR / "merged_pi_govee.csv", index=False)

# Temperature overlay plot
plt.figure(figsize=(10, 5))
plt.plot(merged["time"], merged["pi_tempC"], label="Pi/Nano Temp")
plt.plot(merged["time"], merged["govee_tempC"], label="Govee Temp")
plt.xlabel("Time")
plt.ylabel("Temperature (°C)")
plt.title("Temperature Comparison: Pi/Nano vs Govee")
plt.legend()
plt.tight_layout()
plt.savefig(RUN_DIR / "temperature_overlay.png", dpi=200)
plt.close()

# Humidity overlay plot
plt.figure(figsize=(10, 5))
plt.plot(merged["time"], merged["pi_humPct"], label="Pi/Nano Humidity")
plt.plot(merged["time"], merged["govee_humPct"], label="Govee Humidity")
plt.xlabel("Time")
plt.ylabel("Relative Humidity (%)")
plt.title("Humidity Comparison: Pi/Nano vs Govee")
plt.legend()
plt.tight_layout()
plt.savefig(RUN_DIR / "humidity_overlay.png", dpi=200)
plt.close()

# Temperature scatter
plt.figure(figsize=(6, 6))
plt.scatter(merged["govee_tempC"], merged["pi_tempC"])
min_temp = min(merged["govee_tempC"].min(), merged["pi_tempC"].min())
max_temp = max(merged["govee_tempC"].max(), merged["pi_tempC"].max())
plt.plot([min_temp, max_temp], [min_temp, max_temp])
plt.xlabel("Govee Temp (°C)")
plt.ylabel("Pi/Nano Temp (°C)")
plt.title("Temperature Scatter")
plt.tight_layout()
plt.savefig(RUN_DIR / "temperature_scatter.png", dpi=200)
plt.close()

# Humidity scatter
plt.figure(figsize=(6, 6))
plt.scatter(merged["govee_humPct"], merged["pi_humPct"])
min_h = min(merged["govee_humPct"].min(), merged["pi_humPct"].min())
max_h = max(merged["govee_humPct"].max(), merged["pi_humPct"].max())
plt.plot([min_h, max_h], [min_h, max_h])
plt.xlabel("Govee Humidity (%)")
plt.ylabel("Pi/Nano Humidity (%)")
plt.title("Humidity Scatter")
plt.tight_layout()
plt.savefig(RUN_DIR / "humidity_scatter.png", dpi=200)
plt.close()
