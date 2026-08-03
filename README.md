# Hercules P32 DJ - Ableton Live Custom Script 🎛️

This repository contains a custom MIDI Remote Script for the **Hercules P32 DJ** controller, designed for Ableton Live 9, 10, and 11. It is based on a script originally generated via Remotify, with advanced custom modifications.

## Features

- **Clip Launching:** Full 7x4 clip launching grid on the performance pads.
- **Mixer Controls:** Volume and track navigation.
- **Dynamic Send Controls (Custom Mod):** 
  In the main mixer mode (Mode 0), the left deck's top knobs are configured to dynamically follow the **selected track** in Ableton and control its sends:
  - **HIGH Knob:** Send A (e.g., Reverb)
  - **MID Knob:** Send B (e.g., Delay)
  - **LOW Knob:** Send C
  - *(The Filter knob remains unassigned and free for custom MIDI mapping).*

## Installation

1. Download or clone this repository.
2. Open the cloned folder, and locate the `Hercules_P32_DJ` folder.
3. Move the `Hercules_P32_DJ` folder into your Ableton MIDI Remote Scripts directory:
   - **Windows:** `\ProgramData\Ableton\Live x.x\Resources\MIDI Remote Scripts\`
   - **Mac:** Right-click the Ableton Live application -> Show Package Contents -> `Contents/App-Resources/MIDI Remote Scripts/`
4. Open Ableton Live, go to **Preferences -> Link / MIDI**.
5. Select **Hercules P32 DJ** under Control Surface. Set the Input and Output to your controller.
6. **Important:** Make sure the **"Remote"** switch is turned ON for the Hercules P32 DJ in the MIDI Ports section at the bottom of the preferences.

## Modes

- **Mode 1 (Default):** Clip Launcher and Mixer mode. Left knobs control the selected track's sends.
- **Mode 2 (Finger Drumming):** Press the BROWSE encoder to enter Mode 2. The right pads send MIDI notes for playing drum racks or synths.

## Documentation
For more detailed information on the base script mapping, please refer to the included PDF guides (`EN - Setup and Guide.pdf`).
