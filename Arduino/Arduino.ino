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

PulseOximeter pox;

bool pushingOpBtn = false;
int sendMode = 0;
uint32_t tsLastReport = 0;
int lastSwitchDetectedMIllis;
const char separator = ';';

int tmpCnt = 0;
int ecgCnt = 0;
int hbCnt = 0;
int oxyCnt = 0;
int gsrCnt = 0;

const float minValidTemp = 32;
const float maxValidTemp = 42;
const float minValidEcg = 30;
const float maxValidEcg = 250;
const float minValidPulse = 30;
const float maxValidPulse = 200;
const float minValidOxygen = -1;
const float maxValidOxygen = 101;
const float minValidGsr = -1;
const float maxValidGsr = 101;

const char tempType[4] = "TMP";
const char ecgType[4] = "ECG";
const char pulseType[4] = "BPM";
const char oxygenType[4] = "OXY";
const char gsrType[4] = "GSR";

const int reqTmp = 5;
const int reqEcg = 10;
const int reqHb = 5;
const int reqOxygen = 5;
const int reqGsr = 5;

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
        sendValue(minValidTemp, maxValidTemp, tempType, measureTemperature, &tmpCnt, reqTmp);
        break;
      case 2:
        sendValue(minValidEcg, maxValidEcg, ecgType, measureEcg, &ecgCnt, reqEcg);
        break;
      case 3: 
        sendValue(minValidPulse, maxValidPulse, pulseType, measurePulse, &hbCnt, reqHb);
        sendValue(minValidOxygen, maxValidOxygen, oxygenType, measureSpO2, &oxyCnt, reqOxygen);
        break;
      case 4:
        sendValue(minValidGsr, maxValidGsr, gsrType, measureGsr, &gsrCnt, reqGsr);
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

float measureGsr() {
  float gsr = analogRead(0);
  //Serial.println(a);
  //Serial.write(a);
  timestamp = millis();
  return gsr;
}

void sendValue(float minValue, float maxValue, const char type[], float (*measureValueFunc)(), int *measurementCnt, int reqCnt) {
  float value = measureValueFunc();
  String valueStr = String(value, 3);
  String timestampStr = String(timestamp);
  String sendValue = "";

  if (value >= minValue && value <= maxValue) {
    countMeasurement(measurementCnt, reqCnt);
    sendValue.concat(type);
    sendValue.concat(separator);
    sendValue.concat(valueStr);
    sendValue.concat(separator);
    sendValue.concat(timestampStr);
    Serial.println(sendValue);
  }
}

void countMeasurement(int *measurementCnt, int reqCnt) {
  (*measurementCnt)++;
  if(*measurementCnt >= reqCnt) {
    digitalWrite(DONE_OP_LED, HIGH);
    canGoNextState = true;
    *measurementCnt = 0;
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
