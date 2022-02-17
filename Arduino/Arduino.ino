void setup() {
  setupHeartbeat();
}

void loop() {
  // Heartbeat:
  float heartbeat = measureHeartbeat();
  sendHeartbeat(heartbeat);
  
  delay(1000);
}

void setupHeartbeat() {
  pinMode(A0, INPUT);
  Serial.begin(9600);
}

float measureHeartbeat() {
  float pulse;
  int sum = 0;
  for (int i = 0; i < 20; i++)
    sum += analogRead(A0);
  pulse = sum / 20.00;

  return pulse;
}

void sendHeartbeat(float heartbeat) {
  Serial.println(floatToCharArray(heartbeat));
}

char* floatToCharArray(float val) {
  static char sz[10] = {' '} ;
  int val_int = (int) val;   
  float val_float = abs((val - val_int) * 100);
  int val_fra = (int)val_float;
  sprintf (sz, "%d.%d", val_int, val_fra); 
  return sz;
}
