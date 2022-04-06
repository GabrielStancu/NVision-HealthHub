from SensorType import SensorType

class AnomalyAlerter: 
    def alertAnomaly(anomalies):
        (temp, ecg, pulse, oxygen, gsr) = anomalies
        anomalies = temp + ecg 
        anomalies = anomalies + pulse
        anomalies = anomalies + oxygen 
        anomalies = anomalies + gsr
        for anomaly in anomalies:
            print(str(anomaly.id) + ': ' + str(anomaly.value) + ' at ' + str(anomaly.timestamp) + ', type: ' + str(SensorType(anomaly.sensorType)))