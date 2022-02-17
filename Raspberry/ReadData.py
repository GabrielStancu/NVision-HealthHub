import serial

ser = serial.Serial('/dev/ttyACM0',9600)
s = [0]
while True:
    read_serial = ser.readline()
    line = ser.readline()
    parts = line.split(";")
    print("Heartbeat: " + parts[0] + "\n")
    print("Temperature: " + parts[1] + "\n")
