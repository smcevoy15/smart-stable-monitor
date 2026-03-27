from flask import Flask, render_template_string
from json import JSONDecodeError
import json
import os

app = Flask(__name__)

STATUS_FILE = "/home/pi/smart-stable/status.json"
EVENT_FILE = "/home/pi/smart-stable/events.csv"

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Smart Stable Monitor</title>
    <meta http-equiv="refresh" content="2">
    <style>
        body { font-family: Arial; background: #f4f4f4; text-align: center; }
        .card { background: white; padding: 20px; margin: 20px auto; width: 400px; border-radius: 10px; box-shadow: 0 0 10px #ccc; }
        .alert { background: #ff4d4d; color: white; padding: 10px; font-size: 20px; border-radius: 5px; }
        .normal { background: #4CAF50; color: white; padding: 10px; font-size: 20px; border-radius: 5px; }
        table { margin: auto; }
        td { padding: 5px 10px; }
    </style>
</head>
<body>

<h1> Smart Stable Monitor </h1>

<div class="card">
    <div class="{{ state_class }}">
        {{ state }}
    </div>
    <table>
        <tr><td><b>Time:</b></td><td>{{ time }}</td></tr>
	<tr><td><b>Temperature:</b></td><td>{{ tempC }}</td></tr>
	<tr><td><b>Humidity:</b></td><td>{{ humPct }}</td></tr>
        <tr><td><b>RMS:</b></td><td>{{ rms }}</td></tr>
        <tr><td><b>Peak:</b></td><td>{{ peak }}</td></tr>
        <tr><td><b>Baseline:</b></td><td>{{ baseline }}</td></tr>
        <tr><td><b>Threshold:</b></td><td>{{ threshold }}</td></tr>
    </table>
</div>

<div class="card">
    <h3>Recent Events</h3>
    <pre>{{ events }}</pre>
</div>

</body>
</html>
"""

@app.route("/")
def index():
	if os.path.exists(STATUS_FILE):
		try:
			with open(STATUS_FILE) as f:
				status = json.load(f)
		except (JSONDecodeError, OSError):
			status = {}
	else:
		status = {}
	state = status.get("state", "UNKNOWN")
	state_class = "normal" if state == "NORMAL" else "alert"
	events = ""
	
	if os.path.exists(EVENT_FILE):
		with open(EVENT_FILE) as f:
			lines = f.readlines()
			events = "".join(lines[-10:])
	return render_template_string(
		HTML,
		state=state,
		state_class=state_class,
		time=status.get("iso_time", ""),
		tempC=status.get("tempC", ""),
		humPct=status.get("humPct", ""),
		rms=status.get("rms", ""),
		peak=status.get("peak", ""),
		baseline=status.get("baseline", ""),
		threshold=status.get("threshold", ""),
		events=events
	)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
