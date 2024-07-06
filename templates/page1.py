import asyncio
from typing import Callable
from flet import *
from app import All_General, PlayerInterface, User


class Event:
    def __init__(self) -> None:
        self._listener: dict[str, list[Callable]] = {}

    def on(self, event: str, listener: Callable):
        if event not in self._listener:
            self._listener[event] = []
        self._listener[event].append(listener)

    def emit(self, event: str, data=None):
        if event in self._listener:
            for listener in self._listener[event]:
                listener(data)


class Up(Row):
    def __init__(self, event: Event, page: Page):
        super(Up, self).__init__(height=150, alignment=MainAxisAlignment.SPACE_BETWEEN)
        self.handlers = event
        self.text = TextField(
            label="nickname", value="xake_r777", on_submit=self.on_click_search
        )
        self.page = page
        self.theme = IconButton(icon="SUNNY", on_click=self.change_theme)
        self.search = ElevatedButton(
            icon="search", text="Найти", on_click=self.on_click_search
        )
        self.session = ElevatedButton(
            icon="update", text="Начать сессию", on_click=self.start_session
        )
        self.drop = Dropdown(on_change=self.drop_change)
        self.menu = PopupMenuButton()
        self.controls = [
            Column(
                [Row([self.theme, self.search, self.session]), self.menu, self.drop]
            ),
            self.text,
        ]
        self.handler()

    def start_session(self, e):
        if self.text.value:
            asyncio.run(PlayerInterface(name=self.text.value).reset())
            self.add_menu(self.text.value)

    def on_click_search(self, e):
        if self.text.value:
            self.handlers.emit("text_button", data=self.text.value)
            self.drop_list(self.text.value)
            self.add_menu(self.text.value)
            self.text.value = ""
            self.update()

    def drop_change(self, e):
        self.handlers.emit("period", data=e.control.value)

    def on_click_menu(self, e):
        self.handlers.emit(f"text_button", data=e.control.text)

    def add_menu(self, n):
        for item in self.menu.items:
            if item.text == n:
                return
        self.menu.items.append(PopupMenuItem(text=n, on_click=self.on_click_menu))
        self.update()

    def drop_list(self, n):
        self.drop.options.clear()
        self.drop.options = [
            dropdown.Option(text=i.get("data")) for i in All_General().get(name=n)
        ]
        self.update()

    def change_theme(self, e):
        self.page.theme_mode = "dark" if self.page.theme_mode == "light" else "light"
        self.page.update()

    def handler(self):
        pass


class Middle(Row):
    def __init__(self, event: Event, page: Page):
        super().__init__(
            alignment="center",
            expand=True,
        )
        self.controls = [
            Column(
                [
                    
                ],
                scroll="hidden",
                alignment="center",
                expand=True,
                horizontal_alignment="center",
            )
        ]

        self.event = event
        self.page = page
        self.handler()

    def crate_player(self, name):
        self.player = PlayerInterface(name=name)

    def build_content(self, name, trigger: str = None):
        self.controls[0].clean()
        self.crate_player(name=name)
        try:
            if trigger:
                data:list[dict] = asyncio.run(self.player.result_of_the_period(period=trigger))
            else:
                data:list[dict]= asyncio.run(self.player.results())
            val=data.pop(-1)
            self.text=Text(value=f'Сессия игрока {val.get('name')} длиться {val.get('time')}',size=24,
                           color='red')
            self.table = DataTable(border=border.all(3, "red"))
            keys = list(data[0].keys())[:-1]
            self.table.columns = [
                DataColumn(
                    Text(key),
                    on_sort=self.sorting,
                )
                for key in keys
            ]
            self.table.rows = [
                DataRow(
                    cells=[
                        DataCell(
                            Text(value.get(key, ""), color=value["color"].get(key))
                        )
                        for key in keys
                    ]
                )
                for value in data
            ]
            self.state = {x: True for x in range(len(keys))}
            self.controls[0].controls = [Row([self.table],alignment="center",
                        vertical_alignment="center",
                        scroll=True,)]#ERROR
        except Exception as e:
            print(e)
            data = data if "data" in locals() else None
            self.text = Text(value=(data or e),color='red',size=32)
        finally:
            self.controls[0].controls.insert(0,self.text)
            self.controls[0].controls.insert(0,Divider(height=5,color="transparent"))
            self.update()

    def sorting(self, e: DataColumnSortEvent):
        index = e.column_index
        ascending = self.state[index]
        row = self.table.rows[:-1]
        row = sorted(row, reverse=ascending, key=lambda x: x.cells[index].content.value)
        self.table.rows[:-1] = row
        self.state[index] = not ascending
        self.table.update()

    def period(self, period):
        self.build_content(name=self.player.name, trigger=period)

    def change_update(self, e):
        if hasattr(self, "player"):
            self.build_content(name=self.player.name)

    def handler(self):
        self.event.on("update", self.change_update)
        self.event.on("text_button", self.build_content)
        self.event.on("period", self.period)


class Down(Row):
    """Будет одна кнопка обновить которая запускает верхнюю секции
    та в свою очередь генерирует таблицу"""

    def __init__(
        self,
        event: Event,
    ):
        super().__init__(height=100, alignment="center")
        self.controls = [ElevatedButton(icon=icons.TIPS_AND_UPDATES_ROUNDED,text="Update", on_click=self.get_update)]
        self.handler = event

    def get_update(self, e: ControlEvent):
        self.handler.emit(event="update")


def main(page: Page):
    event = Event()
    up = Up(event, page=page)
    middle = Middle(event, page=page)
    down = Down(event)
    content = Container(Column([up, middle, down]), expand=True)
    return content
