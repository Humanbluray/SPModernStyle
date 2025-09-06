from components import MyButton, MyTextButton, BoxStudentNote, MyMiniIcon
from utils.styles import *
from services.async_functions.notes_functions import *
from services.async_functions.general_functions import get_active_sequence
from translations.translations import languages
import asyncio, os, openpyxl, threading, uuid, io
import pandas as pd
from utils.useful_functions import add_separator

DOCUMENTS_BUCKET = 'documents'


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
                    self.sequence_ct
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        )

        self.search_class = ft.Dropdown(
            **drop_style, label=languages[lang]['class'],
            prefix_icon=ft.Icons.ROOFING, expand=True, menu_height=200,
            on_change=self.on_filter_class_change, options=[
                ft.dropdown.Option(key=' ', text=f"{languages[lang]['select option']}")
            ], value=' ',
        )
        self.search_subject = ft.Dropdown(
            **drop_style, label=languages[lang]['subject'],
            prefix_icon=ft.Icons.BOOK_OUTLINED, expand=True, menu_height=200,
            on_change=None, options=[
                ft.dropdown.Option(key=' ', text=f"{languages[lang]['select option']}")
            ], value=' '
        )
        self.search_sequence = ft.Dropdown(
            **drop_style, label=languages[lang]['sequence'],
            prefix_icon=ft.Icons.BOOK_OUTLINED, expand=True, menu_height=200,
            options=[
                ft.dropdown.Option(
                    key='sequence 1', text=f"{languages[lang]['sequence 1']}"
                ),
                ft.dropdown.Option(
                    key='sequence 2', text=f"{languages[lang]['sequence 2']}"
                ), ft.dropdown.Option(
                    key='sequence 3', text=f"{languages[lang]['sequence 3']}"
                ), ft.dropdown.Option(
                    key='sequence 4', text=f"{languages[lang]['sequence 4']}"
                ),
                ft.dropdown.Option(
                    key='sequence 5', text=f"{languages[lang]['sequence 5']}"
                ), ft.dropdown.Option(
                    key='sequence 6', text=f"{languages[lang]['sequence 6']}"
                ),
                ft.dropdown.Option(
                    key=' ', text=f"{languages[lang]['select option']}"
                )
            ], value=' '
        )
        self.table = ft.DataTable(
            **datatable_style, columns=[
                ft.DataColumn(ft.Text(option)) for option in [
                    languages[lang]['class'], languages[lang]['name'], languages[lang]['sequence'],
                    languages[lang]['subject'], languages[lang]['note'], 'actions'
                ]
            ]
        )
        self.nb_result_search = ft.Text(size=16, font_family="PPM", color='grey')

        self.main_window = ft.Container(
            expand=True, padding=10,
            content=ft.Column(
                expand=True,
                controls=[
                    self.top_menu,
                    ft.Container(
                        padding=ft.padding.only(10, 0, 10, 0),
                        content=ft.Row(
                            controls=[
                                ft.Row(
                                    controls=[
                                        MyTextButton(languages[lang]['add notes'], self.open_new_note_window),
                                        MyTextButton(languages[lang]['import notes'], self.open_import_window),
                                        MyTextButton(languages[lang]['export template'], self.open_export_xls_window),
                                    ]
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                MyTextButton(languages[lang]['filter'], self.open_filter_window),
                                                MyTextButton(languages[lang]['class statistics'],
                                                             self.open_statistics_window),
                                            ]
                                        )
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                ),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        )
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
        self.filter_window = ft.Container(
            **ct_style,
            content=ft.Container(
                **intern_ct_style, width=500,
                content=ft.Column(
                    expand=True, spacing=0, scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Container(
                            **top_ct_style, content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['filter window'], size=20, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=MAIN_COLOR,
                                        on_click=self.close_filter_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            **bottom_ct_style,
                            content=ft.Column(
                                expand=True,
                                controls=[
                                    self.search_sequence,
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    self.search_class,
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    self.search_subject,
                                    MyButton(
                                        languages[lang]['valid'], 'check',
                                        200, self.valid_filters
                                    )
                                ], spacing=10,
                            )
                        )
                    ]
                )
            )
        )

        # new note window...
        self.new_class = ft.Dropdown(
            **drop_style,
            prefix_icon=ft.Icons.ROOFING, width=200, label=languages[lang]['class'],
            on_change=self.on_new_class_change, options=[
                ft.dropdown.Option(key=' ', text=f"{languages[lang]['select option']}")
            ], value=' '
        )
        self.new_subject = ft.Dropdown(
            **drop_style, label=languages[lang]['subject'],
            prefix_icon=ft.Icons.BOOK_OUTLINED, width=350,
            on_change=self.on_new_subject_change, options=[
                ft.dropdown.Option(key=' ', text=f"{languages[lang]['select option']}")
            ], value=' '
        )
        self.new_sequence = ft.TextField(
            **login_style, prefix_icon=ft.Icons.CALENDAR_MONTH_OUTLINED, width=170,
            read_only=True, label=languages[lang]['sequence'],
        )
        self.new_table = ft.ListView(
            expand=True, divider_thickness=1, spacing=5, height=400
        )
        self.nb_students = ft.Text(size=16, font_family='PPB', visible=True)
        self.new_progress_bar = ft.ProgressBar(
            width=150, height=5, color=BASE_COLOR, bgcolor=SECOND_COLOR, border_radius=16,
            value=0
        )
        self.new_coefficient = ft.TextField(
            **login_style, prefix_icon=ft.Icons.ONETWOTHREE, width=150,
            read_only=True, label=languages[lang]['coefficient'], value='0'
        )
        self.no_data = ft.Text(
            size=16, font_family='PPB', color='red', value=languages[lang]['no data'],
            visible=False
        )
        self.new_note_window = ft.Container(
            **ct_style, content=ft.Container(
                **intern_ct_style, width=950,
                content=ft.Column(
                    spacing=0, expand=True, scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Container(
                            **top_ct_style,
                            content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['add notes'], size=20, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=MAIN_COLOR,
                                        on_click=self.close_new_note_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            **bottom_ct_style, content=ft.Column(
                                expand=True,
                                controls=[
                                    ft.Row(controls=[self.new_class, self.new_sequence, self.new_subject, self.new_coefficient]),
                                    ft.Divider(color=ft.Colors.TRANSPARENT),
                                    ft.Column(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Text(languages[lang]['students without note'].upper(), size=16,
                                                            font_family='PPB'),
                                                    ft.Row(
                                                        controls=[
                                                            ft.Text(languages[self.lang]['total'].upper(), size=16,
                                                                    font_family='PPB', color='red'),
                                                            self.nb_students, self.no_data
                                                        ]
                                                    ),

                                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                            ),
                                            ft.Divider(height=1, thickness=1)
                                        ], spacing=0
                                    ),
                                    self.new_table,
                                    ft.Container(
                                        padding=10, content=ft.Row(
                                            controls=[
                                                MyButton(
                                                    languages[lang]['valid'], 'check', 200,
                                                    self.valider_notes
                                                ),
                                                ft.Row(
                                                    controls=[
                                                        ft.Text(
                                                            languages[lang]['progress'], size=16, font_family='PPM',
                                                            color='grey'
                                                        ),
                                                        self.new_progress_bar
                                                    ]
                                                ),
                                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                        )
                                    )
                                ], spacing=10,
                            )
                        )
                    ]
                )
            )
        )

        # edit note window...
        self.edit_student = ft.TextField(
            **login_style, width=400, prefix_icon='person_outlined', read_only=True,
            label=languages[lang]['student']
        )
        self.edit_note_id = ft.Text(visible=False)
        self.edit_subject_name = ft.TextField(
            **login_style, width=400, prefix_icon='book_outlined', read_only=True,
            label=languages[lang]['subject']
        )
        self.edit_sequence = ft.TextField(
            **login_style, width=200, prefix_icon=ft.Icons.CALENDAR_MONTH, read_only=True,
            label=languages[lang]['sequence']
        )
        self.edit_note = ft.TextField(
            **login_style, width=80,
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9.]", replacement_string=""),
            text_align=ft.TextAlign.RIGHT, label=languages[lang]['note']
        )

        self.edit_note_window = ft.Container(
            **ct_style, content=ft.Container(
                **intern_ct_style, width=550,
                content=ft.Column(
                    spacing=0, expand=True, scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Container(
                            **top_ct_style, content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['edit note'], size=20, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=MAIN_COLOR,
                                        on_click=self.close_edit_note_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            **bottom_ct_style,content=ft.Column(
                                expand=True,
                                controls=[ self.edit_note_id,
                                    self.edit_student,
                                    self.edit_sequence,
                                    self.edit_subject_name,
                                    self.edit_note,
                                    ft.Container(
                                        padding=10, content=MyButton(
                                            languages[lang]['valid'], 'check', 200,
                                            self.valider_edit_note
                                        ),
                                    )
                                ], spacing=10
                            )
                        )
                    ]
                )
            )
        )

        # export xls window...
        self.exp_class = ft.Dropdown(
            **drop_style, label=languages[lang]['class'],
            prefix_icon=ft.Icons.ROOFING, width=200, menu_height=200,
            on_change=self.on_export_class_change, options=[
                ft.dropdown.Option(key=' ', text=f"{languages[lang]['select option']}")
            ], value=' '
        )
        self.exp_subject = ft.Dropdown(
            **drop_style, label=languages[lang]['subject'],
            prefix_icon=ft.Icons.BOOK_OUTLINED, width=400, menu_height=200,
            on_change=self.on_export_subject_change, options=[
                ft.dropdown.Option(key=' ', text=f"{languages[lang]['select option']}")
            ], value=' '
        )
        self.exp_sequence = ft.TextField(
            **login_style,
            data=self.active_sequence.data, label=languages[lang]['sequence'],
            prefix_icon=ft.Icons.CALENDAR_MONTH_OUTLINED, width=170, read_only=True
        )
        self.exp_coefficient = ft.TextField(
            **login_style, prefix_icon=ft.Icons.ONETWOTHREE, width=150, value='0', read_only=True,
            label=languages[lang]['coefficient']
        )
        self.exp_class_name = ft.Text(visible=False)

        self.export_xls_window = ft.Container(
            **ct_style, content=ft.Container(
                **intern_ct_style, width=550,
                content=ft.Column(
                    spacing=0, expand=True, scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Container(
                            **top_ct_style, content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['export template'], size=20, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=MAIN_COLOR,
                                        on_click=self.close_export_xls_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            **bottom_ct_style, content=ft.Column(
                                expand=True, spacing=10, controls=[
                                    self.exp_class_name,
                                    ft.Row(controls=[self.exp_class, self.exp_sequence]),
                                    self.exp_subject, self.exp_coefficient,
                                    ft.Container(
                                        padding=10, content=ft.Row(
                                            controls=[
                                                MyButton(
                                                    languages[lang]["valid"], 'check',
                                                    200, self.exporter_template_file
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

        # import_window...
        self.imp_verif_bar = ft.ProgressBar(
            border_radius=16, height=5, color=BASE_COLOR, bgcolor=MAIN_COLOR, width=150
        )
        self.imp_verif_text = ft.Text('0%', size=16, font_family='PPM')
        self.imp_insert_bar = ft.ProgressBar(
            border_radius=16, height=5, value=0, color=BASE_COLOR, bgcolor=MAIN_COLOR, width=150
        )
        self.imp_insert_text = ft.Text('0%', size=16, font_family='PPM')

        self.total_lines_of_file = ft.Text('0', size=16, font_family='PPM')
        self.total_errors = ft.Text('0', size=16, font_family='PPM')
        self.table_errors = ft.DataTable(
            **datatable_style, columns=[
                ft.DataColumn(ft.Text(languages[lang]['line'])),
                ft.DataColumn(ft.Text(languages[lang]['error type']))
            ],
        )
        self.msg_error = ft.Text(languages[self.lang]['correct import errors'], size=16, font_family='PPB', color='red')

        self.bloc_table = ft.Column(
            visible=False, expand=True,
            controls=[
                ft.Text(languages[lang]['errors table'].upper(), size=16,
                        font_family="PPB"),
                ft.Container(
                    border_radius=16, border=ft.border.all(1, MAIN_COLOR), padding=0, expand=True,
                    content=ft.ListView(expand=True, controls=[self.table_errors], height=300)
                ),
                self.msg_error
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        self.bloc_import = ft.Column(
            visible=False,
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(languages[lang]['import lines'].upper(), size=16, font_family="PPB"),
                        ft.Divider(height=1, thickness=1)
                    ], spacing=0
                ),
                ft.Row(
                    controls=[
                        ft.Text(languages[lang]['import'], size=16, font_family='PPM'),
                        ft.Row(controls=[self.imp_insert_bar, self.imp_insert_text])
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

        self.cp.fp_import_notes.on_result = self.importer_notes

        self.import_window = ft.Container(
            **ct_style, content=ft.Container(
                **intern_ct_style, width=700,
                content=ft.Column(
                    spacing=0, expand=True, scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Container(
                            **top_ct_style, content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['import notes'], size=20, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=MAIN_COLOR,
                                        on_click=self.close_import_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            **bottom_ct_style, content=ft.Column(
                                expand=True, spacing=10,
                                controls=[
                                    MyButton(
                                        languages[lang]['import notes'], ft.Icons.DOWNLOAD_DONE, None,
                                        lambda _: self.cp.fp_import_notes.pick_files(
                                            allowed_extensions=['xls', 'xlsx']),
                                    ),
                                    ft.Divider(color=ft.Colors.TRANSPARENT),
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[lang]['file checking'].upper(), size=16,
                                                    font_family="PPB"),
                                            ft.Divider(height=1, thickness=1)
                                        ], spacing=0
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Text(languages[lang]['total number of lines'], size=16,
                                                            font_family='PPR'),
                                                    self.total_lines_of_file
                                                ]
                                            ),
                                            ft.Row(controls=[self.imp_verif_bar, self.imp_verif_text]),
                                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Text(languages[lang]['nb errors'], size=16, font_family='PPM'),
                                            self.total_errors
                                        ]
                                    ),
                                    ft.Divider(color=ft.Colors.TRANSPARENT),
                                    self.bloc_table,
                                    ft.Divider(color=ft.Colors.TRANSPARENT),
                                    self.bloc_import
                                ]
                            )
                        )
                    ]
                )
            )
        )

        # statistics window ________________
        self.stats_class = ft.Dropdown(
            **drop_style, prefix_icon='roofing', label=languages[lang]['class'], options=[
                ft.dropdown.Option(key=' ', text=languages[lang]['select option'])
            ], value=' ', on_change=self.on_stats_class_change, expand=True, menu_height=200
        )
        self.stats_subject = ft.Dropdown(
            **drop_style, prefix_icon='book_outlined', label=languages[lang]['subject'], options=[
                ft.dropdown.Option(key=' ', text=languages[lang]['select option'])
            ], value=' ', on_change=self.on_stats_subject_change, expand=True, menu_height=200
        )
        self.stats_sequence = ft.Dropdown(
            **drop_style,
            prefix_icon=ft.Icons.BOOK_OUTLINED, expand=True, menu_height=200,
            options=[
                ft.dropdown.Option(
                    key='sequence 1', text=f"{languages[lang]['sequence 1']}"
                ),
                ft.dropdown.Option(
                    key='sequence 2', text=f"{languages[lang]['sequence 2']}"
                ), ft.dropdown.Option(
                    key='sequence 3', text=f"{languages[lang]['sequence 3']}"
                ), ft.dropdown.Option(
                    key='sequence 4', text=f"{languages[lang]['sequence 4']}"
                ),
                ft.dropdown.Option(
                    key='sequence 5', text=f"{languages[lang]['sequence 5']}"
                ), ft.dropdown.Option(
                    key='sequence 6', text=f"{languages[lang]['sequence 6']}"
                ),
                ft.dropdown.Option(
                    key=' ', text=f"{languages[lang]['select option']}"
                )
            ], value=' ', label=languages[lang]['sequence'],
        )
        self.stats_success_rate = ft.Text('-', size=20, font_family='PPM')
        self.stats_nb_students = ft.Text('-', size=20, font_family='PPM')
        self.stats_nb_success = ft.Text('-', size=20, font_family='PPM')
        self.stats_nb_boys_success = ft.Text('-', size=20, font_family='PPM')
        self.stats_nb_girls_success = ft.Text('-', size=20, font_family='PPM')

        self.statistics_window = ft.Container(
            **ct_style, content=ft.Container(
                **intern_ct_style, width=500,
                content=ft.Column(
                    spacing=0, expand=True, scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Container(
                            **top_ct_style, content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['statistics window'], size=20, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=MAIN_COLOR,
                                        on_click=self.close_statistics_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            **bottom_ct_style, content=ft.Column(
                                expand=True, spacing=10, scroll=ft.ScrollMode.AUTO,
                                controls=[
                                    ft.Column(
                                        controls=[
                                            self.stats_class,
                                            self.stats_sequence,
                                            self.stats_subject,
                                        ], spacing=15
                                    ),
                                    ft.Divider(height=2, color=ft.Colors.TRANSPARENT),
                                    ft.Column(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Text(languages[lang]['statistics'], size=20, font_family='PPB',
                                                            color='red'),
                                                    ft.Icon(ft.Icons.MULTILINE_CHART, size=24, color='red'),
                                                ], alignment=ft.MainAxisAlignment.CENTER
                                            ),
                                            ft.Divider(height=1, thickness=1),
                                        ], spacing=0
                                    ),
                                    ft.Divider(height=2, color=ft.Colors.TRANSPARENT),
                                    ft.Row(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Icon(ft.Icons.GROUP_OUTLINED, size=24, color='black'),
                                                    ft.Text(languages[lang]['nb students'].upper(), size=16,
                                                            font_family='PPM'),
                                                ]
                                            ),
                                            self.stats_nb_students
                                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                    ft.Divider(height=1, thickness=1),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Row(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Icon(ft.Icons.BAR_CHART_OUTLINED, size=16, color='black'),
                                                    ft.Text(languages[lang]['nb > 10'].upper(), size=16,
                                                            font_family='PPM')
                                                ]
                                            ),
                                            self.stats_nb_success
                                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                    ft.Divider(height=1, thickness=1),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Row(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Icon(ft.Icons.PIE_CHART_OUTLINE_OUTLINED, size=24,
                                                            color='black'),
                                                    ft.Text(languages[lang]['success rate'].upper(), size=16,
                                                            font_family='PPM'),
                                                ]
                                            ),
                                            self.stats_success_rate
                                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                    ft.Divider(height=1, thickness=1),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Row(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Icon(ft.Icons.MAN_OUTLINED, size=24, color='blue'),
                                                    ft.Text(languages[lang]['boys > 10'].upper(), size=16,
                                                            font_family='PPM'),
                                                ]
                                            ),
                                            self.stats_nb_boys_success
                                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Divider(height=1, thickness=1),
                                    ft.Row(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Icon(ft.Icons.WOMAN_OUTLINED, size=24, color='pink'),
                                                    ft.Text(languages[lang]['girls > 10'].upper(), size=16,
                                                            font_family='PPM'),
                                                ]
                                            ),
                                            self.stats_nb_girls_success
                                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                ]
                            )
                        )
                    ]
                )
            )
        )

        # Statistiques individuelles matière
        self.sti_student = ft.Dropdown(
            **drop_style, width=300, label=languages[lang]['name'], prefix_icon=ft.Icons.PERSON_OUTLINE_OUTLINED,
            on_change=None
        )
        self.sti_class = ft.Dropdown(
            **drop_style, width=170, label=languages[lang]['class'], prefix_icon=ft.Icons.ROOFING,
            on_change=None
        )
        self.sti_subject = ft.Dropdown(
            **drop_style, width=300, label=languages[lang]['subject'], prefix_icon=ft.Icons.BOOK_OUTLINED,
        )
        self.sti_ct_graph = ft.Container()

        self.sti_window = ft.Container(
            **ct_style, content=ft.Container(
                **intern_ct_style, width=900, content=ft.Column(
                    expand=True, scroll=ft.ScrollMode.AUTO, controls=[
                        ft.Container(
                            **top_ct_style, content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['individual statistics'], size=20, font_family='PPB'),
                                    ft.IconButton(
                                        'close', bgcolor=MAIN_COLOR, icon_color='black', on_click=None
                                    )
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            **bottom_ct_style, content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            self.sti_class, self.sti_subject, self.sti_subject
                                        ]
                                    ),
                                    self.sti_ct_graph
                                ]
                            )
                        )
                    ]
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
                    ], spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER
                )

            ], alignment=ft.alignment.center
        )
        self.on_mount()

    async def build_main_view(self):
        self.content.controls.clear()

        for widget in (
                self.main_window, self.filter_window, self.new_note_window, self.edit_note_window,
                self.export_xls_window, self.import_window, self.statistics_window
        ):
            self.content.controls.append(widget)

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

    def on_mount(self):
        self.run_async_in_thread(self.on_init_async())

    async def load_datas(self):
        # Variables à utiliser...
        access_token = self.cp.page.client_storage.get('access_token')
        year_id = self.cp.year_id

        # mettre à jour les séquences
        active_sequence = await get_active_sequence(access_token)
        self.active_sequence.value = languages[self.lang][active_sequence['name']]
        self.active_quarter.value = languages[self.lang][active_sequence['quarter']]
        self.active_sequence.data = active_sequence['name']
        self.active_quarter.data = active_sequence['quarter']

        self.new_sequence.value = f"{languages[self.lang][active_sequence['name']]}"
        self.new_sequence.data = active_sequence['name']

        self.exp_sequence.value = f"{languages[self.lang][active_sequence['name']]}"
        self.exp_sequence.data = active_sequence['name']

        # toutes les classes...
        details_classe = await get_all_classes_basic_info(access_token)
        for any_classe in details_classe:
            self.search_class.options.append(
                ft.dropdown.Option(
                    key=any_classe['id'], text=f"{any_classe['code']}"
                )
            )

        await self.build_main_view()

    async def filter_datas(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        year_id = self.cp.year_id

        my_class = self.search_class.value
        my_subject = self.search_subject.value
        my_sequence = self.search_sequence.value

        if not my_class or not my_sequence or not my_subject:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.message.value = languages[self.lang]['error msg']
            self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
            self.cp.icon_message.color = ft.Colors.RED
            self.cp.box.open = True
            self.cp.box.update()

        else:
            filtered_datas = await get_all_notes_with_details(
                access_token, year_id, my_subject, my_class, my_sequence
            )

            if not filtered_datas:
                self.cp.box.title.value = languages[self.lang]['error']
                self.cp.message.value = languages[self.lang]['no data']
                self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
                self.cp.icon_message.color = ft.Colors.RED
                self.cp.box.open = True
                self.cp.box.update()
            else:
                self.table.rows.clear()
                for i, item in enumerate(filtered_datas):
                    line_color = ft.Colors.GREY_100 if i % 2 == 0 else ft.Colors.WHITE
                    self.table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(item['class_code'])),
                                ft.DataCell(ft.Text(f"{item['student_name']} {item['student_surname']}".upper())),
                                ft.DataCell(ft.Text(item['sequence'])),
                                ft.DataCell(ft.Text(item['subject_short_name'])),
                                ft.DataCell(ft.Text(item['value'])),
                                ft.DataCell(
                                    ft.Row(
                                        controls=[
                                            MyMiniIcon(
                                                'edit_outlined', languages[self.lang]['edit'], 'blue',
                                                item, self.open_edit_note_window
                                            ),
                                            MyMiniIcon(
                                                'delete_outlined', languages[self.lang]['delete'], 'red',
                                                item, None
                                            ),
                                        ], spacing=0
                                    )
                                )
                            ], color=line_color
                        )
                    )

                self.cp.page.update()

    def valid_filters(self, e):
        self.run_async_in_thread(self.filter_datas(e))

    def supp_filters(self, e):
        self.run_async_in_thread(self.load_datas())

    async def load_subject_filter(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        subjects = await get_subjects_by_class_id(access_token, self.search_class.value)

        self.search_subject.options.clear()
        self.search_subject.options.append(
            ft.dropdown.Option(
                key=' ', text=languages[self.lang]['select option']
            )
        )
        self.search_subject.value = ' '
        self.search_subject.update()

        for item in subjects:
            self.search_subject.options.append(
                ft.dropdown.Option(
                    key=item['subject_id'], text=f"{item['subject_name']}".upper()
                )
            )

        self.cp.page.update()

    def on_filter_class_change(self, e):
        self.run_async_in_thread(self.load_subject_filter(e))

    def open_filter_window(self, e):
        self.show_one_window(self.filter_window)

    def close_filter_window(self, e):
        self.hide_one_window(self.filter_window)

    async def load_new_notes_data(self, e):
        role = self.cp.page.client_storage.get('role')
        access_token = self.cp.page.client_storage.get('access_token')
        user_id = self.cp.user_id

        if role != 'professeur':
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.message.value = languages[self.lang]['error rights']
            self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
            self.cp.icon_message.color = ft.Colors.RED
            self.cp.box.open = True
            self.cp.box.update()
        else:
            self.show_one_window(self.new_note_window)

            self.new_class.options.clear()
            self.new_class.options.append(
                ft.dropdown.Option(
                    key=' ', text=f"{languages[self.lang]['select option']}"
                )
            )
            self.new_class.value = ' '

            all_teacher_classes = await get_teacher_classes(access_token, user_id)
            for item in all_teacher_classes:
                self.new_class.options.append(
                    ft.dropdown.Option(
                        key=item['class_id'], text=f"{item['class_code']}"
                    )
                )
            self.cp.page.update()

    async def load_subjects_teacher(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        user_id = self.cp.user_id
        subjects = await get_teacher_subjects_for_class(access_token, user_id, self.new_class.value)

        self.new_subject.options.clear()
        self.new_subject.options.append(
            ft.dropdown.Option(
                key=' ', text=languages[self.lang]['select option']
            )
        )
        self.new_subject.value = ' '

        for item in subjects:
            self.new_subject.options.append(
                ft.dropdown.Option(
                    key=item['subject_id'], text=f"{item['subject_name']}".upper()
                )
            )

        self.cp.page.update()

    def on_new_class_change(self, e):
        self.run_async_in_thread(self.load_subjects_teacher(e))

    def open_new_note_window(self, e):
        self.run_async_in_thread(self.load_new_notes_data(e))

    def close_new_note_window(self, e):
        self.new_class.value = ' '
        self.new_coefficient.value = None
        self.new_table.controls.clear()
        self.new_subject.value = ' '

        self.hide_one_window(self.new_note_window)

    async def load_students(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        self.new_coefficient.value = await get_subject_coefficient(access_token, self.new_subject.value)

        students = await get_students_without_note_for_subject(
            access_token, self.new_class.value, self.new_sequence.data, self.new_subject.value, self.cp.year_id
        )
        self.new_table.controls.clear()

        if students:
            for item in students:
                self.new_table.controls.append(BoxStudentNote(item))

            self.nb_students.value = len(students)
            self.nb_students.visible = True
            self.no_data.visible = False

        else:
            self.nb_students.value = len(students)
            self.nb_students.visible = False
            self.no_data.visible = True

        self.cp.page.update()

    def on_new_subject_change(self, e):
        self.run_async_in_thread(self.load_students(e))

    def valider_notes(self, e):
        datas_to_insert = []
        for item in self.new_table.controls:
            total_errors = 0
            if item.check.name == 'close':
                total_errors += 1
            elif item.check.name is None:
                pass
            else:
                datas_to_insert.append(
                    {'year_id': self.cp.year_id, 'student_id': item.infos['student_id'],
                     'class_id': self.new_class.value, 'sequence': self.new_sequence.data,
                     'subject_id': self.new_subject.value, 'value': float(item.my_note.value),
                     'coefficient': int(self.new_coefficient.value), 'author': self.cp.user_id}
                )

        if total_errors > 0:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.message.value = languages[self.lang]['error notes']
            self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
            self.cp.icon_message.color = ft.Colors.RED
            self.cp.box.open = True
            self.cp.box.update()

        else:
            total = len(datas_to_insert)

            for i, data in enumerate(datas_to_insert):
                supabase_client.table('notes').insert(data).execute()
                self.new_progress_bar.value = (i + 1) / total

                self.cp.page.update()

            self.new_table.controls.clear()

            self.new_class.value = ' '
            self.new_coefficient.value = None
            self.new_table.controls.clear()
            self.new_subject.value = ' '

            self.hide_one_window(self.new_note_window)

            self.cp.box.title.value = languages[self.lang]['success']
            self.cp.message.value = languages[self.lang]['notes added']
            self.cp.icon_message.name = ft.Icons.CHECK_CIRCLE
            self.cp.icon_message.color = ft.Colors.LIGHT_GREEN
            self.cp.box.open = True
            self.cp.box.update()

    def open_edit_note_window(self, e):
        role = self.cp.page.client_storage.get('role')
        user_id = self.cp.user_id
        print('user id: ', user_id)
        print('author: ', e.control.data['author'])

        if role != 'professeur':
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.message.value = languages[self.lang]['error rights']
            self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
            self.cp.icon_message.color = ft.Colors.RED
            self.cp.box.open = True
            self.cp.box.update()

        else:
            if e.control.data['author'] != user_id:
                self.cp.box.title.value = languages[self.lang]['error']
                self.cp.message.value = languages[self.lang]['bad teacher error']
                self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
                self.cp.icon_message.color = ft.Colors.RED
                self.cp.box.open = True
                self.cp.box.update()

            else:
                self.edit_note_id.value = e.control.data['note_id']
                self.edit_student.value = f"{e.control.data['student_name']} {e.control.data['student_surname']}".upper()
                self.edit_sequence.value = e.control.data['sequence']
                self.edit_subject_name.value = e.control.data['subject_name']
                self.edit_note.value = e.control.data['valeur']

                self.show_one_window(self.edit_note_window)

    def close_edit_note_window(self, e):
        self.hide_one_window(self.edit_note_window)

    def valider_edit_note(self, e):
        if self.edit_note.vaue is None:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.message.value = languages[self.lang]['missing note']
            self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
            self.cp.icon_message.color = ft.Colors.RED
            self.cp.box.open = True
            self.cp.box.update()

        else:
            if self.edit_sequence.value != self.active_sequence.data:
                self.cp.box.title.value = languages[self.lang]['error']
                self.cp.message.value = languages[self.lang]['error invalid sequence']
                self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
                self.cp.icon_message.color = ft.Colors.RED
                self.cp.box.open = True
                self.cp.box.update()

            else:
                datas = {'value': float(self.edit_note.value)}
                edited_datas = {
                    'note_id': int(self.edit_note_id.value), 'value': float(self.edit_note.value),
                    'author': self.cp.user_id
                }
                supabase_client.table('notes').update(datas).eq('id', self.edit_note_id.value).execute()
                supabase_client.table('edited_notes').insert(edited_datas).execute()

                self.hide_one_window(self.edit_note_window)

                self.cp.box.title.value = languages[self.lang]['success']
                self.cp.message.value = languages[self.lang]['note edited']
                self.cp.icon_message.name = ft.Icons.CHECK_CIRCLE
                self.cp.icon_message.color = ft.Colors.LIGHT_GREEN
                self.cp.box.open = True
                self.cp.box.update()

    async def load_export_datas(self, e):
        role = self.cp.page.client_storage.get('role')
        access_token = self.cp.page.client_storage.get('access_token')
        user_id = self.cp.user_id

        if role != 'professeur':
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.message.value = languages[self.lang]['error rights']
            self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
            self.cp.icon_message.color = ft.Colors.RED
            self.cp.box.open = True
            self.cp.box.update()
        else:
            self.show_one_window(self.export_xls_window)

            self.exp_class.options.clear()

            all_teacher_classes = await get_teacher_classes(access_token, user_id)
            for item in all_teacher_classes:
                self.exp_class.options.append(
                    ft.dropdown.Option(
                        key=item['class_id'], text=f"{item['class_code']}"
                    )
                )
            self.cp.page.update()

    def open_export_xls_window(self, e):
        self.run_async_in_thread(self.load_export_datas(e))

    def close_export_xls_window(self, e):
        self.exp_class.value = ' '
        self.exp_sequence.value = ' '
        self.exp_coefficient.value = None
        self.exp_subject.value = ' '

        self.hide_one_window(self.export_xls_window)

    async def load_export_subjects(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        user_id = self.cp.user_id
        subjects = await get_teacher_subjects_for_class(access_token, user_id, self.exp_class.value)

        classe_details = await get_class_details(access_token, self.exp_class.value)
        self.exp_class_name.value = classe_details['code']

        self.exp_subject.options.clear()
        self.exp_subject.options.append(
            ft.dropdown.Option(
                key=' ', text=languages[self.lang]['select option']
            )
        )
        self.exp_subject.value = ' '
        self.exp_subject.update()

        for item in subjects:
            self.exp_subject.options.append(
                ft.dropdown.Option(
                    key=item['subject_id'], text=f"{item['subject_name']}".upper()
                )
            )

        self.cp.page.update()

    def on_export_class_change(self, e):
        self.run_async_in_thread(self.load_export_subjects(e))

    async def load_export_coefficient(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        self.exp_coefficient.value = await get_subject_coefficient(access_token, self.exp_subject.value)

        self.cp.page.update()

    def on_export_subject_change(self, e):
        self.run_async_in_thread(self.load_export_coefficient(e))

    async def load_export_students_without_note(self, e):
        if self.exp_subject.value is not None or self.exp_subject.value != ' ':
            datas_to_export = []

            access_token = self.cp.page.client_storage.get('access_token')

            subject_details = await get_subject_details(access_token, self.exp_subject.value)
            subject_name = subject_details['name']

            students: list[dict] = await get_students_without_note_for_subject(
                access_token, self.exp_class.value, self.exp_sequence.data, self.exp_subject.value, self.cp.year_id
            )

            if students:
                for item in students:
                    dico = {
                        'student_id': item['student_id'],
                        'student_name': f"{item['name']} {item['surname']}",
                        'class_id': self.exp_class.value,
                        'class_code': self.exp_class_name.value,
                        'sequence': self.exp_sequence.data,
                        'subject_id': self.exp_subject.value,
                        'subject_name': subject_name,
                        'coefficient': self.exp_coefficient.value,
                        'value': '',
                    }
                    datas_to_export.append(dico)

                # Étape 1 : Création du fichier Excel en mémoire (méthode robuste)
                df = pd.DataFrame(datas_to_export)
                output_buffer = io.BytesIO()

                with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Élèves')
                file_bytes = output_buffer.getvalue()

                # Générer un nom de fichier unique pour le stockage
                unique_filename = f"templates/template_{uuid.uuid4().hex}.xlsx"

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

            else:
                self.cp.box.title.value = languages[self.lang]['error']
                self.cp.message.value = languages[self.lang]['no data']
                self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
                self.cp.icon_message.color = ft.Colors.RED
                self.cp.box.open = True
                self.cp.box.update()
        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.message.value = languages[self.lang]['select subject first']
            self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
            self.cp.icon_message.color = ft.Colors.RED
            self.cp.box.open = True
            self.cp.box.update()

    def exporter_template_file(self, e):
        self.run_async_in_thread(self.load_export_students_without_note(e))

    async def load_import_file(self, e: ft.FilePickerResultEvent):
        if e.files:
            # on met toutes les données du fichier excel dans une liste
            file = e.files[0]
            absolute_path = os.path.abspath(file.path)
            workbook = openpyxl.load_workbook(absolute_path)
            sheet = workbook.active
            valeurs = list(sheet.values)
            header = valeurs[0]  # on definit la ligne d'entêtes
            valeurs.remove(header)  # on retire la ligne d'entêtes

            self.total_lines_of_file.value = len(valeurs)

            errors = []  # liste qui va contenir les éventuelles erreurs

            counter_verif = 0
            counter_import = 0
            nb_erreurs = 0
            nb_success = 0

            access_token = self.cp.page.client_storage.get('access_token')

            try:
                # on itère sur chaque ligne du fichier pour les vérifications
                for i, item in enumerate(valeurs):

                    # 1. variable pour savoir si la note existe...
                    is_note_exists = await note_exists(
                        access_token=access_token, student_id=item[0], year_id=self.cp.year_id,
                        subject_id=item[5], sequence=item[4]
                    )

                    # 2. liste des classes et listes des matières du professeur...
                    teacher_classes = await get_teacher_classes(
                        access_token=access_token, teacher_id=self.cp.user_id)
                    classes_id = [element['class_id'] for element in teacher_classes]

                    teacher_subjects_class = await get_teacher_subjects_for_class(
                        access_token, self.cp.user_id, item[2]
                    )
                    teacher_subj_ids = [row['subject_id'] for row in teacher_subjects_class]

                    print(item[8], type(item[8]))

                    # 3. On check toutes les potentielles erreurs
                    if isinstance(item[8], str):
                        errors.append(
                            {'ligne': f"ligne {i + 1}", "nature": languages[self.lang]['note is number']}
                        )
                        nb_erreurs += 1
                        print('verif instance')

                    elif item[8] is None:
                        errors.append(
                            {'ligne': f"ligne {i + 1}", "nature": languages[self.lang]['missing note']}
                        )
                        nb_erreurs += 1
                        print('verif missing note')

                    # CORRECTION : On combine la vérification du type ET de la valeur dans un seul elif
                    elif (isinstance(item[8], float) or isinstance(item[8], int)) and item[8] > 20:
                        errors.append(
                            {'ligne': f"ligne {i + 1}", "nature": languages[self.lang]['note > 20']}
                        )
                        nb_erreurs += 1
                        print('verif note > 20')

                    elif item[2] not in classes_id or item[5] not in teacher_subj_ids:
                        errors.append(
                            {'ligne': f"ligne {i + 1}", "nature": languages[self.lang]['bad teacher error']}
                        )
                        nb_erreurs += 1
                        print('verif bad teacher error')

                    elif is_note_exists:
                        errors.append(
                            {'ligne': f"ligne {i + 1}", "nature": languages[self.lang]['note already exists']}
                        )
                        nb_erreurs += 1

                    elif item[0] is None or item[0] == '' or item[2] is None or item[2] == '' or item[5] is None or \
                            item[5] == '':
                        errors.append(
                            {'ligne': f"ligne {i + 1}", "nature": languages[self.lang]['missing data']}
                        )
                        nb_erreurs += 1
                        print('verif note exists')

                    else:
                        # Maintenant, ce bloc sera atteint pour les lignes valides !
                        nb_success += 1
                        print(f"success: ligne {i + 1}")

                    # Mettez à jour les compteurs à l'extérieur de la boucle if/elif/else
                    self.total_errors.value = nb_erreurs
                    counter_verif += 1
                    self.imp_verif_bar.value = counter_verif / len(valeurs)
                    self.imp_verif_text.value = f"{(counter_verif * 100 / len(valeurs)):.0f}%"
                    self.cp.page.update()

            except Exception as ex:
                print(f"❌ Erreur pendant l’analyse de item[8] : {type(e).__name__} - {e}")

            print('counter verif: ', counter_verif)
            print('erreurs', nb_erreurs)
            print('success', nb_success)
            self.total_errors.value = len(errors)
            self.cp.page.update()

            # si le nombre d'erreurs est non nul on affiche la fenêtre des erreurs sinon on importe les données
            if len(errors) > 0:
                self.bloc_table.visible = True
                self.total_errors.color = 'red'

                for i, error in enumerate(errors):
                    line_color = ft.Colors.GREY_100 if i % 2 == 0 else ft.Colors.WHITE
                    self.table_errors.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(error['ligne'])),
                                ft.DataCell(ft.Text(error['nature']))
                            ], color=line_color
                        )
                    )

                self.msg_error.visible = True
                self.cp.page.update()

            else:
                self.bloc_import.visible = True

                for item in valeurs:
                    datas = {
                        'year_id': self.cp.year_id, 'student_id': item[0],
                        'class_id': item[2], 'sequence': self.active_sequence.data,
                        'subject_id': item[5], 'value': float(item[8]),
                        'coefficient': item[7], 'author': self.cp.user_id
                    }
                    await insert_note(access_token=access_token, note_data=datas)
                    counter_import += 1

                    self.imp_insert_text.value = f"{int(counter_import * 100 / len(valeurs))}%"
                    self.imp_insert_bar.value = counter_import / len(valeurs)
                    self.cp.page.update()

                self.cp.box.title.value = languages[self.lang]['success']
                self.cp.message.value = languages[self.lang]['file imported']
                self.cp.icon_message.name = ft.Icons.CHECK_CIRCLE
                self.cp.icon_message.color = ft.Colors.LIGHT_GREEN
                self.cp.box.open = True
                self.cp.box.update()
                self.on_mount()

        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.message.value = languages[self.lang]['no file selected']
            self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
            self.cp.icon_message.color = ft.Colors.RED
            self.cp.box.open = True
            self.cp.box.update()

    def importer_notes(self, e):
        self.run_async_in_thread(self.load_import_file(e))

    def open_import_window(self, e):
        role = self.cp.page.client_storage.get('role')

        if role != 'professeur':
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.message.value = languages[self.lang]['error rights']
            self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
            self.cp.icon_message.color = ft.Colors.RED
            self.cp.box.open = True
            self.cp.box.update()
        else:
            self.show_one_window(self.import_window)

    def close_import_window(self, e):
        self.bloc_import.visible = False
        self.bloc_table.visible = False
        self.imp_insert_bar.value = 0
        self.imp_insert_text.value = "0 %"
        self.imp_verif_bar.value = None
        self.imp_verif_text.value = "0 %"
        self.imp_insert_bar.value = 0
        self.imp_insert_text.value = '0 %'

        self.total_lines_of_file.value = '0'
        self.total_errors.value = '0'
        self.hide_one_window(self.import_window)

    async def load_statistics_datas(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        all_classes  = await get_all_classes_basic_info(access_token)

        for item in all_classes:
            self.stats_class.options.append(
                ft.dropdown.Option(
                    key=item['id'], text=item['code']
                )
            )

        self.show_one_window(self.statistics_window)

    def open_statistics_window(self, e):
        self.run_async_in_thread(self.load_statistics_datas(e))

    def close_statistics_window(self, e):
        self.stats_class.options.clear()
        self.stats_class.options.append(
            ft.dropdown.Option(
                key=' ', text=languages[self.lang]['select option']
            )
        )
        self.stats_class.value = ' '
        self.stats_subject.options.clear()
        self.stats_subject.options.append(
            ft.dropdown.Option(
                key=' ', text=languages[self.lang]['select option']
            )
        )
        self.stats_subject.value = ' '
        self.stats_nb_students.value = '-'
        self.stats_success_rate.value = '-'
        self.stats_nb_success.value = '-'
        self.stats_nb_girls_success.value = '-'
        self.stats_nb_boys_success.value = '-'
        self.hide_one_window(self.statistics_window)

    async def load_stats_subject(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        subjects = await get_subjects_by_class_id(access_token, self.stats_class.value)

        self.stats_subject.options.clear()
        self.stats_subject.options.append(
            ft.dropdown.Option(
                key=' ', text=languages[self.lang]['select option']
            )
        )
        for item in subjects:
            self.stats_subject.options.append(
                ft.dropdown.Option(
                    key=item['subject_id'], text=item['subject_name'].upper()
                )
            )

        self.cp.page.update()

    def on_stats_class_change(self, e):
        self.run_async_in_thread(self.load_stats_subject(e))

    async def load_all_statistics(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        year_id = self.cp.year_id

        stats = await get_statistics_by_class_subject(
            access_token, year_id, self.stats_class.value, self.stats_subject.value, self.stats_sequence.value
        )
        print(stats)
        self.stats_nb_students.value = stats['total_notes']
        self.stats_success_rate.value = f"{stats['success_rate_percent']:.2f} %"
        self.stats_nb_success.value = stats['notes_ge_10']
        self.stats_nb_girls_success.value = stats['girls_above_10']
        self.stats_nb_boys_success.value = stats['boys_above_10']
        self.cp.page.update()

    def on_stats_subject_change(self, e):
        self.run_async_in_thread(self.load_all_statistics(e))

