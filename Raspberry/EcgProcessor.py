import neurokit2 as nk

class EcgProcessor:
    def get_segments_indices(self, values, frequency):
        # find R peaks
        _, rpeaks = nk.ecg_peaks(values, sampling_rate=frequency)
        # separate P, Q, S, T segments
        _, waves_peak = nk.ecg_delineate(values, rpeaks, sampling_rate=frequency, method="peak")

        return (rpeaks['ECG_R_Peaks'], waves_peak['ECG_P_Peaks'], waves_peak['ECG_Q_Peaks'], 
                                       waves_peak['ECG_S_Peaks'], waves_peak['ECG_T_Peaks'])
