from datetime import datetime
from email.utils import format_datetime
import requests
import urllib3

class AnomalyAlerter: 
    def alertAnomalies(self, anomalies, deviceSerialNumber):
        url = 'https://192.168.220.247:5001/api/device'
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        headers={
            'Content-type':'application/json', 
            'Accept':'application/json'
        }

        #create the alert message
        alert = {'deviceSerialNumber': str(deviceSerialNumber), 
            'alertMoment': format_datetime(datetime.utcnow()),
            'parameters': [a for a in anomalies]}

        _ = requests.post(
            url, 
            json=alert,
            headers=headers,
            verify=False
        )