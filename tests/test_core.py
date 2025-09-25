import unittest
from lib.ui.core import Screen

class TestScreen(unittest.TestCase):
    def setUp(self):
        self.ctx = {"test": True}
        self.screen = Screen(self.ctx)

    def test_context(self):
        self.assertEqual(self.screen.ctx, self.ctx)

    def test_handle_and_render(self):
        try:
            self.screen.handle(None)
            self.screen.render(None)
        except Exception as e:
            self.fail(f"Screen methods raised an exception: {e}")

if __name__ == "__main__":
    unittest.main() 