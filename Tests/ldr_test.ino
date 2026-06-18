#define LDR_PIN 0

void setup() {
  analogReadResolution(12);
  Serial.begin(115200);
  Serial.println("LDR Test — cover and uncover the sensor");
}

void loop() {
  int value = analogRead(LDR_PIN);
  Serial.print("LDR: ");
  Serial.print(value);
  Serial.print(" / 4095");

  if (value > 2000) Serial.println("  -> BRIGHT (lid open)");
  else if (value > 1000) Serial.println("  -> DIM");
  else Serial.println("  -> DARK (lid closed)");

  delay(300);
}
