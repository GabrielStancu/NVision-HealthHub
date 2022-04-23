from AnomalyAlerter import AnomalyAlerter
from DataReader import DataReader
from DataRepository import DataRepository
from DataSender import DataSender
from AnomalyDetector import AnomalyDetector

serialNumber = "2a994998-7c5a-4062-84cd-a20acdaec72f"
reader = DataReader()
repository = DataRepository()
detector = AnomalyDetector()
sender = DataSender()
alerter = AnomalyAlerter()

while True:
    measurement = reader.read()
    if (measurement == None):
        continue

    repository.storeData(measurement)
    measurements = repository.getData()
    anomaly = detector.detectAnomalies(measurements)
    if (anomaly != None):
        alerter.alertAnomaly(anomaly)
    unsentMeasurements = repository.getUnsentData()
    sender.sendNotSentData(unsentMeasurements, serialNumber)
    repository.updateSentData(unsentMeasurements)