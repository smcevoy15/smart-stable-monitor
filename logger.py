
import serial
import time
import csv

PORT ="/dev/ttyACM0"
BAUD = 9600

ser = serial.Serial(PORT, BAUD, timeout=1)

 
print(" Logging started...")

with open("stable_log.csv", "a", newline="") as f:
	writer = csv.writer(f)

	while True:
		line = ser.readline().decode(errors="ignore").strip()

		if line:
			timestamp = time.time()
			print(timestamp, line)
			writer.writerow([timestamp, line])
			f.flush()
