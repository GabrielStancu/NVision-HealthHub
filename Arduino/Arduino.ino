#include <Wire.h>

#define DEB_INTERVAL_MS 1000
#define REPORTING_PERIOD_MS 250
#define HEARTBEAT A0
#define TEMPERATURE A1
#define LO_PLUS 10
#define LO_MINUS 11
#define ECG A2
#define OP_BTN 2
#define NO_OP_LED 7
#define HB_LED 6
#define TEMP_LED 5
#define ECG_LED 4

bool pushingOpBtn = false;
int sendMode = 0;
uint32_t tsLastReport = 0;
int lastSwitchDetectedMIllis;
const char separator = ';';

void setup() { 
  pinMode(HEARTBEAT, INPUT);
  pinMode(TEMPERATURE, INPUT);
  pinMode(LO_PLUS, INPUT); 
  pinMode(LO_MINUS, INPUT); 
  pinMode(OP_BTN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(OP_BTN), opBtnRise, RISING);
  pinMode(NO_OP_LED, OUTPUT);
  pinMode(HB_LED, OUTPUT);
  pinMode(TEMP_LED, OUTPUT);
  pinMode(ECG_LED, OUTPUT);
  lastSwitchDetectedMIllis = millis();
  Serial.begin(9600);
}

void loop() {
  lightOpLeds();
  sendData();
}

void opBtnRise() {
  if (millis() - lastSwitchDetectedMIllis > DEB_INTERVAL_MS) {
    lastSwitchDetectedMIllis = millis();
    sendMode = (sendMode + 1) % 4;
  }
}

void sendData() {
  if (millis() - tsLastReport > REPORTING_PERIOD_MS) {
    switch(sendMode) {
      case 0:
        sendNoOp();
        break;
      case 1:
        sendHeartbeat();
        break;
      case 2:
        sendTemperature();
        break;
      case 3:
        sendEcg();
        break;
      default: 
        break;
    }

    tsLastReport = millis();
  }
}

float measureHeartbeat() {
  float pulse;
  int sum = 0;
  for (int i = 0; i < 20; i++)
    sum += analogRead(HEARTBEAT);
  pulse = sum / 20.00;

  return pulse;
}

float measureTemperature() {
  int tempVal =  analogRead(TEMPERATURE);
  float measuredVal = (tempVal/1024.0)*5000; 
  float celsius = measuredVal/10;

  return celsius;
}

float measureEcg() {
  if((digitalRead(LO_PLUS) == HIGH)||(digitalRead(LO_MINUS) == HIGH)){
    return 0;
  }
  return analogRead(ECG);
}

void sendNoOp() {
  Serial.println("NA");
}

void sendHeartbeat() {
  float heartbeat = measureHeartbeat();
  String heartbeatStr = String(heartbeat, 3);
  String sendValue = "";
  sendValue.concat("HB");
  sendValue.concat(separator);
  sendValue.concat(heartbeatStr);
  Serial.println(sendValue);
}

void sendTemperature() {
  float temperature = measureTemperature();
  String temperatureStr = String(temperature, 3);
  String sendValue = "";
  sendValue.concat("TMP");
  sendValue.concat(separator);
  sendValue.concat(temperatureStr);
  Serial.println(sendValue);
}

void sendEcg() {
  float ecg = measureEcg();
  String ecgStr = String(ecg, 3);
  String sendValue = "";
  sendValue.concat("ECG");
  sendValue.concat(separator);
  sendValue.concat(ecgStr);
  Serial.println(sendValue);
}

void lightOpLeds() {
  digitalWrite(NO_OP_LED, LOW);
  digitalWrite(HB_LED, LOW);
  digitalWrite(TEMP_LED, LOW);
  digitalWrite(ECG_LED, LOW);

  switch(sendMode) {
    case 0:
      digitalWrite(NO_OP_LED, HIGH);
      break;
    case 1: 
      digitalWrite(HB_LED, HIGH);
      break;
    case 2: 
      digitalWrite(TEMP_LED, HIGH);
      break;
    case 3: 
      digitalWrite(ECG_LED, HIGH);
      break;
    default: 
      sendMode = 0;
      break;
  }
}
