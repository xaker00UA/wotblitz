from flet import *
from .page1 import Up, Middle, Down, Event
from app import ClanInterface, Clan
import asyncio


class Up_clan(Up):
    def __init__(self, page, event):
        super().__init__(page=page, event=event)
        self.text = TextField(label="tag", on_submit=self.on_click_search)
        self.controls = [
            Row([Column([self.theme, self.menu]), self.search, self.session]),
            self.text,
        ]
        self.vertical_alignment = CrossAxisAlignment.START
        self.height = 80
        self.session.on_click = self.start_session

    def start_session(self, e):
        if self.text.value:
            asyncio.run(ClanInterface(name=self.text.value).reset())
            self.add_menu(self.text.value)
        else:
            self.handlers.emit("start_session")


class Middle_clan(Middle):
    def __init__(self, page, event):
        super().__init__(page=page, event=event)

    def crate_player(self, name):
        self.player = ClanInterface(name=name)

    def build_content(self, name, trigger: str = None):
        super().build_content(name, trigger)
        if hasattr(self, "table"):
            self.text.value = self.text.value.replace("игрока", "клана")
            self.text.update()


class Down_clan(Down):
    def __init__(self, page, event):
        super().__init__(event)


def main(page: Page):
    event = Event()
    up = Up_clan(page, event)
    middle = Middle_clan(page, event)
    down = Down_clan(page, event)
    return Container(content=Column([up, middle, down]), expand=True)
