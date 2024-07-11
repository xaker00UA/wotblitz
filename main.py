from app.utils import timer
import logging
from flet import *
from templates import *

logger = logging.getLogger()
filename = f"log\\{logger.name}.log"
handler = logging.FileHandler(filename=filename, encoding="utf-8")
handler.setLevel(logging.INFO)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s]-%(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
    handlers=[handler],
)


def main(page: Page):
    page.theme_mode = "dark"
    page.title = "Статистика"
    page.adaptive = True
    pages = {
        "page1": page1.main(page),
        "page2": page2.main(page),
        "page3": page3.main(
            page
        ),  # Возможно стоит добавить настройки приложения пока не работает
    }

    def nav(e):
        if not page.navigation_bar.disabled:
            index = page.navigation_bar.selected_index
            page.clean()
            if index == 0:
                page.add(pages["page1"])
            elif index == 1:
                page.add(pages["page2"])
            elif index == 2:
                page.add(pages["page3"])

    page.navigation_bar = NavigationBar(
        destinations=[
            NavigationDestination(
                icon=icons.VERIFIED_USER_OUTLINED,
                selected_icon=icons.VERIFIED_USER_ROUNDED,
                label="Player",
            ),
            NavigationDestination(
                icon=icons.SUPERVISED_USER_CIRCLE_OUTLINED,
                selected_icon=icons.SUPERVISED_USER_CIRCLE_ROUNDED,
                label="Clans",
            ),
            NavigationDestination(
                icon=icons.SETTINGS_OUTLINED,
                selected_icon=icons.SETTINGS,
                label="Settings",
            ),
        ],
        on_change=nav,
    )
    page.add(pages["page3"])


if __name__ == "__main__":
    app(target=main)
