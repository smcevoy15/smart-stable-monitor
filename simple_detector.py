import serial
import time
import json
import datetime

ser = serial.Serial("/dev/ttyACM0", 9600) #open connection to nano

PEAK_THRESHOLD = 6000
RMS_THRESHOLD = 80 #adjust later, quiet is 6, clap is 500
EVENT_SECONDS = 3

#constants for adaptive threshold
BASELINE_ALPHA = 0.02 #how quickly baseline updates (0.02 is slow)
BASELINE_MIN = 5.0 #prevents baseline becoming too small
RMS_MULTIPLIER = 8.0 #sustained trigger =baseline by this
RMS_ABS_MIN = 50.0 #minimum threshold even if baseline is tiny

#cooldown  constant
COOLDOWN_SECONDS = 15

event_file = open("/home/pi/smart-stable/events.csv", "a") #logging events

print("Detector running...")

high_rms_start = None #stores time when RMS went high
baseline_rms = None
last_alert_time = 0 #variable stores when last alert happened


while True:
	line = ser.readline().decode().strip() #read one csv line from nano
	parts = line.split(",") #splits each part of reading ie time/temp


	if len(parts) !=5:
		continue

	tempC = float(parts[1])
	humPct = float(parts[2])
	rms = float(parts[3])
	peak = int(parts[4])	
	
	temperature_warning = ""
	if tempC < 0:
		temperature_warning = "WARNING: Temperature freezing"
	elif tempC > 18:
		temperature_warning = "WARNING: Temperature above 18°C"

	if baseline_rms is None:
		baseline_rms = max(rms, BASELINE_MIN)
	else:
		#update baseline hen not in loud event
		if rms < baseline_rms * 3:
			baseline_rms = (1-BASELINE_ALPHA)* baseline_rms + BASELINE_ALPHA * rms
			if baseline_rms < BASELINE_MIN:
				baseline_rms = BASELINE_MIN

	adaptive_threshold = max(baseline_rms * RMS_MULTIPLIER, RMS_ABS_MIN)
	current_time = time.time()
	state = "NORMAL"
	
	cooldown_active = (current_time - last_alert_time < COOLDOWN_SECONDS) 
	if cooldown_active:
		state = "COOLDOWN"
	print("Temp:", tempC, "Hum:", humPct, "RMS:", rms, "Peak:", peak, "Baseline:", round(baseline_rms,1), "Thres:", round(adaptive_threshold,1))


	if peak > PEAK_THRESHOLD: #detection algorithm
		if not cooldown_active:
			timestamp = time.time() #current time in seconds
			state = "IMPACT_ALERT"
			print("ALERT: EVENT DETECTED")

			event_file.write(str(timestamp) + ", EVENT DETECTED,"  + str(peak) + "\n") #save event

			event_file.flush() #froced to save immediately in case of power cut
			last_alert_time =  current_time

	if rms> adaptive_threshold:
		if high_rms_start is None:
			high_rms_start =  time.time()
		elif current_time - high_rms_start >= EVENT_SECONDS:
			if not cooldown_active:
				timestamp = time.time()
				state = "SUSTAINED_ALERT"
				print("ALERT: SUSTAINED NOISE")
				event_file.write(str(timestamp)+ ", SUSTAINED," + str(rms) + "\n")
				event_file.flush()
				last_alert_time  =  current_time
			high_rms_start = None
	else:
		high_rms_start = None

	status = {
		"iso_time": datetime.datetime.now().isoformat(timespec="seconds"),
		"tempC": tempC,
                "humPct": humPct,
		"rms": rms,
		"peak": peak,
		"baseline": baseline_rms,
		"threshold": adaptive_threshold,
		"state": state,
		"temperature_warning": temperature_warning
	}
	
	with open("/home/pi/smart-stable/status.json", "w") as f:
		json.dump(status, f)
