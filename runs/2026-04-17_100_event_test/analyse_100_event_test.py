
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import metrics

# ---------------- FILES ----------------
gt_file = "/home/pi/smart-stable/runs/2026-04-17_100_event_test/ground_truth_100_event_run.csv"
pi_file = "/home/pi/smart-stable/runs/2026-04-17_100_event_test/pi_events_run_window.csv"

TIME_WINDOW = 3  # seconds

# ---------------- LOAD DATA ----------------
gt = pd.read_csv(gt_file)
pi = pd.read_csv(
    pi_file,
    header=None,
    names=["iso_time", "detected_class", "value"],
    skipinitialspace=True
)

gt["time"] = pd.to_datetime(gt["iso_time"])
pi["time"] = pd.to_datetime(pi["iso_time"])
pi["detected_class"] = pi["detected_class"].str.strip()

# ---------------- MATCH EVENTS ----------------
used_pi = set()
matched_pairs = []

for _, gt_row in gt.iterrows():
    gt_time = gt_row["time"]
    gt_class = gt_row["true_class"]

    best_idx = None
    best_diff = TIME_WINDOW + 1

    for i, pi_row in pi.iterrows():
        if i in used_pi:
            continue

        diff = abs((pi_row["time"] - gt_time).total_seconds())
        if diff <= TIME_WINDOW and diff < best_diff:
            best_diff = diff
            best_idx = i

    if best_idx is not None:
        used_pi.add(best_idx)
        detected_class = pi.loc[best_idx, "detected_class"]
    else:
        detected_class = "NONE"

    matched_pairs.append((gt_class, detected_class))

# ---------------- BUILD BINARY LABELS ----------------
# For IMPACT matrix:
# actual 1 = IMPACT, 0 = NOT IMPACT
# predicted 1 = IMPACT, 0 = NOT IMPACT
impact_actual = []
impact_pred = []

# For SUSTAINED matrix:
# actual 1 = SUSTAINED, 0 = NOT SUSTAINED
# predicted 1 = SUSTAINED, 0 = NOT SUSTAINED
sust_actual = []
sust_pred = []

for gt_class, det_class in matched_pairs:
    # IMPACT
    impact_actual.append(1 if gt_class == "IMPACT" else 0)
    impact_pred.append(1 if det_class == "IMPACT" else 0)

    # SUSTAINED
    sust_actual.append(1 if gt_class == "SUSTAINED" else 0)
    sust_pred.append(1 if det_class == "SUSTAINED" else 0)

# ---------------- CONFUSION MATRICES ----------------
impact_cm = metrics.confusion_matrix(impact_actual, impact_pred, labels=[1, 0])
sust_cm = metrics.confusion_matrix(sust_actual, sust_pred, labels=[1, 0])

print("\nIMPACT confusion matrix [[TP, FN], [FP, TN]]:")
print(impact_cm)

print("\nSUSTAINED confusion matrix [[TP, FN], [FP, TN]]:")
print(sust_cm)

# ---------------- METRICS ----------------
impact_precision = metrics.precision_score(impact_actual, impact_pred, zero_division=0)
impact_recall = metrics.recall_score(impact_actual, impact_pred, zero_division=0)
impact_accuracy = metrics.accuracy_score(impact_actual, impact_pred)

sust_precision = metrics.precision_score(sust_actual, sust_pred, zero_division=0)
sust_recall = metrics.recall_score(sust_actual, sust_pred, zero_division=0)
sust_accuracy = metrics.accuracy_score(sust_actual, sust_pred)

print(f"\nIMPACT Precision: {impact_precision:.3f}")
print(f"IMPACT Recall:    {impact_recall:.3f}")
print(f"IMPACT Accuracy:  {impact_accuracy:.3f}")

print(f"\nSUSTAINED Precision: {sust_precision:.3f}")
print(f"SUSTAINED Recall:    {sust_recall:.3f}")
print(f"SUSTAINED Accuracy:  {sust_accuracy:.3f}")

# ---------------- PLOTS ----------------
impact_display = metrics.ConfusionMatrixDisplay(
    confusion_matrix=impact_cm,
    display_labels=["IMPACT", "NOT IMPACT"]
)
impact_display.plot()
plt.title("IMPACT Confusion Matrix")
plt.savefig("/home/pi/smart-stable/runs/2026-04-17_100_event_test/impact_confusion_matrix.png", dpi=200)
plt.close()

sust_display = metrics.ConfusionMatrixDisplay(
    confusion_matrix=sust_cm,
    display_labels=["SUSTAINED", "NOT SUSTAINED"]
)
sust_display.plot()
plt.title("SUSTAINED Confusion Matrix")
plt.savefig("/home/pi/smart-stable/runs/2026-04-17_100_event_test/sustained_confusion_matrix.png", dpi=200)
plt.close()
