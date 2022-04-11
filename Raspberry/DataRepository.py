from Measurement import Measurement
from tinydb import TinyDB, Query

class DataRepository:
    db = TinyDB("nvision.json").table('measurements')
    Unsent = Query()

    def storeData(self, measurement):
        self.db.insert({'type':measurement.type, 'value': measurement.value, 'timestamp': str(measurement.timestamp)})

    def getData(self):
        records = self.db.all()   
        return self.__recordsToMeasurements(records)

    def getUnsentData(self):
        records = self.db.get(self.Unsent.unsent == True)
        return self.__recordsToMeasurements(records)

    def __recordsToMeasurements(self, records):
        measurements = []
        if (records):
            for elem in records:
                measurements.append(Measurement(elem['type'], elem['value'], elem['timestamp']))
        return measurements