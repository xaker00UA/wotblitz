from flet import *



class Up(Row):
    def __init__(self):
        self.text=TextField('text', on_submit=self.info)
        self.controls = [self.text]
    def info(self, e):
        data=self.text.value
        self.text.value=''
        return data



class Down(Row):
    def __init__(self):
        self.controls = [Text()]
def main(page: Page):
    Container(content=Column([Up,Down]))
