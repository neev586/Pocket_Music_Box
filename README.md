# Pocket Music Box

A small 3D-printed music box that plays MP3s when the lid opens and pauses when it closes — like a classic ballerina music box, but with your own songs.

## How It Works

- **Open the lid** → music plays
- **Close the lid** → music pauses instantly
- **Reopen within 20 seconds** → resumes where it left off
- **Reopen after 20 seconds** → restarts the track from the beginning
- **Short press the button** → skip to the next track
- **Long press the button (0.5s+)** → cycle through 5 volume levels (mute → low → medium → high → max)
- **Lid stays closed for 60 seconds** → ESP32 enters deep sleep to save battery
- **Deep sleep** → wakes every 1.5 seconds to check if the lid is open

## Components

| Component | Specification |
|---|---|
| Microcontroller | ESP32-C3 Super Mini |
| Audio module | MP3-TF-16P (DFPlayer Mini clone) |
| Speaker | 40mm 8Ω |
| Battery | 3.7V LiPo, 300mAh (32×20×6mm) |
| Charger | TP4056 USB-C module |
| Light sensor | Photoresistor (LDR) |
| Button | 6×6mm tactile push button |
| Resistor | 10kΩ × 1 (LDR pull-down) |
| SD card | MicroSD, FAT32, 32GB or smaller |

## Wiring

```
POWER
  Battery +        → TP4056 B+
  Battery −        → TP4056 B−
  TP4056 OUT+      → ESP32 5V pin + DFPlayer VCC
  TP4056 OUT−      → GND rail (shared by all components)

ESP32 → DFPlayer (serial)
  GPIO 7 (TX)      → DFPlayer RX
  GPIO 6 (RX)      → DFPlayer TX

DFPlayer → Speaker
  SPK_1            → Speaker +
  SPK_2            → Speaker −

Button
  GPIO 9           → one leg
  other leg        → GND
  (uses internal pull-up, no external resistor needed)

LDR (light sensor)
  3.3V → LDR → junction → 10kΩ → GND
                 ↓
              GPIO 0
```

## SD Card Setup

- Format as **FAT32** (not exFAT or NTFS)
- Maximum **32GB** card
- Place MP3 files in the **root folder** (not in subfolders)
- Name files: `001.mp3`, `002.mp3`, `003.mp3`, etc.

## Software Setup

### Arduino IDE Settings

- **Board:** Nologo ESP32C3 Super Mini (or ESP32C3 Dev Module)
- **USB CDC On Boot:** Enabled
- **Flash Frequency:** 80MHz

### Required Library

- [DFRobotDFPlayerMini](https://github.com/DFRobot/DFRobotDFPlayerMini) — install via Arduino Library Manager

### First Upload

If the board connects and disconnects repeatedly when first plugged in, hold the **BOOT button** while plugging in the USB cable, then release after 1 second. Upload your sketch in this state. Subsequent uploads will work normally.

## Enclosure

The enclosure is a 3D-printed hinged box designed to house all components.

### Dimensions

- **Exterior (closed):** 68 × 60 × 52mm (68.5mm deep including hinge)
- **Interior:** 62.4 × 54.4 × 43.2mm
- **Wall thickness:** 2.8mm
- **Lid thickness:** 6mm

### Features

- 5-knuckle barrel hinge (2mm pin)
- Speaker grille on the front wall (40mm, concentric ring pattern)
- 6.4mm square button hole on the right wall
- SD card module holder on the right wall (flat mount, card accessible from top with lid open)
- Battery cradle (back-left)
- USB-C charge port opening on the back wall (14 × 8mm)

### Printing

- **Material:** PLA
- **Layer height:** 0.2mm
- **Walls:** 3 perimeters
- **Infill:** 15%
- **Supports:** none for the body; light support may be needed under the lid's hinge knuckles
- **Hinge pin:** insert a 2mm steel rod or length of filament after printing

### Files

- `enclosure_body.stl` — print floor-down as-is
- `enclosure_lid.stl` — pre-oriented top-face-down for printing
- `enclosure.py` — parametric source (Python + trimesh), edit variables and re-run to customize

## Deep Sleep & Power

The ESP32-C3 draws ~50–80mA when active. After 60 seconds with the lid closed, it enters deep sleep (~0.1–0.2mA average with 1.5-second wake checks). The 300mAh battery lasts:

- **Active playback:** ~4–5 hours
- **Deep sleep:** ~60–90 days

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| ESP32 connects/disconnects on USB | Empty flash | Hold BOOT button while plugging in, then upload |
| DFPlayer not found | Loose wiring or power issue | Check and reflow solder joints on VCC, GND, TX, RX |
| No sound but DFPlayer online | SD card issue | Reformat as FAT32, rename files to 001.mp3 format |
| Audio plays but is silent | Speaker wiring | Check SPK_1 and SPK_2 connections |
| LDR always reads 4095 | Missing pull-down resistor | Add 10kΩ between GPIO 0 and GND |
| Box won't wake from sleep | LDR covered or broken | Check that light reaches the LDR when lid opens |
| Stops working after charging | Solder joint cracked from heat | Reflow all DFPlayer solder joints |
| Audio distorts at max volume | Speaker overdriven | Lower top volume step from 30 to 25 |
| Stuck on "Initialization failed" | DFPlayer boots slower than ESP32 | Press reset button; if persistent, check wiring |
