import requests
import scipy.signal as signal
from Measurement import Measurement
from SensorType import SensorType
import urllib3

from SubjectData import SubjectData

class AnomalyDetector:
    def __init__(self, serialNumber):
        self.serialNumber = serialNumber
        self.api = "https://localhost:5001/api/device/"
        urllib3.disable_warnings() #todo: remove this and make HTTPS requests

    def detectAnomaly(self):
        subjectData = self.__getSubjectData()
        measurements = self.__getMeasurements(subjectData.id)
        (medTemp, medEcg, medPulse, medOxygen, medGsr) = self.__medianFilterMeasurements(measurements)
        
        for mediatedMeasurement in medTemp:
            print(mediatedMeasurement)

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
        return measurements

    def __medianFilter(self, measurements):
        mediatedMeasurements = signal.medfilt(measurements, kernel_size=9)
        return mediatedMeasurements

    def __splitMeasurements(self, measurements):
        temp, ecg, pulse, oxygen, gsr = [], [], [], [], []
        for measurement in measurements:
            sensorType = SensorType(measurement.sensorType)
            if (sensorType == SensorType.TEMPERATURE):
                temp.append(measurement.value)
            elif (sensorType == SensorType.ECG):
                ecg.append(measurement.value)
            elif (sensorType == SensorType.PULSE):
                pulse.append(measurement.value)
            elif (sensorType == SensorType.OXYGEN):
                oxygen.append(measurement.value)
            elif (sensorType == SensorType.GSR):
                gsr.append(measurement.value)
        return (temp, ecg, pulse, oxygen, gsr)

    def __medianFilterMeasurements(self, measurements):
        (temp, ecg, pulse, oxygen, gsr) = self.__splitMeasurements(measurements)
        mediatedTemp = self.__medianFilter(temp)
        mediatedEcg = self.__medianFilter(ecg)
        mediatedPulse = self.__medianFilter(pulse)
        mediatedOxygen = self.__medianFilter(oxygen)
        mediatedGsr = self.__medianFilter(gsr)
        return (mediatedTemp, mediatedEcg, mediatedPulse, mediatedOxygen, mediatedGsr)