import pandas as pd
import numpy as np
from scipy.cluster.vq import kmeans
from scipy.cluster.vq import vq
from sklearn.cluster import KMeans

class AnomalyDetector:
    def detectAnomalies(self, measurements):
        (temp, ecg, pulse, oxygen, gsr) = self.__splitMeasurements(measurements)

        tempAnomaly = self.__detectAnomalies(temp)
        print(tempAnomaly)
        if (tempAnomaly == True):
            return temp[-1]
        #self.__detectAnomalies(pulse)
        #self.__detectAnomalies(oxygen)
        #self.__detectAnomalies(gsr)
        #self.__detectAnomalies(ecg)

        return None
        

    def __splitMeasurements(self, measurements):
        temp, ecg, pulse, oxygen, gsr = [], [], [], [], []
        for measurement in measurements:
            sensorType = measurement.type
            if (sensorType == 'TMP'):
                temp.append(measurement)
            elif (sensorType == 'ECG'):
                ecg.append(measurement)
            elif (sensorType == 'BPM'):
                pulse.append(measurement)
            elif (sensorType == 'OXY'):
                oxygen.append(measurement)
            elif (sensorType == 'GSR'):
                gsr.append(measurement)
        return (temp, ecg, pulse, oxygen, gsr)

    def __detectAnomalies(self, measurements):
        if (len(measurements) < 10):
            return

        # Create pandas DataFrame
        measurements_df = pd.DataFrame(
            {
                'Timestamp': [m.timestamp for m in measurements],
                'Value': [m.value for m in measurements]
            })

        # Convert the measurement values to a numpy array
        values_raw = measurements_df['Value'].values

        # For compatibility with the SciPy implementation
        values_raw = values_raw.reshape(-1, 1)
        values_raw = values_raw.astype('float64')

        # Determine number of clusters
        clustersCnt = self.__determineClustersCount(measurements)
        
        # Specify the data and the number of clusters to kmeans()
        centroids, avg_distance = kmeans(values_raw, clustersCnt)

        # Get the groups (clusters) and distances
        groups, cdist = vq(values_raw, centroids)

        # Check if any cluster represents an anomaly cluster
        (histo, bins) = np.histogram(groups, bins=np.arange(clustersCnt + 1))

        for idx, el in enumerate(histo):
            print(str(idx) + ': ' + str(el))

        # Return any anomaly
        return np.any(histo[:] == 1)

    def __determineClustersCount(self, measurements):
        # build DataFrame
        data = pd.DataFrame(
            {
                'Value': [m.value for m in measurements]
            })

        # determine number of clusters with Elbow curve
        n_cluster = range(1, 20)
        kmeans = [KMeans(n_clusters = i).fit(data) for i in n_cluster]
        scores = [kmeans[i].score(data) for i in range(len(kmeans))]

        # return the index where no significant changes occur anymore
        for idx, score in enumerate(scores):
            if (idx > 0):
                if (score - scores[idx-1] < 1.5):
                    return idx + 1
        return len(scores)