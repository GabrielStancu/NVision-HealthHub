from DataReader import DataReader
from DataRepository import DataRepository
from DataSender import DataSender
from AnomalyDetector import AnomalyDetector
from AnomalyAlerter import AnomalyAlerter
from Predictor import Predictor
from DiagnosisGenerator import DiagnosisGenerator
from EcgProcessor import EcgProcessor

serial_number = "2a994998-7c5a-4062-84cd-a20acdaec72f"
reader = DataReader()
predictor = Predictor()
repository = DataRepository()
diagnosis_generator = DiagnosisGenerator()
ecg_processor = EcgProcessor()
detector = AnomalyDetector(diagnosis_generator, ecg_processor)
sender = DataSender()
alerter = AnomalyAlerter()
booted = True

while True:
    measurement = reader.read()
    if (measurement.type == 'NOP'):
        if (booted == True):
            booted = False
            continue
        repository.store_data()
        measurements = repository.get_data()
        predictions = predictor.predict(measurements)
        anomalies = detector.detect_anomalies(measurements, predictions)
        if (len(anomalies) > 0):
            alerter.alertAnomalies(anomalies, serial_number)
    elif (measurement.type == 'NIL'):
        unsent_measurements = repository.get_unsent_data()
        sender.send_not_sent_data(unsent_measurements, serial_number)
        repository.update_sent_data()
    else:
        repository.keep_data(measurement)
        