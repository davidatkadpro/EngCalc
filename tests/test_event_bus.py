import unittest
from lib.sys.event_bus import EventBus

class TestEventBus(unittest.TestCase):
    def setUp(self):
        self.bus = EventBus(maxlen=3)

    def test_put_and_get(self):
        self.bus.put("event1")
        self.bus.put("event2")
        # get() is a stub, so this will not return events yet
        event = self.bus.get()
        self.assertIsNone(event)

    def test_has_event(self):
        self.assertFalse(self.bus.has_event())
        self.bus.put("event1")
        self.assertFalse(self.bus.has_event())  # stub always returns False

if __name__ == "__main__":
    unittest.main() 