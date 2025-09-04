from components import MyButton, MyTextButton, BoxStudentNote
from utils.styles import *
from services.async_functions.notes_functions import *
from services.async_functions.general_functions import get_active_sequence
from translations.translations import languages


class Notes(ft.Container):
    def __init__(self, cp: object):
        super().__init__(
            expand=True, alignment=ft.alignment.center, bgcolor=MAIN_COLOR
        )
        self.cp = cp
        lang = self.cp.language
        self.lang = lang

        self.menu_button = ft.IconButton(
            ft.Icons.MENU, icon_size=24, icon_color='black',
            on_click=lambda e: self.cp.page.open(self.cp.drawer)
        )
        self.active_sequence = ft.Text(size=13, font_family='PPM')
        self.active_quarter = ft.Text(size=13, font_family='PPM')
        self.sequence_ct = ft.Container(
            padding=5, border_radius=16, border=ft.border.all(1, BASE_COLOR),
            alignment=ft.alignment.center,  # visible=False,
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED, size=16, color='black'),
                    self.active_sequence
                ]
            )
        )
        self.quarter_ct = ft.Container(
            padding=5, border_radius=16, border=ft.border.all(1, BASE_COLOR),
            alignment=ft.alignment.center,  # visible=False,
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CALENDAR_TODAY, size=16, color='black'),
                    self.active_quarter
                ]
            )
        )
        self.top_menu = ft.Container(
            padding=10, content=ft.Row(
                controls=[
                    ft.Row(
                        controls=[
                            self.menu_button,
                            ft.Row(
                                controls=[
                                    ft.Text(languages[self.lang]['menu notes'].capitalize(), size=24,
                                            font_family="PEB"),
                                ], spacing=0
                            )
                        ]
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("School", size=28, font_family="PEB", color=BASE_COLOR),
                            ft.Text("Pilot", size=28, font_family="PEB"),
                        ], spacing=0
                    ),
                    ft.Row([self.sequence_ct, self.quarter_ct])
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        )
