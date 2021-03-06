#include <Wire.h>
#include <TimerOne.h>
#include "MAX30100_PulseOximeter.h"
#include "Constants.h"

PulseOximeter pox;

bool pushingOpBtn = false;
int sendMode = 0;
int tmpCnt = 0;
int ecgCnt = 0;
int hbCnt = 0;
int oxyCnt = 0;
int gsrCnt = 0;

bool canGoNextState = false;
bool sentNoOp = false;
bool bootRun = true;
bool resetCycle = false;
static volatile bool canSendData = false;
unsigned long timestamp;

float value = 0;
int crtMeasurementCnt = averageCounts;

void setup() { 
  Serial.begin(115200);
  pinMode(TEMPERATURE, INPUT);
  pinMode(LO_PLUS, INPUT); 
  pinMode(LO_MINUS, INPUT); 
  pinMode(OP_BTN, INPUT_PULLUP);
  pinMode(GSR, INPUT);
  attachInterrupt(digitalPinToInterrupt(OP_BTN), opBtnChange, CHANGE);
  pinMode(NO_OP_LED, OUTPUT);
  pinMode(TEMP_LED, OUTPUT);
  pinMode(ECG_LED, OUTPUT);
  pinMode(BPM_LED, OUTPUT);
  pinMode(OXY_LED, OUTPUT);
  pinMode(GSR_LED, OUTPUT);
  
  pox.begin();
  pox.setIRLedCurrent(MAX30100_LED_CURR_7_6MA);
  timestamp = millis();
  timerSetup();
}

void loop() {
  lightOpLeds();
  sendData();
}

void timerSetup()
{
  Timer1.initialize(REPORTING_PERIOD_MS);
  Timer1.attachInterrupt(takeMeasurement); 
}

void takeMeasurement()
{
  canSendData = true;
}

void opBtnChange() {
  if(digitalRead(OP_BTN) == LOW){
    pushingOpBtn = true;
    if (sendMode == 0 && !resetCycle) {
      sendMode = 1;
      pushingOpBtn = false;
      sentNoOp = false;
    }  
  } else {
    pushingOpBtn = false;
    resetCycle = false;
  }
}

void sendData() { 
  pox.update();
  if (canSendData) {
    switch(sendMode) {
      case 0:
        sendNoOp();
        break;
      case 1:
        sendValue(minValidTemp, maxValidTemp, tempType, measureTemperature, &tmpCnt, reqTmp);
        break;
      case 2:
        sendValue(minValidGsr, maxValidGsr, gsrType, measureGsr, &gsrCnt, reqGsr);
        break;
      case 3: 
        sendValue(minValidPulse, maxValidPulse, pulseType, measurePulse, &hbCnt, reqHb);
        break;
      case 4:
        sendValue(minValidOxygen, maxValidOxygen, oxygenType, measureSpO2, &oxyCnt, reqOxygen);
        break;
      case 5:
        sendValue(minValidEcg, maxValidEcg, ecgType, measureEcg, &ecgCnt, reqEcg);
        break;
      default: 
        break;
    }
    if (canGoNextState) {
      if (sendMode > 0) {
        sendMode = (sendMode + 1) % 6;
      }
      if (sendMode == 0) {
        resetCycle = true;
      }
      pushingOpBtn = false;
      resetState();
    }
    canSendData = false;
  }
}

float measureTemperature() {
  float tempVal = analogRead(TEMPERATURE);
  timestamp = millis();
  float celsius = (tempVal/1024.0)*265; 
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
  int gsr = analogRead(GSR);
  timestamp = millis();
  
  return gsr;
}

void sendValue(float minValue, float maxValue, const char type[], float (*measureValueFunc)(), int *measurementCnt, int reqCnt) {
  if (!pushingOpBtn)
   return;

  float measuredValue = measureValueFunc();
  if (measuredValue < minValue || measuredValue > maxValue)
    return;
    
  value += measuredValue;

  if (reqCnt == 1) 
  {
    if (crtMeasurementCnt > 0) 
    {
      crtMeasurementCnt--;
      return;
    }
      
    value /= averageCounts;
    crtMeasurementCnt = averageCounts;
  }
  String valueStr = String(value, 3);
  String timestampStr = String(timestamp);
  String sendValue = "";
  if (value >= minValue && value <= maxValue && pushingOpBtn) {
    countMeasurement(measurementCnt, reqCnt);
    sendValue.concat(type);
    sendValue.concat(separator);
    sendValue.concat(valueStr);
    sendValue.concat(separator);
    sendValue.concat(timestampStr);
    Serial.println(sendValue);
  } 

  value = 0;
}

void sendNoOp() {
  if (!sentNoOp) 
  {
    Serial.println("NOP");
    sentNoOp = true;
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
  digitalWrite(NO_OP_LED, HIGH);
  digitalWrite(TEMP_LED, HIGH);
  digitalWrite(ECG_LED, HIGH);
  digitalWrite(BPM_LED, HIGH);
  digitalWrite(OXY_LED, HIGH);
  digitalWrite(GSR_LED, HIGH);

  switch(sendMode) {
    case 0:
      digitalWrite(NO_OP_LED, LOW);
      break;
    case 1: 
      digitalWrite(TEMP_LED, LOW);
      break;
    case 2: 
      digitalWrite(ECG_LED, LOW);
      break;
    case 3: 
      digitalWrite(BPM_LED, LOW);
      break;
    case 4: 
      digitalWrite(OXY_LED, LOW);
      break;
    case 5: 
      digitalWrite(GSR_LED, LOW);
      break;
    default: 
      sendMode = 0;
      break;
  }
}
