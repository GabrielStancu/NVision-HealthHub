class Splitter:
    def splitMeasurements(self, measurements):
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