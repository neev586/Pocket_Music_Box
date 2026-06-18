#define BUTTON_PIN 9

void setup() {
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  Serial.begin(115200);
  Serial.println("Button Test — press the button");
}

void loop() {
  if (digitalRead(BUTTON_PIN) == LOW) {
    Serial.println("PRESSED");
  } else {
    Serial.println("released");
  }
  delay(200);
}
