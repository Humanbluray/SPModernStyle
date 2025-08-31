from utils.couleurs import *


class ItemMenu(ft.Container):
    def __init__(self, title: str, my_icon: str, my_icon_2: str, visible:bool):
        super().__init__(
            shape=ft.BoxShape.RECTANGLE, visible=visible,
            padding=ft.padding.only(30, 10, 30, 10),
            on_hover=self.hover_ct,
            border_radius=12, scale=ft.Scale(1),
            animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN)
        )
        self.title = title
        self.my_icon = my_icon
        self.my_icon_2 = my_icon_2
        self.is_clicked = False

        self.visuel = ft.Icon(self.my_icon, size=20, color=ft.Colors.BLACK)
        self.visuel_2 = ft.Icon(self.my_icon_2, size=20, color=BASE_COLOR, visible=False)
        self.name = ft.Text(
            title.capitalize(),
            font_family="PPM", size=20,
            color=ft.Colors.BLACK87
        )
        self.name_2 = ft.Text(
            title.capitalize(), font_family="PPB", size=20,
            color='black',  # if BASE_COLOR == ft.Colors.AMBER else ft.Colors.WHITE,
            visible=False
        )
        self.content = ft.Row(
            controls=[ft.Row([self.visuel, self.visuel_2]), ft.Row([self.name_2, self.name])],
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

    def hover_ct(self, e):
        if e.data == "true":
            e.control.scale = 1.085
            if self.is_clicked:
                self.visuel.visible = False
                self.visuel_2.visible = True
                self.name.visible = False
                self.name_2.visible = True
                self.bgcolor = MAIN_COLOR
                self.update()
            else:
                self.visuel.visible = True
                self.visuel_2.visible = False
                self.name.visible = True
                self.name_2.visible = False
                self.bgcolor = None
                self.update()

        else:
            e.control.scale = 1
            if self.is_clicked:
                self.visuel.visible = False
                self.visuel_2.visible = True
                self.name.visible = False
                self.name_2.visible = True
                self.bgcolor = MAIN_COLOR
                self.update()
            else:
                self.visuel.visible = True
                self.visuel_2.visible = False
                self.name.visible = True
                self.name_2.visible = False
                self.bgcolor = None
                self.update()

        e.control.update()

    def set_is_clicked_true(self):
        self.visuel.visible = False
        self.visuel_2.visible = True
        self.name.visible = False
        self.name_2.visible = True
        self.bgcolor = MAIN_COLOR
        self.update()

    def set_is_clicked_false(self):
        self.visuel.visible = True
        self.visuel_2.visible = False
        self.name.visible = True
        self.name_2.visible = False
        self.bgcolor = None
        self.update()

