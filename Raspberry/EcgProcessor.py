import neurokit2 as nk
from datetime import datetime

class EcgProcessor:
    __date_format = '%Y-%m-%d %H:%M:%S.%f'
    __no_anom = ""

    def detect_anomalies(self, measurements, frequency):
        anomalies = []
        if (len(measurements) < 4000):
            return anomalies

        values = [m.value for m in measurements]
        (r_peaks, p_peaks, q_peaks, s_peaks, t_peaks) = self.__get_segments_indices(values, frequency)

        pr_anomaly = self.__check_pr_complex(measurements, p_peaks, r_peaks)
        if (pr_anomaly != self.__no_anom):
            anomalies.append(pr_anomaly)
        qrs_anomaly = self.__check_qrs_complex(measurements, q_peaks, s_peaks)
        if (qrs_anomaly != self.__no_anom):
            anomalies.append(qrs_anomaly) 
        qt_anomaly = self.__check_qt_complex(measurements, q_peaks, t_peaks)
        if (qt_anomaly != self.__no_anom):
            anomalies.append(qt_anomaly) 
        hrv_anomaly = self.__check_hrv_complex(measurements, r_peaks)
        if (hrv_anomaly != self.__no_anom):
            anomalies.append(hrv_anomaly)

        return anomalies

    def __get_segments_indices(self, values, frequency):
        # clean the ecg 
        clean_ecg = nk.ecg_clean(values, sampling_rate=frequency)
        # find R peaks
        _, rpeaks = nk.ecg_peaks(clean_ecg, sampling_rate=frequency)
        # separate P, Q, S, T segments
        _, waves_peak = nk.ecg_delineate(clean_ecg, rpeaks, sampling_rate=frequency, method="peak")

        return (rpeaks['ECG_R_Peaks'], waves_peak['ECG_P_Peaks'], waves_peak['ECG_Q_Peaks'], 
                                       waves_peak['ECG_S_Peaks'], waves_peak['ECG_T_Peaks'])

    def __check_pr_complex(self, measurements, p_peaks, r_peaks):
        min_valid = 120
        max_valid = 220
        interval = self.__check_time_length(measurements, p_peaks, r_peaks, min_valid, max_valid)
        if (interval > max_valid):
            return "ECG_PR_AB" # atrioventricular block
        return self.__no_anom # false alsert 

    def __check_qrs_complex(self, measurements, q_peaks, s_peaks):
        min_valid = 80
        max_valid = 120
        interval = self.__check_time_length(measurements, q_peaks, s_peaks, min_valid, max_valid)
        if (interval > max_valid):
            return "ECG_QRS_BB" # branch block
        return self.__no_anom # false alsert 

    def __check_qt_complex(self, measurements, q_peaks, t_peaks):
        min_valid = 400
        max_valid = 470
        interval = self.__check_time_length(measurements, q_peaks, t_peaks, 400, 470)
        if (interval < min_valid):
            return "ECG_QT_S" # short qt syndrome
        if (interval > max_valid):
            return "ECG_QT_L" # long qt syndrome
        return self.__no_anom # false alsert 

    def __check_hrv_complex(self, measurements, r_peaks):
        min_valid = 600
        max_valid = 1000
        for i in range(len(r_peaks) - 1):
            m1 = measurements[r_peaks[i]]
            m2 = measurements[r_peaks[2]]
            t1 = datetime.strptime(m1.timestamp, self.__date_format)
            t2 = datetime.strptime(m2.timestamp, self.__date_format)
            diff = t2 - t1
            millis = diff.microseconds / 1000
            if (millis < min_valid):
                return "ECG_HRV_T" # tachycardia
            if (millis > max_valid):
                return "ECG_HRV_B" # bradycardia
        return self.__no_anom # false alsert 

    def __check_time_length(self, measurements, segments1, segments2, min_len, max_len):
        seg_len = min(len(segments1), len(segments2))
        # check if seg1 comes before seg2 or measurements started with an seg2
        first_1 = measurements[segments1[0]]
        first_2 = measurements[segments2[0]]
        time_1 = datetime.strptime(first_1.timestamp, self.__date_format)
        time_2 = datetime.strptime(first_2.timestamp, self.__date_format)
        offset = 0
        if (time_2 < time_1):
            offset = 1

        # check the difference in time between consecutive seg1 and seg2
        for i in range(seg_len - offset):
            m1 = measurements[segments1[i]]
            m2 = measurements[segments2[i + offset]]
            time_1 = datetime.strptime(m1.timestamp, self.__date_format)
            time_2 = datetime.strptime(m2.timestamp, self.__date_format)
            diff = time_2 - time_1
            millis = diff.microseconds / 1000
            # valid values should be between min_len-max_len [ms]
            if (millis < min_len or millis > max_len):
                return millis 
        return -1