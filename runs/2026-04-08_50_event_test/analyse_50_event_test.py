import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

RUN_DIR = Path("/home/pi/smart-stable/runs/2026-04-08_50_event_test")

gt_file = RUN_DIR / "ground_truth_50_event_run.csv"
pi_file = RUN_DIR / "pi_events_overlap.csv"

# ---------- Load files ----------
gt = pd.read_csv(gt_file)
gt["iso_time"] = pd.to_datetime(gt["iso_time"])

pi = pd.read_csv(
    pi_file,
    header=None,
    names=["iso_time", "detected_class", "value"],
    skipinitialspace=True
)
pi["iso_time"] = pd.to_datetime(pi["iso_time"])
pi["detected_class"] = pi["detected_class"].str.strip()

# ---------- Match events ----------
TIME_TOLERANCE_SECONDS = 8

matches = []
used_pi = set()

for i, gt_row in gt.iterrows():
    gt_time = gt_row["iso_time"]
    gt_class = gt_row["true_class"]

    candidates = []
    for j, pi_row in pi.iterrows():
        if j in used_pi:
            continue
        dt = abs((pi_row["iso_time"] - gt_time).total_seconds())
        if dt <= TIME_TOLERANCE_SECONDS:
            candidates.append((dt, j, pi_row))

    if candidates:
        candidates.sort(key=lambda x: x[0])
        best_dt, best_j, best_row = candidates[0]
        used_pi.add(best_j)

        matches.append({
            "trial_id": gt_row["trial_id"],
            "gt_time": gt_time,
            "gt_class": gt_class,
            "pi_time": best_row["iso_time"],
            "detected_class": best_row["detected_class"],
            "time_error_s": best_dt,
            "matched": True,
            "class_correct": gt_class == best_row["detected_class"]
        })
    else:
        matches.append({
            "trial_id": gt_row["trial_id"],
            "gt_time": gt_time,
            "gt_class": gt_class,
            "pi_time": pd.NaT,
            "detected_class": "MISS",
            "time_error_s": None,
            "matched": False,
            "class_correct": False
        })

results = pd.DataFrame(matches)

# ---------- False positives ----------
false_positives = []
for j, pi_row in pi.iterrows():
    if j not in used_pi:
        false_positives.append({
            "pi_time": pi_row["iso_time"],
            "detected_class": pi_row["detected_class"]
        })

fp_df = pd.DataFrame(false_positives)

# ---------- Summary ----------
total_gt = len(gt)
matched_count = int(results["matched"].sum())
miss_count = int((~results["matched"]).sum())
class_correct_count = int(results["class_correct"].sum())
class_wrong_count = matched_count - class_correct_count
fp_count = len(fp_df)

accuracy_on_all_gt = class_correct_count / total_gt if total_gt else 0.0
recall = matched_count / total_gt if total_gt else 0.0
precision = matched_count / (matched_count + fp_count) if (matched_count + fp_count) else 0.0

print("Total ground truth events:", total_gt)
print("Matched detections:", matched_count)
print("Misses:", miss_count)
print("False positives:", fp_count)
print("Class-correct matches:", class_correct_count)
print("Class-wrong matches:", class_wrong_count)
print(f"Recall: {recall:.3f}")
print(f"Precision: {precision:.3f}")
print(f"Accuracy on all ground-truth events: {accuracy_on_all_gt:.3f}")

# ---------- Confusion matrix ----------
labels = ["IMPACT", "SUSTAINED", "MISS"]
cm = pd.crosstab(
    results["gt_class"],
    results["detected_class"],
    rownames=["Ground Truth"],
    colnames=["Detected"],
    dropna=False
).reindex(index=["IMPACT", "SUSTAINED"], columns=labels, fill_value=0)

print("\nConfusion Matrix:")
print(cm)

# ---------- Save tables ----------
results.to_csv(RUN_DIR / "event_match_results.csv", index=False)
fp_df.to_csv(RUN_DIR / "false_positives.csv", index=False)
cm.to_csv(RUN_DIR / "confusion_matrix.csv")

# ---------- Confusion matrix plot ----------
plt.figure(figsize=(6, 4))
plt.imshow(cm.values, aspect="auto")
plt.xticks(range(len(cm.columns)), cm.columns)
plt.yticks(range(len(cm.index)), cm.index)
plt.xlabel("Detected")
plt.ylabel("Ground Truth")
plt.title("Confusion Matrix")

for r in range(cm.shape[0]):
    for c in range(cm.shape[1]):
        plt.text(c, r, str(cm.iloc[r, c]), ha="center", va="center")

plt.tight_layout()
plt.savefig(RUN_DIR / "confusion_matrix.png", dpi=200)
plt.close()

# ---------- Time error plot ----------
matched_only = results[results["matched"]].copy()
if not matched_only.empty:
    plt.figure(figsize=(8, 4))
    plt.plot(matched_only["trial_id"], matched_only["time_error_s"], marker="o")
    plt.xlabel("Trial ID")
    plt.ylabel("Absolute Time Error (s)")
    plt.title("Matched Event Time Error")
    plt.tight_layout()
    plt.savefig(RUN_DIR / "time_error_plot.png", dpi=200)
    plt.close()
