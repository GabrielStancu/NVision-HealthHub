import neurokit2 as nk
from datetime import datetime

class EcgProcessor:
    __date_format = '%Y-%m-%d %H:%M:%S.%f'

    def detect_anomalies(self, measurements, frequency):
        if (len(measurements) < 4000):
            return False

        values = [m.value for m in measurements]
        (r_peaks, p_peaks, q_peaks, s_peaks, t_peaks) = self.__get_segments_indices(values, frequency)

        pr_anomaly = self.__check_pr_complex(measurements, p_peaks, r_peaks)
        if (pr_anomaly == True):
            return True 
        qrs_anomaly = self.__check_qrs_complex(measurements, q_peaks, s_peaks)
        if (qrs_anomaly == True):
            return True 
        qt_anomaly = self.__check_qt_complex(measurements, q_peaks, t_peaks)
        if (qt_anomaly == True):
            return True 
        hrv_anomaly = self.__check_hrv_complex(measurements, r_peaks)
        return hrv_anomaly

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
        return self.__check_time_length(measurements, p_peaks, r_peaks, 100, 240)

    def __check_qrs_complex(self, measurements, q_peaks, s_peaks):
        return self.__check_time_length(measurements, q_peaks, s_peaks, 70, 120)

    def __check_qt_complex(self, measurements, q_peaks, t_peaks):
        return self.__check_time_length(measurements, q_peaks, t_peaks, 300, 480)

    def __check_hrv_complex(self, measurements, r_peaks):
        for i in range(len(r_peaks) - 1):
            m1 = measurements[r_peaks[i]]
            m2 = measurements[r_peaks[2]]
            t1 = datetime.strptime(m1.timestamp, self.__date_format)
            t2 = datetime.strptime(m2.timestamp, self.__date_format)
            diff = t2 - t1
            millis = diff.microseconds / 1000
            if (millis < 600 or millis > 1000):
                return True
        return False

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
                return True 
        return False