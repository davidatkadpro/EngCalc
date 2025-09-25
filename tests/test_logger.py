import unittest
from lib.sys.logger import Logger

class TestLogger(unittest.TestCase):
    def setUp(self):
        self.logger = Logger(size=3)

    def test_log_and_get_logs(self):
        self.logger.log("A")
        self.logger.log("B")
        self.logger.log("C")
        logs = self.logger.get_logs()
        self.assertEqual(logs, [])  # Stub returns empty; update when implemented

    def test_ring_buffer(self):
        # This is a stub; update when ring buffer is implemented
        for i in range(5):
            self.logger.log(f"msg{i}")
        logs = self.logger.get_logs()
        self.assertEqual(logs, [])  # Stub returns empty

if __name__ == "__main__":
    unittest.main() 