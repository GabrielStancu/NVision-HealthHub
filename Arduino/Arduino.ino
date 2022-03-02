#include <Wire.h>
#include "MAX30100_PulseOximeter.h"

#define DEB_INTERVAL_MS 5000
#define REPORTING_PERIOD_MS 1
#define TEMPERATURE A1
#define LO_PLUS 10
#define LO_MINUS 11
#define ECG A2
#define GSR A0
#define OP_BTN 2

#define DONE_OP_LED 8
#define NO_OP_LED 7
#define TEMP_LED 6
#define ECG_LED 5
#define MAX_LED 4
#define GSR_LED 3

#define REQ_HB 5
#define REQ_TMP 5
#define REQ_ECG 10
#define REQ_GSR 5

PulseOximeter pox;

bool pushingOpBtn = false;
int sendMode = 0;
uint32_t tsLastReport = 0;
int lastSwitchDetectedMIllis;
const char separator = ';';

int hbCnt = 0;
int tmpCnt = 0;
int ecgCnt = 0;
int gsrCnt = 0;

bool canGoNextState = false;
unsigned long timestamp;

void setup() { 
  pinMode(TEMPERATURE, INPUT);
  pinMode(LO_PLUS, INPUT); 
  pinMode(LO_MINUS, INPUT); 
  pinMode(OP_BTN, INPUT_PULLUP);
  //pin A0 ???
  attachInterrupt(digitalPinToInterrupt(OP_BTN), opBtnRise, RISING);
  pinMode(DONE_OP_LED, OUTPUT);
  pinMode(NO_OP_LED, OUTPUT);
  pinMode(TEMP_LED, OUTPUT);
  pinMode(ECG_LED, OUTPUT);
  pinMode(GSR_LED, OUTPUT);
  pox.setIRLedCurrent(MAX30100_LED_CURR_7_6MA);
  lastSwitchDetectedMIllis = millis();
  timestamp = millis();
  Serial.begin(9600);
}

void loop() {
  lightOpLeds();
  sendData();
}

void opBtnRise() {
  if (sendMode == 0) {
    sendMode = 1;
    return;
  }
  if (millis() - lastSwitchDetectedMIllis > DEB_INTERVAL_MS && canGoNextState) {
    lastSwitchDetectedMIllis = millis();
    sendMode = (sendMode + 1) % 4;
    resetState();
  }
}

void sendData() {
  if (millis() - tsLastReport > REPORTING_PERIOD_MS) {
    switch(sendMode) {
      case 1:
        sendTemperature();
        break;
      case 2:
        sendEcg();
        break;
      case 3: 
        sendPulse();
        sendOxygen();
        break;
      case 4:
        sendGSR();
        break;
      default: 
        break;
    }

    tsLastReport = millis();
  }
}

float measureTemperature() {
  int tempVal =  analogRead(TEMPERATURE);
  float correctiveFactor = 1.33;
  float measuredVal = (tempVal/1024.0)*5000*correctiveFactor; 
  float celsius = measuredVal/10;
  timestamp = millis();

  return celsius;
}

float measureEcg() {
  if((digitalRead(LO_PLUS) == HIGH)||(digitalRead(LO_MINUS) == HIGH)){
    return 0;
  }
  float ecg = analogRead(ECG);
  timestamp = millis();
  return ecg;
}

float measurePulse() {
  float pulse = pox.getHeartRate();
  timestamp = millis();
  return pulse;
}

float measureSpO2() {
  float spO2 = pox.getSpO2();
  timestamp = millis();
  return spO2;
}

float measureGSR() {
  float gsr = analogRead(0);
  //Serial.println(a);
  //Serial.write(a);
  timestamp = millis();
  return gsr;
}

void sendTemperature() {
  float temperature = measureTemperature();
  String temperatureStr = String(temperature, 3);
  String timestampStr = String(timestamp);
  String sendValue = "";
  const float minValidValue = 32;
  const float maxValidValue = 42;
  if (temperature >= minValidValue && temperature <= maxValidValue) {
    countTemperature();
    sendValue.concat("TMP");
    sendValue.concat(separator);
    sendValue.concat(temperatureStr);
    sendValue.concat(separator);
    sendValue.concat(timestampStr);
    Serial.println(sendValue);
  }
}

void sendEcg() {
  float ecg = measureEcg();
  String ecgStr = String(ecg, 3);
  String timestampStr = String(timestamp);
  String sendValue = "";
  const int minValidValue = 30;
  const int maxValidValue = 250;
  if (ecg >= minValidValue && ecg <= maxValidValue) {
    countEcg();
    sendValue.concat("ECG");
    sendValue.concat(separator);
    sendValue.concat(ecgStr);
    sendValue.concat(separator);
    sendValue.concat(timestampStr);
    Serial.println(sendValue);
  }
}

void sendPulse() {
  float pulse = measurePulse();
  String pulseStr = String(pulse, 3);
  String timestampStr = String(timestamp);
  String sendValue = "";
  const int minValidValue = 30;
  const int maxValidValue = 200;
  if (pulse >= minValidValue && pulse <= maxValidValue) {
    countEcg();
    sendValue.concat("BPM");
    sendValue.concat(separator);
    sendValue.concat(pulseStr);
    sendValue.concat(separator);
    sendValue.concat(timestampStr);
    Serial.println(sendValue);
  }
}

void sendOxygen() {
  float oxygen = measureSpO2();
  String oxygenStr = String(oxygen, 3);
  String timestampStr = String(timestamp);
  String sendValue = "";
  const int minValidValue = -1;
  const int maxValidValue = 101;
  if (oxygen >= minValidValue && oxygen <= maxValidValue) {
    countEcg();
    sendValue.concat("OXY");
    sendValue.concat(separator);
    sendValue.concat(oxygenStr);
    sendValue.concat(separator);
    sendValue.concat(timestampStr);
    Serial.println(sendValue);
  }
}

void sendGSR() {
  float gsr = measureGSR();
  String gsrStr = String(gsr, 3);
  String timestampStr = String(timestamp);
  String sendValue = "";
  const int minValidValue = -1;
  const int maxValidValue = 101;
  if (gsr >= minValidValue && gsr <= maxValidValue) {
    countEcg();
    sendValue.concat("GSR");
    sendValue.concat(separator);
    sendValue.concat(gsrStr);
    sendValue.concat(separator);
    sendValue.concat(timestampStr);
    Serial.println(sendValue);
  }
}

void countTemperature() {
  tmpCnt++;
  if(tmpCnt >= REQ_TMP) {
    digitalWrite(DONE_OP_LED, HIGH);
    canGoNextState = true;
  }
  else {
    canGoNextState = false;
  }
}

void countEcg() {
  ecgCnt++;
  if(ecgCnt >= REQ_ECG) {
    digitalWrite(DONE_OP_LED, HIGH);
    canGoNextState = true;
  }
  else {
    canGoNextState = false;
  }
}

void countGsr() {
  gsrCnt++;
  if(gsrCnt >= REQ_GSR) {
    digitalWrite(DONE_OP_LED, HIGH);
    canGoNextState = true;
  }
  else {
    canGoNextState = false;
  }
}

void resetState() {
  hbCnt = 0;
  tmpCnt = 0;
  ecgCnt = 0;
  gsrCnt = 0;
  canGoNextState = false;
  digitalWrite(DONE_OP_LED, LOW);
}

void lightOpLeds() {
  digitalWrite(NO_OP_LED, LOW);
  digitalWrite(TEMP_LED, LOW);
  digitalWrite(ECG_LED, LOW);
  digitalWrite(MAX_LED, LOW);
  digitalWrite(GSR_LED, LOW);

  switch(sendMode) {
    case 0:
      digitalWrite(NO_OP_LED, HIGH);
      break;
    case 1: 
      digitalWrite(TEMP_LED, HIGH);
      break;
    case 2: 
      digitalWrite(ECG_LED, HIGH);
      break;
    case 3: 
      digitalWrite(MAX_LED, HIGH);
      break;
    case 4: 
      digitalWrite(GSR_LED, HIGH);
      break;
    default: 
      sendMode = 0;
      break;
  }
}
