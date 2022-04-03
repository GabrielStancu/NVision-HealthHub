import requests
import scipy.signal as signal
from Measurement import Measurement
from SensorType import SensorType
import urllib3
from sklearn.cluster import DBSCAN
import numpy as np

from SubjectData import SubjectData

class AnomalyDetector:
    def __init__(self, serialNumber):
        self.serialNumber = serialNumber
        self.api = "https://localhost:5001/api/device/"
        urllib3.disable_warnings() #todo: remove this and make HTTPS requests

    def detectAnomaly(self):
        subjectData = self.__getSubjectData()
        (temp, ecg, pulse, oxygen, gsr) = self.__getMeasurements(subjectData.id)
        tempAnom = self.__dbscanAnomalies(temp, 1)
        ecgAnom = self.__dbscanAnomalies(ecg, 10) #experimentally find values for these
        pulseAnom = self.__dbscanAnomalies(pulse, 5) #experimentally find values for these
        oxygenAnom = self.__dbscanAnomalies(oxygen, 10) #experimentally find values for these
        gsrAnom = self.__dbscanAnomalies(gsr, 3) #experimentally find values for these
        
        return (tempAnom, ecgAnom, pulseAnom, oxygenAnom, gsrAnom)

    def __getSubjectData(self):
        query = { 'serialNumber': self.serialNumber }
        response = requests.get(self.api, params=query, verify=False)
        jsonResponse = response.json()
        subjectData = SubjectData(jsonResponse)
        return subjectData

    def __getMeasurements(self, id):
        subjectQuery = { 'subjectId': id } #this will be removed
        measurementsResponse = requests.get(self.api + "measurements/", params=subjectQuery, verify=False) #this will be removed
        measurementsList = measurementsResponse.json() #this data is obtained locally outside and passed as parameter
        measurements = []
        for measurementElem in measurementsList:
            measurements.append(Measurement(measurementElem))
        return self.__splitMeasurements(measurements)

    def __medianFilter(self, measurements):
        mediatedMeasurements = signal.medfilt(measurements, kernel_size=9)
        return mediatedMeasurements

    def __splitMeasurements(self, measurements):
        temp, ecg, pulse, oxygen, gsr = [], [], [], [], []
        for measurement in measurements:
            sensorType = SensorType(measurement.sensorType)
            if (sensorType == SensorType.TEMPERATURE):
                temp.append(measurement)
            elif (sensorType == SensorType.ECG):
                ecg.append(measurement)
            elif (sensorType == SensorType.PULSE):
                pulse.append(measurement)
            elif (sensorType == SensorType.OXYGEN):
                oxygen.append(measurement)
            elif (sensorType == SensorType.GSR):
                gsr.append(measurement)
        return (temp, ecg, pulse, oxygen, gsr)

    def __dbscanAnomalies(self, measurements, epsilon):
        clustering1 = DBSCAN(eps=epsilon, min_samples=6).fit(np.array([m.value for m in measurements]).reshape(-1,1))
        labels = clustering1.labels_
        outlier_pos = np.where(labels == -1)[0]
        anomalies = []
        for pos in outlier_pos:
            anomalies.append(np.array(measurements)[pos])
            
        return anomalies