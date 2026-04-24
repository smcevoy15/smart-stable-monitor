import time, json, csv, os

STATUS = "/home/pi/smart-stable/status.json"
OUT = "/home/pi/smart-stable/runs/2026-03-09_run1/raw_log.csv"

if not os.path.exists(OUT):
    with open(OUT, "w", newline="") as f:
        csv.writer(f).writerow(["iso_time","state","rms","peak","baseline","threshold"])

print("Logging status.json -> raw_log.csv (Ctrl+C to stop)")

while True:
    try:
        with open(STATUS) as f:
            s = json.load(f)
        row = [s.get("iso_time",""),
               s.get("state",""),
               s.get("rms",""),
               s.get("peak",""),
               s.get("baseline",""),
               s.get("threshold","")]
        with open(OUT, "a", newline="") as f:
            csv.writer(f).writerow(row)
    except Exception:
        pass
    time.sleep(1)
