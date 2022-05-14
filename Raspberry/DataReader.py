from Measurement import Measurement
import serial
import datetime

def myconverter(o):
        if isinstance(o, datetime.datetime):
            return o.__str__()

class DataReader:
    ser = serial.Serial(
        port='/dev/ttyACM0',
        baudrate = 115200,
        bytesize=serial.EIGHTBITS,
        stopbits=serial.STOPBITS_ONE,
        parity=serial.PARITY_NONE,
        timeout=1
    )   
    refTimestamp = datetime.datetime.now()
    refMillis = 0

    def read(self):
        line = self.ser.readline()
        try:
            parts = line.decode("utf-8").replace('\n', '').replace('\r', '').split(";")
            mType = parts[0]

            if (mType == 'NOP'):
                return Measurement('NOP', None, None)
            elif (len(parts) == 0):
                return Measurement('NIL', None, None)

            print(line)

            value = float(parts[1])
            measurementMillis = float(parts[2])
            timestamp = self.__getMeasurementTime(measurementMillis)
            return Measurement(mType, value, timestamp)
        except: 
            return Measurement('NIL', None, None)

    def __getMeasurementTime(self, relMillis):
        if (self.refMillis == 0):
            self.refMillis = relMillis
            self.refTimestamp = datetime.datetime.now()

        relTime = relMillis - self.refMillis
        timestamp = self.refTimestamp + datetime.timedelta(milliseconds=relTime)
        return timestamp
