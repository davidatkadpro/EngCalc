# main.py
# Entry point for Engineering Calculator (MicroPython)

import config
from lib.sys.event_bus import EventBus
from lib.sys.input_manager import InputManager
from lib.sys.display_manager import DisplayManager
from lib.ui.menu import HomeMenuScreen
from lib.apps import registry  # triggers all calc register on import

def boot():
    bus = EventBus(64)
    disp = DisplayManager(config.DISPLAY)
    inputs = InputManager(config.PINS, bus)
    ctx = {"bus": bus, "display": disp, "config": config}
    screen = HomeMenuScreen(ctx)
    run_mainloop(bus, inputs, disp, screen)

if __name__ == "__main__":
    boot() 