import pandas as pd
import numpy as np
from scipy.cluster.vq import kmeans
from scipy.cluster.vq import vq

class AnomalyDetector:
    __clustersCnt = 5
    def detectAnomalies(self, measurements):
        (temp, ecg, pulse, oxygen, gsr) = self.__splitMeasurements(measurements)

        tempAnomaly = self.__detectAnomalies(temp)
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
        
        # Specify the data and the number of clusters to kmeans()
        centroids, avg_distance = kmeans(values_raw, self.__clustersCnt)

        # Get the groups (clusters) and distances
        groups, cdist = vq(values_raw, centroids)

        # Check if any cluster represents an anomaly cluster
        (histo, bins) = np.histogram(groups, bins=np.arange(self.__clustersCnt + 1))

        # Return any anomaly
        return np.any(histo[:] == 1)


            
        


# # Convert the salary values to a numpy array
# salary_raw = salary_df['Salary (in USD)'].values

# # For compatibility with the SciPy implementation
# salary_raw = salary_raw.reshape(-1, 1)
# salary_raw = salary_raw.astype('float64')

# # Import kmeans from SciPy
# from scipy.cluster.vq import kmeans
# from scipy.cluster.vq import vq
    
# # Specify the data and the number of clusters to kmeans()
# centroids, avg_distance = kmeans(salary_raw, 4)

# # Get the groups (clusters) and distances
# groups, cdist = vq(salary_raw, centroids)

# # %%
# plt.scatter(salary_raw, np.arange(0,100), c=groups)
# plt.xlabel('Salaries in (USD)')
# plt.ylabel('Indices')
# plt.show()
# # %%
