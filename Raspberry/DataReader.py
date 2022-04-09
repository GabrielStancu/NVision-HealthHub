from Measurement import Measurement
import serial
import datetime

def myconverter(o):
        if isinstance(o, datetime.datetime):
            return o.__str__()

class DataReader:
    ser = serial.Serial('/dev/ttyACM0',9600)
    refTimestamp = datetime.datetime.now()
    refMillis = 0

    def read(self):
        line = self.ser.readline()

        parts = line.split(";")
        type = parts[0]

        if (type == "NOP"):
            return None

        value = float(parts[1])
        measurementMillis = float(parts[2])
        timestamp = self.__getMeasurementTime(measurementMillis)
        return Measurement(type, value, timestamp)

    def __getMeasurementTime(relMillis):
        global refMillis
        global refTimestamp
        if (refMillis == 0):
            refMillis = relMillis
            refTimestamp = datetime.datetime.now()

        relTime = relMillis - refMillis
        timestamp = refTimestamp + datetime.timedelta(milliseconds=relTime)
        return timestamp
