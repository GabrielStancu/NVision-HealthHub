from Measurement import Measurement
from Splitter import Splitter
from tinydb import TinyDB, Query
import json 

class DataRepository:
    db = TinyDB("nvision.json").table('measurements')
    sent = Query()
    splitter = Splitter()
    measurements = [None for _ in range(5004)]
    counter = 0

    def keep_data(self, measurement):
        self.measurements[self.counter] = {"type": measurement.type, "value": measurement.value, "timestamp": str(measurement.timestamp), "sent": 0}
        self.counter = self.counter + 1

    def store_data(self):
        if (self.counter == 5004):
            self.counter = 0
            self.db.insert_multiple(self.measurements)
            self.measurements = [None for _ in range(5004)]

    def get_data(self):
        records = self.db.all()   
        measurements = self.__records_to_measurements(records)
        return self.splitter.split_measurements(measurements)

    def get_unsent_data(self):
        records = self.db.search(self.sent.sent == 0)
        return self.__records_to_measurements(records)

    def update_sent_data(self, measurements):
        for measurement in measurements:    
            self.db.update({"sent": 1}, self.sent.timestamp == measurement.timestamp)

    def __records_to_measurements(self, records):
        measurements = []
        if (records):
            for record in records:  
                str_record = str(record).replace('\'', '"')
                json_record = json.loads(str_record)
                type = json_record['type']
                value = json_record['value']
                timestamp = json_record['timestamp']
                measurements.append(Measurement(type, value, timestamp))
        return measurements