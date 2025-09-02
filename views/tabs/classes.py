from utils.couleurs import *
from components import MyButton, MyTextButton, OneClass
from services.async_functions.general_functions import *
from services.async_functions.class_functions import *
from services.supabase_client import supabase_client
from utils.styles import *
from translations.translations import languages
import threading, asyncio, time


class Classes(ft.Container):
    def __init__(self, cp: object):
        super().__init__(
            expand=True, alignment=ft.alignment.center, bgcolor=MAIN_COLOR
        )
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
        self.table = ft.DataTable(
            **datatable_style, columns=[
                ft.DataColumn(ft.Text(choice)) for choice in [
                    "Label", languages[self.lang]['capacity'].capitalize(), languages[self.lang]['head count'].capitalize(),
                    languages[self.lang]['rate'].capitalize(), languages[self.lang]['head teacher'].capitalize(), 'Actions'
                ]
            ]
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
                                    ft.Text(languages[self.lang]['menu classes'].capitalize(), size=24, font_family="PEB"),
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

        self.main_window = ft.Container(
            expand=True, padding=20, border_radius=16,
            content=ft.Column(
                controls=[
                    self.top_menu,
                    ft.Row(
                        controls=[
                            ft.Row(
                                controls=[
                                    MyTextButton( languages[self.lang]['new class'], self.open_new_class_window),
                                ]
                            ),
                            self.search
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Container(
                        padding=0, border_radius=16, border=ft.border.all(1, ft.Colors.GREY_300),
                        expand=True, bgcolor='white', content=ft.ListView(
                            expand=True, controls=[self.table]
                        )
                    )
                ]
            )
        )

        # new class window _______________________________________________________________________________
        self.new_code = ft.TextField(
            **login_style, prefix_icon=ft.Icons.ROOFING, expand=True, label='Label'
        )
        self.new_level = ft.Dropdown(
            **drop_style, prefix_icon=ft.Icons.ACCOUNT_BALANCE_OUTLINED, expand=True,
            label=languages[self.lang]['level'], menu_height=200
        )
        self.new_capacity = ft.TextField(
            **login_style, prefix_icon=ft.Icons.GROUPS_3_OUTLINED, expand=True,
            text_align=ft.TextAlign.RIGHT, input_filter=ft.NumbersOnlyInputFilter(),
            label=languages[self.lang]['capacity']
        )
        self.new_progression_text = ft.Text("0 %", size=16, font_family="PEB", color='white')
        self.new_progression_container = ft.Container(
            padding=5, border_radius=8, bgcolor="black",
            content=ft.Row([self.new_progression_text], alignment=ft.MainAxisAlignment.CENTER)
        )
        self.new_bar = ft.ProgressBar(
            height=5, border_radius=16, color=BASE_COLOR, bgcolor=SECOND_COLOR,
            expand=True
        )
        self.new_check = ft.Icon(
            'check_circle', color=BASE_COLOR, size=24,
            scale=ft.Scale(0), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN)
        )
        self.new_class_window = ft.Container(
            **ct_style,
            content=ft.Container(
                **intern_ct_style,
                width=500, height=520, padding=0,
                content=ft.Column(
                    expand=True,
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(
                                bottom=ft.BorderSide(1, MAIN_COLOR)
                            ),
                            border_radius=ft.border_radius.only(top_left=8, top_right=8),
                            content=ft.Row(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.ADD_HOME_OUTLINED, size=24, color="black"),
                                            ft.Text(languages[self.lang]['new class'], size=20, font_family='PEB'),
                                        ]
                                    ),
                                    ft.IconButton('close', icon_color='black87', bgcolor=MAIN_COLOR,
                                                  on_click=self.close_new_class_window),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            padding=20, border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True,
                            bgcolor='white',
                            content=ft.Column(
                                expand=True, scroll=ft.ScrollMode.AUTO,
                                controls=[
                                    self.new_level,
                                    ft.Divider(color=ft.Colors.TRANSPARENT),
                                    self.new_code, self.new_capacity,
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Column(
                                        spacing=0, controls=[
                                            ft.Text(
                                                languages[self.lang]['slots generation'].upper(), size=16,
                                                font_family='PPB', color='black'
                                            ),
                                            ft.Divider(height=1, thickness=1),
                                        ]
                                    ),
                                    ft.Container(
                                        alignment=ft.alignment.center, padding=10,
                                        content=ft.Row(
                                            controls=[
                                                self.new_bar, self.new_check, self.new_progression_container
                                            ]
                                        )
                                    ),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Row(
                                        [MyButton(languages[self.lang]['valid'], 'check', 180, self.add_new_class)]
                                    )
                                ], spacing=10,
                            )
                        )
                    ]
                )
            )
        )

        # Details window...
        self.det_main_teacher = ft.Text(size=16, font_family='PPM')
        self.det_count = ft.Text(size=16, font_family='PPM')
        self.det_level = ft.Text(size=16, font_family='PPM')

        self.det_table_registered = ft.DataTable(
            **datatable_style, columns=[
                ft.DataColumn(ft.Text(option)) for option in [
                    languages[self.lang]['name'].capitalize(), languages[self.lang]['gender'].capitalize()
                ]
            ]
        )
        self.det_table_affectations = ft.DataTable(
            **datatable_style, columns=[
                ft.DataColumn(ft.Text(option)) for option in [
                    languages[self.lang]['day'].capitalize(), languages[self.lang]['slot'].capitalize(),
                    languages[self.lang]['subject'].capitalize(), languages[self.lang]['teacher'].capitalize(),
                ]
            ]
        )

        self.dt_container = ft.Column(
            expand=True,
            controls=[
                ft.Text(languages[self.lang]['loading screen'], size=18, font_family='PPR'),
                ft.ProgressBar(color=BASE_COLOR)
            ], alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

        self.st_details_window = ft.Container(
            **ct_style, content=ft.Container(
                **intern_ct_style, width=850, height=700, padding=0,
                content=ft.Column(
                    expand=True,
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20,
                            border=ft.border.only(bottom=ft.BorderSide(1, MAIN_COLOR)),
                            border_radius=ft.border_radius.only(top_left=16, top_right=16),
                            content=ft.Row(
                                controls=[
                                    ft.Text(languages[self.lang]["class details"].capitalize(), size=20, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=MAIN_COLOR,
                                        on_click=self.close_details_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(top=ft.BorderSide(1, MAIN_COLOR)),
                            border_radius=ft.border_radius.only(bottom_left=16, bottom_right=16), expand=True,
                            content=ft.Column(
                                expand=True,
                                controls=[
                                    self.dt_container
                                ]
                            )
                        )
                    ], spacing=0
                )
            )
        )

        # Contenu principal...
        self.content = ft.Stack(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(languages[self.lang]['loading screen'], size=18, font_family='PPR'),
                        ft.ProgressRing(color=BASE_COLOR)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20,
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ], alignment=ft.alignment.center
        )

        # lancer le chargement des données...
        self.on_mount()

    async def build_main_view(self):
        self.content.controls.clear()

        for widget in (
            self.main_window, self.new_class_window, self.st_details_window
        ):
            self.content.controls.append(
                widget
            )

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
        await self.load_levels()

    def on_mount(self):
        self.run_async_in_thread(self.on_init_async())

    async def load_levels(self):
        items = await get_all_level_codes(self.cp.page.client_storage.get('access_token'))

        for item in items:
            self.new_level.options.append(
                ft.dropdown.Option(key=item['id'], text=f"{item['code']}")
            )
        self.new_level.update()

    async def load_datas(self):
        access_token = self.cp.page.client_storage.get("access_token")
        year_id = self.cp.year_id

        # mettre à jour les séquences
        active_sequence = await get_active_sequence(access_token)
        self.active_sequence.value = languages[self.lang][active_sequence['name']]
        self.active_quarter.value = languages[self.lang][active_sequence['quarter']]
        self.active_sequence.data = active_sequence['name']
        self.active_quarter.data = active_sequence['quarter']

        details = await get_classes_details_by_year(access_token, year_id)
        self.table.rows.clear()

        for i, item in enumerate(details):
            line_color = ft.Colors.GREY_100 if i % 2 == 0 else ft.Colors.WHITE
            rate = item['student_count'] / item['capacity']
            if item['head_teacher_name']:
                teacher_name = f"{item['head_teacher_name']} {item['head_teacher_surname']}"
            else:
                teacher_name = ''

            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(f"{item['code']}")),
                        ft.DataCell(ft.Text(f"{item['capacity']}")),
                        ft.DataCell(ft.Text(f"{item['student_count']}")),
                        ft.DataCell(
                            ft.ProgressBar(
                                value=rate, height=5, border_radius=16,
                                bgcolor=MAIN_COLOR, color=BASE_COLOR
                            )
                        ),
                        ft.DataCell(ft.Text(f"{teacher_name}")),
                        ft.DataCell(
                            ft.IconButton(
                                ft.Icons.FORMAT_LIST_BULLETED, icon_size=24, icon_color='black',
                                data=item, on_click=self.show_class_details
                            )
                        )
                    ], color=line_color
                )
            )

        await self.build_main_view()

    async def load_filter_datas(self, e):
        access_token = self.cp.page.client_storage.get("access_token")
        year_id = self.cp.year_id

        # mettre à jour les séquences
        active_sequence = await get_active_sequence(access_token)
        self.active_sequence.value = languages[self.lang][active_sequence['name']]
        self.active_quarter.value = languages[self.lang][active_sequence['quarter']]
        self.active_sequence.data = active_sequence['name']
        self.active_quarter.data = active_sequence['quarter']

        search = self.search.value if self.search.value else ''
        details = await get_classes_details_by_year(access_token, year_id)
        self.table.rows.clear()

        filtered_datas = list(filter(lambda x: search in x['code'], details))

        for i, item in enumerate(filtered_datas):
            line_color = ft.Colors.GREY_100 if i % 2 == 0 else ft.Colors.WHITE
            rate = item['student_count'] / item['capacity']
            if item['head_teacher_name']:
                teacher_name = f"{item['head_teacher_name']} {item['head_teacher_surname']}"
            else:
                teacher_name = ''

            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(f"{item['code']}")),
                        ft.DataCell(ft.Text(f"{item['capacity']}")),
                        ft.DataCell(ft.Text(f"{item['student_count']}")),
                        ft.DataCell(
                            ft.ProgressBar(
                                value=rate, height=5, border_radius=16,
                                bgcolor=MAIN_COLOR, color=BASE_COLOR
                            )
                        ),
                        ft.DataCell(ft.Text(f"{teacher_name}")),
                        ft.DataCell(
                            ft.IconButton(
                                ft.Icons.FORMAT_LIST_BULLETED, icon_size=24, icon_color='black',
                                data=item, on_click=self.show_class_details
                            )
                        )
                    ], color=line_color
                )
            )

        await self.build_main_view()

    def filter_datas(self, e):
        self.run_async_in_thread(self.load_filter_datas(e))

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

    def open_new_class_window(self, e):
        if self.cp.page.client_storage.get("role") in ['principal', 'préfet']:
            self.show_one_window(self.new_class_window)
        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.message.value = languages[self.lang]['error rights']
            self.cp.box.open = True
            self.cp.box.update()

    def close_new_class_window(self, e):
        self.new_bar.value = 0
        self.hide_one_window(self.new_class_window)

    def add_new_class(self, e):
        count = 0
        days = ['day 1', 'day 2', 'day 3', 'day 4', 'day 5']
        slots = ['07:30-08:30', '08:30-09:30', '09:30-10:30', '10:45-11:45', '11:45-12:45', '13:00-14:00', '14:00-15:00', '15:00-16:00']

        if self.new_level.value and self.new_code.value and self.new_capacity.value:

            # create a class
            resp = supabase_client.table('classes').insert(
                {'code': self.new_code.value, 'capacity': int(self.new_capacity.value), 'level_id': self.new_level.value}
            ).execute()
            time.sleep(2)
            print('created')

            # get id of the new created class
            resp = supabase_client.table('classes').select('id').eq('code', self.new_code.value).execute()
            class_id = resp.data[0]['id']
            print(class_id)
            print("année id", self.cp.year_id)

            # create affectations
            for day in days:
                for slot in slots:
                    supabase_client.table('affectations').insert(
                        {'year_id': self.cp.year_id, 'class_id': class_id, 'nb_hour': 1, 'day': day, 'slot': slot}
                    )
                    count += 1
                    value = count / 40
                    self.new_bar.value = value
                    self.new_progression_text = f"{value:.0f} %"
                    self.new_bar.update()

                    if 0 < value <= 0.3:
                        color = 'red'
                    elif 0.3 < value < 0.6:
                        color = BASE_COLOR
                    elif 0.6 < value <= 0.99:
                        color = ft.Colors.LIGHT_GREEN
                    else:
                        color = 'green'

                    self.new_progression_container.bgcolor = color
                    self.new_progression_container.update()

            for widget in (self.new_code, self.new_level, self.new_capacity):
                widget.value = None
                widget.update()

            self.new_check.scale = 1
            self.new_check.update()
            self.cp.box.title.value = languages[self.lang]['success']
            self.cp.message.value = languages[self.lang]['class creation success']
            self.cp.icon_message.name = ft.Icons.CHECK_CIRCLE
            self.cp.icon_message.color = ft.Colors.LIGHT_GREEN
            self.cp.box.open = True
            self.cp.box.update()

            time.sleep(2)
            self.new_check.scale = 0
            self.new_check.update()
            self.on_mount()

        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.message.value = languages[self.lang]['error msg']
            self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
            self.cp.icon_message.color = ft.Colors.RED
            self.cp.box.open = True
            self.cp.box.update()

    async def open_details_window(self, e):
        self.det_level.value = e.control.data['level_code']
        self.det_count.value = e.control.data['student_count']

        access_token = self.cp.page.client_storage.get('access_token')
        self.show_one_window(self.st_details_window)

        prof_datas = f"{e.control.data['head_teacher_name']} {e.control.data['head_teacher_surname']}"

        self.det_main_teacher.value = prof_datas

        # students ___________________________________
        details = await get_students_by_class_id(e.control.data['id'], access_token)
        self.det_table_registered.rows.clear()

        for d, detail in enumerate(details):
            line_color = ft.Colors.GREY_100 if d % 2 == 0 else ft.Colors.WHITE
            self.det_table_registered.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(f"{detail['name']} {detail['surname']}".upper())),
                        ft.DataCell(ft.Text(f"{detail['gender']}"))
                    ], color=line_color
                )
            )

        # schedule _______________________________________
        slots = await get_class_schedule(e.control.data['id'], access_token)
        self.det_table_affectations.rows.clear()

        for s, slot in enumerate(slots):
            line_color = ft.Colors.GREY_100 if s % 2 == 0 else ft.Colors.WHITE
            self.det_table_affectations.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(languages[self.lang][slot['day']])),
                        ft.DataCell(ft.Text(slot['slot'])),
                        ft.DataCell(ft.Text(slot['short_name'])),
                        ft.DataCell(ft.Text(slot['teacher_name'].upper())),
                    ], color=line_color
                )
            )

        self.build_details_container()

    def show_class_details(self, e):
        self.run_async_in_thread(self.open_details_window(e))

    def close_details_window(self, e):
        self.hide_one_window(self.st_details_window)
        self.dt_container.controls.clear()
        self.dt_container.controls.append(
            ft.Column(
                controls=[
                    ft.Text(languages[self.lang]['loading screen'], size=18, font_family='PPR'),
                    ft.ProgressRing(color=BASE_COLOR)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER
            )
        )
        self.cp.page.update()

    def build_details_container(self):
        self.dt_container.controls.clear()

        self.dt_container.controls.append(
            ft.Column(
                expand=True,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.ACCOUNT_BALANCE_OUTLINED, size=24, color=ACCENT_PLUS_COLOR),
                                    ft.Text(languages[self.lang]['level'], size=16, color='grey',
                                            font_family='PPM'),
                                    self.det_level,

                                ], spacing=7
                            ),
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.ASSIGNMENT_IND, size=24, color=ACCENT_PLUS_COLOR),
                                    ft.Text(languages[self.lang]['head teacher'], size=16,
                                            color='grey', font_family='PPM'),
                                    self.det_main_teacher,

                                ], spacing=7
                            ),
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.GROUPS, size=24, color=ACCENT_PLUS_COLOR),
                                    ft.Text(languages[self.lang]['head count'], size=16,
                                            color='grey',
                                            font_family='PPM'),
                                    self.det_count,

                                ], spacing=7
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    ft.Tabs(
                        tab_alignment=ft.TabAlignment.START, selected_index=0, expand=True,
                        animation_duration=300,
                        unselected_label_color='black54', label_color='black',
                        indicator_border_radius=24, indicator_border_side=ft.BorderSide(2, ACCENT_PLUS_COLOR),
                        indicator_tab_size=True,
                        tabs=[
                            ft.Tab(
                                tab_content=ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.GROUPS, size=24),
                                        ft.Text(languages[self.lang]["registered students list"].capitalize(),
                                                size=16,
                                                font_family="PPM")
                                    ]
                                ),
                                content=ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                                            ft.Container(
                                                padding=0,
                                                expand=True, border=ft.border.all(1, 'grey300'),
                                                border_radius=16,
                                                content=ft.ListView(
                                                    expand=True, controls=[self.det_table_registered]
                                                )
                                            )
                                        ]
                                    )
                                )
                            ),
                            ft.Tab(
                                tab_content=ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.SCHOOL, size=24),
                                        ft.Text(languages[self.lang]['menu time table'].capitalize(), size=16,
                                                font_family="PPM")
                                    ]
                                ),
                                content=ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                                            ft.Container(
                                                padding=0, expand=True,
                                                border=ft.border.all(1, 'grey300'),
                                                border_radius=16,
                                                content=ft.ListView(
                                                    expand=True, controls=[self.det_table_affectations]
                                                )
                                            )
                                        ]
                                    )
                                )
                            )
                        ]
                    )
                ]
            )
        )
        self.cp.page.update()




