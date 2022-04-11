class AnomalyAlerter: 
    def alertAnomaly(self, anomalies):
        (temp, ecg, pulse, oxygen, gsr) = anomalies
        anomalies = temp + ecg 
        anomalies = anomalies + pulse
        anomalies = anomalies + oxygen 
        anomalies = anomalies + gsr
        for anomaly in anomalies:
            print(str(anomaly.value) + ' at ' + str(anomaly.timestamp) + ', type: ' + str(anomaly.type))