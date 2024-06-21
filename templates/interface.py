from flet import *


class Theme_Button(IconButton):
    def __init__(self, icon: str, page: Page):
        super().__init__(icon=icon)
        self.on_click = self.theme
        self.page: Page = page
        print(type(page))

    def theme(self, e):
        self.page.theme_mode = "dark" if self.page.theme_mode == "light" else "light"
        self.page.update()


class Text_Field(TextField):
    def __init__(self, text: str):
        super().__init__(label=text, width=150, height=50)
        self.on_submit = self.get_info

    def get_info(self, *args):
        res = self.value
        print(res)
        self.value = ""
        # self.update()
        return res
