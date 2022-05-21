from statsmodels.tsa.arima.model import ARIMA
from Measurement import Measurement

class Predictor:
    def predict(self, measurements):
        (temp, _, pulse, oxygen, gsr) = measurements
        predictions = (
            self.__predict_for_type(temp, 1, 'TMP'),
            self.__predict_for_type(pulse, 1, 'BPM'),
            self.__predict_for_type(oxygen, 1, 'OXY'),
            self.__predict_for_type(gsr, 1, 'GSR')
        )
        return predictions

    def __predict_for_type(self, measurements, count, type):
        if (len(measurements) < 10):
            return []

        history = [m.value for m in measurements]
        model = ARIMA(history, order=(5,1,0))
        model_fit = model.fit()
        output = model_fit.forecast()
        predictions = []

        for i in range(0, count):
            measurement = self.__prediction_to_measurement(output[i], type)
            predictions.append(measurement)
        
        return predictions 

    def __prediction_to_measurement(self, prediction, type):
        return Measurement(type, prediction, None)
	

