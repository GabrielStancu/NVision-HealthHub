from Measurement import Measurement
import serial
import datetime

def myconverter(o):
        if isinstance(o, datetime.datetime):
            return o.__str__()

class DataReader:
    ser = serial.Serial(
        port='/dev/ttyACM0',
        baudrate = 9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
    )   
    refTimestamp = datetime.datetime.now()
    refMillis = 0

    def read(self):
        line = self.ser.readline()
        parts = line.decode("utf-8").replace('\n', '').replace('\r', '').split(";")
        mType = parts[0]

        if (mType == 'NOP' or len(parts) <= 1):
            return None

        print(line)

        value = float(parts[1])
        measurementMillis = float(parts[2])
        timestamp = self.__getMeasurementTime(measurementMillis)
        return Measurement(mType, value, timestamp)

    def __getMeasurementTime(self, relMillis):
        if (self.refMillis == 0):
            self.refMillis = relMillis
            self.refTimestamp = datetime.datetime.now()

        relTime = relMillis - self.refMillis
        timestamp = self.refTimestamp + datetime.timedelta(milliseconds=relTime)
        return timestamp
