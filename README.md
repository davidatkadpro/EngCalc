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

## System Robustness & Features

- **Logging:** All major actions, events, and errors are logged to a ring buffer (RAM) and can be optionally printed to serial. This helps with debugging and diagnostics both during development and in the field.
- **User-Facing Error Messages:** When errors occur (e.g., settings load/save, display redraw, UI handler), a user-friendly error message is shown. Currently, this prints to the console, but is designed to be shown on the device display in the future.
- **Settings Persistence:**
  - Settings are loaded at boot and saved periodically (every 5 seconds by default) to preserve user preferences and state.
  - On-demand saves are supported: any part of the code can request an immediate save (e.g., after a key remap or preference change).
  - All settings operations are robustly error-handled and logged.
- **Robust Error Handling:**
  - The main loop and all critical operations are wrapped in try/except blocks.
  - Errors are logged and shown to the user, but do not crash the system.

## Developer Notes

- To log an event or error, use the `Logger` instance from the context (`ctx['logger']`).
- To show a user-facing error, use `show_error(ctx, "message")` from anywhere in the code.
- To trigger an on-demand settings save, call `ctx['settings'].request_save()`.
- All persistent settings are managed via the `Settings` class and are automatically loaded/saved.
