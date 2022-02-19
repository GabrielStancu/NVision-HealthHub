import serial

ser = serial.Serial('/dev/ttyACM0',9600)
while True:
    read_serial = ser.readline()
    line = ser.readline()
    parts = line.split(";")
    print("Heartbeat: " + parts[0])
    print("Temperature: " + parts[1])
    print("Ecg: " + parts[2])
