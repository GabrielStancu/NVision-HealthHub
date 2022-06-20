import pandas as pd
import numpy as np
from scipy.cluster.vq import kmeans
from scipy.cluster.vq import vq
from sklearn.cluster import KMeans

class AnomalyDetector:
    __ecg_processor = None
    __diagnosis_generator = None
    __pred_iso = "P_ISO"
    __meas_iso = "M_ISO"
    __pred_far = "P_FAR"
    __meas_far = "M_FAR"
    __no_anom = ""

    def __init__(self, diagnosis_generator, ecg_processor):
        self.__diagnosis_generator = diagnosis_generator
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
        if (temp_anomaly != self.__no_anom):
            diagnosis = self.__diagnosis_generator.diagnose_temperature(temp_anomaly, temp_m[-1], temp_p[0])
            if (diagnosis != self.__no_anom):
                anomalies.append(diagnosis)

        pulse_anomaly = self.__detect_anomalies(pulse, len(pulse_p))
        if (pulse_anomaly != self.__no_anom):
            diagnosis = self.__diagnosis_generator.diagnose_temperature(pulse_anomaly, pulse_m[-1], pulse_p[0])
            if (diagnosis != self.__no_anom):
                anomalies.append(diagnosis)

        oxygen_anomaly = self.__detect_anomalies(oxygen, len(oxygen_p))
        if (oxygen_anomaly != self.__no_anom):
            diagnosis = self.__diagnosis_generator.diagnose_oxygen_saturation(oxygen_anomaly, oxygen_m[-1], oxygen_p[0])
            if (diagnosis != self.__no_anom):
                anomalies.append(diagnosis)

        gsr_anomaly = self.__detect_anomalies(gsr, len(gsr_p))
        if (gsr_anomaly != self.__no_anom):
            diagnosis = self.__diagnosis_generator.diagnose_gsr(gsr_anomaly, gsr_m[-1], gsr_p[0])
            if (diagnosis != self.__no_anom):
                anomalies.append(diagnosis)

        ecg_frequency = 200
        ecg_anomalies = self.__ecg_processor.detect_anomalies(ecg_m, ecg_frequency)
        if (len(ecg_anomalies) > 0):
            anomalies = anomalies + ecg_anomalies

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
        if (is_isolated != self.__no_anom):
            return is_isolated
        
        # Check if prediction is placed far away from the centroid of the cluster it belongs to 
        is_far_from_centroid = self.__is_far_from_centroid(cdist, pred_cnt)
        return is_far_from_centroid

    def __is_isolated_cluster(self, groups, cnt):
        pred_groups = groups[-cnt:]
        meas_group = groups[-cnt-1]
        (histo, _) = np.histogram(groups, bins=np.arange(len(groups) + 1))
        for pred_group in pred_groups:
            if (histo[pred_group] == 1):
                return self.__pred_iso
        if (histo[meas_group] == 1):
            return self.__meas_iso
        return self.__no_anom

    def __is_far_from_centroid(self, distances, cnt):
        pred_distances = distances[-cnt:] 
        real_distances = distances[0:-cnt-1] 
        max_distance = max(real_distances)
        for pred_distance in pred_distances:
            if (pred_distance > max_distance):
                return self.__pred_far
        if (real_distances[-1] >= max_distance):
            return self.__meas_far
        return self.__no_anom        

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
                if (score - scores[idx-1] < 10):
                    return idx
        return len(scores)