from statsmodels.tsa.arima.model import ARIMA
from Measurement import Measurement

class Predictor:
    def predict(self, measurements):
        (temp, ecg, pulse, oxygen, gsr) = measurements
        predictions = (
            self.__predictForType(temp, 1, 'TMP'),
            self.__predictForType(ecg, 5, 'ECG'),
            self.__predictForType(pulse, 1, 'BPM'),
            self.__predictForType(oxygen, 1, 'OXY'),
            self.__predictForType(gsr, 1, 'GSR')
        )
        return predictions

    def __predictForType(self, measurements, count, type):
        if (len(measurements) < 10):
            return []

        history = [m.value for m in measurements]
        model = ARIMA(history, order=(5,1,0))
        model_fit = model.fit()
        output = model_fit.forecast()
        predictions = []

        for i in range(0, count):
            measurement = self.__predictionToMeasurement(output[i], type)
            predictions.append(measurement)
        
        return predictions 

    def __predictionToMeasurement(self, prediction, type):
        return Measurement(type, prediction, None)
	

