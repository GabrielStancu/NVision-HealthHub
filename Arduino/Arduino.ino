#include <MAX30100.h>
#include <Wire.h>

int heartbeatPin = A0;
int temperaturePin = A1;

void setup() {
  pinMode(heartbeatPin, INPUT);
  pinMode(temperaturePin, INPUT);
  Serial.begin(9600);
}

void loop() {
  float heartbeat = measureHeartbeat();
  float temperature = measureTemperature();
  String heartbeatStr = String(heartbeat, 3);
  String temperatureStr = String(temperature, 3);
  String values = "";
  char separator = ';';
  values.concat(heartbeatStr);
  values.concat(separator);
  values.concat(temperatureStr);
  Serial.println(values);
  delay(1000);
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

char* floatToCharArray(float val) {
  static char sz[10] = {' '} ;
  int val_int = (int) val;   
  float val_float = abs((val - val_int) * 100);
  int val_fra = (int)val_float;
  sprintf (sz, "%d.%d", val_int, val_fra); 
  return sz;
}
