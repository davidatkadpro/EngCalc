# lib/sys/settings.py
# Persistent settings store

class Settings:
    def __init__(self):
        self._save_requested = False

    def load(self):
        pass

    def save(self):
        pass

    def request_save(self):
        """Request a settings save on the next main loop iteration."""
        self._save_requested = True

    def should_save(self):
        """Check if a save was requested, and clear the flag."""
        if self._save_requested:
            self._save_requested = False
            return True
        return False 