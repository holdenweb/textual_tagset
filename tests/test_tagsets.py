import asyncio
import pytest

from rich.text import Text
from textual.app import App
from textual.widgets import Input


pytest_plugins = ('pytest_asyncio',)

from textual_tagset import TagSet, FilteredTagSet

def ignore(i):
    pass


def build_app(ts_type, members=[], fmt="{v}", number_from=0):

    class TestApp(App):

        def __init__(self):
            super().__init__()
            self.members = dict(enumerate(members, start=number_from))
            self.action_func = ignore
            self.fmt = fmt
            # assert ts_type == list
            self.component = ts_type(self.members, ignore, fmt)

        def compose(self):
            yield self.component

        def on_click(self, event):
            self.log(self.tree)

    return TestApp

@pytest.mark.asyncio
@pytest.mark.parametrize("ts_class", [TagSet, FilteredTagSet])
async def test_tagset_static_empty(ts_class):
    app = build_app(ts_type=ts_class, fmt="{v}")
    test_app = app()
    async with test_app.run_test() as pilot:
        ch = test_app.query_one(ts_class)
        assert type(ch.render()) == Text
        assert ch.render().plain == ""


@pytest.mark.asyncio
@pytest.mark.parametrize("ts_class", [TagSet, FilteredTagSet])
async def test_tagset_static_nonempty(ts_class):
    app = build_app(ts_class, ["a", "b"], fmt="{v}")
    test_app = app()
    async with test_app.run_test() as pilot:
        ch = test_app.query_one(ts_class)
        assert ch.render().plain == "a b"


@pytest.mark.asyncio
@pytest.mark.parametrize("ts_class", [TagSet, FilteredTagSet])
async def test_tagset_static_formatting(ts_class):
    app = build_app(ts_class, ["a", "b"], fmt="\\[{v} [@click='klick({i})']x[/]]")
    test_app = app()
    async with test_app.run_test() as pilot:
        ch = test_app.query_one(TagSet)
        assert ch.render().plain == "[a x] [b x]"


@pytest.mark.asyncio
async def test_tagset_static_push_pop():
    app = build_app(TagSet, [], fmt="[{i} {v}]")
    test_app = app()
    async with test_app.run_test() as pilot:
        static = test_app.component
        static.push(1, "a")
        assert static.render().plain == "[1 a]"
        static.push(2, "b")
        assert static.render().plain == "[1 a] [2 b]"
        static.pop(1)
        assert static.render().plain == "[2 b]"


@pytest.mark.asyncio
async def test_filtered_tagset_static_render():
    """
    Verify correct operation of FilteredTagSet under input.
    """
    app = build_app(FilteredTagSet, ["a", "bz", "cz"], fmt="{v}")
    test_app = app()
    async with test_app.run_test() as pilot:
        assert test_app.query_one(TagSet).render().plain == "a bz cz"
        await pilot.press("a")
        assert test_app.query_one(TagSet).render().plain == "a"
        await pilot.press('backspace', 'b')
        assert test_app.component.render().plain == "bz"
        await pilot.press('z')
        assert test_app.component.render().plain == "bz"
        await pilot.press('backspace', 'backspace', 'z')
        assert test_app.component.render().plain == "bz cz"
        await pilot.press('backspace')
        assert test_app.component.render().plain == "a bz cz"
