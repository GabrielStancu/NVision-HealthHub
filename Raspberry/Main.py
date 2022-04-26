from AnomalyAlerter import AnomalyAlerter
from DataReader import DataReader
from DataRepository import DataRepository
from DataSender import DataSender
from AnomalyDetector import AnomalyDetector
from Predictor import Predictor

serialNumber = "2a994998-7c5a-4062-84cd-a20acdaec72f"
reader = DataReader()
predictor = Predictor()
repository = DataRepository()
detector = AnomalyDetector()
sender = DataSender()
alerter = AnomalyAlerter()
analyzed = True

while True:
    measurement = reader.read()
    if (measurement != None):
        repository.storeData(measurement)
        analyzed = False
    elif (measurement == None and analyzed == False):
        measurements = repository.getData()
        predictions = predictor.predict(measurements)
        anomalies = detector.detectAnomalies(measurements, predictions)
        if (anomalies != None):
            alerter.alertAnomaly(anomalies)
        analyzed = True
    else:
        unsentMeasurements = repository.getUnsentData()
        sender.sendNotSentData(unsentMeasurements, serialNumber)
        repository.updateSentData(unsentMeasurements)