from AnomalyDetector import AnomalyDetector
from SensorType import SensorType


serialNumber = "2a994998-7c5a-4062-84cd-a20acdaec72f"
detector = AnomalyDetector(serialNumber)
(temp, ecg, pulse, oxygen, gsr) = detector.detectAnomaly()
anomalies = temp + ecg 
anomalies = anomalies + pulse
anomalies = anomalies + oxygen 
anomalies = anomalies + gsr
for anomaly in anomalies:
    print(str(anomaly.id) + ': ' + str(anomaly.value) + ' at ' + str(anomaly.timestamp) + ', type: ' + str(SensorType(anomaly.sensorType)))