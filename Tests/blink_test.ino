#define LED_PIN 8

void setup() {
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(115200);
  Serial.println("Blink test running!");
}

void loop() {
  digitalWrite(LED_PIN, LOW);   // ON (active LOW)
  Serial.println("LED ON");
  delay(1000);
  digitalWrite(LED_PIN, HIGH);  // OFF
  Serial.println("LED OFF");
  delay(1000);
}
