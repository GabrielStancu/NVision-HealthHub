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

while True:
    measurement = reader.read()
    if (measurement.type == 'NOP'):
        measurements = repository.getData()
        predictions = predictor.predict(measurements)
        anomalies = detector.detectAnomalies(measurements, predictions)
        if (len(anomalies) > 0):
            alerter.alertAnomaly(anomalies)
    elif (measurement.type == 'NIL'):
        unsentMeasurements = repository.getUnsentData()
        sender.sendNotSentData(unsentMeasurements, serialNumber)
        repository.updateSentData(unsentMeasurements)
    else:
        repository.storeData(measurement)
        
    