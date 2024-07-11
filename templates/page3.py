from flet import *
from app import Container_class
import json
import asyncio
from config import config


class Item(Container):
    def __init__(self, value: str, callback):
        super().__init__()
        self.callback = callback
        self.value = value
        self.delete = IconButton(
            icon="delete", on_click=self.delete_text, icon_size=15, height=20
        )
        self.content = Row(
            [Text(value), self.delete], alignment=MainAxisAlignment.SPACE_BETWEEN
        )

    def delete_text(self, e):
        self.content.clean()
        self.callback(self)


class Items(Column):
    def __init__(self, players: list, clans: list):
        super().__init__()
        self.player = Column()
        self.clan = Column()
        self.player.controls = [
            Item(players, self.remove_item) for players in (players or [])
        ]
        self.clan.controls = [Item(clan, self.remove_item) for clan in (clans or [])]
        self.controls = [
            Text("Save players", selectable=True),
            self.player,
            Divider(height=3),
            Text("Save clans"),
            self.clan,
        ]

    def add(self, name, trigger: bool):
        if trigger:
            self.player.controls.append(Item(name, self.remove_item))
        else:
            self.clan.controls.append(Item(name, self.remove_item))
        self.update()

    def remove_item(self, item):
        if item in self.player.controls:
            self.player.controls.remove(item)
        elif item in self.clan.controls:
            self.clan.controls.remove(item)
        self.update()


def main(page: Page):

    async def process(e, bar):
        if e.control.data:
            await Container_class().update_player(bar)
        else:
            await Container_class().update_clan(bar)

    def reset_sess(e):
        bar = ProgressBar(width=500)
        text = page.overlay[0].content
        page.overlay[0].content = bar
        page.overlay[0].disabled = True
        page.update()
        asyncio.run(process(e, bar))
        page.overlay[0].disabled = False
        page.overlay[0].content = text
        page.update()

    def reset(e):
        def close(e):
            dialog.open = False
            page.update()

        dialog = AlertDialog(
            title=Text("Сброс сессии"),
            content=Text("Do you want to reset"),
            modal=True,
            actions=[
                Row(
                    [
                        ElevatedButton(text="Clan", on_click=reset_sess, data=False),
                        ElevatedButton(text="Player", on_click=reset_sess, data=True),
                    ]
                ),
                IconButton(icon=icons.CLOSE, on_click=close),
            ],
            actions_alignment=MainAxisAlignment.SPACE_BETWEEN,
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def add(e: ControlEvent):
        items.add(e.control.value, e.control.data)

    def submit(e):
        with open("config.json", "w") as f:
            config["players"] = [p.value for p in items.player.controls]
            config["clans"] = [c.value for c in items.clan.controls]
            config["start_session"] = start_session.value
            json.dump(config, f, indent=4)

    player_text = TextField(label="nickname", on_submit=add, data=True)
    clan_text = TextField(label="clan", on_submit=add, data=False)
    items = Items(config.get("players"), config.get("clans"))
    reset_sessions = ElevatedButton(text="reset session", on_click=reset)
    start_session = Switch(
        label="start session",
        value=config.get("start_session", False),
    )
    button_submit = OutlinedButton(text="submit", on_click=submit)

    content = Container(
        content=Column(
            [
                player_text,
                clan_text,
                items,
                reset_sessions,
                start_session,
                button_submit,
            ]
        ),
        expand=True,
    )
    return content
