# main.py
# Entry point for Engineering Calculator (MicroPython)

import config
from lib.sys.event_bus import EventBus
from lib.sys.input_manager import InputManager
from lib.sys.display_manager import DisplayManager
from lib.ui.menu import HomeMenuScreen
from lib.apps import registry  # triggers all calc register on import
from lib.sys.logger import Logger
from lib.sys.settings import Settings
from lib.ui.dialogs import show_error

def boot():
    bus = EventBus(64)
    disp = DisplayManager(config.DISPLAY)
    inputs = InputManager(config.PINS, bus)
    logger = Logger(size=200)
    settings = Settings()
    ctx = {"bus": bus, "display": disp, "config": config, "logger": logger, "settings": settings}
    try:
        settings.load()
        logger.log("Settings: Loaded")
    except Exception as e:
        logger.log(f"Settings: Load error: {e}")
        show_error(ctx, "Could not load settings. Defaults will be used.")
    screen = HomeMenuScreen(ctx)
    run_mainloop(bus, inputs, disp, screen, logger, settings, ctx)

def run_mainloop(bus, inputs, disp, screen, logger, settings, ctx):
    """Synchronous main loop: poll inputs, process events, manage screen stack, log actions, persist settings, handle errors, show user errors."""
    import time
    screen_stack = [screen]
    last_save = time.time()
    SAVE_INTERVAL = 5  # seconds
    while True:
        try:
            # 1. Poll all input devices (keypad, encoder, etc.)
            # This updates the event bus with any new user actions.
            inputs.poll()

            # 2. Process all events in the event bus queue.
            # Each event is handled by the current top screen.
            while bus.has_event():
                evt = bus.get()
                logger.log(f"Event: {evt}")
                top = screen_stack[-1]
                try:
                    # The screen handles the event and may return an action (e.g., redraw, push, pop)
                    action = top.handle(evt)
                except Exception as e:
                    logger.log(f"Screen handle error: {e}")
                    show_error(ctx, f"An error occurred in the UI: {e}")
                    continue
                logger.log(f"Screen: {type(top).__name__}, Action: {action}")

                # 3. Handle screen actions: redraw, push new screen, or pop current screen
                if action == getattr(top, 'REDRAW', None):
                    logger.log("Display: REDRAW")
                    try:
                        disp.redraw(top)
                    except Exception as e:
                        logger.log(f"Display redraw error: {e}")
                        show_error(ctx, f"Display error: {e}")
                elif isinstance(action, tuple):
                    if action[0] == "push":
                        logger.log(f"Screen stack: PUSH {type(action[1]).__name__}")
                        screen_stack.append(action[1])
                        try:
                            disp.redraw(screen_stack[-1])
                        except Exception as e:
                            logger.log(f"Display redraw error: {e}")
                            show_error(ctx, f"Display error: {e}")
                    elif action[0] == "pop" and len(screen_stack) > 1:
                        logger.log("Screen stack: POP")
                        screen_stack.pop()
                        try:
                            disp.redraw(screen_stack[-1])
                        except Exception as e:
                            logger.log(f"Display redraw error: {e}")
                            show_error(ctx, f"Display error: {e}")

            # 4. On-demand save: if any part of the code requested a settings save, do it now
            if settings.should_save():
                try:
                    settings.save()
                    logger.log("Settings: On-demand save")
                except Exception as e:
                    logger.log(f"Settings: On-demand save error: {e}")
                    show_error(ctx, f"Could not save settings: {e}")
                last_save = time.time()

            # 5. Periodic save: save settings every SAVE_INTERVAL seconds to persist user changes
            now = time.time()
            if now - last_save > SAVE_INTERVAL:
                try:
                    settings.save()
                    logger.log("Settings: Saved")
                except Exception as e:
                    logger.log(f"Settings: Save error: {e}")
                    show_error(ctx, f"Could not save settings: {e}")
                last_save = now

            # 6. Sleep briefly to reduce CPU usage and allow other system tasks to run
            time.sleep(0.01)
        except Exception as e:
            # Catch any unexpected errors in the main loop, log and show to user, then continue
            logger.log(f"Main loop error: {e}")
            show_error(ctx, f"A system error occurred: {e}")
            time.sleep(0.1)

if __name__ == "__main__":
    boot() 