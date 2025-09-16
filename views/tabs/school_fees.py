from utils.styles import *
from components import MyButton, MyTextButton, MyMiniIcon, ColoredIcon
from translations.translations import languages
from services.async_functions.fees_functions import *
from services.async_functions.general_functions import get_active_sequence
import threading, asyncio
from utils.useful_functions import add_separator, format_number


class SchoolFees(ft.Container):
    def __init__(self, cp: object):
        super().__init__(
            expand=True, alignment=ft.alignment.center, bgcolor=MAIN_COLOR
        )
        self.cp = cp
        lang = self.cp.language
        self.lang = lang

        # main window...
        # Kpi
        self.expected_amount = ft.Text('-', size=28, font_family="PEB",)
        self.amount_collected = ft.Text('-', size=28, font_family="PEB",)
        self.amount_stayed = ft.Text('-', size=28, font_family="PEB",)
        self.recovery_rate = ft.Text('-', size=28, font_family="PEB",)
        self.ct_expected = ft.Container(
            width=170, height=120, padding=10, border_radius=24,
            bgcolor='white', content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ColoredIcon(ft.Icons.BAR_CHART_ROUNDED, 'indigo', 'indigo50'),
                            ft.Text(languages[lang]['expected'].upper(), size=14, font_family='PPR', color='indigo')
                        ], alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Column(
                        controls=[
                            self.expected_amount,
                            ft.Text(languages[lang]['expected amount'], size=12, font_family='PPR', color='grey')
                        ], spacing=0
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.ct_collected = ft.Container(
            width=170, height=120, padding=10, border_radius=24,
            bgcolor='white', content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ColoredIcon(ft.Icons.RECEIPT_SHARP, 'teal', 'teal50'),
                            ft.Text(languages[lang]['received'].upper(), size=14, font_family='PPR', color='teal')
                        ], alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Column(
                        controls=[
                            self.amount_collected,
                            ft.Text(languages[lang]['collected amount'], size=12, font_family='PPR', color='grey')
                        ], spacing=0
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.ct_remaining = ft.Container(
            width=170, height=120, padding=10, border_radius=24,
            bgcolor='white', content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ColoredIcon(ft.Icons.REAL_ESTATE_AGENT, 'deeporange', 'deeporange50'),
                            ft.Text(languages[lang]['remaining'].upper(), size=14, font_family='PPR',
                                    color='deeporange')
                        ], alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Column(
                        controls=[
                            self.amount_stayed,
                            ft.Text(languages[lang]['remaining balance'], size=12, font_family='PPR', color='grey')
                        ], spacing=0
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.ct_rate = ft.Container(
            width=170, height=120, padding=10, border_radius=24,
            bgcolor='white', content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ColoredIcon(ft.Icons.PIE_CHART_SHARP, 'green', 'green50'),
                            ft.Text(languages[lang]['rate'].upper(), size=14, font_family='PPR', color='green')
                        ], alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Column(
                        controls=[
                            self.recovery_rate,
                            ft.Text(languages[lang]['recovery rate'], size=12, font_family='PPR', color='grey')
                        ], spacing=0
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

        self.menu_button = ft.IconButton(
            ft.Icons.MENU, icon_size=24, icon_color='black',
            on_click=lambda e: self.cp.page.open(self.cp.drawer)
        )
        self.active_sequence = ft.Text(size=14, font_family='PPB')
        self.active_quarter = ft.Text(size=14, font_family='PPB')
        self.sequence_ct = ft.Chip(
            label=self.active_sequence,
            leading=ft.Icon(ft.Icons.CALENDAR_MONTH_OUTLINED, size=16, color='black87'),
            shape=ft.RoundedRectangleBorder(radius=16)
        )
        # widget
        self.search_class = ft.Dropdown(
            **drop_style,
            prefix_icon=ft.Icons.ROOFING, label=languages[lang]['class'], width=180,
            on_change=None, menu_height=200,
            options=[ft.dropdown.Option(key=" ", text=f"global")], value=" "
        )
        self.search_tranche = ft.Dropdown(
            **drop_style, width=160, label=languages[lang]['fees part'], value='tout',
            options=[
                ft.dropdown.Option(
                    key=choice['clé'], text=f"{choice['valeur']}"
                )
                for choice in [
                    {'clé': 'fees part 1', 'valeur': languages[lang]['fees part 1']},
                    {'clé': 'fees part 2', 'valeur': languages[lang]['fees part 2']},
                    {'clé': 'fees part 3', 'valeur': languages[lang]['fees part 3']},
                    {'clé': 'tout', 'valeur': 'global'},
                ]
            ]
        )
        self.table = ft.DataTable(
            **datatable_style, expand=True,
            columns=[
                ft.DataColumn(
                    ft.Text(languages[lang]['name']),
                ),
                ft.DataColumn(
                    ft.Text(languages[lang]['class']),
                ),
                ft.DataColumn(
                    ft.Text(languages[lang]['amount paid']),
                ),
                ft.DataColumn(
                    ft.Text(languages[lang]['total to pay']),
                ),
                ft.DataColumn(
                    ft.Text(languages[lang]['remaining balance']),
                ),
                ft.DataColumn(
                    ft.Text(languages[lang]['status']),
                )
            ]
        )

        self.main_window = ft.Container(
            expand=True, padding=20, border_radius=16,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Row(
                                controls=[
                                    MyTextButton(
                                        languages[self.lang]['export pdf'], ft.Icons.DOWNLOAD_OUTLINED,
                                        None
                                    ),
                                    MyTextButton(
                                        languages[self.lang]['export excel'], ft.Icons.DOWNLOAD_OUTLINED,
                                        None
                                    ),
                                    MyTextButton(
                                        languages[self.lang]['display KPI'], ft.Icons.DATA_USAGE_OUTLINED,
                                        self.open_ki_window
                                    ),
                                ]
                            ),
                            ft.Row(
                                controls=[
                                    self.search_class, self.search_tranche,
                                    MyMiniIcon(
                                        ft.Icons.FILTER_ALT_OUTLINED, languages[lang]['filter'], 'black',
                                        None, self.click_on_filter
                                    ),
                                    MyMiniIcon(
                                        ft.Icons.FILTER_ALT_OFF_OUTLINED, languages[lang]['filter'], 'black',
                                        None, self.delete_filter
                                    )
                                ]
                            )
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

        # fenêtre des KPI...
        self.kpi_classe = ft.Text('Global', size=18, font_family='PPM')
        self.kpi_tranche = ft.Text('Global', size=18, font_family='PPM')
        self.kpi_window  = ft.Container(
            **ct_style, content=ft.Container(
                **intern_ct_style, width=850,
                content=ft.Column(
                    expand=True, scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Container(
                            **top_ct_style, content=ft.Row(
                                controls=[
                                    ft.Text('KPI', size=20, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black', bgcolor=MAIN_COLOR,
                                        on_click=self.close_kpi_window
                                    )
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            **bottom_ct_style, content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[lang]['fees part'], size=16, font_family='PPM',
                                                            color='grey'),
                                                    ft.Row(
                                                        controls=[
                                                            ft.Icon(ft.Icons.MONETIZATION_ON_ROUNDED, size=24, color='black'),
                                                            self.kpi_tranche
                                                        ]
                                                    )
                                                ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                            ),
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[lang]['class'], size=16, font_family='PPM',
                                                            color='grey'),
                                                    ft.Row(
                                                        controls=[
                                                            ft.Icon('roofing', size=24, color='black'),
                                                            self.kpi_classe
                                                        ]
                                                    )
                                                ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                            )
                                        ], alignment=ft.MainAxisAlignment.SPACE_AROUND
                                    ),
                                    ft.Divider(height=10, thickness=1),
                                    ft.Row(
                                        controls=[
                                            self.ct_expected,
                                            ft.VerticalDivider(width=1, thickness=1),
                                            self.ct_collected,
                                            ft.VerticalDivider(width=1, thickness=1),
                                            self.ct_remaining,
                                            ft.VerticalDivider(width=1, thickness=1),
                                            self.ct_rate
                                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    )
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            )
                        )
                    ], spacing=0, alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
        )

        self.content = ft.Stack(
            expand=True,
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(languages[self.lang]['loading screen'], size=18, font_family='PPR'),
                        ft.ProgressRing(color=BASE_COLOR)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ], alignment=ft.alignment.center
        )
        self.on_mount()

    async def build_main_view(self):
        self.content.controls.clear()
        self.content.controls = [self.main_window, self.kpi_window]
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
        all_classes = await get_all_classes_basic_info(access_token)

        # mettre à jour les séquences
        active_sequence = await get_active_sequence(access_token)
        self.active_sequence.value = languages[self.lang][active_sequence['name']]
        self.active_quarter.value = languages[self.lang][active_sequence['quarter']]
        self.active_sequence.data = active_sequence['name']
        self.active_quarter.data = active_sequence['quarter']

        print(all_classes)

        for one_classe in all_classes:
            self.search_class.options.append(
                ft.dropdown.Option(
                    key=one_classe['id'], text=f"{one_classe['code']}"
                )
            )

        self.cp.page.update()

        datas = await get_student_fees_summary(access_token, self.cp.year_id)
        self.table.rows.clear()

        # Variables pour calculer les indicateurs...
        paid = 0
        total_expected = 0
        remaining = 0

        for d, data in enumerate(datas):
            line_color = ft.Colors.GREY_100 if d % 2 == 0 else ft.Colors.WHITE
            paid += data['total_paid']
            total_expected += data['total_to_pay']
            remaining += data['reste_a_payer']

            if data['reste_a_payer'] == 0:
                status_color = 'teal'
                status_bgcolor = 'teal50'
                status_icone = ft.Icons.CHECK_CIRCLE
                status_text = languages[self.lang]['sold out']
            else:
                status_color = 'red'
                status_bgcolor = 'red50'
                status_icone = ft.Icons.INFO_ROUNDED
                status_text = languages[self.lang]['on going']

            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Text(f"{data['student_name']} {data['student_surname']}".upper())
                        ),
                        ft.DataCell(ft.Text(data['class_code'])),
                        ft.DataCell(ft.Text(f"{add_separator(data['total_paid'])}")),
                        ft.DataCell(ft.Text(f"{add_separator(data['total_to_pay'])}")),
                        ft.DataCell(
                            ft.Text(
                                f"{add_separator(data['reste_a_payer'])}",
                                color="red" if data['reste_a_payer'] > 0 else 'black'
                            )
                        ),
                        ft.DataCell(
                            ft.Icon(status_icone, size=20, color=status_color)
                        ),
                    ], color=line_color
                )
            )

        self.expected_amount.value = format_number(total_expected)
        self.amount_collected.value = format_number(paid)
        self.amount_stayed.value = format_number(remaining)
        self.recovery_rate.value = f"{(paid * 100 / total_expected):.2f}%"

        await self.build_main_view()

    async def filter_datas(self, e):
        access_token = self.cp.page.client_storage.get("access_token")

        # cas du rapport global...
        if self.search_tranche.value == 'tout':
            self.kpi_tranche.value = 'Global'

            # if class field is empty...
            if self.search_class.value == " ":
                self.kpi_classe.value = 'Global'
                datas = await get_student_fees_summary(access_token, self.cp.year_id)
                self.table.rows.clear()

                # Variables pour calculer les indicateurs...
                paid = 0
                total_expected = 0
                remaining = 0

                for d, data in enumerate(datas):
                    line_color = ft.Colors.GREY_100 if d % 2 == 0 else ft.Colors.WHITE
                    paid += data['total_paid']
                    total_expected += data['total_to_pay']
                    remaining += data['reste_a_payer']

                    if data['reste_a_payer'] == 0:
                        status_color = 'teal'
                        status_bgcolor = 'teal50'
                        status_icone = ft.Icons.CHECK_CIRCLE
                        status_text = languages[self.lang]['sold out']
                    else:
                        status_color = 'red'
                        status_bgcolor = 'red50'
                        status_icone = ft.Icons.CHECK_CIRCLE
                        status_text = languages[self.lang]['on going']

                    self.table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(
                                    ft.Text(f"{data['student_name']} {data['student_surname']}".upper())
                                ),
                                ft.DataCell(ft.Text(data['class_code'])),
                                ft.DataCell(ft.Text(f"{add_separator(data['total_paid'])}")),
                                ft.DataCell(ft.Text(f"{add_separator(data['total_to_pay'])}")),
                                ft.DataCell(
                                    ft.Text(
                                        f"{add_separator(data['reste_a_payer'])}",
                                        color="red" if data['reste_a_payer'] > 0 else 'black'
                                    )
                                ),
                                ft.DataCell(
                                    ft.Icon(status_icone, size=20, color=status_color)
                                ),
                            ], color=line_color,
                        )
                    )

                self.expected_amount.value = format_number(total_expected)
                self.amount_collected.value = format_number(paid)
                self.amount_stayed.value = format_number(remaining)
                self.recovery_rate.value = f"{(paid * 100 / total_expected):.2f}%"

                self.cp.page.update()

            # if class filed is filled
            else:
                self.kpi_classe.value = await get_class_code_by_id_async(self.search_class.value, access_token)
                class_filtered = self.search_class.value if self.search_class.value else ""
                datas = await get_student_fees_summary(access_token, self.cp.year_id)
                self.table.rows.clear()

                filtered_datas = list(filter(lambda x: class_filtered in x['class_id'], datas))

                # Variables pour calculer les indicateurs...
                paid = 0
                total_expected = 0
                remaining = 0

                for d, data in enumerate(filtered_datas):
                    line_color = ft.Colors.GREY_100 if d % 2 == 0 else ft.Colors.WHITE
                    paid += data['total_paid']
                    total_expected += data['total_to_pay']
                    remaining += data['reste_a_payer']

                    if data['reste_a_payer'] == 0:
                        status_color = 'teal'
                        status_bgcolor = 'teal50'
                        status_icone = ft.Icons.CHECK_CIRCLE
                        status_text = languages[self.lang]['sold out']
                    else:
                        status_color = 'red'
                        status_bgcolor = 'red50'
                        status_icone = ft.Icons.INFO_ROUNDED
                        status_text = languages[self.lang]['on going']

                    self.table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(
                                    ft.Text(f"{data['student_name']} {data['student_surname']}".upper())
                                ),
                                ft.DataCell(ft.Text(data['class_code'])),
                                ft.DataCell(ft.Text(f"{add_separator(data['total_paid'])}")),
                                ft.DataCell(ft.Text(f"{add_separator(data['total_to_pay'])}")),
                                ft.DataCell(
                                    ft.Text(
                                        f"{add_separator(data['reste_a_payer'])}",
                                        color="red" if data['reste_a_payer'] > 0 else 'black'
                                    )
                                ),
                                ft.DataCell(
                                    ft.Icon(status_icone, size=20, color=status_color)
                                ),
                            ], color=line_color
                        )
                    )

                self.expected_amount.value = format_number(total_expected)
                self.amount_collected.value = format_number(paid)
                self.amount_stayed.value = format_number(remaining)
                self.recovery_rate.value = f"{(paid * 100 / total_expected):.2f}%"

                self.cp.page.update()

        #  cas du rapport par tranche...
        else:
            self.kpi_tranche.value = languages[self.lang][self.search_tranche.value]

            # if class filed is empty...
            if self.search_class.value is None:
                self.kpi_classe.value = 'Global'
                datas = await get_student_fees_summary_by_part(
                    access_token, self.search_tranche.value, self.cp.year_id
                )
                self.table.rows.clear()

                # Variables pour calculer les indicateurs...
                paid = 0
                total_expected = 0
                remaining = 0

                for d, data in enumerate(datas):
                    line_color = ft.Colors.GREY_100 if d % 2 == 0 else ft.Colors.WHITE
                    paid += data['total_paid']
                    total_expected += data['total_to_pay']
                    remaining += data['reste_a_payer']

                    if data['reste_a_payer'] == 0:
                        status_color = 'teal'
                        status_bgcolor = 'teal50'
                        status_icone = ft.Icons.CHECK_CIRCLE
                        status_text = languages[self.lang]['sold out']
                    else:
                        status_color = 'red'
                        status_bgcolor = 'red50'
                        status_icone = ft.Icons.INFO_ROUNDED
                        status_text = languages[self.lang]['on going']

                    self.table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(
                                    ft.Text(f"{data['student_name']} {data['student_surname']}".upper())
                                ),
                                ft.DataCell(ft.Text(data['class_code'])),
                                ft.DataCell(ft.Text(f"{add_separator(data['total_paid'])}")),
                                ft.DataCell(ft.Text(f"{add_separator(data['total_to_pay'])}")),
                                ft.DataCell(
                                    ft.Text(
                                        f"{add_separator(data['reste_a_payer'])}",
                                        color="red" if data['reste_a_payer'] > 0 else 'black'
                                    )
                                ),
                                ft.DataCell(
                                    ft.Icon(status_icone, size=20, color=status_color)
                                ),
                            ], color=line_color
                        )
                    )

                self.expected_amount.value = format_number(total_expected)
                self.amount_collected.value = format_number(paid)
                self.amount_stayed.value = format_number(remaining)
                self.recovery_rate.value = f"{(paid * 100 / total_expected):.2f}%"

                self.cp.page.update()

            # if class field is filled ...
            else:
                self.kpi_classe.value = await get_class_code_by_id_async(self.search_class.value, access_token)
                sc = self.search_class.value
                datas = await get_student_fees_summary_by_part(access_token, self.search_tranche.value, self.cp.year_id)
                self.table.rows.clear()

                filtered_datas = list(filter(lambda x: sc in x['class_id'], datas))

                # Variables pour calculer les indicateurs...
                paid = 0
                total_expected = 0
                remaining = 0

                for d, data in enumerate(filtered_datas):
                    line_color = ft.Colors.GREY_100 if d % 2 == 0 else ft.Colors.WHITE
                    paid += data['total_paid']
                    total_expected += data['total_to_pay']
                    remaining += data['reste_a_payer']
                    print(f"paid {paid}")
                    print(f"total_expected {total_expected}")
                    print(f"remaining {remaining}")

                    if data['reste_a_payer'] == 0:
                        status_color = 'teal'
                        status_bgcolor = 'teal50'
                        status_icone = ft.Icons.CHECK_CIRCLE
                        status_text = languages[self.lang]['sold out']
                    else:
                        status_color = 'red'
                        status_bgcolor = 'red50'
                        status_icone = ft.Icons.INFO_ROUNDED
                        status_text = languages[self.lang]['on going']

                    self.table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(
                                    ft.Text(f"{data['student_name']} {data['student_surname']}".upper())
                                ),
                                ft.DataCell(ft.Text(data['class_code'])),
                                ft.DataCell(ft.Text(f"{add_separator(data['total_paid'])}")),
                                ft.DataCell(ft.Text(f"{add_separator(data['total_to_pay'])}")),
                                ft.DataCell(
                                    ft.Text(
                                        f"{add_separator(data['reste_a_payer'])}",
                                        color="red" if data['reste_a_payer'] > 0 else 'black'
                                    )
                                ),
                                ft.DataCell(
                                    ft.Icon(status_icone, size=20, color=status_color)
                                ),
                            ], color=line_color
                        )
                    )

                self.expected_amount.value = format_number(total_expected)
                self.amount_collected.value = format_number(paid)
                self.amount_stayed.value = format_number(remaining)
                self.recovery_rate.value = f"{(paid * 100 / total_expected):.2f}%" if total_expected > 0 else '0 %'

                self.cp.page.update()

    def click_on_filter(self, e):
        self.run_async_in_thread(self.filter_datas(e))

    async def supp_filter(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        datas = await get_student_fees_summary(access_token, self.cp.year_id)
        self.table.rows.clear()

        # Variables pour calculer les indicateurs...
        paid = 0
        total_expected = 0
        remaining = 0
        self.kpi_classe.value = 'Global'
        self.kpi_tranche.value = 'Global'

        for d, data in enumerate(datas):
            line_color = ft.Colors.GREY_100 if d % 2 == 0 else ft.Colors.WHITE
            paid += data['total_paid']
            total_expected += data['total_to_pay']
            remaining += data['reste_a_payer']

            if data['reste_a_payer'] == 0:
                status_color = 'teal'
                status_bgcolor = 'teal50'
                status_icone = ft.Icons.CHECK_CIRCLE
                status_text = languages[self.lang]['sold out']
            else:
                status_color = 'red'
                status_bgcolor = 'red50'
                status_icone = ft.Icons.INFO_ROUNDED
                status_text = languages[self.lang]['on going']

            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Text(f"{data['student_name']} {data['student_surname']}".upper())
                        ),
                        ft.DataCell(ft.Text(data['class_code'])),
                        ft.DataCell(ft.Text(f"{add_separator(data['total_paid'])}")),
                        ft.DataCell(ft.Text(f"{add_separator(data['total_to_pay'])}")),
                        ft.DataCell(
                            ft.Text(
                                f"{add_separator(data['reste_a_payer'])}", color="red" if data['reste_a_payer'] > 0 else 'black'
                            )
                        ),
                        ft.DataCell(
                            ft.Icon(status_icone, size=20, color=status_color)
                        ),
                    ], color=line_color
                )
            )

        self.expected_amount.value = format_number(total_expected)
        self.amount_collected.value = format_number(paid)
        self.amount_stayed.value = format_number(remaining)
        self.recovery_rate.value = f"{(paid * 100 / total_expected):.2f}%"

        self.search_class.value = " "
        self.search_tranche.value = 'tout'

        self.cp.page.update()

    def delete_filter(self, e):
        self.run_async_in_thread(self.supp_filter(e))

    def open_ki_window(self, e):
        self.show_one_window(self.kpi_window)

    def close_kpi_window(self, e):
        self.hide_one_window(self.kpi_window)

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