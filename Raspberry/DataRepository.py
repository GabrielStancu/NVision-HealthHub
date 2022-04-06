from Measurement import Measurement
import pymongo

class DataRepository:
    dbClient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = dbClient["healthDb"]
    measurementsCollection = db["measurements"]
    unsentQuery = { "sent": False }
    updateQuery = { "$set": { "sent": True } }

    def storeData(self, measurement):
        self.measurementsCollection.insert_one(measurement)

    def getData(self):
        collection = self.measurementsCollection
        return self.__collectionToMeasurements(collection)     

    def getUnsentData(self):
        collection = self.getData().find(self.unsentQuery)
        return self.__collectionToMeasurements(collection)

    def __collectionToMeasurements(collection):
        measurements = []
        for elem in collection:
            measurements.append(Measurement(elem.type, elem.value, elem.timestamp))
        return measurements