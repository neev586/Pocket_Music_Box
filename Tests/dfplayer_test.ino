#include "Arduino.h"
#include "DFRobotDFPlayerMini.h"

#define FPS_RX 6
#define FPS_TX 7

HardwareSerial mySerial(1);
DFRobotDFPlayerMini myDFPlayer;

void setup() {
  Serial.begin(115200);
  mySerial.begin(9600, SERIAL_8N1, FPS_RX, FPS_TX);
  delay(2000);

  Serial.println("--- DFPlayer / SD Card Test ---");

  if (!myDFPlayer.begin(mySerial)) {
    Serial.println("FAIL: Cannot talk to DFPlayer. Check wiring.");
    while (true);
  }
  Serial.println("PASS: DFPlayer connected.");

  int files = myDFPlayer.readFileCounts();
  Serial.print("Files on SD card: ");
  Serial.println(files);

  if (files <= 0) {
    Serial.println("FAIL: No files found. Check SD card is FAT32 with MP3s named 001.mp3, 002.mp3 etc.");
    while (true);
  }
  Serial.println("PASS: SD card readable.");

  myDFPlayer.volume(20);
  myDFPlayer.play(1);
  Serial.println("Playing track 1 — you should hear audio now.");
}

void loop() {
  delay(1000);
}
