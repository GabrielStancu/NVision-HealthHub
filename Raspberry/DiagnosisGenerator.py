class DiagnosisGenerator:
    __pred_iso = "P_ISO"
    __meas_iso = "M_ISO"
    __pred_far = "P_FAR"
    __meas_far = "M_FAR"
    __no_anom = ""

    __min_temp = 36.0
    __max_temp = 37.2

    __gsr = 150

    __min_bpm = 60
    __max_bpm = 100

    __min_hypoxic = 85
    __max_hypoxic = 93

    def diagnose_temperature(self, code, meas, pred):
        diagnose = "TMP_" + code
        if (code == self.__meas_iso or code == self.__meas_far):
            if (meas.value < self.__min_temp):
                return diagnose + "_L" # registered low temperature
            if (meas.value > self.__max_temp):
                return diagnose + "_H" # registered high temperature
        elif (code == self.__pred_iso or code == self.__pred_far):
            if (pred.value < self.__min_temp):
                return diagnose + "_L" # expected low temperature
            if (pred.value > self.__max_temp):
                return diagnose + "_H" # expected high temperature
        return self.__no_anom # false alert

    def diagnose_gsr(self, code, meas, pred):
        diagnose = "GSR_" + code
        if (code == self.__meas_iso or code == self.__meas_far):
            if (meas.value > self.__gsr):
                return diagnose + "H" # registered high stress level
        elif (code == self.__pred_iso or code == self.__pred_far):
            if (pred.value > self.__gsr):
                return diagnose + "H" # expected high stress level
        return self.__no_anom # false alert

    def diagnose_pulse(self, code, meas, pred):
        diagnose = "BPM_" + code 
        if (code == self.__meas_iso or code == self.__meas_far):
            if (meas.value < self.__min_bpm):
                return diagnose + "_B" # registered low value => Bradycardia
            if (meas.value > self.__max_bpm):
                return diagnose + "_T" # registered high value => Tachycardia
        elif (code == self.__pred_iso or code == self.__pred_far):
            if (pred.value < self.__min_bpm):
                return diagnose + "_B" # expected low value => Bradycardia
            if (pred.value > self.__max_bpm):
                return diagnose + "_T" # expected high value => Tachycardia
        return self.__no_anom # false alert

    def diagnose_oxygen_saturation(self, code, meas, pred):
        diagnose = "OXY_" + code 
        if (code == self.__meas_iso or code == self.__meas_far):
            if (meas.value >= self.__min_hypoxic or meas.value <= self.__max_hypoxic):
                return diagnose + "_H" # registered hypoxic value
            if (meas.value < self.__min_hypoxic):
                return diagnose + "_SH" # registered severly hypoxic value
        elif (code == self.__pred_iso or code == self.__pred_far):
            if (pred.value > self.__min_hypoxic or pred.value <= self.__max_hypoxic):
                return diagnose + "_H" # expected severly hypoxic value
            if (pred.value < self.__min_hypoxic):
                return diagnose + "_SH" # expected severly hypoxic value  
        return self.__no_anom # false alert

