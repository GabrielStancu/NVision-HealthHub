import pandas as pd
import numpy as np
from scipy.cluster.vq import kmeans
from scipy.cluster.vq import vq
from sklearn.cluster import KMeans

class AnomalyDetector:
    __ecg_processor = None

    def __init__(self, ecg_processor):
        self.__ecg_processor = ecg_processor

    def detect_anomalies(self, measurements, predictions):
        (temp_m, ecg_m, pulse_m, oxygen_m, gsr_m) = measurements 
        (temp_p, pulse_p, oxygen_p, gsr_p) = predictions

        temp = temp_m + temp_p
        pulse = pulse_m + pulse_p
        oxygen = oxygen_m + oxygen_p
        gsr = gsr_m + gsr_p

        anomalies = []

        temp_anomaly = self.__detect_anomalies(temp, len(temp_p))
        if (temp_anomaly == True):
            anomalies.append('TMP')

        pulse_anomaly = self.__detect_anomalies(pulse, len(pulse_p))
        if (pulse_anomaly == True):
            anomalies.append('BPM')

        oxygen_anomaly = self.__detect_anomalies(oxygen, len(oxygen_p))
        if (oxygen_anomaly == True):
            anomalies.append('OXY')

        gsr_anomaly = self.__detect_anomalies(gsr, len(gsr_p))
        if (gsr_anomaly == True):
            anomalies.append('GSR')

        ecg_frequency = 200
        ecg_anomaly = self.__ecg_processor.detect_anomalies(ecg_m, ecg_frequency)
        if (ecg_anomaly == True):
            anomalies.append('ECG')

        return anomalies

    def __detect_anomalies(self, measurements, pred_cnt):
        if (len(measurements) < 30):
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
        clustersCnt = self.__determine_clusters_count(measurements)
        
        # Specify the data and the number of clusters to kmeans()
        centroids, _ = kmeans(values_raw, clustersCnt)

        # Get the groups (clusters) and distances
        groups, cdist = vq(values_raw, centroids)

        # Check if prediction finds itself in isolated cluster
        is_isolated = self.__is_isolated_cluster(groups, pred_cnt)
        if (is_isolated == True):
            return True 
        
        # Check if prediction is placed far away from the centroid of the cluster it belongs to 
        is_far_from_centroid = self.__is_far_from_centroid(cdist, pred_cnt)
        return is_far_from_centroid

    def __is_isolated_cluster(self, groups, cnt):
        pred_groups = groups[-cnt:]
        (histo, _) = np.histogram(groups, bins=np.arange(len(groups) + 1))
        for pred_group in pred_groups:
            if (histo[pred_group] == 1):
                return True
        return False

    def __is_far_from_centroid(self, distances, cnt):
        pred_distances = distances[-cnt:] 
        real_distances = distances[0:-cnt-1] 
        for pred_distance in pred_distances:
            if (pred_distance > max(real_distances)):
                return True
        return False        

    def __determine_clusters_count(self, measurements):
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
                if (score - scores[idx-1] < 3):
                    return idx + 1
        return len(scores)