# Product Requirements Document (PRD)

## Project: Engineering Calculator for Structural Engineers

### 1. Purpose & Scope

Develop a portable, extensible engineering calculator for structural engineers, supporting advanced calculations, material data lookup, and unit conversions. The device should be robust, user-friendly, and easily updatable.

### 2. Target Users
- Structural engineers (field and office)
- Engineering students
- Professionals needing quick, reliable calculations and material data

### 3. Hardware Requirements
- **Microcontroller:** RP2040 (Raspberry Pi Pico or similar)
- **Display:** SSD1309 OLED, 128x64, SPI interface
- **Keypad:** 36-key (6x6 matrix), 12 GPIOs
- **Rotary Encoder:** With push switch (optional)
- **Power:** USB or battery
- **Storage:** Internal flash (external optional)

### 4. Software Requirements
- **Language:** MicroPython
- **Architecture:** Layered, event-driven, modular (see RESEARCH.md)
- **UI:** Menu-driven, stack-based screens, numeric input forms, material selectors
- **Persistence:** JSON or key/value for settings, last-used values, key remaps
- **Testability:** Core logic runs on desktop Python for unit testing

### 5. Key Features
- Modular calculation plugins (e.g., span, load, section properties)
- Material data libraries (steel, timber, concrete, extensible)
- Unit conversion (SI and imperial)
- Persistent user settings and key remapping
- Event-driven input handling (keypad, encoder)
- OLED display with efficient update (double-buffered or dirty region)
- Logging and diagnostics (optional)

### 6. Constraints & Considerations
- **Memory:** Optimize for RP2040 RAM/flash limits; freeze static libs
- **Performance:** Responsive UI, avoid display flicker
- **Power:** Support for low-power modes if battery-powered
- **Extensibility:** New calcs/materials added as modules/plugins
- **Updatability:** Filesystem access via USB for updates

### 7. Out of Scope (MVP)
- Wireless connectivity
- On-device editing of material tables
- Graphical plotting

### 8. Success Criteria
- Accurate, reliable calculations for structural engineering tasks
- Fast, intuitive UI navigation
- Easy to add new calculation modules and material data
- Runs stably on RP2040 hardware

### 9. Open Questions
- Final display size and type (SSD1309 confirmed?)
- Battery life requirements
- Need for on-device data editing/import?
- Required calculation domains for launch

---

For architecture and implementation details, see RESEARCH.md. 