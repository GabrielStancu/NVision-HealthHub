#define REPORTING_PERIOD_MS 20000
#define TEMPERATURE A1
#define LO_PLUS 10
#define LO_MINUS 11
#define ECG A2
#define GSR A0
#define OP_BTN 2

#define NO_OP_LED 8
#define TEMP_LED 7
#define ECG_LED 6
#define BPM_LED 5
#define OXY_LED 4
#define GSR_LED 3

#define TIMER_COUNT_UP 250

const float minValidTemp = 32;
const float maxValidTemp = 42;
const float minValidEcg = 1;
const float maxValidEcg = 500;
const float minValidPulse = 30;
const float maxValidPulse = 200;
const float minValidOxygen = 80;
const float maxValidOxygen = 101;
const float minValidGsr = 1;
const float maxValidGsr = 1022;

const char separator = ';';

const char tempType[4] = "TMP";
const char ecgType[4] = "ECG";
const char pulseType[4] = "BPM";
const char oxygenType[4] = "OXY";
const char gsrType[4] = "GSR";

const int reqTmp = 1;
const int reqEcg = 3000;
const int reqHb = 1;
const int reqOxygen = 1;
const int reqGsr = 1;

const int averageCounts = 500;
