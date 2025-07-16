# Engineering Calculator for Structural Engineers

## Overview

This project is an open-source, extensible engineering calculator designed for structural engineers. It runs on MicroPython and targets the RP2040 microcontroller, featuring a 36-key (6x6) matrix keypad and an SSD1309 OLED display (SPI). The calculator is modular, supporting advanced engineering calculations, material libraries, and a robust, testable architecture.

## Hardware Summary

- **Microcontroller:** RP2040 (Raspberry Pi Pico or similar)
- **Display:** SSD1309 OLED (128x64, SPI)
- **Keypad:** 36-key (6x6 matrix, 12 GPIOs)
- **I/O:** Rotary encoder (with push), I2C/SPI peripherals
- **Power:** USB or battery (optional low-power modes)

## Software Stack

- **Language:** MicroPython
- **Architecture:** Layered, event-driven (see RESEARCH.md)
- **Core Features:**
  - Modular calculation plugins (e.g., span, load, section properties)
  - Material data libraries (steel, timber, concrete)
  - Unit conversion and SI/imperial support
  - Persistent settings and key remapping
  - Testable core logic (runs on desktop Python)

## Getting Started

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd EngCalc
   ```
2. **Install MicroPython on your RP2040 device.**
3. **Copy project files to the device:**
   - Use `mpremote`, Thonny, or similar tools.
4. **Connect hardware:**
   - Wire the 6x6 keypad matrix to 12 GPIOs.
   - Connect the SSD1309 OLED via SPI.
5. **Run main.py**

## Directory Structure

```
/main.py                # Boot, init, main loop
/config.py              # Pin maps, display config
/lib/
  hal/                  # Hardware abstraction (display, keypad, encoder)
  sys/                  # Event bus, input, display manager, settings
  ui/                   # Screens, menus, forms, dialogs
  apps/                 # Calculation modules, material libraries
  util/                 # Bitmaps, fonts, debounce, timer
```

See `RESEARCH.md` for detailed architecture and design notes.

## Contribution Guidelines

- Follow the modular structure; add new calcs as plugins.
- Write core logic as pure Python for testability.
- Document hardware pinouts and config changes.
- Submit issues or PRs for discussion.

## License

MIT (or specify your preferred license)
