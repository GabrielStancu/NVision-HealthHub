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