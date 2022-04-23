class AnomalyAlerter: 
    def alertAnomaly(self, anomaly):
        print(str(anomaly.value) + ' at ' + str(anomaly.timestamp) + ', type: ' + str(anomaly.type))
            