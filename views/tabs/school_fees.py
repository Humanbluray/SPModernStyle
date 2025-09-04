from utils.styles import *
from components import MyButton, MyTextButton, MyMiniIcon
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
                                    ft.Text(languages[self.lang]['menu school fees'].capitalize(), size=24,
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
                    self.top_menu,
                    ft.Row(
                        controls=[
                            ft.Row(
                                controls=[
                                    MyTextButton(languages[self.lang]['export pdf'], None),
                                    MyTextButton(languages[self.lang]['export excel'], None),
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
        self.content.controls.append(self.main_window)
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

            # if class field is empty...
            if self.search_class.value == " ":
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
            # if class filed is empty...
            if self.search_class.value is None:
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