from components import MyButton, SingleOption, EditSingleOption, MyTextButton, MyMiniIcon, OneTeacher
from utils.styles import drop_style, datatable_style, login_style, ct_style, intern_ct_style
from utils.couleurs import *
from translations.translations import languages
import os, mimetypes, asyncio, threading, json
from services.async_functions.teachers_functions import *
from services.async_functions.general_functions import *
from utils.useful_functions import add_separator, format_number


class Teachers(ft.Container):
    def __init__(self, cp: object):
        super().__init__(
            expand=True, alignment=ft.alignment.center, bgcolor=MAIN_COLOR
        )
        # parent container (Home) ___________________________________________________________
        self.cp = cp
        lang = self.cp.language
        self.lang = lang
        # main window...
        self.menu_button = ft.IconButton(
            ft.Icons.MENU, icon_size=24, icon_color='black',
            on_click=lambda e: self.cp.page.open(self.cp.drawer)
        )
        self.search = ft.TextField(
            **login_style, prefix_icon='search', width=300, on_change=self.filter_datas
        )
        self.table = ft.GridView(
            expand=True,
            max_extent=250,
            child_aspect_ratio=0.7,
            spacing=15,
            run_spacing=15
        )

        self.active_sequence = ft.Text(size=13, font_family='PPM')
        self.active_quarter = ft.Text(size=13, font_family='PPM')
        self.sequence_ct = ft.Container(
            padding=5, border_radius=10, border=ft.border.all(1, BASE_COLOR),
            alignment=ft.alignment.center,  # visible=False,
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED, size=16, color='black'),
                    self.active_sequence
                ]
            )
        )
        self.quarter_ct = ft.Container(
            padding=5, border_radius=10, border=ft.border.all(1, BASE_COLOR),
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
                                    ft.Text(languages[lang]['menu teachers'].capitalize(), size=24, font_family="PEB"),
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
        self.search = ft.TextField(
            **login_style, prefix_icon="search", width=300,
            on_change=self.on_search_change
        )

        self.main_window = ft.Container(
            expand=True, padding=20, border_radius=16,
            content=ft.Column(
                controls=[
                    self.top_menu,
                    ft.Row(
                        controls=[
                            ft.Row(
                                controls=[
                                    MyTextButton(languages[lang]['new teacher'], self.open_new_teacher_window),
                                    MyTextButton(languages[lang]['assign head'], self.open_head_teacher_window),
                                ]
                            ),
                            self.search
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Container(
                        padding=10, border_radius=16,
                        expand=True, content=ft.ListView(
                            expand=True, controls=[self.table]
                        )
                    )
                ]
            )
        )

        # New teacher window ____________________________________________________________________
        self.new_uid = ft.TextField(
            **login_style, width=500, prefix_icon=ft.Icons.CREDIT_CARD
        )
        self.new_name = ft.TextField(
            **login_style, prefix_icon="person_outlined", width=300, label=languages[lang]['name']
        )
        self.new_surname = ft.TextField(
            **login_style, prefix_icon="person_outlined", width=300, label=languages[lang]['surname']
        )
        self.new_gender = ft.Dropdown(
            **drop_style, label=languages[lang]['gender'],
            prefix_icon=ft.Icons.WC_OUTLINED, options=[
                ft.dropdown.Option(gender) for gender in ['M', 'F']
            ], width=180
        )
        self.new_pay = ft.TextField(
            **login_style, width=180, prefix_icon='monetization_on_outlined', value='0', read_only=True,
            input_filter=ft.NumbersOnlyInputFilter(), label=languages[lang]['hourly load']
        )
        self.new_contact = ft.TextField(
            **login_style, prefix_icon=ft.Icons.PHONE_ANDROID_OUTLINED, width=200, prefix_text="+237 ",
            input_filter=ft.NumbersOnlyInputFilter(), label=languages[lang]['contact']
        )
        self.new_subjects = ft.GridView(
            expand=True,
            max_extent=120,  # largeur max par cellule (laisser assez pour le padding)
            child_aspect_ratio=4,  # largeur / hauteur
            spacing=10,
            run_spacing=10,
        )
        self.count_subject = ft.Text('0', size=13, font_family='PPB')
        self.new_teacher_window = ft.Container(
            **ct_style,
            content=ft.Container(
                **intern_ct_style, width=700,  # height=700,
                content=ft.Column(
                    expand=True, scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20,
                            border=ft.border.only(bottom=ft.BorderSide(1, MAIN_COLOR)),
                            border_radius=ft.border_radius.only(top_left=8, top_right=8),
                            content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['new teacher'], size=20, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=MAIN_COLOR, scale=0.7,
                                        on_click=self.close_new_teacher_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(top=ft.BorderSide(1, MAIN_COLOR)),
                            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True,
                            content=ft.Column(
                                scroll=ft.ScrollMode.AUTO,
                                controls=[
                                    self.new_uid,
                                    ft.Row(controls=[self.new_name, self.new_surname]),
                                    ft.Row(controls=[self.new_gender, self.new_contact, self.new_pay]),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Row(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Text(languages[lang]['subjects taught'].upper(), size=16,
                                                            font_family='PPB'),
                                                    ft.Text(f"({languages[lang]['click to select']})", size=16,
                                                            font_family='PPM', color='grey'),
                                                ]
                                            ),
                                            self.count_subject
                                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                    ft.Container(
                                        padding=10, expand=True, height=220,
                                        border_radius=10, border=ft.border.all(1, MAIN_COLOR),
                                        alignment=ft.alignment.center,
                                        content=self.new_subjects
                                    ),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Row([MyButton(languages[lang]['valid'], 'check', 180, self.add_teacher)])
                                ], spacing=10, expand=True
                            )
                        )
                    ], spacing=0
                )
            )
        )

        # Schedule window...
        self.table_schedule = ft.DataTable(
            **datatable_style, columns=[
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.CALENDAR_TODAY_OUTLINED, size=16, color=ft.Colors.WHITE),
                            ft.Text(languages[lang]['day'].upper())
                        ]
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.TIMER_OUTLINED, size=16, color=ft.Colors.WHITE),
                            ft.Text(languages[lang]['slot'].upper())
                        ]
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.ROOFING_OUTLINED, size=16, color=ft.Colors.WHITE),
                            ft.Text(languages[lang]['class'].upper())
                        ]
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.BOOK_OUTLINED, size=16, color=ft.Colors.WHITE),
                            ft.Text(languages[lang]['subject'].upper())
                        ]
                    )
                )
            ]
        )
        self.no_data = ft.Text(
            languages[lang]['no data'], size=16, font_family="PPB", color='red', visible=False
        )
        self.nb_hours = ft.Text('0', size=28, font_family="PEB")
        self.sc_head_class = ft.Text('-', size=28, font_family="PPM")
        self.nb_classes = ft.Text('0', size=28, font_family="PEB")
        self.sc_container = ft.Column(
            controls=[
                ft.Text(languages[lang]['loading screen'], size=18, font_family='PPR'),
                ft.ProgressBar(color=BASE_COLOR)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10,
            alignment=ft.MainAxisAlignment.CENTER
        )
        self.schedule_window = ft.Container(
            **ct_style, content=ft.Container(
                **intern_ct_style, width=800,  # height=700,
                content=ft.Column(
                    expand=True, scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20,
                            border=ft.border.only(bottom=ft.BorderSide(1, MAIN_COLOR)),
                            border_radius=ft.border_radius.only(top_left=8, top_right=8),
                            content=ft.Row(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.CALENDAR_MONTH, size=24, color='black'),
                                            ft.Text(languages[lang]['schedule'], size=20, font_family='PPB'),
                                        ]
                                    ),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=MAIN_COLOR,
                                        on_click=self.close_schedule_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(top=ft.BorderSide(1, MAIN_COLOR)),
                            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True,
                            content=ft.Column(
                                expand=True, scroll=ft.ScrollMode.AUTO,
                                controls=[self.sc_container, self.no_data]
                            )
                        )
                    ], spacing=0
                )
            )
        )

        # edit teacher window___________________________________________
        self.edit_uid = ft.TextField(
            **login_style, width=400, prefix_icon='credit_card', visible=False, label="uid",
        )
        self.edit_name = ft.TextField(
            **login_style, prefix_icon="person_outlined", width=350, label=languages[lang]['name']
        )
        self.edit_surname = ft.TextField(
            **login_style, prefix_icon="person_outlined", width=350, label=languages[lang]['surname']
        )
        self.edit_gender = ft.TextField(
            **login_style, prefix_icon='wc', width=150, label=languages[lang]['gender']
        )
        self.edit_pay = ft.TextField(
            **login_style, width=150, prefix_icon='monetization_on_outlined', input_filter=ft.NumbersOnlyInputFilter(),
            read_only=True if self.cp.page.client_storage.get('role') != 'principal' else False,
            label=languages[lang]['hourly load']
        )
        self.edit_contact = ft.TextField(
            **login_style, prefix_icon=ft.Icons.PHONE_ANDROID_OUTLINED, width=200,
            input_filter=ft.NumbersOnlyInputFilter(), label=languages[lang]['contact']
        )
        self.edit_subject = ft.TextField(
            **login_style, expand=True, prefix_icon=ft.Icons.BOOK_OUTLINED, label=languages[lang]['subject']
        )
        self.edit_select_subjects = ft.GridView(
            expand=True,
            max_extent=120,  # largeur max par cellule (laisser assez pour le padding)
            child_aspect_ratio=4,  # largeur / hauteur
            spacing=10,
            run_spacing=10,
        )
        self.edit_count_subject = ft.Text('0', size=13, font_family='PPB')
        self.edit_teacher_window = ft.Container(
            **ct_style, content=ft.Container(
                **intern_ct_style, width=750,  # height=700,
                content=ft.Column(
                    expand=True, scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20,
                            border=ft.border.only(bottom=ft.BorderSide(1, MAIN_COLOR)),
                            border_radius=ft.border_radius.only(top_left=8, top_right=8),
                            content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['edit teacher'], size=20, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=MAIN_COLOR,
                                        on_click=self.close_edit_teacher_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(top=ft.BorderSide(1, MAIN_COLOR)),
                            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True,
                            content=ft.Column(
                                scroll=ft.ScrollMode.AUTO, expand=True,
                                controls=[
                                    self.edit_uid,
                                    ft.Row(controls=[self.edit_name, self.edit_surname]),
                                    ft.Row(controls=[self.edit_gender, self.edit_contact, self.edit_pay]),
                                    self.edit_subject,
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Row(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Text(languages[lang]['subjects taught'].upper(), size=13,
                                                            font_family='PPB'),
                                                    ft.Text(f"({languages[lang]['click to select']})", size=13,
                                                            font_family='PPI', color='grey'),
                                                ]
                                            ),
                                            self.edit_count_subject
                                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                    ft.Container(
                                        padding=10, expand=True, height=220,
                                        border_radius=10, border=ft.border.all(1, '#f0f0f6'),
                                        alignment=ft.alignment.center,
                                        content=self.edit_select_subjects
                                    ),
                                    ft.Container(
                                        padding=ft.padding.only(10, 0, 10, 0),
                                        content=ft.Row(
                                            [
                                                MyButton(
                                                    languages[lang]['valid'], 'check', 180,
                                                    self.edit_teacher
                                                )
                                            ]
                                        )
                                    )
                                ], spacing=10,
                            )
                        )
                    ], spacing=0
                )
            )
        )

        # Head teacher window ....
        self.head_teacher_name = ft.Dropdown(
            **drop_style, expand=True, prefix_icon='person_outlined',
            options=[ft.dropdown.Option(key=' ', text=languages[lang]['select option'])],
            menu_height=200, value=' ', label=languages[lang]['name']
        )
        self.head_class_name = ft.Dropdown(
            **drop_style, expand=True, prefix_icon='roofing',
            options=[ft.dropdown.Option(key=' ', text=languages[lang]['select option'])],
            menu_height=200, value=' ', label=languages[lang]['class']
        )
        self.head_teacher_window = ft.Container(
            **ct_style, content=ft.Container(
                **intern_ct_style, width=500,  # height=350,
                content=ft.Column(
                    spacing=0, expand=True, scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20,
                            border=ft.border.only(bottom=ft.BorderSide(1, MAIN_COLOR)),
                            border_radius=ft.border_radius.only(top_left=8, top_right=8),
                            content=ft.Row(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.ASSIGNMENT_IND, size=24, color='black'),
                                            ft.Text(languages[lang]['assign head'], size=20, font_family='PPB'),
                                        ]
                                    ),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=MAIN_COLOR,
                                        on_click=self.close_head_teacher_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(top=ft.BorderSide(1, MAIN_COLOR)),
                            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True,
                            content=ft.Column(
                                controls=[
                                    self.head_teacher_name, self.head_class_name,
                                    ft.Container(
                                        padding=10,
                                        content=ft.Row(
                                            [
                                                MyButton(
                                                    languages[lang]['valid'], 'check', 330,
                                                    self.valid_assignment
                                                )
                                            ]
                                        )
                                    )
                                ]
                            )
                        )
                    ]
                )
            )
        )

        # contenu ....
        self.content = ft.Stack(
            expand=True,
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(languages[lang]['loading screen'], size=18, font_family='PPR'),
                        ft.ProgressRing(color=BASE_COLOR)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20,
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ], alignment=ft.alignment.center
        )

        self.on_mount()

    async def build_main_view(self):
        self.content.controls.clear()

        for widget in (
                self.main_window, self.new_teacher_window, self.schedule_window, self.edit_teacher_window,
                self.head_teacher_window
        ):
            self.content.controls.append(widget)

    def show_one_window(self, window_to_show):
        # La surcouche (ct_registrations) est mise en avant
        window_to_show.visible = True
        window_to_show.opacity = 1
        self.cp.page.update()

    def hide_one_window(self, window_to_hide):
        # La surcouche est masquée
        window_to_hide.visible = False
        window_to_hide.opacity = 0
        self.cp.page.update()

    @staticmethod
    def run_async_in_thread(coro):
        def runner():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(coro)
            loop.close()

        thread = threading.Thread(target=runner)
        thread.start()

    async def on_init_async(self):
        await self.load_datas()

    def on_mount(self):
        self.run_async_in_thread(self.on_init_async())

    async def load_datas(self):
        access_token = self.cp.page.client_storage.get("access_token")
        year_id = self.cp.year_id

        active_sequence = await get_active_sequence(access_token)

        self.active_sequence.value = languages[self.lang][active_sequence['name']]
        self.active_quarter.value = languages[self.lang][active_sequence['quarter']]
        self.active_sequence.data = active_sequence['name']
        self.active_quarter.data = active_sequence['quarter']

        self.table.controls.clear()
        details = await get_all_teachers(access_token)

        total_pay = 0

        for d, detail in enumerate(details):
            self.table.controls.append(OneTeacher(self, detail))

        await self.build_main_view()

        short_names = await get_all_distinct_subject_short_names(access_token)
        for name in short_names:
            self.edit_select_subjects.controls.append(
                EditSingleOption(self, name)
            )

        for name in short_names:
            self.new_subjects.controls.append(
                SingleOption(self, name)
            )

        self.cp.page.update()

    async def filter_datas(self, e):
        details = await get_all_teachers(self.cp.page.client_storage.get('access_token'))
        search = self.search.value.lower() if self.search.value else ''
        filtered_datas = list(filter(lambda x: search in x['name'].lower() or search in x['surname'].lower(), details))

        self.table.controls.clear()
        for d, detail in enumerate(filtered_datas):
            self.table.controls.append(OneTeacher(self, detail))

        self.cp.page.update()

    def on_search_change(self, e):
        self.run_async_in_thread(self.filter_datas(e))

    def open_new_teacher_window(self, e):
        role = self.cp.page.client_storage.get('role')
        if role != 'admin':
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.message.value = languages[self.lang]['error rights']
            self.cp.box.open = True
            self.cp.box.update()
        else:
            self.show_one_window(self.new_teacher_window)

    def close_new_teacher_window(self, e):
        self.hide_one_window(self.new_teacher_window)

    def add_teacher(self, e):
        count = 0

        for widget in (self.new_name, self.new_surname, self.new_pay, self.new_gender, self.new_contact, self.new_uid):
            if widget.value is None:
                count += 1

        if count == 0 and self.count_subject.value != '0':
            subjects_selected = []

            for widget in self.new_subjects.controls[:]:
                if widget.selected:
                    subjects_selected.append(widget.name)

            supabase_client.table('teachers').insert(
                {
                    "name": self.new_name.value, 'surname': self.new_surname.value, 'gender': self.new_gender.value,
                    "pay": int(self.new_pay.value), "contact": self.new_contact.value,
                    "subjects": subjects_selected, 'id': self.new_uid.value
                }
            ).execute()

            for widget in (self.new_name, self.new_surname, self.new_pay, self.new_gender, self.new_contact):
                widget.value = None
                widget.update()

            self.count_subject.value = '0'
            self.count_subject.update()

            for widget in self.new_subjects.controls[:]:
                widget.set_initial()

            self.cp.box.title.value = languages[self.lang]['success']
            self.cp.message.value = languages[self.lang]['teacher registered']
            self.cp.box.open = True
            self.cp.box.update()

            self.on_mount()
            self.cp.page.update()

        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.message.value = languages[self.lang]['error msg']
            self.cp.box.open = True
            self.cp.box.update()

    async def load_schedule(self, e):
        self.table_schedule.rows.clear()
        self.cp.page.update()
        self.show_one_window(self.schedule_window)

        access_token = self.cp.page.client_storage.get('access_token')
        time_table = await get_teacher_affectations(e.control.data['id'], access_token)

        count_classes: set = set()

        for item in time_table:
            count_classes.add(item['class_code'])

        self.nb_classes.value = len(count_classes)
        self.sc_head_class.value = await get_head_class_code_by_teacher_id(
            access_token, e.control.data['id'], self.cp.year_id
        )
        self.nb_hours.value = len(time_table)

        if not time_table:
            self.no_data.visible = True
            self.no_data.update()

        else:
            self.no_data.visible = False
            self.no_data.update()

            for d, data in enumerate(time_table):
                line_color = ft.Colors.GREY_100 if d % 2 == 0 else ft.Colors.WHITE
                self.table_schedule.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(languages[self.lang][data['day']])),
                            ft.DataCell(ft.Text(data['slot'])),
                            ft.DataCell(ft.Text(data['class_code'])),
                            ft.DataCell(ft.Text(data['subject_name'].upper()))
                        ], color=line_color
                    )
                )

        self.cp.page.update()

    def open_schedule_window(self, e):
        self.run_async_in_thread(self.load_schedule(e))

    def close_schedule_window(self, e):
        self.hide_one_window(self.schedule_window)
        self.nb_hours.value = 0
        self.nb_classes.value = 0
        self.sc_head_class.value = '-'

        self.sc_container.controls.clear()
        self.sc_container.controls = [
            ft.Text(languages[self.lang]['loading screen'], size=18, font_family='PPR'),
            ft.ProgressBar(color=BASE_COLOR)
        ]
        self.cp.page.update()

    def open_edit_teacher_window(self, e):

        role = self.cp.page.client_storage.get('role')

        if role not in ['admin', 'principal']:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.message.value = languages[self.lang]['error rights']
            self.cp.box.open = True
            self.cp.box.update()
        else:
            self.edit_name.value = e.control.data['name']
            self.edit_gender.value = e.control.data['gender']
            self.edit_surname.value = e.control.data['surname']
            self.edit_uid.value = e.control.data['id']
            self.edit_pay.value = e.control.data['pay'] if role == 'principal' else '*****'
            self.edit_pay.read_only = True if role == 'admin' else False
            self.edit_contact.value = e.control.data['contact']
            self.edit_count_subject.value = len(e.control.data['subjects']) if e.control.data['subjects'] else '0'

            if not e.control.data['subjects']:
                pass
            else:
                for item, subject in enumerate(e.control.data['subjects']):
                    if item == 0:
                        self.edit_subject.value = self.edit_subject.value + f"{subject}"
                    else:
                        self.edit_subject.value = self.edit_subject.value + '; ' + f"{subject}"

                for item in self.edit_select_subjects.controls[:]:
                    if item.name in e.control.data['subjects']:
                        item.set_selected()

            self.show_one_window(self.edit_teacher_window)

    def close_edit_teacher_window(self, e):
        for item in self.edit_select_subjects.controls[:]:
            item.set_initial()

        self.edit_name.value = None
        self.edit_surname.value = None
        self.edit_uid.value = None
        self.edit_pay.value = None
        self.edit_pay.read_only = None
        self.edit_contact.value = None
        self.edit_count_subject.value = None
        self.edit_subject.value = None

        self.hide_one_window(self.edit_teacher_window)

    def edit_teacher(self, e):
        role = self.cp.page.client_storage.get('role')

        if role == 'principal':
            count = 0

            for widget in (self.edit_name, self.edit_surname, self.edit_pay, self.edit_gender, self.edit_contact):
                if widget.value is None:
                    count += 1

            if count == 0 and self.edit_count_subject.value != '0':
                subjects_selected = []

                for widget in self.edit_select_subjects.controls[:]:
                    if widget.selected:
                        subjects_selected.append(widget.name)

                for item in subjects_selected:
                    print(item)

                supabase_client.table('teachers').update(
                    {'name': self.edit_name.value, 'surname': self.edit_surname.value,
                     'contact': self.edit_contact.value,
                     'pay': int(self.edit_pay.value), "gender": self.edit_gender.value,
                     "subjects": subjects_selected}
                ).eq('id', self.edit_uid.value).execute()

        else:
            count = 0

            for widget in (self.edit_name, self.edit_surname, self.edit_pay, self.edit_gender, self.edit_contact):
                if widget.value is None:
                    count += 1

            if count == 0 and self.edit_count_subject.value != '0':
                subjects_selected = []

                for widget in self.edit_select_subjects.controls[:]:
                    if widget.selected:
                        subjects_selected.append(widget.name)

                for item in subjects_selected:
                    print(item)

                supabase_client.table('teachers').update(
                    {'name': self.edit_name.value, 'surname': self.edit_surname.value,
                     'contact': self.edit_contact.value,
                     "gender": self.edit_gender.value, "subjects": subjects_selected}
                ).eq('id', self.edit_uid.value).execute()

        self.on_mount()
        self.hide_one_window(self.edit_teacher_window)

        for item in self.edit_select_subjects.controls[:]:
            item.set_initial()

        self.edit_select_subjects.controls.clear()

        self.edit_name.value = None
        self.edit_surname.value = None
        self.edit_uid.value = None
        self.edit_pay.value = None
        self.edit_pay.read_only = None
        self.edit_contact.value = None
        self.edit_count_subject.value = None
        self.edit_subject.value = None

        self.cp.box.title.value = languages[self.lang]['success']
        self.cp.message.value = languages[self.lang]['teacher edited']
        self.cp.icon_message.name = ft.Icons.CHECK_CIRCLE
        self.cp.icon_message.color = ft.Colors.LIGHT_GREEN
        self.cp.box.open = True
        self.cp.box.update()

    async def load_head_teacher_datas(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        non_head_teachers = await get_non_head_teachers(access_token, self.cp.year_id)

        for item in non_head_teachers:
            self.head_teacher_name.options.append(
                ft.dropdown.Option(
                    key=item['id'], text=f"{item['name']} {item['surname']}".upper()
                )
            )

        classes_without_head_teacher = await get_classes_without_head_teacher(
            access_token, self.cp.year_id
        )
        for item in classes_without_head_teacher:
            self.head_class_name.options.append(
                ft.dropdown.Option(
                    key=item['id'], text=f"{item['code']}"
                )
            )

        self.show_one_window(self.head_teacher_window)

    def open_head_teacher_window(self, e):
        self.run_async_in_thread(self.load_head_teacher_datas(e))

    def close_head_teacher_window(self, e):
        for widget in (self.head_teacher_name, self.head_class_name):
            widget.options.clear()
            widget.options.append(
                ft.dropdown.Option(
                    key=' ', text=languages[self.lang]['select option']
                )
            )
            widget.value = ' '
            widget.update()

        self.hide_one_window(self.head_teacher_window)

    def valid_assignment(self, e):
        if self.head_class_name.value != ' ' and self.head_teacher_name.value != ' ':
            datas = {
                "class_id": self.head_class_name.value,
                "teacher_id": self.head_teacher_name.value,
                'year_id': self.cp.year_id
            }
            supabase_client.table('head_teachers').insert(datas).execute()
            self.cp.box.title.value = languages[self.lang]['success']
            self.cp.message.value = languages[self.lang]['head teacher assigned']
            self.cp.icon_message.name = ft.Icons.CHECK_CIRCLE
            self.cp.icon_message.color = ft.Colors.LIGHT_GREEN
            self.cp.box.open = True
            self.cp.box.update()

            for widget in (self.head_teacher_name, self.head_class_name):
                widget.options.clear()
                widget.options.append(
                    ft.dropdown.Option(
                        key=' ', text=languages[self.lang]['select option']
                    )
                )
                widget.value = ' '
                widget.update()

            self.on_mount()
            self.hide_one_window(self.head_teacher_window)

        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.message.value = languages[self.lang]['error msg']
            self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
            self.cp.icon_message.color = ft.Colors.RED
            self.cp.box.open = True
            self.cp.box.update()

    def build_schedule_view(self):
        self.sc_container.controls.clear()
        self.sc_container.controls = [
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text(languages[self.lang]['head class'], size=16, font_family='PPM', color='grey'),
                                ft.Row(
                                    controls=[
                                        ft.Icon("roofing", size=28, color=ACCENT_PLUS_COLOR),
                                        self.sc_head_class
                                    ]
                                )
                            ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        ft.Row(
                            controls=[
                                ft.Column(
                                    controls=[
                                        ft.Text(languages[self.lang]['count classes'], size=16, font_family='PPM',
                                                color='grey'),
                                        ft.Row(
                                            controls=[
                                                ft.Icon("account_balance_outlined", size=28, color=ACCENT_PLUS_COLOR),
                                                self.nb_classes
                                            ]
                                        )
                                    ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                ),
                                ft.VerticalDivider(width=1, thickness=1),
                                ft.Column(
                                    controls=[
                                        ft.Text(languages[self.lang]['nb hours affected'], size=16, font_family='PPM',
                                                color='grey'),
                                        ft.Row(
                                            controls=[
                                                ft.Icon("timer_outlined", size=28, color=ACCENT_PLUS_COLOR),
                                                self.nb_hours
                                            ]
                                        )
                                    ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                )
                            ]
                        )

                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            ),
            ft.Divider(color=ft.Colors.TRANSPARENT),
            ft.Container(
                padding=0, border_radius=16, border=ft.border.all(1, MAIN_COLOR), expand=True,
                height=400,
                content=ft.ListView([self.table_schedule], expand=True),
            ),
            ft.Row([self.no_data], alignment=ft.MainAxisAlignment.CENTER)
        ]
        self.cp.page.update()










