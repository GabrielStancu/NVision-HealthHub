import serial

ser = serial.Serial('/dev/ttyACM0',9600)
s = [0]
while True:
    read_serial = ser.readline()
    line = ser.readline()
    print(line)
    # s[0] = str(float(line))
    # print(s[0])
    # print(read_serial)