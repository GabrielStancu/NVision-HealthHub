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
    ref_timestamp = datetime.datetime.now()
    ref_millis = 0

    def read(self):
        line = self.ser.readline()
        try:
            parts = line.decode("utf-8").replace('\n', '').replace('\r', '').split(";")
            m_type = parts[0]

            if (m_type == 'NOP'):
                return Measurement('NOP', None, None)
            elif (len(parts) == 0):
                return Measurement('NIL', None, None)

            value = float(parts[1])
            measurement_millis = float(parts[2])
            timestamp = self.__get_measurement_time(measurement_millis)
            return Measurement(m_type, value, timestamp)
        except: 
            return Measurement('NIL', None, None)

    def __get_measurement_time(self, rel_millis):
        if (self.ref_millis == 0):
            self.ref_millis = rel_millis
            self.ref_timestamp = datetime.datetime.now()

        rel_time = rel_millis - self.ref_millis
        timestamp = self.ref_timestamp + datetime.timedelta(milliseconds=rel_time)
        return timestamp
