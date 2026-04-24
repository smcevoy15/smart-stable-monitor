import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import re

run_dir = Path("/home/pi/smart-stable/runs/2026-03-09_run1")
raw_path = run_dir / "raw_log.csv"
evt_path = run_dir / "events.csv"

# ---- Load raw_log.csv robustly ----
# Expect: iso_time,state,rms,peak,baseline,threshold (sometimes messy spacing)
raw_lines = raw_path.read_text().splitlines()

# Build rows manually so minor formatting doesn't break parsing
rows = []
for i, line in enumerate(raw_lines[1:], start=2):
    parts = [p.strip() for p in line.split(",")]
    # We want at least: iso_time, state, rms, peak, baseline, threshold
    if len(parts) < 6:
        continue
    iso_time = parts[0]
    state = parts[1]
    try:
        rms = float(parts[2])
        peak = float(parts[3])
        baseline = float(parts[4])
        threshold = float(parts[5])
    except ValueError:
        continue
    rows.append([iso_time, state, rms, peak, baseline, threshold])

df = pd.DataFrame(rows, columns=["iso_time","state","rms","peak","baseline","threshold"])
df["t"] = pd.to_datetime(df["iso_time"], errors="coerce")
df = df.dropna(subset=["t"]).sort_values("t")

# ---- Load events.csv (unix_time, message, value) ----
evt_times = []
if evt_path.exists():
    for line in evt_path.read_text().splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 1:
            try:
                evt_times.append(float(parts[0]))
            except ValueError:
                pass

# Convert unix times to datetime (assumes Pi clock correct)
evt_dt = pd.to_datetime(evt_times, unit="s", errors="coerce")
evt_dt = evt_dt.dropna()

# ---- Plot RMS ----
plt.figure()
plt.plot(df["t"], df["rms"], label="RMS")
plt.plot(df["t"], df["threshold"], label="Threshold")
for t in evt_dt:
    plt.axvline(t, linestyle="--", linewidth=1)
plt.xlabel("Time")
plt.ylabel("RMS")
plt.title("Run 1: RMS with event markers")
plt.legend()
plt.tight_layout()
plt.savefig(run_dir / "run1_rms.png", dpi=300)

# ---- Plot Peak ----
plt.figure()
plt.plot(df["t"], df["peak"], label="Peak")
for t in evt_dt:
    plt.axvline(t, linestyle="--", linewidth=1)
plt.xlabel("Time")
plt.ylabel("Peak")
plt.title("Run 1: Peak with event markers")
plt.legend()
plt.tight_layout()
plt.savefig(run_dir / "run1_peak.png", dpi=300)

print("Saved:", run_dir / "run1_rms.png")
print("Saved:", run_dir / "run1_peak.png")
