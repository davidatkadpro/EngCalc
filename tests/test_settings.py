import unittest
from lib.sys.settings import Settings

class TestSettings(unittest.TestCase):
    def setUp(self):
        self.settings = Settings()

    def test_request_and_should_save(self):
        self.assertFalse(self.settings.should_save())
        self.settings.request_save()
        self.assertTrue(self.settings.should_save())
        self.assertFalse(self.settings.should_save())  # should clear flag

    def test_load_and_save(self):
        # These are stubs; in real tests, mock file I/O
        try:
            self.settings.load()
            self.settings.save()
        except Exception as e:
            self.fail(f"Settings load/save raised an exception: {e}")

if __name__ == "__main__":
    unittest.main() 