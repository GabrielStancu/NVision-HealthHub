from datetime import datetime
from email.utils import format_datetime
import requests

class AnomalyAlerter: 
    def alertAnomaly(self, anomalies, deviceSerialNumber):
        url = 'https://192.168.136.247:5001/api/device'

        headers={
            'Content-type':'application/json', 
            'Accept':'application/json'
        }

        #create the alert message
        alert = {'deviceSerialNumber': str(deviceSerialNumber), 
            'alertMoment': format_datetime(datetime.utcnow()),
            'parameters': [a for a in anomalies]}

        resp = requests.post(
            url, 
            json=alert,
            headers=headers,
            verify=False
        )
        print(resp)