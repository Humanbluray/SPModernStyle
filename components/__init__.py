import flet as ft
import flet.core.alignment

from utils.couleurs import *
from translations.translations import languages
from utils.styles import drop_style, login_style, outline_style
from services.supabase_client import supabase_client
from services.async_functions.students_functions import *
from services.async_functions.teachers_functions import *
from utils.useful_functions import *
import threading

day_color = {
    'day 1' : {'fg_color': ft.Colors.DEEP_ORANGE, 'bg_color': ft.Colors.DEEP_ORANGE_50},
    'day 2' : {'fg_color': ft.Colors.TEAL, 'bg_color': ft.Colors.TEAL_50},
    'day 3' : {'fg_color': ft.Colors.INDIGO, 'bg_color': ft.Colors.INDIGO_50},
    'day 4' : {'fg_color': ft.Colors.PINK, 'bg_color': ft.Colors.PINK_50},
    'day 5' : {'fg_color': ft.Colors.BROWN, 'bg_color': ft.Colors.BROWN_50},
}
day_short_name = {
    'day 1' : {'en': 'MON', 'fr': 'LUN'},
    'day 2' : {'en': 'TUE', 'fr': 'MAR'},
    'day 3' : {'en': 'WED', 'fr': 'MER'},
    'day 4' : {'en': 'THU', 'fr': 'JEU'},
    'day 5' : {'en': 'FRI', 'fr': 'VEN'},
}


class MyMiniIcon(ft.Container):
    def __init__(self, icon: str, text: str, color:str, data, click):
        super().__init__(
            border_radius=6, alignment=ft.alignment.center,
            padding=5,
            content=ft.Icon(name=icon, size=24, color=color), on_click=click,
            on_hover=self.hover_effect, tooltip=text, data=data,
            scale=ft.Scale(1), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN)
        )

    def hover_effect(self, e):
        if e.data == "true":
            self.scale = 1.1
        else:
            self.scale = 1
        self.update()


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


class OneStudent(ft.Card):
    def __init__(self, cp: object, infos: dict):
        super().__init__(
            elevation=10, shape=ft.RoundedRectangleBorder(radius=16)
        )
        self.infos = infos
        self.cp = cp

        self.rep_container = ft.Container(
            alignment=ft.alignment.center, width=30, shape=ft.BoxShape.CIRCLE, bgcolor='red50',
            content=ft.Text('R', size=13, font_family='PEB', color='red700'),
             border=ft.border.all(1, 'red700'), visible=True if infos['repeater'] else False
        )
        self.new_container = ft.Container(
            alignment=ft.alignment.center, width=30, shape=ft.BoxShape.CIRCLE, bgcolor='teal50',
            content=ft.Text('N', size=13, font_family='PEB', color='teal700'),
             border=ft.border.all(1, 'teal700'), visible=True if not infos['repeater'] else False
        )
        self.ct = ft.Container(
            padding=10, border_radius=16, bgcolor='white', width=260, height=300,
            on_hover=self.effect_hover,
            scale=ft.Scale(1), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            content=ft.Column(
                controls=[
                    ft.Stack(
                        alignment=ft.alignment.bottom_right,
                        controls=[
                            ft.CircleAvatar(radius=30, foreground_image_src=infos['image_url']),
                            ft.Icon(
                                ft.Icons.CIRCLE, size=10,
                                color='pink' if infos['student_gender'] == "F" else 'blue'
                            )
                        ]
                    ),
                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                    ft.Column(
                        controls=[
                            ft.Text(
                                f"{infos['student_name']}".upper(), size=16, font_family='PPB',
                            ),
                            ft.Text(
                                f"{infos['student_surname']}", size=14, font_family="PPR"
                            )
                        ], spacing=0,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    ft.Row(
                        controls=[
                            ft.Icon("roofing", size=24, color="grey"),
                            ft.Text(f"{infos['class_code']}", size=16, font_family="PPM"),
                            ft.Row([self.rep_container, self.new_container]),
                        ], alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Divider(height=1, thickness=1),
                    ft.Row(
                        controls=[
                            ft.Text('Actions', size=16, font_family='PPM'),
                            ft.PopupMenuButton(
                                content=ft.Icon(ft.Icons.FORMAT_LIST_BULLETED, size=24, color='black'),
                                bgcolor="white",
                                items=[
                                    ft.PopupMenuItem(
                                        content=ft.Row(
                                            controls=[
                                                ft.Icon(ft.Icons.CONTACT_PAGE, size=18, color='black'),
                                                ft.Text(languages[self.cp.lang]['student file'].capitalize(), size=18,
                                                        font_family="PPM")
                                            ]
                                        ), on_click=self.open_edit_window, data=infos
                                    ),
                                    ft.PopupMenuItem(
                                        content=ft.Row(
                                            controls=[
                                                ft.Icon(ft.Icons.ATTACH_MONEY, size=18, color='black'),
                                                ft.Text(languages[self.cp.lang]['school fees'].capitalize(), size=18,
                                                        font_family="PPM")
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
                                                ft.Text(languages[self.cp.lang]['print receipt'].capitalize(), size=18,
                                                        font_family="PPM"),
                                                ft.IconButton(
                                                    ft.Icons.ATTACH_FILE, icon_size=18, icon_color='black',
                                                    url=infos['receipt_url'],
                                                    visible=True if infos['receipt_url'] else False
                                                )
                                            ]
                                        ), on_click=None, data=infos,
                                    )
                                ]
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.content = self.ct

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
            self.ct.scale = 1.1
            self.ct.update()
        else:
            self.ct.scale = 1
            self.ct.update()


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


class OneClass(ft.Container):
    def __init__(self, cp: object, infos: dict):
        super().__init__(
            padding=10, data=infos, border_radius=16,  # margin=10,
            on_hover=None, on_click=None,
        )
        self.infos = infos
        self.cp = cp

        self.content = ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.SCHOOL if infos['is_examination_class'] else ft.Icons.ACCOUNT_BALANCE_OUTLINED
                                ),
                                ft.Text(f"{infos['code']}", size=16, font_family="PPM")
                            ]
                        ),
                        ft.VerticalDivider(10, 1,),
                        ft.Text(f"{infos['head_teacher_name']} {infos['head_teacher_surname']}", size=16, font_family="PPM")
                    ]
                ),
                ft.IconButton(
                    ft.Icons.FORMAT_LIST_BULLETED_OUTLINED, icon_size=24, icon_color='black'
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )


class SingleOption(ft.Container):
    def __init__(self, cp: object, name: str):
        super().__init__(
            bgcolor='grey100',
            alignment=ft.alignment.center, border_radius=7, on_click=self.set_status,
            padding=ft.padding.only(5, 3, 5, 3)
        )
        self.cp = cp
        self.name = name
        self.selected: bool = False
        self.element = ft.Text(name, size=13, font_family='PPM', color='black54')
        self.content=self.element

    def set_status(self, e):
        if self.selected:
            self.selected = False
            self.bgcolor = 'grey100'
            self.element.color = 'black54'
            self.element.update()
            self.cp.count_subject.value = int(self.cp.count_subject.value) - 1 if int(self.cp.count_subject.value) > 0 else 0
            self.cp.count_subject.update()
            self.update()
        else:
            self.selected = True
            self.bgcolor = EMERALD_GREEN
            self.element.color = 'white'
            self.element.update()
            self.cp.count_subject.value = int(self.cp.count_subject.value) + 1
            self.cp.count_subject.update()
            self.update()

    def set_initial(self):
        self.selected = True
        self.bgcolor = 'grey100'
        self.element.color = 'black54'
        self.element.update()
        self.update()

    def set_selected(self):
        self.selected = True
        self.bgcolor = EMERALD_GREEN
        self.element.color = 'white'
        self.element.update()
        self.update()


class EditSingleOption(ft.Container):
    def __init__(self, cp: object, name: str):
        super().__init__(
            bgcolor='#f0f0f6',
            alignment=ft.alignment.center, border_radius=7, on_click=self.set_status,
            padding=ft.padding.only(5, 3, 5, 3)
        )
        self.cp = cp
        self.name = name
        self.selected: bool = False
        self.element = ft.Text(name, size=13, font_family='PPM', color='black')
        self.content = self.element

    def set_status(self, e):
        if self.selected:
            self.selected = False
            self.bgcolor = '#f0f0f6'
            self.element.color = 'black'
            self.element.update()
            self.cp.edit_count_subject.value = int(self.cp.edit_count_subject.value) - 1 if int(
                self.cp.edit_count_subject.value) > 0 else 0
            self.cp.edit_count_subject.update()
            self.update()
        else:
            self.selected = True
            self.bgcolor = EMERALD_GREEN
            self.element.color = 'white'
            self.element.update()
            self.cp.edit_count_subject.value = int(self.cp.edit_count_subject.value) + 1
            self.cp.edit_count_subject.update()
            self.update()

    def set_initial(self):
        self.selected = False
        self.bgcolor = '#f0f0f6'
        self.element.color = 'black'
        self.element.update()
        self.update()

    def set_selected(self):
        self.selected = True
        self.bgcolor = EMERALD_GREEN
        self.element.color = 'white'
        self.element.update()
        self.update()


class SlotCard(ft.Container):
    def __init__(self, cp: object, infos: dict):
        super().__init__(
            border_radius=16, bgcolor = day_color[infos['day']]['bg_color'],
            # border=ft.border.all(1, 'black')
        )
        self.cp = cp
        self.infos = infos
        self.delete_bt = MyMiniIcon('delete_outlined', languages[self.cp.lang]['free slot'], "black", self.infos, self.free_affectation)
        self.assign_bt = MyMiniIcon(ft.Icons.ADD, languages[self.cp.lang]['assign slot'], "black", self.infos, self.add_affectation)
        self.check = ft.Checkbox()
        role = self.cp.cp.page.client_storage.get('role')

        if infos['status']:
            if role not in ['principal', 'préfet']:
                self.status_icon = ft.Icons.INDETERMINATE_CHECK_BOX_OUTLINED
                self.status_color = 'red'
                self.delete_bt.visible = False
                self.assign_bt.visible = False
                self.check.disabled = True
                self.visible_bgcolor = day_color[infos['day']]['fg_color']

            else:
                self.status_icon = ft.Icons.INDETERMINATE_CHECK_BOX_OUTLINED
                self.status_color = 'red'
                self.delete_bt.visible = True
                self.assign_bt.visible = False
                self.check.disabled = True
                self.visible_bgcolor = day_color[infos['day']]['fg_color']

        else:
            if role not in ['principal', 'préfet']:
                self.status_icon = ft.Icons.CHECK_CIRCLE
                self.status_color = 'green'
                self.delete_bt.visible = False
                self.assign_bt.visible = False
                self.check.disabled = False
                self.visible_bgcolor = 'white'

            else:
                self.status_icon = ft.Icons.CHECK_CIRCLE
                self.status_color = 'green'
                self.delete_bt.visible = False
                self.assign_bt.visible = True
                self.check.disabled = False
                self.visible_bgcolor = 'white'

        self.prof = "" if infos['teacher_id'] is None else infos['teacher_name']
        self.mat = "" if infos['subject_id'] is None else infos['subject_short_name']
        self.class_code = "" if infos['class_id'] is None else infos['class_code']

        self.content = ft.Container(
            border_radius=16, padding=10, width=210,
            content=ft.Column(
                controls=[
                    ft.Container(
                        padding=5, border_radius=8, bgcolor='white', content=ft.Row(
                            controls=[
                                ft.Icon(self.status_icon, size=18, color=self.status_color),
                                ft.Text(languages[self.cp.lang][infos['day']].upper(), size=14, font_family="PPM"),
                            ], alignment=ft.MainAxisAlignment.CENTER
                        )
                    ),
                    ft.Row(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon('timer_outlined', size=18, color='black45'),
                                    ft.Text(infos['slot'], font_family='PPM', size=14),
                                ]
                            ),
                            ft.Row([self.assign_bt, self.delete_bt])
                        ], alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Container(
                        padding=8, border_radius=8, expand=True,
                        bgcolor=self.visible_bgcolor,
                        content=ft.Row(
                            controls=[
                                ft.Text(f"{self.mat} - {self.class_code}", size=14, font_family="PPL", color="white"),

                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        ), tooltip=f"{languages[self.cp.lang]['day']}: {languages[self.cp.lang][infos['day']]}\n"
                                   f"{languages[self.cp.lang]['slot']}: {infos['slot']}\n"
                                   f"{languages[self.cp.lang]['class']}: {infos['class_code']}\n"
                                   f"{languages[self.cp.lang]['subject']}: {infos['subject_name']}\n"
                                   f"{languages[self.cp.lang]['teacher']}: {infos['teacher_name']}\n"
                    ),
                ]
            )
        )

    @staticmethod
    def run_async_in_thread(coro):
        def runner():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(coro)
            loop.close()

        thread = threading.Thread(target=runner)
        thread.start()

    def add_affectation(self, e):
        self.cp.new_prof_id.value = self.cp.prof_id.value

        self.cp.new_day.value = e.control.data['day']
        self.cp.new_day_display.value = languages[self.cp.lang][e.control.data['day']]
        self.cp.new_slot.value = e.control.data['slot']
        self.cp.new_day.update()
        self.cp.new_day_display.update()
        self.cp.new_slot.update()

        self.cp.new_affectation_window.scale = 1
        self.cp.new_affectation_window.update()
        self.cp.main_window.opacity = 0.2
        self.cp.main_window.disabled = True
        self.cp.main_window.update()
        self.cp.cp.cp.left_menu.opacity = 0.2
        self.cp.cp.cp.left_menu.disabled = True
        self.cp.cp.cp.left_menu.update()

    async def delete_affectation(self, e):
        role = self.cp.cp.page.client_storage.get('role')
        print(role)

        if role in ['principal', 'préfet']:
            # supprimer affectation
            resp = supabase_client.table('affectations').update(
                {
                    "teacher_id": None, "subject_id": None
                }
            ).eq("day", self.infos['day']).eq('slot', self.infos['slot']).eq("year_id", self.infos['year_id']).execute()

            self.cp.cp.cp.box.title.value = languages[self.cp.lang]['success']
            self.cp.cp.cp.message.value = languages[self.cp.lang]['free time slot']
            self.cp.cp.icon_message.name = ft.Icons.CHECK_CIRCLE
            self.cp.cp.icon_message.color = ft.Colors.LIGHT_GREEN
            self.cp.cp.cp.box.open = True
            self.cp.cp.cp.box.update()

            await self.cp.refresh_view()

        else:
            self.cp.cp.cp.box.title.value = languages[self.cp.lang]['error']
            self.cp.cp.cp.message.value = languages[self.cp.lang]['error rights']
            self.cp.cp.icon_message.name = ft.Icons.INFO_SHARP
            self.cp.cp.icon_message.color = ft.Colors.RED
            self.cp.cp.cp.box.open = True
            self.cp.cp.cp.box.update()

    def free_affectation(self, e):
        self.run_async_in_thread(self.delete_affectation(e))


class SlotCardRoom(ft.Container):
    def __init__(self, cp: object, infos: dict):
        super().__init__(
            border_radius=16, bgcolor = day_color[infos['day']]['bg_color'],
            # border=ft.border.all(1, 'black')
        )
        self.cp = cp
        self.infos = infos
        self.delete_bt = MyMiniIcon('delete_outlined', languages[self.cp.lang]['free slot'], "black", self.infos, self.delete_affectation)
        self.assign_bt = MyMiniIcon(ft.Icons.ADD, languages[self.cp.lang]['assign slot'], "black", self.infos, self.add_affectation)
        self.check = ft.Checkbox()
        role = self.cp.cp.page.client_storage.get('role')

        if infos['status']:
            if role not in ['principal', 'préfet']:
                self.status_icon = ft.Icons.INDETERMINATE_CHECK_BOX_OUTLINED
                self.status_color = 'red'
                self.delete_bt.visible = False
                self.assign_bt.visible = False
                self.check.disabled = True
                self.visible_bgcolor = day_color[infos['day']]['fg_color']

            else:
                self.status_icon = ft.Icons.INDETERMINATE_CHECK_BOX_OUTLINED
                self.status_color = 'red'
                self.delete_bt.visible = True
                self.assign_bt.visible = False
                self.check.disabled = True
                self.visible_bgcolor = day_color[infos['day']]['fg_color']

        else:
            if role not in ['principal', 'préfet']:
                self.status_icon = ft.Icons.CHECK_CIRCLE
                self.status_color = 'green'
                self.delete_bt.visible = False
                self.assign_bt.visible = False
                self.check.disabled = False
                self.visible_bgcolor = 'white'

            else:
                self.status_icon = ft.Icons.CHECK_CIRCLE
                self.status_color = 'green'
                self.delete_bt.visible = False
                self.assign_bt.visible = True
                self.check.disabled = False
                self.visible_bgcolor = 'white'

        self.prof = "" if infos['teacher_id'] is None else infos['teacher_name']
        self.mat = "" if infos['subject_id'] is None else infos['subject_short_name']
        self.class_code = "" if infos['class_id'] is None else infos['class_code']

        self.content = ft.Container(
            border_radius=16, padding=10, width=190,
            content=ft.Column(
                controls=[
                    ft.Container(
                        padding=5, border_radius=8, bgcolor='white', content=ft.Row(
                            controls=[
                                ft.Icon(self.status_icon, size=18, color=self.status_color),
                                ft.Text(languages[self.cp.lang][infos['day']].upper(), size=14, font_family="PPM"),
                            ], alignment=ft.MainAxisAlignment.CENTER
                        )
                    ),
                    ft.Row(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon('timer_outlined', size=18, color='black45'),
                                    ft.Text(infos['slot'], font_family='PPM', size=14),
                                ]
                            ),
                            ft.Row([self.assign_bt, self.delete_bt])
                        ], alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Container(
                        padding=8, border_radius=8, expand=True,
                        bgcolor=self.visible_bgcolor,
                        content=ft.Row(
                            controls=[
                                ft.Text(f"{self.mat} - {self.prof}", size=14, font_family="PPL", color="white"),

                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        tooltip=f"{languages[self.cp.lang]['day']}: {languages[self.cp.lang][infos['day']]}\n"
                                   f"{languages[self.cp.lang]['slot']}: {infos['slot']}\n"
                                   f"{languages[self.cp.lang]['class']}: {infos['class_code']}\n"
                                   f"{languages[self.cp.lang]['subject']}: {infos['subject_name']}\n"
                                   f"{languages[self.cp.lang]['teacher']}: {infos['teacher_name']}\n"
                    ),
                ]
            )
        )

    @staticmethod
    def run_async_in_thread(coro):
        def runner():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(coro)
            loop.close()

        thread = threading.Thread(target=runner)
        thread.start()

    def add_affectation(self, e):
        role = self.cp.cp.page.client_storage.get('role')

        if role in ['principal', 'préfet']:
            self.cp.new_affectation_id = e.control.data['id']
            self.cp.new_day.value = e.control.data['day']
            self.cp.new_day_display.value = languages[self.cp.lang][e.control.data['day']]
            self.cp.new_slot.value = e.control.data['slot']
            self.cp.new_day.update()
            self.cp.new_day_display.update()
            self.cp.new_slot.update()

            self.cp.new_affectation_window.scale = 1
            self.cp.new_affectation_window.update()
            self.cp.main_window.opacity = 0.2
            self.cp.main_window.disabled = True
            self.cp.main_window.update()
            self.cp.cp.cp.left_menu.opacity = 0.2
            self.cp.cp.cp.left_menu.disabled = True
            self.cp.cp.cp.left_menu.update()

        else:
            self.cp.cp.cp.box.title.value = languages[self.cp.lang]['error']
            self.cp.cp.cp.message.value = languages[self.cp.lang]['error rights']
            self.cp.cp.icon_message.name = ft.Icons.INFO_SHARP
            self.cp.cp.icon_message.color = ft.Colors.RED
            self.cp.cp.cp.box.open = True
            self.cp.cp.cp.box.update()



    def delete_affectation(self, e):
        role = self.cp.cp.page.client_storage.get('role')

        if role in ['principal', 'préfet']:
            # supprimer affectation
            resp = supabase_client.table('affectations').update(
                {
                    "teacher_id": None, "subject_id": None
                }
            ).eq('id', self.infos['id']).execute()

            self.cp.cp.cp.box.title.value = languages[self.cp.lang]['success']
            self.cp.cp.cp.message.value = languages[self.cp.lang]['free time slot']
            self.cp.cp.icon_message.name = ft.Icons.CHECK_CIRCLE
            self.cp.cp.icon_message.color = ft.Colors.LIGHT_GREEN
            self.cp.cp.cp.box.open = True
            self.cp.cp.cp.box.update()

            self.cp.refresh_view()

        else:
            self.cp.cp.cp.box.title.value = languages[self.cp.lang]['error']
            self.cp.cp.cp.message.value = languages[self.cp.lang]['error rights']
            self.cp.cp.icon_message.name = ft.Icons.INFO_SHARP
            self.cp.cp.icon_message.color = ft.Colors.RED
            self.cp.cp.cp.box.open = True
            self.cp.cp.cp.box.update()


class BoxStudentNote(ft.Container):
    def __init__(self, infos: dict):
        super().__init__(
            padding=ft.padding.only(10, 5, 10, 5), data=infos,
        )
        self.check = ft.Icon(size=16)
        self.infos = infos
        self.my_note = ft.TextField(
            **login_style, width=70,
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9.]", replacement_string=""),
            text_align=ft.TextAlign.RIGHT, on_blur=self.on_note_change
        )
        self.my_name = ft.Text(f"{infos['name']} {infos['surname']}".upper(), size=13, font_family='PPM', data=infos)
        self.content = ft.Row(
            controls=[
                self.my_name,
                ft.Row([self.my_note, self.check], spacing=2)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

    def on_note_change(self, e):
        if float(self.my_note.value) > 20:
            self.check.name = ft.Icons.DANGEROUS
            self.check.color = 'red'

        elif self.my_note.value is None:
            pass

        else:
            self.check.name = ft.Icons.CHECK_CIRCLE
            self.check.color = ft.Colors.LIGHT_GREEN

        self.check.update()


class OneTeacher(ft.Card):
    def __init__(self, cp: object, infos: dict):
        super().__init__(
            elevation=10, shape=ft.RoundedRectangleBorder(radius=16),
            scale=ft.Scale(1), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_OUT_EXPO)
        )
        self.cp = cp
        self.infos = infos

        if self.infos['is_head_teacher']:
            assign_icon = ft.Icons.ASSIGNMENT_IND
            assign_color = ft.Colors.BLACK
        else:
            assign_icon = ft.Icons.PERSON
            assign_color = ft.Colors.GREY

        gender_icon = "man" if infos['gender'] == 'M' else "woman"
        gender_color = "blue" if infos['gender'] == 'M' else "pink"

        pay = infos['pay'] if infos['pay'] else '*****'


        self.content = ft.Container(
            border_radius=16, bgcolor='white', on_click=self.open_edit_teacher_window,
            width=220, height=260, padding=ft.padding.only(10, 20, 10, 20),
            content=ft.Column(
                controls=[
                    ft.CircleAvatar(radius=30),
                    ft.Column(
                        controls=[
                            ft.Text(
                                f"{infos['name']}", size=16, font_family='PPM',
                            ),
                            ft.Text(
                                f"{infos['surname']}", size=14, font_family="PPR"
                            )
                        ], spacing=0,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    ft.Divider(height=1, thickness=1),
                    ft.Row(
                        controls=[
                            MyMiniIcon('edit_outlined', '', 'black', infos, self.open_edit_teacher_window),
                            MyMiniIcon(
                                'calendar_month', '', 'black', infos,
                                self.open_schedule_window
                            )
                        ], alignment=ft.MainAxisAlignment.END
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

    def effect_hover(self, e):
        if e.data == 'true':
            self.scale = 1.1
            self.update()
        else:
            self.scale = 1
            self.update()

    async def load_schedule(self, e):
        self.cp.table_schedule.rows.clear()
        self.cp.cp.page.update()
        self.cp.show_one_window(self.cp.schedule_window)

        access_token = self.cp.cp.page.client_storage.get('access_token')
        time_table = await get_teacher_affectations(self.infos['id'], access_token)

        count_classes: set = set()

        for item in time_table:
            count_classes.add(item['class_code'])

        self.cp.nb_classes.value = len(count_classes)
        self.cp.sc_head_class.value = await get_head_class_code_by_teacher_id(
            access_token, self.infos['id'], self.cp.cp.year_id
        )
        self.cp.nb_hours.value = len(time_table)

        if not time_table:
            pass

        else:
            for d, data in enumerate(time_table):
                line_color = ft.Colors.GREY_100 if d % 2 == 0 else ft.Colors.WHITE
                self.cp.table_schedule.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(languages[self.cp.lang][data['day']])),
                            ft.DataCell(ft.Text(data['slot'])),
                            ft.DataCell(ft.Text(data['class_code'])),
                            ft.DataCell(ft.Text(data['subject_name'].upper()))
                        ], color=line_color
                    )
                )

        self.cp.build_schedule_view()

    def open_schedule_window(self, e):
        self.cp.run_async_in_thread(self.load_schedule(e))

    def open_edit_teacher_window(self, e):

        role = self.cp.cp.page.client_storage.get('role')

        if role not in ['admin', 'principal']:
            self.cp.cp.box.title.value = languages[self.lang]['error']
            self.cp.cp.message.value = languages[self.lang]['error rights']
            self.cp.cp.box.open = True
            self.cp.cp.box.update()
        else:
            self.cp.edit_name.value = self.infos['name']
            self.cp.edit_gender.value = self.infos['gender']
            self.cp.edit_surname.value = self.infos['surname']
            self.cp.edit_uid.value = self.infos['id']
            self.cp.edit_pay.value = self.infos['pay'] if role == 'principal' else '*****'
            self.cp.edit_pay.read_only = True if role == 'admin' else False
            self.cp.edit_contact.value = self.infos['contact']
            self.cp.edit_count_subject.value = len(self.infos['subjects']) if self.infos['subjects'] else '0'

            if not self.infos['subjects']:
                pass
            else:
                for item, subject in enumerate(self.infos['subjects']):
                    if item == 0:
                        self.cp.edit_subject.value = self.cp.edit_subject.value + f"{subject}"
                    else:
                        self.cp.edit_subject.value = self.cp.edit_subject.value + '; ' + f"{subject}"

                for item in self.cp.edit_select_subjects.controls[:]:
                    if item.name in self.infos['subjects']:
                        item.set_selected()

            self.cp.show_one_window(self.cp.edit_teacher_window)

    def close_edit_teacher_window(self, e):
        for item in self.cp.edit_select_subjects.controls[:]:
            item.set_initial()

        self.cp.edit_name.value = None
        self.cp.edit_surname.value = None
        self.cp.edit_uid.value = None
        self.cp.edit_pay.value = None
        self.cp.edit_pay.read_only = None
        self.cp.edit_contact.value = None
        self.cp.edit_count_subject.value = None
        self.cp.edit_subject.value = None

        self.cp.hide_one_window(self.cp.edit_teacher_window)








