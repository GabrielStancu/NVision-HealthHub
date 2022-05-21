from DataReader import DataReader
from DataRepository import DataRepository
from DataSender import DataSender
from AnomalyDetector import AnomalyDetector
from Predictor import Predictor
from EcgProcessor import EcgProcessor

serial_number = "2a994998-7c5a-4062-84cd-a20acdaec72f"
reader = DataReader()
predictor = Predictor()
repository = DataRepository()
ecg_processor = EcgProcessor()
detector = AnomalyDetector(ecg_processor)
sender = DataSender()

while True:
    measurement = reader.read()
    if (measurement.type == 'NOP'):
        measurements = repository.get_data()
        predictions = predictor.predict(measurements)
        anomalies = detector.detect_anomalies(measurements, predictions, ecg_processor)
        if (len(anomalies) > 0):
            sender.send_alert(anomalies, serial_number)
    elif (measurement.type == 'NIL'):
        unsent_measurements = repository.get_unsent_data()
        sender.send_not_sent_data(unsent_measurements, serial_number)
        repository.update_sent_data(unsent_measurements)
    else:
        repository.store_data(measurement)
        