import pandas as pd
import numpy as np
from scipy.cluster.vq import kmeans
from scipy.cluster.vq import vq
from sklearn.cluster import KMeans

class AnomalyDetector:
    def detectAnomalies(self, measurements, predictions):
        (tempM, ecgM, pulseM, oxygenM, gsrM) = measurements 
        (tempP, ecgP, pulseP, oxygenP, gsrP) = predictions

        temp = tempM + tempP
        ecg = ecgM + ecgP
        pulse = pulseM + pulseP
        oxygen = oxygenM + oxygenP
        gsr = gsrM + gsrP

        anomalies = []
        tempAnomaly = self.__detectAnomalies(temp, len(tempP))
        if (tempAnomaly == True):
            anomalies.append('TMP')
        #self.__detectAnomalies(pulse)
        #self.__detectAnomalies(oxygen)
        #self.__detectAnomalies(gsr)
        #self.__detectAnomalies(ecg)
        
        return anomalies

    def __detectAnomalies(self, measurements, predCnt):
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

        # Check if prediction finds itself in isolated cluster
        isIsolated = self.__isIsolatedCluster(groups, predCnt)
        if (isIsolated == True):
            return True 
        
        # Check if prediction is placed far away from the centroid of the cluster it belongs to 
        isFarFromCentroid = self.__isFarFromCentroid(cdist, predCnt, avg_distance)
        return isFarFromCentroid

    def __isIsolatedCluster(self, groups, cnt):
        predGroups = groups[-cnt:]
        (histo, _) = np.histogram(groups, bins=np.arange(len(groups) + 1))
        for predGroup in predGroups:
            if (histo[predGroup] < 5):
                return True
        return False

    def __isFarFromCentroid(self, distances, cnt, avgDistance):
        predDistances = distances[-cnt:]
        for predDistance in predDistances:
            if (predDistance >= 2 * avgDistance):
                return True
        return False        

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