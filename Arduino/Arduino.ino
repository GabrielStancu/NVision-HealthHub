#include <Wire.h>
#include "MAX30100_PulseOximeter.h"
#include "Constants.h"

PulseOximeter pox;

bool pushingOpBtn = false;
int sendMode = 0;
uint32_t tsLastReport = 0;

int tmpCnt = 0;
int ecgCnt = 0;
int hbCnt = 0;
int oxyCnt = 0;
int gsrCnt = 0;

bool canGoNextState = false;
unsigned long timestamp;

void setup() { 
  Serial.begin(9600);
  pinMode(TEMPERATURE, INPUT);
  pinMode(LO_PLUS, INPUT); 
  pinMode(LO_MINUS, INPUT); 
  pinMode(OP_BTN, INPUT_PULLUP);
  pinMode(GSR, INPUT);
  attachInterrupt(digitalPinToInterrupt(OP_BTN), opBtnRise, RISING);
  pinMode(NO_OP_LED, OUTPUT);
  pinMode(TEMP_LED, OUTPUT);
  pinMode(ECG_LED, OUTPUT);
  pinMode(BPM_LED, OUTPUT);
  pinMode(OXY_LED, OUTPUT);
  pinMode(GSR_LED, OUTPUT);
  pox.begin();
  pox.setIRLedCurrent(MAX30100_LED_CURR_7_6MA);
  timestamp = millis();
}

void loop() {
  lightOpLeds();
  sendData();
}

void opBtnRise() {
  if (sendMode == 0) {
    sendMode = 1;
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
        break;
      case 4:
        sendValue(minValidOxygen, maxValidOxygen, oxygenType, measureSpO2, &oxyCnt, reqOxygen);
        break;
      case 5:
        sendValue(minValidGsr, maxValidGsr, gsrType, measureGsr, &gsrCnt, reqGsr);
        break;
      default: 
        break;
    }

    tsLastReport = millis();

    if (canGoNextState) {
      sendMode = (sendMode + 1) % 6;
      resetState();
    }
  }
}

float measureTemperature() {
  float tempVal =  0;
  
  for(int i = 0; i < 100; i++) {
    tempVal += analogRead(TEMPERATURE);
  }
  tempVal /= 100;
  
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
  pox.update();
  float pulse = pox.getHeartRate();
  timestamp = millis();
  return pulse;
}

float measureSpO2() {
  pox.update();
  float spO2 = pox.getSpO2();
  timestamp = millis();
  return spO2;
}

float measureGsr() {
  float gsr = analogRead(0);
  //Serial.write(gsr);
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
}

void lightOpLeds() {
  digitalWrite(NO_OP_LED, LOW);
  digitalWrite(TEMP_LED, LOW);
  digitalWrite(ECG_LED, LOW);
  digitalWrite(BPM_LED, LOW);
  digitalWrite(OXY_LED, LOW);
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
      digitalWrite(BPM_LED, HIGH);
      break;
    case 4: 
      digitalWrite(OXY_LED, HIGH);
      break;
    case 5: 
      digitalWrite(GSR_LED, HIGH);
      break;
    default: 
      sendMode = 0;
      break;
  }
}
