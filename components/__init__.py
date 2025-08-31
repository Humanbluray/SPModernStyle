import flet as ft
from utils.couleurs import *
from translations.translations import languages
from utils.styles import drop_style, login_style
from services.supabase_client import supabase_client
from services.async_functions.students_functions import *
from utils.useful_functions import *


class MyButton(ft.ElevatedButton):
    def __init__(self, title: str, my_icon, my_width, click):
        super().__init__(
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=ft.border_radius.all(12)),
                bgcolor=ACCENT_PLUS_COLOR,
                color=ft.Colors.WHITE,
                padding=ft.padding.symmetric(horizontal=30, vertical=15),
            ),
            on_click=click, width=my_width, height=50, on_hover=self.hover_effect,
            elevation=0,
        )
        self.title = ft.Text(
            title.capitalize(), size=16, font_family="PPM",
            scale=ft.Scale(1), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_OUT_CUBIC),
        )
        self.my_icon = ft.Icon(
            my_icon, size=20, color="white", visible=False if my_icon is None else True,
            scale=ft.Scale(1), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_OUT_CUBIC),
        )
        self.content=ft.Row(
            controls=[
                self.my_icon,
                self.title
            ], alignment=ft.MainAxisAlignment.CENTER
        )

    def hover_effect(self, e):
        if e.data == 'true':
            self.title.scale =1.2
            self.my_icon.scale =1.2
            self.title.update()
            self.my_icon.update()
        else:
            self.title.scale = 1
            self.my_icon.scale = 1
            self.title.update()
            self.my_icon.update()


class OneStudent(ft.Container):
    def __init__(self, cp: object, infos: dict):
        super().__init__(
            padding=10, data=infos, border_radius=16,
            on_hover=self.effect_hover, on_click=self.open_edit_window
            # shadow=ft.BoxShadow(
            #     spread_radius=2,
            #     blur_radius=10,
            #     color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            # )
        )
        self.infos = infos
        self.cp = cp

        self.rep_container = ft.Container(
            alignment=ft.alignment.center, width=30, shape=ft.BoxShape.CIRCLE, bgcolor='red50',
            content=ft.Text('R', size=13, font_family='PEB', color='red700'),
             border=ft.border.all(1, 'red700'), visible=True if infos['repeater'] else False
        )

        self.content = ft.ListTile(
            leading=ft.CircleAvatar(
                background_image_src=infos['image_url'], radius=30
            ),
            title=ft.Text(
                f"{infos['student_name']} {infos['student_surname']}".upper(),
                size=16, font_family="PPB"
            ),
            subtitle=ft.Row(
                controls=[
                    ft.Text(
                        f"{infos['class_code']}", size=16, font_family='PPM'
                    ),
                    self.rep_container

                ]
            ),
            trailing=ft.PopupMenuButton(
                content=ft.Icon(ft.Icons.FORMAT_LIST_BULLETED, size=24, color='black'),
                bgcolor="white",
                items=[
                    ft.PopupMenuItem(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.CONTACT_PAGE, size=18, color='black'),
                                ft.Text(languages[self.cp.lang]['student file'].capitalize(), size=18, font_family="PPM")
                            ]
                        ), on_click=self.open_edit_window, data=infos
                    ),
                    ft.PopupMenuItem(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.ATTACH_MONEY, size=18, color='black'),
                                ft.Text(languages[self.cp.lang]['school fees'].capitalize(), size=18, font_family="PPM")
                            ]
                        ), on_click=self.open_school_fees_window, data=infos,
                    ),
                    ft.PopupMenuItem(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.EMERGENCY, size=18, color='black'),
                                ft.Text('discipline'.capitalize(), size=18, font_family="PPM")
                            ]
                        ), on_click=self.open_report_window, data=infos,
                    ),
                    ft.PopupMenuItem(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.FILE_PRESENT, size=18, color='black'),
                                ft.Text(languages[self.cp.lang]['print receipt'].capitalize(), size=18, font_family="PPM"),
                                ft.IconButton(
                                    ft.Icons.ATTACH_FILE, icon_size=18, icon_color='black', url=infos['receipt_url'],
                                    visible=True if infos['receipt_url'] else False
                                )
                            ]
                        ), on_click=None, data=infos,
                    )
                ]
            ),


        )

    def open_edit_window(self, e):
        self.cp.edit_id_student = e.control.data['student_id']

        resp = supabase_client.table("students").select('*').eq('id', e.control.data['student_id']).single().execute()

        self.cp.edit_nom.value = resp.data['name']
        self.cp.edit_prenom.value = resp.data['surname']
        self.cp.edit_sex.value = resp.data['gender']
        self.cp.edit_lieu.value = resp.data['birth_place']
        self.cp.edit_date.value = resp.data['birth_date']
        self.cp.edit_pere.value = resp.data['father']
        self.cp.edit_mere.value = resp.data['mother']
        self.cp.edit_contact.value = resp.data['contact']
        self.cp.edit_other.value = resp.data['other_contact']
        self.cp.edit_residence.value = resp.data['city']
        self.cp.edit_mat.value = resp.data['registration_number']
        self.cp.edit_image_url.value = resp.data['image_url']
        self.cp.image_preview.foreground_image_src = e.control.data['image_url'] if e.control.data['image_url'] is not None else ''
        self.cp.show_one_window(self.cp.ct_edit_student)

    async def load_fees_widgets(self, e):
        self.cp.show_one_window(self.cp.school_fees_window)
        access_token = self.cp.cp.page.client_storage.get('access_token')
        year_id = self.cp.cp.year_id

        all_fees_part = await get_fees_amount_by_year(access_token, year_id)
        total_to_pay = all_fees_part['fees_part_1'] + all_fees_part['fees_part_2'] + all_fees_part['fees_part_3'] + all_fees_part['registration']

        total_payments = await get_student_payments_for_active_year(
            access_token, e.control.data['student_id'], year_id
        )
        total_paid = sum(item['amount'] for item in total_payments)

        total_due = total_to_pay - total_paid
        self.cp.sc_student_id.value = e.control.data['student_id']

        if total_due > 0:
            self.cp.sc_amount_due.color = 'red'
            self.cp.status_icon.name = ft.Icons.INDETERMINATE_CHECK_BOX
            self.cp.status_icon.color = 'red'
            self.cp.status.value = languages[self.cp.lang]['on going']
            self.cp.status.color = 'red'
            self.cp.status_container.bgcolor = 'red50'
            self.cp.status_container.border = ft.border.all(1, 'red')
            self.cp.payment_container.visible = True

        else:
            self.cp.sc_amount_due.color = 'green'
            self.cp.status_icon.name = ft.Icons.CHECK_CIRCLE
            self.cp.status_icon.color = 'green'
            self.cp.status.value = languages[self.cp.lang]['sold out']
            self.cp.status.color = 'green'
            self.cp.status_container.bgcolor = 'green50'
            self.cp.status_container.border = ft.border.all(1, 'green')
            self.cp.payment_container.visible = False

        if total_paid < total_due:
            self.cp.sc_amount_paid.color = 'grey'
        else:
            self.cp.sc_amount_paid.color = 'green'

        self.cp.sc_amount_paid.value = add_separator(total_paid)
        self.cp.sc_amount_due.value = add_separator(total_due)
        self.cp.sc_amount_expected.value =  add_separator(total_to_pay)
        self.cp.sc_name.value = e.control.data['student_name']
        self.cp.sc_surname.value = e.control.data['student_surname']

        self.cp.sc_payment_table.rows.clear()

        for p, payment in enumerate(total_payments):
            line_color = ft.Colors.GREY_100 if p % 2 == 0 else ft.Colors.WHITE
            self.cp.sc_payment_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(payment['date'])[0:10])),
                        ft.DataCell(ft.Text(payment['part'])),
                        ft.DataCell(ft.Text(add_separator(payment['amount'])))
                    ],
                    color=line_color
                )
            )

        await self.cp.build_school_fees_container()

    def open_school_fees_window(self, e):
        self.cp.run_async_in_thread(self.load_fees_widgets(e))

    async def load_report_window_datas(self, e):
        self.cp.show_one_window(self.cp.report_window)
        year_id = self.cp.cp.year_id
        access_token = self.cp.cp.page.client_storage.get('access_token')
        active_sequence = self.cp.active_sequence.data

        self.cp.report_name.value = f"{self.infos['student_name']}"
        self.cp.report_surname.value = f"{self.infos['student_surname']}"
        self.cp.report_image.background_image_src = f"{self.infos['image_url']}"
        self.cp.report_class.value  = f"{self.infos['class_code']}"

        datas = await get_student_discipline_active_sequence(
            access_token, e.control.data['student_id'], year_id, active_sequence
        )

        self.cp.report_table.rows.clear()

        for d, data in enumerate(datas):
            for item in (
                    self.cp.count_unjustified, self.cp.count_justified, self.cp.count_warning, self.cp.count_ban,
                    self.cp.count_permanent_ban, self.cp.count_reprimand, self.cp.count_detention, self.cp.count_late,
            ):
                if data['type'] == item.data:
                    old_data = int(item.value)
                    new_data = old_data + data['quantity']
                    item.value = new_data

            line_color = ft.Colors.GREY_100 if d % 2 == 0 else ft.Colors.WHITE
            self.cp.report_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(data["sequence"])),
                        ft.DataCell(ft.Text(languages[self.cp.lang][data["type"]])),
                        ft.DataCell(ft.Text(data["quantity"])),
                        ft.DataCell(ft.Text(data["comments"])),
                    ], color=line_color
                ),
            )

        for item in (
                self.cp.count_unjustified, self.cp.count_justified, self.cp.count_warning, self.cp.count_ban,
                self.cp.count_permanent_ban, self.cp.count_reprimand, self.cp.count_detention, self.cp.count_late,
        ):
            if int(item.value) > 0:
                if item.data == "justified absence":
                    item.color = 'green'
                else:
                    item.color = "red"


        self.cp.build_discipline_report()

    def open_report_window(self, e):
        self.cp.run_async_in_thread(self.load_report_window_datas(e))

    def effect_hover(self, e):
        if e.data == 'true':
            self.bgcolor = MAIN_COLOR
            self.update()
        else:
            self.bgcolor = None
            self.update()


class MyTextButton(ft.TextButton):
    def __init__(self, title: str, click):
        super().__init__(
            content=ft.Row(
                [
                    ft.Text(title.capitalize(), size=16, font_family='PPM'),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=5,
            ), on_click=click,
            style=ft.ButtonStyle(
                bgcolor={
                    ft.ControlState.HOVERED: SECOND_COLOR,
                    ft.ControlState.DEFAULT: BASE_COLOR,
                },
                # Couleurs du texte par défaut et au survol
                color={
                    ft.ControlState.HOVERED: BASE_COLOR,
                    ft.ControlState.DEFAULT: ft.Colors.WHITE,
                },
            )

        )


class DateSelection(ft.Row):
    def __init__(self, cp):
        super().__init__()
        self.cp = cp
        self.day = ft.Dropdown(
            **drop_style, width=95, text_align=ft.TextAlign.RIGHT, menu_height=200,
            options=[ft.dropdown.Option(f"{i}") for i in range(1, 32)], hint_text=languages[self.cp.lang]['jj']
        )
        self.month = ft.Dropdown(
            **drop_style, width=95, text_align=ft.TextAlign.RIGHT, hint_text=languages[self.cp.lang]['mm'],
            menu_height=200,
            options=[ft.dropdown.Option(f"{i}") for i in range(1, 13)]
        )
        self.year = ft.TextField(
            **login_style,
            input_filter=ft.NumbersOnlyInputFilter(), width=80, text_align=ft.TextAlign.RIGHT,
        )
        self.controls=[
            ft.Row(
                controls=[
                    self.day, self.month, self.year
                ], spacing=3
            )
        ]
