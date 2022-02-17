#include <Wire.h>

#define REPORTING_PERIOD_MS 250

uint32_t tsLastReport = 0;

int heartbeatPin = A0;
int temperaturePin = A1;
int loPlusPin = 10;
int loMinusPin = 11;
int ecgPin = A2;

void setup() {
  Serial.begin(9600);
  pinMode(heartbeatPin, INPUT);
  pinMode(temperaturePin, INPUT);
  pinMode(loPlusPin, INPUT); 
  pinMode(loMinusPin, INPUT); 
}

void loop() {
  if (millis() - tsLastReport > REPORTING_PERIOD_MS) {
    float heartbeat = measureHeartbeat();
    float temperature = measureTemperature();   
    float ecg = measureEcg();
    String heartbeatStr = String(heartbeat, 3);
    String temperatureStr = String(temperature, 3);
    String ecgStr = String(ecg, 3);
    String values = "";
    char separator = ';';
    values.concat(heartbeatStr);
    values.concat(separator);
    values.concat(temperatureStr);
    values.concat(separator);
    values.concat(ecgStr);
    Serial.println(values);

    tsLastReport = millis();
  }
}

float measureHeartbeat() {
  float pulse;
  int sum = 0;
  for (int i = 0; i < 20; i++)
    sum += analogRead(heartbeatPin);
  pulse = sum / 20.00;

  return pulse;
}

float measureTemperature() {
  int tempVal =  analogRead(temperaturePin);
  float measuredVal = (tempVal/1024.0)*5000; 
  float celsius = measuredVal/10;

  return celsius;
}

float measureEcg() {
  if((digitalRead(loPlusPin) == 1)||(digitalRead(loMinusPin) == 1)){
    return 0;
  }
  return analogRead(ecgPin);
}
