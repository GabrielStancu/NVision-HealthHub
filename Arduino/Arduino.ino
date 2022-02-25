#include <Wire.h>

#define DEB_INTERVAL_MS 5000
#define REPORTING_PERIOD_MS 1
#define HEARTBEAT A0
#define TEMPERATURE A1
#define LO_PLUS 10
#define LO_MINUS 11
#define ECG A2
#define OP_BTN 2

#define DONE_OP_LED 8
#define NO_OP_LED 7
#define HB_LED 6
#define TEMP_LED 5
#define ECG_LED 4

#define REQ_HB 5
#define REQ_TMP 5
#define REQ_ECG 10

bool pushingOpBtn = false;
int sendMode = 0;
uint32_t tsLastReport = 0;
int lastSwitchDetectedMIllis;
const char separator = ';';
unsigned long timestamp;

int hbCnt = 0;
int tmpCnt = 0;
int ecgCnt = 0;

bool canGoNextState = false;

void setup() { 
  pinMode(HEARTBEAT, INPUT);
  pinMode(TEMPERATURE, INPUT);
  pinMode(LO_PLUS, INPUT); 
  pinMode(LO_MINUS, INPUT); 
  pinMode(OP_BTN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(OP_BTN), opBtnRise, RISING);
  pinMode(DONE_OP_LED, OUTPUT);
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
  float correctiveFactor = 1.5;
  int sum = 0;
  for (int i = 0; i < 20; i++)
    sum += analogRead(HEARTBEAT);
  pulse = sum / 20.00 * correctiveFactor;
  timestamp = millis();

  return pulse;
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

  timestamp = millis();
  return analogRead(ECG);
}

void sendHeartbeat() {
  float heartbeat = measureHeartbeat();
  String heartbeatStr = String(heartbeat, 3);
  String timestampStr = String(timestamp);
  String sendValue = "";
  const float minValidValue = 0;
  const float maxValidValue = 250;
  if (heartbeat >= minValidValue && heartbeat <= maxValidValue) {
    countHeartbeat();
    sendValue.concat("HB");
    sendValue.concat(separator);
    sendValue.concat(heartbeatStr);
    sendValue.concat(separator);
    sendValue.concat(timestampStr);
    Serial.println(sendValue);
  }
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

void countHeartbeat() {
  hbCnt++;
  if(hbCnt >= REQ_HB) {
    digitalWrite(DONE_OP_LED, HIGH);
    canGoNextState = true;
  } 
  else {
    canGoNextState = false;
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

void resetState() {
  hbCnt = 0;
  tmpCnt = 0;
  ecgCnt = 0;
  canGoNextState = false;
  digitalWrite(DONE_OP_LED, LOW);
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
