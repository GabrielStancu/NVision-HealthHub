from Measurement import Measurement
from tinydb import TinyDB, Query
import json 

class DataRepository:
    db = TinyDB("nvision.json").table('measurements')
    Sent = Query()

    def storeData(self, measurement):
        self.db.insert({"type":measurement.type, "value": measurement.value, "timestamp": str(measurement.timestamp), "sent": 0})

    def getData(self):
        records = self.db.all()   
        return self.__recordsToMeasurements(records)

    def getUnsentData(self):
        records = self.db.search(self.Sent.sent == 0)
        return self.__recordsToMeasurements(records)

    def updateSentData(self, measurements):
        for measurement in measurements:    
            self.db.update({"sent": 1}, self.Sent.timestamp == measurement.timestamp)

    def __recordsToMeasurements(self, records):
        measurements = []
        if (records):
            for record in records:  
                strRecord = str(record).replace('\'', '"')
                jsonRecord = json.loads(strRecord)
                type = jsonRecord['type']
                value = jsonRecord['value']
                timestamp = jsonRecord['timestamp']
                measurements.append(Measurement(type, value, timestamp))
        return measurements