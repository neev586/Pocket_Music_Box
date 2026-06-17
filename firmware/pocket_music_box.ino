#include "Arduino.h"
#include "DFRobotDFPlayerMini.h"
#include <Preferences.h>

// ==========================================
// PIN DEFINITIONS
// ==========================================
#define FPS_RX 6      // ESP32 RX (Can leave disconnected)
#define FPS_TX 7       // ESP32 TX -> Connects to 1k resistor -> DFPlayer RX
#define BUTTON_PIN 9   // Song cycle / Volume button -> Connects to GPIO 4 and GND
#define LDR_PIN 0      // Photoresistor -> Connects to GPIO 0 (Analog pin)

// ==========================================
// CALIBRATION & TIMING CONFIGURATION
// ==========================================
const int LIGHT_THRESHOLD = 1000;       // LDR threshold (0-4095)
const unsigned long TIME_LIMIT = 20000; // Resume window (20 sec)
const unsigned long LONG_PRESS_TIME = 500;       // Long press = volume cycle
const unsigned long SLEEP_TIMEOUT = 60000;       // Sleep after 60 sec lid-closed
const uint64_t SLEEP_INTERVAL_US = 1 * 1500000;  // Wake every 1.5 second

// ==========================================
// GLOBAL VARIABLES
// ==========================================
HardwareSerial mySerial(1);
DFRobotDFPlayerMini myDFPlayer;
Preferences prefs;

unsigned long buttonPressTime = 0;
bool buttonActive = false;

bool boxWasOpen = false;
unsigned long boxCloseTime = 0;

int currentTrack = 1;
int totalTracks = 0;
int volumeStep = 2;
const int volumeLevels[] = {0, 12, 18, 24, 30};

bool wokeFromSleep = false;

// ==========================================
// HELPER: Save state and enter deep sleep
// ==========================================
void enterDeepSleep() {
  Serial.println("Entering deep sleep...");
  prefs.putInt("track", currentTrack);
  prefs.putInt("vol", volumeStep);
  prefs.end();
  
  esp_sleep_enable_timer_wakeup(SLEEP_INTERVAL_US);
  esp_deep_sleep_start();
}

void setup() {
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  analogReadResolution(12);
  
  Serial.begin(115200);

  // -------------------------------------------------------
  // DEEP SLEEP WAKE CHECK — run before full init
  // -------------------------------------------------------
  esp_sleep_wakeup_cause_t wakeReason = esp_sleep_get_wakeup_cause();

  if (wakeReason == ESP_SLEEP_WAKEUP_TIMER) {
    // Lid still closed? Stay asleep.
    int lightLevel = analogRead(LDR_PIN);
    if (lightLevel <= LIGHT_THRESHOLD) {
      esp_sleep_enable_timer_wakeup(SLEEP_INTERVAL_US);
      esp_deep_sleep_start();
    }

    // Lid is open — full wake
    wokeFromSleep = true;
    Serial.println(F("Woke from deep sleep — lid is open!"));
  }

  // -------------------------------------------------------
  // FULL INITIALIZATION
  // -------------------------------------------------------
  mySerial.begin(9600, SERIAL_8N1, FPS_RX, FPS_TX);
  Serial.println(F("Initializing Pocket Music Box..."));

  if (!myDFPlayer.begin(mySerial)) {
    Serial.println(F("Initialization failed. Check SD card or wiring!"));
    while(true);
  }

  Serial.println(F("DFPlayer Mini Online."));

  totalTracks = myDFPlayer.readFileCounts();
  if (totalTracks <= 0) {
    Serial.println("WARNING: No tracks found! Check SD card.");
    totalTracks = 10;
  }

  prefs.begin("musicbox", false);
  if (wokeFromSleep) {
    currentTrack = prefs.getInt("track", 1);
    volumeStep = prefs.getInt("vol", 2);
    Serial.print(F("Restored track: ")); Serial.println(currentTrack);
    Serial.print(F("Restored volume step: ")); Serial.println(volumeStep);
  }

  myDFPlayer.volume(volumeLevels[volumeStep]);

  if (wokeFromSleep) {
    boxWasOpen = true;
    Serial.println("Playing saved track after deep sleep.");
    myDFPlayer.play(currentTrack);
  } else {
    myDFPlayer.play(currentTrack);
    delay(200);
    myDFPlayer.pause();
  }
}

void loop() {
  // -----------------------------------------------------------------
  // 1. LID SENSOR LOGIC (PHOTORESISTOR)
  // -----------------------------------------------------------------
  int lightLevel = analogRead(LDR_PIN);
  bool isBoxOpen = (lightLevel > LIGHT_THRESHOLD);

  if (isBoxOpen && !boxWasOpen) {
    boxWasOpen = true;
    unsigned long timeSpentClosed = millis() - boxCloseTime;

    if (timeSpentClosed <= TIME_LIMIT) {
      Serial.println("Opened quickly! Resuming track.");
      myDFPlayer.start();
    } else {
      Serial.println("Opened after a while! Restarting track from start.");
      myDFPlayer.play(currentTrack);
    }
    delay(200);
  } 
  else if (!isBoxOpen && boxWasOpen) {
    myDFPlayer.pause();
    boxCloseTime = millis();
    boxWasOpen = false;
    Serial.println("Box closed. Audio paused.");
    delay(200);
  }

  // -----------------------------------------------------------------
  // 2. DEEP SLEEP CHECK (lid closed too long)
  // -----------------------------------------------------------------
  if (!isBoxOpen && !boxWasOpen) {
    unsigned long closedDuration = millis() - boxCloseTime;
    if (closedDuration > SLEEP_TIMEOUT) {
      enterDeepSleep();
    }
  }

  // -----------------------------------------------------------------
  // 3. BUTTON CONTROLS (only when lid is open)
  // -----------------------------------------------------------------
  if (isBoxOpen) {
    bool isPressed = (digitalRead(BUTTON_PIN) == LOW);

    if (isPressed && !buttonActive) {
      buttonActive = true;
      buttonPressTime = millis();
    } 
    else if (!isPressed && buttonActive) {
      long pressDuration = millis() - buttonPressTime;
      buttonActive = false;

      if (pressDuration < LONG_PRESS_TIME) {
        currentTrack++;
        if (currentTrack > totalTracks) {
          currentTrack = 1;
        }
        Serial.print("Short Press: Skipping to track ");
        Serial.println(currentTrack);
        myDFPlayer.play(currentTrack);
      } 
      else {
        volumeStep++;
        if (volumeStep > 4) {
          volumeStep = 0;
        }
        Serial.print("Long Press: Setting volume step to ");
        Serial.println(volumeStep);
        myDFPlayer.volume(volumeLevels[volumeStep]);
      }
      delay(200);
    }
  }

  delay(30);
}
