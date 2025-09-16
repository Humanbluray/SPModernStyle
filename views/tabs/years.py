from utils.couleurs import *
from translations.translations import languages
from components import MyButton, MyTextButton
from services.async_functions.general_functions import get_active_sequence
from services.async_functions.sequences_functions import *
from services.supabase_client import school_code
from utils.styles import *
from utils.useful_functions import add_separator
import threading, openpyxl, uuid, statistics, datetime, time
import pandas as pd
from io import BytesIO

DOCUMENTS_BUCKET = 'documents'


class Years(ft.Container):
    def __init__(self, cp: object):
        super().__init__(
            expand=True, alignment=ft.alignment.center, bgcolor=MAIN_COLOR
        )
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
            padding=ft.padding.only(7, 5, 7, 5),
            border_radius=10,
            border=ft.border.all(1, BASE_COLOR),
            bgcolor=SECOND_COLOR,
            alignment=ft.alignment.center,
            content=ft.Row(
                controls=[
                    ft.Icon('calendar_month_outlined', size=16, color='black'),
                    self.active_sequence
                ]
            )
        )

        # Main window...
        self.table_years = ft.DataTable(
            **datatable_style, expand=True,
            columns=[
                ft.DataColumn(ft.Text(option))
                for option in [
                    languages[lang]['label'].capitalize(), languages[lang]['year'].capitalize(),
                    languages[lang]['status'].capitalize(), languages[lang]['start'].capitalize(),
                    languages[lang]['end'].capitalize(),
                ]
            ]
        )
        self.main_window = ft.Container(
            expand=True, padding=20, border_radius=16,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.Container(
                        padding=ft.padding.only(10, 0, 10, 0),
                        content=ft.Row(
                            controls=[
                                ft.Row(
                                    controls=[
                                        MyTextButton(
                                            languages[lang]['close sequence'], ft.Icons.EVENT_BUSY_OUTLINED,
                                            self.open_check_sequence_window
                                        ),
                                        MyTextButton(
                                            languages[lang]['close school year'], ft.Icons.LOCK_OUTLINED,
                                            self.open_generation_window
                                        )
                                    ]
                                ),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        )
                    ),
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, size=36, color='amber'),
                            ft.Text(
                                languages[lang]['caution'].upper(), size=24, font_family='PBL',
                            )
                        ], alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Container(
                        padding=10, content=ft.Row(
                        controls=[
                                ft.TextField(
                                    languages[lang]['caution text'], multiline=True,
                                    border=ft.InputBorder.NONE, expand=True,
                                    text_style=ft.TextStyle(size=16, font_family='PPM'),
                                    text_align=ft.TextAlign.CENTER
                                )
                            ], alignment=ft.MainAxisAlignment.CENTER
                        )
                    ),
                    ft.Container(
                        expand=True, padding=20, border=ft.border.all(1, MAIN_COLOR),
                        border_radius=16,
                        content=ft.ListView(
                            expand=True, controls=[
                                ft.Row(
                                    controls=[
                                        self.table_years
                                    ]
                                )
                            ]
                        )
                    )
                ]
            )
        )
        # close year window ...
        self.new_year_label = ft.TextField(
            **login_style, width=150, read_only=True, prefix_icon=ft.Icons.CALENDAR_TODAY_OUTLINED,
            label='label'
        )
        self.new_year_short = ft.TextField(
            **login_style, width=200, read_only=True, prefix_icon=ft.Icons.LABEL_OUTLINED,
            label=languages[lang]['new school year']
        )
        self.new_tranche_1 = ft.TextField(
            **login_style, width=145, input_filter=ft.NumbersOnlyInputFilter(),
            prefix_icon=ft.Icons.MONETIZATION_ON_OUTLINED,
            text_align=ft.TextAlign.RIGHT, label=languages[lang]['fees part 1']
        )
        self.new_tranche_2 = ft.TextField(
            **login_style, width=145, input_filter=ft.NumbersOnlyInputFilter(),
            prefix_icon=ft.Icons.MONETIZATION_ON_OUTLINED,
            text_align=ft.TextAlign.RIGHT, label=languages[lang]['fees part 1']
        )
        self.new_tranche_3 = ft.TextField(
            **login_style, width=145, input_filter=ft.NumbersOnlyInputFilter(),
            prefix_icon=ft.Icons.MONETIZATION_ON_OUTLINED,
            text_align=ft.TextAlign.RIGHT, label=languages[lang]['fees part 1']
        )
        self.new_reg_fees = ft.TextField(
            **login_style, width=145, input_filter=ft.NumbersOnlyInputFilter(),
            prefix_icon=ft.Icons.MONETIZATION_ON_OUTLINED,
            text_align=ft.TextAlign.RIGHT, label=languages[lang]['registration']
        )
        self.switch_fees = ft.Switch(
            **switch_style, on_change=self.on_fees_switch_change
        )
        self.switch_affectations = ft.Switch(
            **switch_style
        )
        self.new_affectations_bar = ft.ProgressBar(
            color=BASE_COLOR, bgcolor=SECOND_COLOR, width=100, height=5, border_radius=16, value=0
        )
        self.new_affectations_status = ft.Text('0 %', size=12, font_family='PPB')

        self.new_year_informations_window = ft.Container(
            **ct_style, content=ft.Container(
                **intern_ct_style, width=700,
                content=ft.Column(
                    spacing=0, expand=True, scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Container(
                            **top_ct_style, content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['new year informations'], size=20, font_family='PPB'),
                                    ft.IconButton('close', icon_color='black87', bgcolor=MAIN_COLOR,
                                                  on_click=self.close_new_year_infos_window),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            **bottom_ct_style, content=ft.Column(
                                spacing=10, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    # label...
                                    ft.Container(
                                        padding=10,
                                        content=ft.Column(
                                            controls=[
                                                ft.Container(
                                                    bgcolor='#f0f0f6', expand=True, border_radius=8, padding=10,
                                                    alignment=ft.alignment.center,
                                                    content=ft.Text(languages[lang]['1- new school year'].upper(),
                                                                    size=16,
                                                                    font_family='PPB'),
                                                ),
                                                ft.Row(
                                                    controls=[self.new_year_label, self.new_year_short],
                                                    alignment=ft.MainAxisAlignment.SPACE_AROUND
                                                ),
                                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                        )
                                    ),
                                    # new school fees...
                                    ft.Container(
                                        padding=10,
                                        content=ft.Column(
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            controls=[
                                                ft.Container(
                                                    bgcolor='#f0f0f6', expand=True, border_radius=8, padding=10,
                                                    alignment=ft.alignment.center,
                                                    content=ft.Text(languages[lang]['2- new school fees'].upper(),
                                                                    size=16,
                                                                    font_family='PPB'),
                                                ),
                                                ft.Row(
                                                    controls=[
                                                        ft.Text(languages[lang]['renew tuition fees'], size=16,
                                                                font_family='PPM'),
                                                        self.switch_fees
                                                    ], alignment=ft.MainAxisAlignment.CENTER
                                                ),
                                                ft.Row(
                                                    controls=[
                                                        self.new_reg_fees, self.new_tranche_1,
                                                        self.new_tranche_2, self.new_tranche_3
                                                    ], alignment=ft.MainAxisAlignment.SPACE_AROUND
                                                ),
                                            ]
                                        )
                                    ),
                                    # renew affectations...
                                    ft.Container(
                                        padding=10,
                                        content=ft.Column(
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            controls=[
                                                ft.Container(
                                                    bgcolor='#f0f0f6', expand=True, border_radius=8, padding=10,
                                                    alignment=ft.alignment.center,
                                                    content=ft.Text(languages[lang]['3- manage affectations'].upper(),
                                                                    size=16,
                                                                    font_family='PPB'),
                                                ),
                                                ft.Row(
                                                    controls=[
                                                        ft.Text(
                                                            languages[lang]['renew affectations'], size=16,
                                                            font_family='PPM',
                                                        ),
                                                        self.switch_affectations
                                                    ], spacing=5, alignment=ft.MainAxisAlignment.CENTER
                                                ),
                                            ],

                                        )
                                    ),
                                    MyButton(
                                        languages[lang]['valid'], 'check', 200, self.open_final_window
                                    )
                                ]
                            )
                        )
                    ]
                )
            )
        )
        self.final_window = ft.Container(
            **ct_style, content=ft.Container(
                **intern_ct_style, width=400,
                content=ft.Column(
                    spacing=0, expand=True, scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Container(
                            **top_ct_style, content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['new year generation'].capitalize(), size=20, font_family='PPB'),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            **bottom_ct_style, content=ft.Column(
                                spacing=10, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Icon(ft.Icons.WARNING_AMBER, color='red', size=24),
                                    ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.GPP_BAD, color='red', size=24),
                                            ft.Text(languages[lang]['last step'], size=16, color='red',
                                                    font_family='PPB')
                                        ], alignment=ft.MainAxisAlignment.CENTER
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text('Progression', size=16, font_family='PPM', color='grey'),
                                            ft.Row(
                                                alignment=ft.MainAxisAlignment.CENTER,
                                                controls=[
                                                    self.new_affectations_bar, self.new_affectations_status
                                                ]
                                            )
                                        ], spacing=0,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                    )
                                ]
                            )
                        )
                    ]
                )
            )
        )
        self.generation_window = ft.Container(
            **ct_style, content=ft.Container(
                **intern_ct_style, width=600,
                content=ft.Column(
                    spacing=0, expand=True, scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Container(
                            **top_ct_style, content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['new year generation'], size=20, font_family='PPB'),
                                    ft.IconButton('close', icon_color='black87', bgcolor=MAIN_COLOR,
                                                  on_click=self.close_generation_window),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            **bottom_ct_style, content=ft.Column(
                                spacing=10, expand=True,
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.GPP_BAD, color='red', size=24),
                                            ft.Text(languages[lang]['caution'], size=16, color='red', font_family='PPB')
                                        ], alignment=ft.MainAxisAlignment.CENTER
                                    ),
                                    ft.TextField(
                                        languages[lang]['generation caution'], multiline=True,
                                        border=ft.InputBorder.NONE, expand=True,
                                        text_style=ft.TextStyle(size=16, font_family='PPM', color='black87'),
                                        text_align=ft.TextAlign.CENTER
                                    ),
                                    ft.Container(
                                        padding=10,
                                        content=MyButton(
                                            languages[lang]['confirm'], 'check', None,
                                            self.open_new_year_infos_window
                                        )
                                    )
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            )
                        )
                    ]
                )
            )
        )

        self.check_table = ft.DataTable(
            **datatable_style, columns=[
                ft.DataColumn(ft.Text(option)) for option in [
                    languages[lang]['class'], languages[lang]['head count'],
                    languages[lang]['nb subjects'], languages[lang]['expected'],
                    languages[lang]['total missing'], ""
                ]
            ]
        )
        self.total_classes = ft.Text("-", size=18, font_family="PPM")
        self.check_nb_classes = ft.Text("-", size=18, font_family="PPM")
        self.check_status = ft.Text('0 %', size=18, font_family='PPM')
        self.nb_missing = ft.Text('0', size=18, font_family='PPM')
        self.nb_total_missing = ft.Text('0', size=18, font_family='PPM')
        self.nb_students = ft.Text('0', size=18, font_family='PPM')
        self.nb_notes_attendues = ft.Text('0', size=18, font_family='PPM')
        self.class_checked = ft.Text('0', size=18, font_family='PPM')
        self.no_data = ft.Text(size=18, color='red', font_family='PPB', value=languages[lang]['no data'], visible=False)
        self.check_bt_close_despite = MyButton(
            languages[lang]['close despite missing'], 'info_outlined', None, self.close_sequence_despite
        )
        self.check_bt_close_despite.visible = False
        self.report_book_bar = ft.ProgressBar(
            color=BASE_COLOR, bgcolor=SECOND_COLOR, width=100, height=5, border_radius=16,
        )
        self.report_book_status = ft.Text("0 %", size=16, font_family='PPM')
        self.cv_bar = ft.ProgressBar(
            color=BASE_COLOR, bgcolor=SECOND_COLOR, width=100, height=5, border_radius=16,
        )
        self.cv_status = ft.Text("0 %", size=16, font_family='PPM')
        self.report_book_container = ft.Container(
            padding=10, border_radius=16, visible=False,
            content=ft.Row(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(languages[lang]['generation sequence average'], size=12, font_family='PPM',
                                    color='grey'),
                            ft.Row(
                                controls=[
                                    self.report_book_bar, self.report_book_status
                                ]
                            )
                        ], alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Row(
                        controls=[
                            ft.Text(languages[lang]['class statistics'], size=12, font_family='PPM',
                                    color='grey'),
                            ft.Row(
                                controls=[
                                    self.cv_bar, self.cv_status
                                ]
                            )
                        ], alignment=ft.MainAxisAlignment.CENTER
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        )
        self.check_notes_bar = ft.ProgressBar(
            color=BASE_COLOR, bgcolor=SECOND_COLOR, width=100, height=5, border_radius=16,
        )
        self.checking_container = ft.Container(
            padding=10, border_radius=16, visible=True,
            content=ft.Column(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(languages[lang]["checking"].upper(), size=16, font_family="PEB"),
                                    ft.Icon(ft.Icons.CHECKLIST, size=28, color="red")
                                ], alignment=ft.MainAxisAlignment.CENTER
                            ),
                            ft.Divider(height=1, thickness=1)
                        ], spacing=0,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    ft.Row(
                        controls=[
                            ft.Text(languages[lang]['total classes'], size=18, font_family="PPM"),
                            self.total_classes
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Divider(height=1, thickness=1),
                    ft.Row(
                        controls=[
                            ft.Text(languages[lang]['checked classes'], size=18, font_family="PPM"),
                            self.check_nb_classes
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Divider(height=1, thickness=1),
                    ft.Row(
                        controls=[
                            ft.Text(languages[lang]['class checked'], size=18, font_family="PPM"),
                            self.class_checked,
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Divider(height=1, thickness=1),
                    ft.Row(
                        controls=[
                            ft.Text(languages[lang]['head count'], size=18, font_family="PPM"),
                            self.nb_students,
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Divider(height=1, thickness=1),
                    ft.Row(
                        controls=[
                            ft.Text(languages[lang]['expected'], size=18, font_family="PPM"),
                            self.nb_notes_attendues,
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Divider(height=1, thickness=1),
                    ft.Row(
                        controls=[
                            ft.Text(languages[lang]['nb missing notes'], size=18, font_family="PPM"),
                            self.nb_missing
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Row(
                        spacing=10, controls=[
                            ft.Text('progression', size=18, font_family='PPM'),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    self.check_notes_bar, self.check_status
                                ]
                            )
                        ], alignment=ft.MainAxisAlignment.CENTER
                    )
                ]
            )
        )
        self.report_container = ft.Container(
            visible=False,
            content=ft.Column(
                controls=[
                    ft.Text(languages[lang]['report'].upper(), size=18, font_family="PEB"),
                    ft.Container(
                        expand=True, border=ft.border.all(1, MAIN_COLOR), border_radius=16, padding=0,
                        content=ft.ListView(expand=True, controls=[self.check_table], height=400)
                    ),
                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                    ft.Container(
                        padding=10, content=ft.Row(
                            controls=[
                                self.check_bt_close_despite
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        )
                    ),
                    self.report_book_container
                ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

        # close sequence window...
        self.check_sequence_window = ft.Container(
            **ct_style, content=ft.Container(
                **intern_ct_style, width=800,
                content=ft.Column(
                    spacing=0, expand=True, scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Container(
                            **top_ct_style, content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['check missing notes'], size=20, font_family='PPB'),
                                    ft.IconButton('close', icon_color='black87', bgcolor=MAIN_COLOR,
                                                  on_click=self.close_check_sequence_window),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            **bottom_ct_style, content=ft.Column(
                                spacing=10, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[

                                    # vérification...
                                    self.checking_container,
                                    # Rapport ...
                                    self.report_container,
                                    # génération des statistiques...

                                ]
                            )
                        )
                    ]
                )
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

    def build_main_view(self):
        self.content.controls.clear()
        self.content.controls = [
            self.main_window, self.generation_window,
            self.check_sequence_window, self.new_year_informations_window
        ]
        self.cp.page.update()

    def show_one_window(self, window_to_show):
        # La surcouche (ct_registrations) est mise en avant
        window_to_show.visible = True
        window_to_show.opacity = 1
        self.cp.top_menu.opacity = 0.2
        self.cp.top_menu.disabled = True
        self.cp.page.update()

    def hide_one_window(self, window_to_hide):
        # La surcouche est masquée
        window_to_hide.visible = False
        window_to_hide.opacity = 0
        self.cp.top_menu.opacity = 1
        self.cp.top_menu.disabled = False
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
        active_sequence = await get_active_sequence(access_token)
        self.active_sequence.value = languages[self.lang][active_sequence['name']]
        self.active_quarter.value = languages[self.lang][active_sequence['quarter']]
        self.active_sequence.data = active_sequence['name']
        self.active_quarter.data = active_sequence['quarter']

        years_datas = await get_all_years(access_token)
        self.table_years.rows.clear()

        # table des années
        for item in years_datas:

            if item['active']:
                my_icon = ft.Icons.CHECK
                color = "teal"
                background_color = 'teal50'
                text_icon = 'active'

            else:
                my_icon = None
                color = "teal"
                background_color = 'teal50'
                text_icon = 'inactive'

            self.table_years.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(item['name'])),
                        ft.DataCell(ft.Text(item['short'])),
                        ft.DataCell(
                            ft.Container(
                                bgcolor=background_color, padding=5, border_radius=10, width=100,
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(my_icon, size=16, color=color),
                                        ft.Text(text_icon, size=16, color=color, font_family='PPM'),
                                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=3
                                )
                            )
                        ),
                        ft.DataCell(ft.Text(item['start'])),
                        ft.DataCell(ft.Text(item['end'])),
                    ]
                )
            )

        self.build_main_view()

    async def load_sequences_informations_despite(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        year_id = self.cp.year_id

        # on clôture la séquence...
        active_sequence = await get_active_sequence(access_token)
        next_seq_dict = {
            'sequence 1': 'sequence 2',
            'sequence 2': 'sequence 3',
            'sequence 3': 'sequence 4',
            'sequence 4': 'sequence 5',
            'sequence 5': 'sequence 6',
        }

        if active_sequence['name'] != 'sequence 6':
            next_sequence = next_seq_dict[active_sequence['name']]

            # on met à jour les séquences...
            await update_sequence_active_status(access_token, active_sequence['name'], False)
            await update_sequence_active_status(access_token, next_sequence, True)

            # on récupère la nouvelle séquence
            new_active_sequence = await get_active_sequence(access_token)

            if new_active_sequence['name'] == "sequence 3":
                # on met à jour les trimestres...
                next_quarter = 'quarter 2'
                previous_quarter = 'quarter 1'
                await update_quarter_active_status(access_token, next_quarter, True)
                await update_quarter_active_status(access_token, previous_quarter, False)
                self.active_quarter.data = next_quarter
                self.active_quarter.value = languages[self.lang][next_quarter]

            elif new_active_sequence['name'] == 'sequence 5':
                # on met à jour les trimestres...
                next_quarter = 'quarter 3'
                previous_quarter = 'quarter 2'
                await update_quarter_active_status(access_token, next_quarter, True)
                await update_quarter_active_status(access_token, previous_quarter, False)
                self.active_quarter.data = next_quarter
                self.active_quarter.value = languages[self.lang][next_quarter]

            else:
                pass

            # on met à jour l'affichage du home...
            self.on_mount()
            self.cp.page.update()

            self.cp.box.title.value = languages[self.lang]['success']
            self.cp.message.value = languages[self.lang]['sequence closed']
            self.cp.icon_message.name = ft.Icons.CHECK_CIRCLE
            self.cp.icon_message.color = ft.Colors.LIGHT_GREEN
            self.cp.box.open = True
            self.cp.box.update()

        else:
            pass

    def close_sequence_despite(self, e):
        self.run_async_in_thread(self.load_sequences_informations_despite(e))

    async def load_sequence_informations_normally(self):
        access_token = self.cp.page.client_storage.get('access_token')
        active_sequence = await get_active_sequence(access_token)

        next_seq_dict = {
            'sequence 1': 'sequence 2',
            'sequence 2': 'sequence 3',
            'sequence 3': 'sequence 4',
            'sequence 4': 'sequence 5',
            'sequence 5': 'sequence 6',
        }

        if active_sequence['name'] != 'sequence 6':
            next_sequence = next_seq_dict[active_sequence['name']]

            # on met à jour les séquences...
            await update_sequence_active_status(access_token, active_sequence['name'], False)
            await update_sequence_active_status(access_token, next_sequence, True)

            # on récupère la nouvelle séquence
            new_active_sequence = await get_active_sequence(access_token)

            if new_active_sequence['name'] == "sequence 3":
                # on met à jour les trimestres...
                next_quarter = 'quarter 2'
                previous_quarter = 'quarter 1'
                await update_quarter_active_status(access_token, next_quarter, True)
                await update_quarter_active_status(access_token, previous_quarter, False)
                self.active_quarter.data = next_quarter
                self.active_quarter.value = languages[self.lang][next_quarter]

            elif new_active_sequence['name'] == 'sequence 5':
                # on met à jour les trimestres...
                next_quarter = 'quarter 3'
                previous_quarter = 'quarter 2'
                await update_quarter_active_status(access_token, next_quarter, True)
                await update_quarter_active_status(access_token, previous_quarter, False)
                self.active_quarter.data = next_quarter
                self.active_quarter.value = languages[self.lang][next_quarter]

            else:
                pass

            # on met à jour l'affichage du home...
            self.active_sequence.data = new_active_sequence['name']
            self.active_sequence.value = languages[self.lang][new_active_sequence['name']]
            self.on_mount()
            self.cp.page.update()

            self.cp.box.title.value = languages[self.lang]['success']
            self.cp.box.content.value = languages[self.lang]['sequence closed']
            self.cp.box.open = True
            self.cp.box.update()

        else:
            pass

    def close_sequence_normally(self):
        self.run_async_in_thread(self.load_sequence_informations_normally())

    def close_generation_window(self, e):
        self.hide_one_window(self.generation_window)

    def open_generation_window(self, e):
        self.show_one_window(self.generation_window)

    def close_check_sequence_window(self, e):
        self.report_book_container.visible = False
        self.check_bt_close_despite.visible = False
        self.report_book_bar.value = 0
        self.report_book_status.value = '0 %'
        self.check_status.value = '0 %'
        self.check_notes_bar.value = 0
        self.class_checked.value = '-'
        self.check_table.rows.clear()
        self.nb_missing.value = '0'
        self.hide_one_window(self.check_sequence_window)

    def open_check_sequence_window(self, e):
        self.run_async_in_thread(self.load_checking(e))

    async def load_checking(self, e):
        self.check_table.rows.clear()
        self.check_status.value = '0 %'
        self.class_checked.value = '-'
        self.check_notes_bar.value = 0
        self.show_one_window(self.check_sequence_window)

        # on définit quelques variables qui nous seront utiles...
        access_token = self.cp.page.client_storage.get('access_token')
        year_id = self.cp.year_id
        sequence = self.active_sequence.data

        # liste des notes manquantes
        missing_list: list = []

        all_classes = await get_classes_with_student_count(access_token, year_id)
        self.total_classes.value = len(all_classes)
        self.cp.page.update()

        total_classes_checked = 0
        big_total_missing = 0

        # on itère sur chaque classe
        for item in all_classes:
            self.check_nb_classes.value = total_classes_checked
            self.check_nb_classes.update()

            self.class_checked.value = item['class_name']
            self.class_checked.update()
            self.nb_students.value = item['effectif']
            self.nb_students.update()

            subjects = await get_subjects_by_level(access_token, item['level_id'])
            total_subjects = len(subjects)
            self.nb_notes_attendues.value = total_subjects * item['effectif']
            self.nb_notes_attendues.update()
            total_missing = 0
            total_checked = 0

            for subj in subjects:
                missing_notes = await get_students_without_note_for_subject(
                    access_token, item['class_id'], self.active_sequence.data, subj['id'], year_id
                )
                if missing_notes:
                    for element, note_details in enumerate(missing_notes):
                        missing_list.append(note_details)
                        total_missing += 1
                        big_total_missing += 1
                        self.nb_missing.value = big_total_missing
                        self.nb_missing.update()

                total_checked += 1
                self.check_notes_bar.value = total_checked / total_subjects
                self.check_notes_bar.update()
                time.sleep(0.01)
                self.check_status.value = f"{int(total_checked * 100 / total_subjects)} %"
                self.check_status.update()

            if total_missing == 0:
                status_icon = ft.Icons.CHECK_CIRCLE
                status_color = 'green'
            else:
                status_icon = ft.Icons.INFO_ROUNDED
                status_color = 'red'

            self.check_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(item['class_name'])),
                        ft.DataCell(ft.Text(f"{item['effectif']}")),
                        ft.DataCell(ft.Text(f"{total_subjects}")),
                        ft.DataCell(ft.Text(f"{total_subjects * item['effectif']}")),
                        ft.DataCell(ft.Text(f"{total_missing}")),
                        ft.DataCell(ft.Icon(status_icon, color=status_color, size=24))
                    ]
                )
            )
            total_classes_checked += 1

        self.report_container.visible = True
        self.checking_container.visible = False
        self.cp.page.update()

        # s'il y a des notes manquantes
        if missing_list:
            self.report_book_container.visible = False
            self.check_bt_close_despite.visible = True
            datas_to_export = []

            for item in missing_list:
                datas_to_export.append(
                    {
                        'sequence': self.active_sequence.data,
                        'nom': f"{item['name']} {item['surname']}",
                        'classe': item['class_name'],
                        'matière': item['subject_name']
                    }
                )

            # Étape 1 : Création du fichier Excel en mémoire (méthode robuste)
            df = pd.DataFrame(datas_to_export)
            output_buffer = BytesIO()

            with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name=f"Élèves sans notes {self.active_sequence.data}")
            file_bytes = output_buffer.getvalue()

            # Générer un nom de fichier unique pour le stockage
            unique_filename = f"rapport/sans_notes_{uuid.uuid4().hex}.xlsx"

            # Étape 2 : Upload vers Supabase avec httpx (méthode directe et fiable)
            headers = {
                "apikey": key,
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            }
            upload_url = f"{url}/storage/v1/object/{DOCUMENTS_BUCKET}/{unique_filename}"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    upload_url,
                    headers=headers,
                    content=file_bytes
                )

            if response.status_code not in [200, 201]:
                print("❌ Erreur pendant l'upload avec httpx:", response.text)
                # Afficher une erreur à l'utilisateur ici
                return

            # Étape 3 : Création de l'URL signée (en utilisant le client supabase, c'est fiable pour ça)
            signed_url_response = supabase_client.storage.from_(DOCUMENTS_BUCKET).create_signed_url(
                path=unique_filename,
                expires_in=3600  # 1 heure
            )
            signed_url = signed_url_response.get("signedURL")
            self.cp.page.launch_url(signed_url)

        # s'il n'y a aucune note manquante...
        else:
            self.report_book_container.visible = True
            self.check_bt_close_despite.visible = False
            self.cp.page.update()

            # cloture de la séquence ...
            self.close_sequence_normally()

        self.cp.page.update()

    def open_new_year_infos_window(self, e):
        self.run_async_in_thread(self.load_new_year_infos(e))

    async def load_new_year_infos(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        current_year = await current_year_data(access_token)

        new_year_short = current_year['short'] + 1
        new_year_label = f"{new_year_short - 1}-{new_year_short}"
        self.new_year_label.value = new_year_label
        self.new_year_short.value = new_year_short

        # open window...
        self.hide_one_window(self.generation_window)
        self.show_one_window(self.new_year_informations_window)

    def close_new_year_infos_window(self, e):
        self.hide_one_window(self.new_year_informations_window)

    def open_final_window(self, e):
        self.run_async_in_thread(self.load_final_window(e))

    async def load_final_window(self, e):

        count_empty = 0
        for widget in (self.new_tranche_1, self.new_tranche_2, self.new_tranche_3, self.new_reg_fees):
            if not widget.value:
                count_empty += 1

        if count_empty == 0:
            self.hide_one_window(self.new_year_informations_window)
            self.show_one_window(self.final_window)

            year_id = self.cp.year_id
            access_token = self.cp.page.client_storage.get('access_token')

            all_affectations = await get_affectations_by_year_simple(access_token, year_id)
            count = 0

            # on met à jour le champ active de l'ancienne année à False...
            await update_year_by_id(access_token, year_id, {'active': False})

            # on crée la nouvelle année...
            datas_to_insert = {
                "name": self.new_year_label.value,
                "active": True,
                "short": self.new_year_short.value,
                "start": datetime.date(int(self.new_year_short.value) - 1, 8, 1),
                "end": datetime.date(int(self.new_year_short.value), 7, 31),
            }
            await insert_year(access_token, datas_to_insert)

            # on récupère l'id de la nouvelle année...
            new_active_year = await get_active_year_id(access_token)

            # si on reconduit les affectations...
            if self.switch_affectations.value:
                for item in all_affectations:
                    affectations_datas_to_insert = {
                        "year_id": new_active_year,
                        "teacher_id": item['teacher_id'],
                        "class_id": item['class_id'],
                        "subject_id": item['subject_id'],
                        "nb_hour": 1,
                        "day": item['day'],
                        "slot": item['slot'],
                        "busy": True
                    }
                    await insert_affectation(access_token, affectations_datas_to_insert)
                    count += 1
                    percent_value = count / len(all_affectations)
                    self.new_affectations_bar.value = percent_value

                    if percent_value < 1:
                        self.new_affectations_status.value = f"{percent_value:.2f} %"
                    else:
                        self.new_affectations_status.value = f"{percent_value:.2f} %"

                    self.cp.page.update()

            else:
                for item in all_affectations:
                    affectations_datas_to_insert = {
                        "year_id": new_active_year,
                        "class_id": item['class_id'],
                        "nb_hour": 1,
                        "day": item['day'],
                        "slot": item['slot'],
                        "busy": False
                    }
                    await insert_affectation(access_token, affectations_datas_to_insert)

                    count += 1
                    percent_value = count / len(all_affectations)
                    self.new_affectations_bar.value = percent_value

                    if percent_value < 1:
                        self.new_affectations_status.value = f"{percent_value:.2f} %"
                    else:
                        self.new_affectations_status.value = f"{percent_value:.2f} %"

                    self.cp.page.update()

            # on se déconnecte...
            time.sleep(3)

            try:
                supabase_client.auth.sign_out()
            except Exception as e:
                print(f"Erreur lors de la déconnexion : {e}")
            self.page.client_storage.clear()
            self.page.go('/')

        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.message.value = languages[self.lang]['error msg']
            self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
            self.cp.icon_message.color = ft.Colors.RED
            self.cp.box.open = True
            self.cp.box.update()

    async def change_fees(self, e):
        access_token = self.cp.page.client_storage.get("access_token")
        year_id = self.cp.year_id

        if self.switch_fees.value:
            fees = await get_fees_amount_by_year(access_token, year_id)

            self.new_tranche_1.value = fees['fees_part_1']
            self.new_tranche_2.value = fees['fees_part_2']
            self.new_tranche_3.value = fees['fees_part_3']
            self.new_reg_fees.value = fees['registration']

            self.cp.page.update()

        else:
            self.new_tranche_1.value = None
            self.new_tranche_2.value = None
            self.new_tranche_3.value = None
            self.new_reg_fees.value = None
            self.cp.page.update()

    def on_fees_switch_change(self, e):
        self.run_async_in_thread(self.change_fees(e))