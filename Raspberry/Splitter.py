class Splitter:
    def split_measurements(self, measurements):
        temp, ecg, pulse, oxygen, gsr = [], [], [], [], []
        for measurement in measurements:
            sensor_type = measurement.type
            if (sensor_type == 'TMP'):
                temp.append(measurement)
            elif (sensor_type == 'ECG'):
                ecg.append(measurement)
            elif (sensor_type == 'BPM'):
                pulse.append(measurement)
            elif (sensor_type == 'OXY'):
                oxygen.append(measurement)
            elif (sensor_type == 'GSR'):
                gsr.append(measurement)
        return (temp, ecg, pulse, oxygen, gsr)