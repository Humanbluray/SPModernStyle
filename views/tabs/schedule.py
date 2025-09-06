from components import MyTextButton, MyButton, SlotCard, SlotCardRoom
from utils.styles import *
from translations.translations import languages
import asyncio, threading
from services.async_functions.general_functions import *
from services.async_functions.teachers_functions import *
from services.supabase_client import supabase_client

days = ['day 1', 'day 2', 'day 3', 'day 4', 'day 5']
slots = [
    '07:30-08:30', '08:30-09:30', '09:30-10:30', '10:45-11:45',
    '11:45-12:45', '13:00-14:00', '14:00-15:00', '15:00-16:00'
]


class Schedule(ft.Container):
    def __init__(self, cp: object):
        super().__init__(
            expand=True, alignment=ft.alignment.center, bgcolor=MAIN_COLOR
        )

        # parent container (Home) ___________________________________________________________
        self.cp = cp
        lang = self.cp.language
        self.lang = lang

        # objets main window...
        # -------------------------------------------------------
        self.menu_button = ft.IconButton(
            ft.Icons.MENU, icon_size=24, icon_color='black',
            on_click=lambda e: self.cp.page.open(self.cp.drawer)
        )

        self.active_sequence = ft.Text(size=14, font_family='PPB')
        self.active_quarter = ft.Text(size=14, font_family='PPB')
        self.sequence_ct = ft.Container(
            **seq_ct_style, content=ft.Row(
                controls=[
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.WATCH_LATER, size=20, color='black'),
                            self.active_quarter
                        ]
                    ),
                    ft.Text(" | ", size=16, font_family='PPM'),
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED, size=20, color='black'),
                            self.active_sequence
                        ]
                    )
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
                                    ft.Text(languages[lang]['menu time table'].capitalize(), size=24, font_family="PEB"),
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
                    ft.Row([self.sequence_ct])
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        )
        self.monday = ft.Column()
        self.tuesday = ft.Column()
        self.wednesday = ft.Column()
        self.thursday = ft.Column()
        self.friday = ft.Column()
        # fin objets main window...
        # -------------------------------------------------------


        # Objet de la vue par professeurs...
        # -------------------------------------------------------
        self.prof_id = ft.Text(size=12, font_family="PPM", visible=False)
        self.filtered_subjects: list = []
        self.search_prof = ft.Dropdown(
            **drop_style, width=300, prefix_icon='person_outlined', label=languages[lang]['name'],
            on_change=self.on_search_change, menu_height=200, visible=False
        )
        self.bt_prof_details = MyTextButton(languages[lang]['affectations details'], self.open_prof_details_window)
        self.bt_prof_details.visible = False
        self.new_prof = ft.Text(size=16, font_family='PPM')
        self.new_prof_id = ft.Text(visible=True)
        self.new_day = ft.TextField(
            **login_style, label=languages[lang]['day'], prefix_icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
            read_only=True, width=170, visible=False
        )
        self.new_day_display = ft.TextField(
            **login_style, label=languages[lang]['day'], prefix_icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
            read_only=True, width=170
        )
        self.new_slot = ft.TextField(
            **login_style, label=languages[lang]['slot'], prefix_icon=ft.Icons.TIMER_OUTLINED,
            read_only=True, width=170
        )
        self.new_class = ft.Dropdown(
            **drop_style, width=200, label=languages[lang]['class'], prefix_icon='roofing',
            on_change=self.on_class_change, menu_height=200,
            options=[ft.dropdown.Option(key=" ", text=f"{languages[self.lang]['select option']}")],
            value=" "
        )
        self.new_level = ft.TextField(
            **login_style, width=200, label=languages[lang]['level'], visible=False
        )
        self.new_subject = ft.Dropdown(
            **drop_style, width=220, label=languages[lang]['subject'], prefix_icon='book_outlined',
            options=[ft.dropdown.Option(key=" ", text=f"{languages[self.lang]['select option']}")],
            on_change=self.on_subject_change, value=" ",
        )
        self.check_validity = ft.Icon(name=None, size=28, color=None)
        self.check_validity_load = ft.Icon(name=None, size=28, color=None)

        self.new_affectation_window = ft.Container(
            **ct_style, content=ft.Container(
                **intern_ct_style, width=600,
                content=ft.Column(
                    expand=True, scroll=ft.ScrollMode.AUTO,
                    spacing=0, controls=[
                        ft.Container(
                            **top_ct_style,
                            content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['new affectation'], size=20, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=MAIN_COLOR,
                                        on_click=self.close_new_affectation_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            **bottom_ct_style,
                            content=ft.Column(
                                expand=True, scroll=ft.ScrollMode.AUTO,
                                controls=[
                                    ft.Row([self.new_prof, self.new_prof_id, ], visible=False),
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[lang]['slot'].upper(), size=16, font_family='PPB'),
                                            ft.Divider(),
                                        ], spacing=0
                                    ),
                                    ft.Row([self.new_day, self.new_day_display, self.new_slot, ]),
                                    ft.Divider(color='transparent'),
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[lang]['class and subject'].upper(), size=16,
                                                    font_family='PPB'),
                                            ft.Divider(),
                                        ], spacing=0
                                    ),
                                    ft.Container(
                                        border_radius=8, padding=10,
                                        content=ft.Column(
                                            controls=[
                                                self.new_class,
                                                ft.Row(
                                                    controls=[
                                                        ft.Text(
                                                            value=f"{languages[self.lang]['class availability check']}",
                                                            size=16, font_family='PPM'),
                                                        self.check_validity
                                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                                ),
                                            ]
                                        )
                                    ),
                                    ft.Divider(height=1, thickness=1),
                                    self.new_level,
                                    ft.Container(
                                        border_radius=8, padding=10,
                                        content=ft.Row(
                                            controls=[
                                                ft.Column(
                                                    controls=[
                                                        self.new_subject,
                                                        ft.Text(value=f"{languages[self.lang]['hourly load check']}",
                                                                size=16, font_family='PPM'),
                                                    ]
                                                ),
                                                self.check_validity_load
                                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                            vertical_alignment=ft.CrossAxisAlignment.CENTER
                                        )
                                    ),
                                    ft.Container(
                                        padding=ft.padding.only(10, 0, 10, 0),
                                        content=ft.Row(
                                            [MyButton(languages[lang]['valid'], None, 150, self.validate_affectation)]
                                        )
                                    )
                                ]
                            ),
                        )
                    ]
                )
            )
        )

        self.prof_det_name = ft.Text("-", size=16, font_family='PPM')
        self.prof_det_nb_hours = ft.Text("0", size=24, font_family='PEB')
        self.prof_det_print = MyButton(languages[lang]['print'], 'print', 200, None)
        self.prof_det_table = ft.DataTable(
            **datatable_style, columns=[
                ft.DataColumn(ft.Text(choice)) for choice in [
                    languages[lang]['day'], languages[lang]['slot'], languages[lang]['class'], languages[lang]['subject'],
                ]
            ]
        )
        self.prof_details_view = ft.Column(
            controls=[
                ft.Text(languages[lang]['loading screen'], size=18, font_family='PPR'),
                ft.ProgressBar(color=BASE_COLOR)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER
        )

        self.prof_details_window = ft.Container(
            **ct_style, content=ft.Container(
                **intern_ct_style, width=800, content=ft.Column(
                    expand=True, scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Container(
                            **top_ct_style,
                            content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['affectations details'], size=20, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=MAIN_COLOR,
                                        on_click=self.close_prof_details_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            **bottom_ct_style,
                            content=ft.Column(
                                expand=True, scroll=ft.ScrollMode.AUTO,
                                controls=[self.prof_details_view]
                            ),
                        )
                    ], spacing=0,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
        )


        # -------------------------------------------------------
        # fin des objet de la vue par professeurs...


        # Objet de la vue par classes...
        # -------------------------------------------------------
        self.search_class = ft.Dropdown(
            **drop_style, width=200, prefix_icon='roofing', label=languages[lang]['class'],
            on_change=self.c_on_class_change, menu_height=200, visible=False
        )
        self.check_class_button = MyTextButton(languages[lang]['affectations details'], self.open_details_window)
        self.check_class_button.visible = False

        # New affectation window...
        self.c_new_affectation_id = ""
        self.c_new_prof = ft.Dropdown(
            **drop_style, width=400, prefix_icon='person_outlined', label=languages[lang]['teacher'],
            menu_height=200,
            options=[ft.dropdown.Option(key=" ", text=f"{languages[self.lang]['select option']}")],
            value=" ", on_change=self.c_on_change_teacher
        )
        self.c_new_day = ft.TextField(
            **login_style, label=languages[lang]['day'], prefix_icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
            read_only=True, width=170, visible=False
        )
        self.c_new_day_display = ft.TextField(
            **login_style, label=languages[lang]['day'], prefix_icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
            read_only=True, width=170
        )
        self.c_new_slot = ft.TextField(
            **login_style, label=languages[lang]['slot'], prefix_icon=ft.Icons.TIMER_OUTLINED,
            read_only=True, width=170
        )
        self.c_new_class_id = ''
        self.c_new_level = ft.TextField(
            **login_style, width=200, label=languages[lang]['level'], visible=False
        )
        self.c_new_subject = ft.Dropdown(
            **drop_style, width=250, label=languages[lang]['subject'], prefix_icon='book_outlined',
            options=[ft.dropdown.Option(key=" ", text=f"{languages[self.lang]['select option']}")],
            on_change=self.c_on_subject_change, value=" ",
        )
        self.c_check_validity = ft.Icon(name=None, size=24, color=None)
        self.c_check_validity_load = ft.Icon(name=None, size=24, color=None)

        self.c_new_affectation_window = ft.Container(
            **ct_style, content=ft.Container(
                **intern_ct_style, width=600, content=ft.Column(
                    expand=True, scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Container(
                            **top_ct_style,
                            content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['new affectation'], size=20, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=MAIN_COLOR,
                                        on_click=self.c_close_new_affectation_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            **bottom_ct_style,
                            content=ft.Column(
                                controls=[
                                    ft.Row([self.c_new_prof], visible=False),
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[lang]['slot'].upper(), size=16, font_family='PPB'),
                                            ft.Divider(height=1, thickness=1),
                                        ], spacing=0
                                    ),
                                    ft.Row([self.c_new_day, self.c_new_day_display, self.c_new_slot, ]),
                                    ft.Divider(color=ft.Colors.TRANSPARENT),
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[lang]['teacher and subject'].upper(), size=16,
                                                    font_family='PPB'),
                                            ft.Divider(height=1, thickness=1),
                                        ], spacing=0
                                    ),
                                    ft.Container(
                                        border_radius=8, padding=10,
                                        content=ft.Column(
                                            controls=[
                                                self.c_new_prof,
                                                ft.Row(
                                                    controls=[
                                                        ft.Text(
                                                            value=f"{languages[self.lang]['teacher availability check']}",
                                                            size=16, font_family='PPM'),
                                                        self.c_check_validity
                                                    ]
                                                ),
                                            ]
                                        )
                                    ),
                                    self.c_new_level,
                                    ft.Container(
                                        border_radius=8, padding=10,
                                        content=ft.Column(
                                            controls=[
                                                self.c_new_subject,
                                                ft.Row(
                                                    controls=[
                                                        ft.Text(value=f"{languages[self.lang]['hourly load check']}",
                                                                size=16, font_family='PPM'),
                                                        self.c_check_validity_load
                                                    ]
                                                ),
                                            ]
                                        )
                                    ),
                                    ft.Container(
                                        padding=ft.padding.only(10, 10, 10, 10),
                                        content=ft.Row(
                                            controls=[
                                                MyButton(languages[lang]['valid'], 'check',
                                                         150, self.c_validate_affectation)
                                            ]
                                        )
                                    )
                                ]
                            ),
                        )
                    ], spacing=0
                )
            )
        )

        self.det_class = ft.Text("-", size=24, font_family='PPM')
        self.det_progress_bar = ft.ProgressBar(
            color=BASE_COLOR, bgcolor=MAIN_COLOR, width=150, height=5, border_radius=16,
        )
        self.det_percent = ft.Text(size=18, font_family='PPB')
        self.det_table = ft.DataTable(
            **datatable_style, columns=[
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color='white', size=20),
                            ft.Text(languages[lang]['status'])
                        ]
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.BOOK_OUTLINED, color='white', size=20),
                            ft.Text(languages[lang]['subject'])
                        ]
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.WATCH_LATER_OUTLINED, color='white', size=20),
                            ft.Text(languages[lang]['hourly load'])
                        ]
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.CHECK_BOX_OUTLINED, color='white', size=20),
                            ft.Text(languages[lang]['affected'])
                        ]
                    )
                )
            ]
        )
        self.details_window = ft.Container(
            **ct_style, content=ft.Container(
                **intern_ct_style, width=650, content=ft.Column(
                    expand=True, scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Container(
                            **top_ct_style,
                            content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['affectations details'].capitalize(), size=20, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=MAIN_COLOR,
                                        on_click=self.close_details_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            **bottom_ct_style,
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Icon('roofing', size=24, color="grey"),
                                                    self.det_class,
                                                ]
                                            ),
                                            ft.Column(
                                                [
                                                    ft.Text(languages[lang]['affectations state'], size=16,
                                                            font_family='PPM', color='grey'),
                                                    ft.Row([self.det_progress_bar, self.det_percent])
                                                ], spacing=5
                                            )
                                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        vertical_alignment=ft.CrossAxisAlignment.END
                                    ),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Container(
                                        border_radius=16, padding=0, border=ft.border.all(1, MAIN_COLOR),
                                        expand=True, height=500,
                                        content=ft.ListView(expand=True, controls=[self.det_table])
                                    )
                                ]
                            ),
                        )
                    ], spacing=0
                )
            )
        )
        # -------------------------------------------------------
        # Fin des objet de la vue par classes...


        # Main window...
        self.main_window = ft.Container(
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    self.top_menu,
                    ft.Container(
                        padding=ft.padding.only(10, 0,10, 0),
                        content=ft.Row(
                            controls=[
                                ft.Row(
                                    controls=[
                                        MyTextButton(languages[lang]['teacher view'], self.pass_to_teacher_view),
                                        MyTextButton(languages[lang]['class view'], self.pass_to_class_view)
                                    ]
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                self.search_prof, self.bt_prof_details, self.search_class, self.check_class_button
                                            ]
                                        )
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                ),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        )
                    ),
                    ft.Container(
                        expand=True, padding=20,
                        content=ft.ListView(
                            expand=True, controls=[
                                ft.Row(
                                    controls=[
                                        self.monday, self.tuesday, self.wednesday, self.thursday, self.friday
                                    ]
                                )
                            ]
                        )
                    )
                ]
            )
        )

        self.content = ft.Stack(
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

    # Fonctions générales...
    # -------------------------------------------------------
    async def build_main_view(self):
        self.content.controls.clear()
        self.content.controls=[
            self.main_window, self.new_affectation_window, self.c_new_affectation_window,
            self.details_window, self.prof_details_window
        ]
        self.cp.page.update()

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
        await self.load_informations()

    def on_mount(self):
        self.run_async_in_thread(self.on_init_async())

    async def load_datas(self):
        access_token = self.cp.page.client_storage.get('access_token')

        # On charge la liste des professeurs...
        teachers_names = await get_all_teachers(access_token)
        for teacher in teachers_names:
            self.search_prof.options.append(
                ft.dropdown.Option(
                    key=teacher['id'], text=f"{teacher['name']} {teacher['surname']}".upper()
                )
            )
            self.c_new_prof.options.append(
                ft.dropdown.Option(
                    key=teacher['id'], text=f"{teacher['name']} {teacher['surname']}".upper()
                )
            )

        # on charge la liste des classes...
        classes = await get_all_classes_basic_info(access_token)
        for item in classes:
            self.new_class.options.append(
                ft.dropdown.Option(
                    key=item['id'], text=f"{item['code']}"
                )
            )
            self.search_class.options.append(
                ft.dropdown.Option(
                    key=item['id'], text=f"{item['code']}"
                )
            )

        await self.build_main_view()

    async def load_informations(self):
        access_token = self.cp.page.client_storage.get("access_token")
        active_sequence = await get_active_sequence(access_token)
        self.active_sequence.value = languages[self.lang][active_sequence['name']]
        self.active_quarter.value = languages[self.lang][active_sequence['quarter']]
        self.active_sequence.data = active_sequence['name']
        self.active_quarter.data = active_sequence['quarter']
        self.cp.page.update()

    def pass_to_teacher_view(self, e):
        self.run_async_in_thread(self.how_to_pass_to_teacher_view(e))

    async def how_to_pass_to_teacher_view(self, e):
        self.search_prof.visible = True
        self.bt_prof_details.visible = True
        self.search_class.visible = False
        self.check_class_button.visible = False

        for widget in (self.monday, self.tuesday, self.wednesday, self.thursday, self.friday):
            widget.controls.clear()

        # Si le champs du choix du professeur n'est pas vide...
        if self.search_prof.value:
            self.new_subject.options.clear()
            self.prof_id.value = self.search_prof.value
            access_token = self.cp.page.client_storage.get('access_token')
            year_id = self.cp.year_id

            # on récupère toutes les matières enseignées par le professeur...
            teachers = await get_all_teachers(access_token)
            filtered_teacher = list(filter(lambda x: self.prof_id.value in x['id'], teachers))[0]
            filtered_subjects = filtered_teacher['subjects']

            for subject in filtered_subjects:
                self.filtered_subjects.append(subject)

            for widget in [self.monday, self.tuesday, self.wednesday, self.thursday, self.friday]:
                widget.controls.clear()

            all_affectations = await get_teacher_affectations_details(self.search_prof.value, access_token, year_id)

            for day in days:
                for slot in slots:
                    filtered_datas = list(filter(lambda x: slot in x['slot'] and day in x['day'], all_affectations))

                    if filtered_datas:
                        card = SlotCard(self, filtered_datas[0])
                    else:
                        card = SlotCard(
                            self, {
                                "id": None,
                                "day": day,
                                "slot": slot,
                                "teacher_id": None,
                                "teacher_name": None,
                                "subject_id": None,
                                "subject_name": None,
                                "subject_short_name": None,
                                "class_id": None,
                                "class_code": None,
                                "status": False
                            }
                        )
                    if day == "day 1":
                        self.monday.controls.append(card)

                    elif day == 'day 2':
                        self.tuesday.controls.append(card)

                    elif day == 'day 3':
                        self.wednesday.controls.append(card)

                    elif day == 'day 4':
                        self.thursday.controls.append(card)

                    else:
                        self.friday.controls.append(card)

        self.cp.page.update()

    def pass_to_class_view(self, e):
        self.run_async_in_thread(self.how_to_pass_to_class_view(e))

    async def how_to_pass_to_class_view(self, e):
        self.search_prof.visible = False
        self.bt_prof_details.visible = False
        self.search_class.visible = True
        self.check_class_button.visible = True

        for widget in (self.monday, self.tuesday, self.wednesday, self.thursday, self.friday):
            widget.controls.clear()

        if self.search_class.value:
            access_token = self.cp.page.client_storage.get('access_token')
            affectations = await get_all_affectations_details(access_token)

            search = self.search_class.value
            filtered_datas = list(filter(lambda x: search in x['class_id'], affectations))

            for widget in [self.monday, self.tuesday, self.wednesday, self.thursday, self.friday]:
                widget.controls.clear()
                widget.update()

            for affectation in filtered_datas:
                card = SlotCardRoom(self, affectation)
                if affectation['day'] == "day 1":
                    self.monday.controls.append(card)

                elif affectation['day'] == 'day 2':
                    self.tuesday.controls.append(card)

                elif affectation['day'] == 'day 3':
                    self.wednesday.controls.append(card)

                elif affectation['day'] == 'day 4':
                    self.thursday.controls.append(card)

                else:
                    self.friday.controls.append(card)

            level = await get_level_by_class_id(search, access_token)
            self.c_new_level.value = level['level_id']

        self.cp.page.update()

    # Fin des fonctions générales...
    # -------------------------------------------------------


    # Fonctions des affectations de professeurs...
    # -------------------------------------------------------
    async def filter_on_teacher(self, e):
        self.new_subject.options.clear()
        self.prof_id.value = self.search_prof.value
        access_token = self.cp.page.client_storage.get('access_token')
        year_id = self.cp.year_id

        # on récupère toutes les matières enseignées par le professeur...
        teachers = await get_all_teachers(access_token)
        filtered_teacher = list(filter(lambda x: self.prof_id.value in x['id'], teachers))[0]
        filtered_subjects = filtered_teacher['subjects']

        for subject in filtered_subjects:
            self.filtered_subjects.append(subject)

        for widget in [self.monday, self.tuesday, self.wednesday, self.thursday, self.friday]:
            widget.controls.clear()

        all_affectations = await get_teacher_affectations_details(self.search_prof.value, access_token, year_id)

        for day in days:
            for slot in slots:
                filtered_datas = list(filter(lambda x: slot in x['slot'] and day in x['day'], all_affectations))

                if filtered_datas:
                    card = SlotCard(self, filtered_datas[0])
                else:
                    card = SlotCard(
                        self, {
                            "id": None,
                            "day": day,
                            "slot": slot,
                            "teacher_id": None,
                            "teacher_name": None,
                            "subject_id": None,
                            "subject_name": None,
                            "subject_short_name": None,
                            "class_id": None,
                            "class_code": None,
                            "status": False
                        }
                    )
                if day == "day 1":
                    self.monday.controls.append(card)

                elif day == 'day 2':
                    self.tuesday.controls.append(card)

                elif day == 'day 3':
                    self.wednesday.controls.append(card)

                elif day == 'day 4':
                    self.thursday.controls.append(card)

                else:
                    self.friday.controls.append(card)

        self.cp.page.update()

    def on_search_change(self, e):
        self.run_async_in_thread(self.filter_on_teacher(e))

    async def update_current_view(self):
        self.prof_id.value = self.search_prof.value
        print(self.prof_id.value)
        access_token = self.cp.page.client_storage.get('access_token')

        for widget in [self.monday, self.tuesday, self.wednesday, self.thursday, self.friday]:
            widget.controls.clear()
            widget.update()

        all_affectations = await get_teacher_affectations_details(self.search_prof.value, access_token, self.cp.year_id)

        for day in days:
            for slot in slots:
                filtered_datas = list(filter(lambda x: slot in x['slot'] and day in x['day'], all_affectations))

                if filtered_datas:
                    card = SlotCard(self, filtered_datas[0])
                else:
                    card = SlotCard(
                        self, {
                            "id": None,
                            "day": day,
                            "slot": slot,
                            "teacher_id": None,
                            "teacher_name": None,
                            "subject_id": None,
                            "subject_name": None,
                            "subject_short_name": None,
                            "class_id": None,
                            "class_code": None,
                            "status": False
                        }
                    )
                if day == "day 1":
                    self.monday.controls.append(card)

                elif day == 'day 2':
                    self.tuesday.controls.append(card)

                elif day == 'day 3':
                    self.wednesday.controls.append(card)

                elif day == 'day 4':
                    self.thursday.controls.append(card)

                else:
                    self.friday.controls.append(card)

        for widget in [self.monday, self.tuesday, self.wednesday, self.thursday, self.friday]:
            widget.update()
            print(len(widget.controls))

        self.cp.page.update()

    def refresh_view(self):
        self.run_async_in_thread(self.update_current_view())

    def on_class_change(self, e):
        self.run_async_in_thread(self.filter_by_class(e))

    async def filter_by_class(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        level = await get_level_by_class_id(self.new_class.value, access_token)

        self.new_level.value = level['level_id']
        self.new_level.update()

        # on trouve toutes les matières liées à ce level
        subjects = await get_subjects_by_level_id(level['level_id'], access_token)
        self.new_subject.options.clear()
        for subject in subjects:
            if subject['short_name'] in self.filtered_subjects:
                self.new_subject.options.append(
                    ft.dropdown.Option(
                        key=subject['id'], text=f"{subject['short_name']}"
                    )
                )

        self.new_subject.update()

        # on vérifie la disponibilité du créneau pour la classe...
        status = await is_class_slot_occupied(self.new_class.value, self.new_day.value, self.new_slot.value,
                                              access_token)
        if status['occupied']:
            self.check_validity.name = ft.Icons.INFO_ROUNDED
            self.check_validity.color = ft.Colors.RED
            self.check_validity.update()
        else:
            self.check_validity.name = ft.Icons.CHECK_CIRCLE
            self.check_validity.color = ft.Colors.LIGHT_GREEN
            self.check_validity.update()

    def validate_affectation(self, e):
        if self.new_class.value is None or self.new_subject.value is None:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.message.value = languages[self.lang]['error msg']
            self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
            self.cp.icon_message.color = ft.Colors.RED
            self.cp.box.open = True
            self.cp.box.update()

        else:
            if self.check_validity.name == 'check_circle' and self.check_validity_load.name == 'check_circle':
                supabase_client.table('affectations').update(
                    {
                        'subject_id': self.new_subject.value,
                        "teacher_id": self.prof_id.value,
                    }
                ).eq('day', self.new_day.value).eq('slot', self.new_slot.value).eq(
                    "class_id", self.new_class.value).eq('year_id', self.cp.year_id).execute()

                self.hide_one_window(self.new_affectation_window)

                self.cp.box.title.value = languages[self.lang]['success']
                self.cp.message.value = languages[self.lang]['successful assignment']
                self.cp.icon_message.name = ft.Icons.CHECK_CIRCLE
                self.cp.icon_message.color = ft.Colors.LIGHT_GREEN
                self.cp.box.open = True
                self.cp.box.update()

                self.new_subject.options.clear()
                self.new_subject.options.append(
                    ft.dropdown.Option(key=" ", text=f"{languages[self.lang]['select option']}")
                )
                self.new_subject.value = " "
                self.new_subject.update()

                for widget in (self.check_validity, self.check_validity_load):
                    widget.name = None
                    widget.color = None
                    widget.update()

                self.refresh_view()

            elif self.check_validity.name == 'close' and self.check_validity_load.name == 'check_circle':
                self.cp.box.title.value = languages[self.lang]['error']
                self.cp.message.value = languages[self.lang]['slot class busy']
                self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
                self.cp.icon_message.color = ft.Colors.RED
                self.cp.box.open = True
                self.cp.box.update()

            elif self.check_validity.name == 'check_circle' and self.check_validity_load.name == 'close':
                self.cp.box.title.value = languages[self.lang]['error']
                self.cp.message.value = languages[self.lang]['hourly load exceeded']
                self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
                self.cp.icon_message.color = ft.Colors.RED
                self.cp.box.open = True
                self.cp.box.update()

            else:
                self.cp.box.title.value = languages[self.lang]['error']
                self.cp.message.value = (f"{languages[self.lang]['slot class busy']}\n"
                                                f"{languages[self.lang]['hourly load exceeded']}")
                self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
                self.cp.icon_message.color = ft.Colors.RED
                self.cp.box.open = True
                self.cp.box.update()

    def on_subject_change(self, e):
        self.run_async_in_thread(self.on_filter_subject(e))

    async def on_filter_subject(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        hourly_load = await get_hourly_load_by_subject_id(self.new_subject.value, access_token)
        nb_affectations = await count_affectations_by_subject_and_class(self.new_subject.value, self.new_class.value,
                                                                        access_token)

        if nb_affectations >= hourly_load:
            self.check_validity_load.name = 'close'
            self.check_validity_load.color = 'red'
            self.check_validity_load.update()
        else:
            self.check_validity_load.name = 'check_circle'
            self.check_validity_load.color = 'green'
            self.check_validity_load.update()

    def close_new_affectation_window(self, e):
        self.hide_one_window(self.new_affectation_window)
        self.new_subject.value = " "
        self.new_class.value = " "
        self.check_validity.name = None
        self.check_validity_load.name = None
        self.cp.page.update()

    async def load_prof_details_window(self, e):
        # on affiche la fenêtre...
        self.show_one_window(self.prof_details_window)

        # on récupère l'access token...
        access_token = self.cp.page.client_storage.get('access_token')
        year_id = self.cp.year_id

        # On effectue la requête...
        details = await get_teachers_detailed_affectations(
            access_token, self.search_prof.value, year_id
        )

        # On initialise les variables...
        self.prof_det_name.value = f"{details[0]['teacher_name']} {details[0]['teacher_surname']}"
        total_hours = 0
        self.prof_det_table.rows.clear()

        # On remplit la table...
        for d, item in enumerate(details):
            line_color = ft.Colors.GREY_100 if d % 2 == 0 else ft.Colors.WHITE
            total_hours += 1

            self.prof_det_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(languages[self.lang][item['day']])),
                        ft.DataCell(ft.Text(item['slot'])),
                        ft.DataCell(ft.Text(item['class_code'])),
                        ft.DataCell(ft.Text(item['subject_name'])),
                    ],
                    color=line_color
                )
            )

        # On met à jour les variables...
        self.prof_det_nb_hours.value = total_hours

        # on construit la fenêtre...
        await self.build_prof_details_window()

    async def build_prof_details_window(self):
        # On vide les élements de la fenêtre...
        self.prof_details_view.controls.clear()

        # on insère les nouveaux éléments pour la reconstruire...
        self.prof_details_view.controls = [
            ft.Row(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(languages[self.lang]['name'], size=16, font_family='PPM', color='grey'),
                                    ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.PERSON_OUTLINE_OUTLINED, size=28, color="grey"),
                                            self.prof_det_name
                                        ]
                                    ),
                                ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            ft.VerticalDivider(width=1, thickness=1),
                            ft.Column(
                                controls=[
                                    ft.Text(languages[self.lang]['nb hours affected'], size=16, font_family='PPM',
                                            color='grey'),
                                    ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.TIMER, size=28, color='black'),
                                            self.prof_det_nb_hours,
                                        ]
                                    )
                                ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                        ]
                    ),
                    self.prof_det_print
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
            ft.Container(
                padding=0, border_radius=16, border=ft.border.all(1, MAIN_COLOR), expand=True,
                content=ft.ListView(expand=True, controls=[self.prof_det_table], height=450)
            )
        ]
        # on update la vue...
        self.cp.page.update()

    def open_prof_details_window(self, e):
        self.run_async_in_thread(self.load_prof_details_window(e))

    def close_prof_details_window(self, e):
        self.prof_det_name.value = '-'
        self.prof_det_nb_hours.value = '0'
        self.prof_details_view.controls.clear()
        self.prof_details_view.controls = [
            ft.Text(languages[self.lang]['loading screen'], size=18, font_family='PPR'),
            ft.ProgressBar(color=BASE_COLOR)
        ]
        self.hide_one_window(self.prof_details_window)

    # Fin des fonctions des affectations de professeurs...
    # -------------------------------------------------------

    # Fonctions des affectations de classes...
    # -------------------------------------------------------

    async def c_filter_datas(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        affectations = await get_all_affectations_details(access_token)

        search = self.search_class.value
        filtered_datas = list(filter(lambda x: search in x['class_id'], affectations))

        for widget in [self.monday, self.tuesday, self.wednesday, self.thursday, self.friday]:
            widget.controls.clear()
            widget.update()

        for affectation in filtered_datas:
            card = SlotCardRoom(self, affectation)
            if affectation['day'] == "day 1":
                self.monday.controls.append(card)

            elif affectation['day'] == 'day 2':
                self.tuesday.controls.append(card)

            elif affectation['day'] == 'day 3':
                self.wednesday.controls.append(card)

            elif affectation['day'] == 'day 4':
                self.thursday.controls.append(card)

            else:
                self.friday.controls.append(card)

        level = await get_level_by_class_id(search, access_token)
        self.c_new_level.value = level['level_id']

        self.cp.page.update()

    def c_on_class_change(self, e):
        self.run_async_in_thread(self.c_filter_datas(e))

    def c_close_new_affectation_window(self, e):
        self.c_new_subject.value = " "
        self.c_new_prof.value = " "
        self.c_new_prof.update()
        self.c_new_subject.value = " "
        self.c_check_validity.name  = None
        self.c_check_validity_load.name = None
        self.hide_one_window(self.c_new_affectation_window)

    def c_refresh_view(self):
        self.run_async_in_thread(self.update_c_current_view())

    async def update_c_current_view(self):
        access_token = self.cp.page.client_storage.get('access_token')
        affectations = await get_all_affectations_details(access_token)

        search = self.search_class.value
        filtered_datas = list(filter(lambda x: search in x['class_id'], affectations))

        for widget in [self.monday, self.tuesday, self.wednesday, self.thursday, self.friday]:
            widget.controls.clear()
            widget.update()

        for affectation in filtered_datas:
            card = SlotCardRoom(self, affectation)
            if affectation['day'] == "day 1":
                self.monday.controls.append(card)

            elif affectation['day'] == 'day 2':
                self.tuesday.controls.append(card)

            elif affectation['day'] == 'day 3':
                self.wednesday.controls.append(card)

            elif affectation['day'] == 'day 4':
                self.thursday.controls.append(card)

            else:
                self.friday.controls.append(card)

        level = await get_level_by_class_id(search, access_token)
        self.c_new_level.value = level['level_id']

        self.cp.page.update()

    async def c_select_teacher(self, e):
        access_token = self.cp.page.client_storage.get('access_token')

        # check if the teacher is busy of free for this slot
        teacher_slot = await is_teacher_busy(self.c_new_prof.value, self.c_new_day.value, self.c_new_slot.value, access_token)
        if teacher_slot['status']:
            self.c_check_validity.name = "close"
            self.c_check_validity.color = "red"
            self.c_check_validity.update()
        else:
            self.c_check_validity.name = "check_circle"
            self.c_check_validity.color = "green"
            self.c_check_validity.update()

        # all subjects id for this teacher for this level...

        # all subjects for this level
        subjects = await get_teacher_subjects_for_level(self.c_new_prof.value, self.c_new_level.value, access_token)
        print(subjects)
        self.c_new_subject.options.clear()
        for subject in subjects:
            self.c_new_subject.options.append(
                ft.dropdown.Option(
                    key=subject['id'], text=f"{subject['short_name']}"
                )
            )

        self.cp.page.update()

    def c_on_change_teacher(self, e):
        self.run_async_in_thread(self.c_select_teacher(e))

    async def c_select_subject(self, e):
        # check hourly load for the class
        access_token = self.cp.page.client_storage.get('access_token')
        hourly_load = await get_hourly_load_by_subject_id(self.c_new_subject.value, access_token)
        nb_affectations = await count_affectations_by_subject_and_class(self.c_new_subject.value, self.search_class.value, access_token)

        if nb_affectations >= hourly_load:
            self.c_check_validity_load.name = 'close'
            self.c_check_validity_load.color = 'red'
            self.c_check_validity_load.update()
        else:
            self.c_check_validity_load.name = 'check_circle'
            self.c_check_validity_load.color = 'green'
            self.c_check_validity_load.update()

    def c_on_subject_change(self, e):
        self.run_async_in_thread(self.c_select_subject(e))

    def c_validate_affectation(self, e):
        if self.c_new_prof.value is None or self.c_new_subject.value is None:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.message.value = languages[self.lang]['error msg']
            self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
            self.cp.icon_message.color = ft.Icons.RED
            self.cp.box.open = True
            self.cp.box.update()

        else:
            if self.c_check_validity.name == 'check_circle' and self.c_check_validity_load.name == 'check_circle':
                supabase_client.table('affectations').update(
                    {
                        'subject_id': self.c_new_subject.value,
                        "teacher_id": self.c_new_prof.value,
                    }
                ).eq('id', self.c_new_affectation_id).execute()

                self.hide_one_window(self.c_new_affectation_window)

                self.cp.box.title.value = languages[self.lang]['success']
                self.cp.message.value = languages[self.lang]['successful assignment']
                self.cp.icon_message.name = ft.Icons.CHECK_CIRCLE
                self.cp.icon_message.color = ft.Colors.LIGHT_GREEN
                self.cp.box.open = True
                self.cp.box.update()

                self.c_new_subject.options.clear()
                self.c_new_subject.options.append(
                    ft.dropdown.Option(key=" ", text=f"{languages[self.lang]['select option']}")
                )
                self.c_new_subject.value = " "
                self.c_new_subject.update()

                self.c_new_prof.value = " "
                self.c_new_prof.update()

                for widget in (self.check_validity, self.c_check_validity_load):
                    widget.name = None
                    widget.color = None
                    widget.update()

                self.c_refresh_view()

            elif self.c_check_validity.name == 'close' and self.c_check_validity_load.name == 'check_circle':
                self.cp.box.title.value = languages[self.lang]['error']
                self.cp.message.value = languages[self.lang]['teacher slot busy']
                self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
                self.cp.icon_message.color = ft.Colors.RED
                self.cp.box.open = True
                self.cp.box.update()

            elif self.c_check_validity.name == 'check_circle' and self.c_check_validity_load.name == 'close':
                self.cp.box.title.value = languages[self.lang]['error']
                self.cp.message.value = languages[self.lang]['hourly load exceeded']
                self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
                self.cp.icon_message.color = ft.Colors.RED
                self.cp.box.open = True
                self.cp.box.update()

            elif self.c_check_validity.name is None or self.c_check_validity_load.name is None:
                pass

            else:
                self.cp.box.title.value = languages[self.lang]['error']
                self.cp.message.value = (f"{languages[self.lang]['teacher slot busy']}\n"
                                                f"{languages[self.lang]['hourly load exceeded']}")
                self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
                self.cp.icon_message.color = ft.Colors.RED
                self.cp.box.open = True
                self.cp.box.update()

    async def load_details(self, e):
        self.show_one_window(self.details_window)

        access_token = self.cp.page.client_storage.get('access_token')
        self.det_class.value = await get_class_code_by_id_async(self.search_class.value, access_token)

        details = await get_class_subjects_with_affectations(access_token, self.search_class.value)

        total, total_affected = 0, 0
        self.det_table.rows.clear()
        self.cp.page.update()

        for d, detail in enumerate(details):
            line_color = ft.Colors.GREY_100 if d % 2 == 0 else ft.Colors.WHITE
            total += detail['hourly load']
            total_affected += detail["nombre_affectations"]

            if detail['hourly load'] > detail["nombre_affectations"]:
                status_icon = ft.Icons.INFO_ROUNDED
                status_color = 'red'
            else:
                status_icon = ft.Icons.CHECK_CIRCLE
                status_color = 'teal'

            self.det_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Icon(status_icon, color=status_color, size=24)),
                        ft.DataCell(ft.Text(detail['short_name'].upper())),
                        ft.DataCell(ft.Text(detail['hourly load'])),
                        ft.DataCell(ft.Text(detail['nombre_affectations']))
                    ], color=line_color
                )
            )

        percent = total_affected * 100 / total
        self.det_percent.value = f"{percent:.0f}%"
        self.det_progress_bar.value = total_affected / total

        if 0 < percent < 33:
            self.det_progress_bar.color = 'deeporange'
        elif 33 <= percent < 66:
            self.det_progress_bar.color = 'amber'
        elif 66 <= percent < 100:
            self.det_progress_bar.color = 'green'
        else:
            self.det_progress_bar.color = ft.Colors.LIGHT_GREEN


        self.cp.page.update()

    def open_details_window(self, e):
        self.run_async_in_thread(self.load_details(e))

    def close_details_window(self, e):
        self.det_class.value = None
        self.det_percent.value = None
        self.det_table.rows.clear()
        self.det_progress_bar.value = None
        self.hide_one_window(self.details_window)

    # Fonctions des affectations de classes...
    # -------------------------------------------------------


















