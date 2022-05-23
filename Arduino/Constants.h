#define REPORTING_PERIOD_MS 5000
#define TEMPERATURE A2
#define LO_PLUS 10
#define LO_MINUS 11
#define ECG A0
#define GSR A3
#define OP_BTN 2

#define NO_OP_LED 8
#define TEMP_LED 7
#define ECG_LED 6
#define BPM_LED 5
#define OXY_LED 4
#define GSR_LED 3

#define TIMER_COUNT_UP 250

const float minValidTemp = 32;
const float maxValidTemp = 40;
const float minValidEcg = 1;
const float maxValidEcg = 1000;
const float minValidPulse = 60;
const float maxValidPulse = 150;
const float minValidOxygen = 85;
const float maxValidOxygen = 99;
const float minValidGsr = 1;
const float maxValidGsr = 30;

const char separator = ';';

const char tempType[4] = "TMP";
const char ecgType[4] = "ECG";
const char pulseType[4] = "BPM";
const char oxygenType[4] = "OXY";
const char gsrType[4] = "GSR";

const int reqTmp = 1;
const int reqEcg = 5000;
const int reqHb = 1;
const int reqOxygen = 1;
const int reqGsr = 1;

const int averageCounts = 50;
