"""
demo_tagset.py: show off the features of textual_tagset.
"""
from textual.app import App
from textual.containers import Vertical
from textual.validation import Integer
from textual.widgets import Input, Button
from textual_tagset import TagSet
from textual_tagset.demo.data import random_names

from .baseapp import BaseScreen

class TagSetScreen(BaseScreen):
    def __init__(self, n):
        super().__init__()
        self.n = n

    def demo_widget(self):
        self.items = dict(enumerate(random_names(self.n)))
        return TagSet(self.items, action_func=self.log_item, key=None, sep="\n")

class SelTestApp(App):

    CSS = """
    Screen {
        layout: vertical;
    }
    """

    def compose(self):
        self.input = Input(placeholder="How many names",
                    validators=[Integer()],
                    id="name-count")
        yield self.input

    def on_input_submitted(self, event):
        n = int(event.control.value)
        self.app.push_screen(TagSetScreen(n), self.reset_inputs)
        self.reset_inputs()

    def reset_inputs(self):
        self.input.clear()
        self.input.focus()

app = SelTestApp()

if __name__ == '__main__':
    app.run()
