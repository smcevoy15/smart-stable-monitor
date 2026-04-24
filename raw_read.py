import serial, time

PORT = "/dev/serial/by-id/usb-Arduino_Nano_33_BLE_9E92D1BF71894DF2-if00"
BAUD = 9600 

ser = serial.Serial(PORT, BAUD, timeout=1)

time.sleep(2)
ser.reset_input_buffer()

print("reading raw lines ")

while True:
	line = ser.readline().decode(errors="ignore").strip()
	if line:
		print(line)

