# lib/ui/core.py
# Base Screen, Widget, MenuItem classes

class Screen:
    def __init__(self, ctx):
        self.ctx = ctx

    def handle(self, event):
        pass

    def render(self, buf):
        pass

class Widget:
    pass

class MenuItem:
    pass 