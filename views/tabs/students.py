from utils.couleurs import *
from utils.styles import login_style, drop_style, switch_style, ct_style, intern_ct_style, datatable_style, ml_style
from components import OneStudent, MyTextButton, MyButton, DateSelection
from services.async_functions.students_functions import *
from services.async_functions.general_functions import *
from services.supabase_client import supabase_client
from translations.translations import languages
from utils.useful_functions import format_number, add_separator
import os, qrcode, uuid, mimetypes, asyncio, threading, io
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import datetime

# Bucket for pictures
BUCKET_STUDENTS_PICTURES = "students_pictures"
BUCKET_REGISTRATIONS = 'receipts'
DEFAULT_IMAGE_URL = ''


class Students(ft.Container):
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
        self.table = ft.GridView(
            expand=True,
            max_extent=250,
            child_aspect_ratio=0.8,
            spacing=20,
            run_spacing=20
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
                                    ft.Text(languages[lang]['menu students'].capitalize(), size=24, font_family="PEB"),
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
                                    MyTextButton( languages[lang]['new registration'], self.open_registrations_ct),
                                    MyTextButton(languages[lang]['new student'], self.open_new_student_container),
                                    MyTextButton('disicpline', self.open_discipline_window)
                                ]
                            ),
                            self.search
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Container(
                        padding=0, border_radius=16,
                        expand=True, content=self.table
                    )
                ]
            )
        )

        # Nouvelle inscription...
        self.ins_class = ft.Dropdown(
            **drop_style, prefix_icon=ft.Icons.ACCOUNT_BALANCE_OUTLINED,
            on_change=self.changing_class, menu_height=200, expand=True, hint_text=languages[lang]['class'],
            options=[ft.dropdown.Option(key=' ', text=languages[lang]['select option'])], value=' '
        )
        self.unregistered = ft.Dropdown(
            **drop_style, prefix_icon=ft.Icons.PERSON_OUTLINED, expand=True,
            on_change=self.changing_class, menu_height=200, hint_text=languages[lang]['student'],
        )
        self.ins_mat = ft.TextField(
            **login_style, prefix_icon=ft.Icons.CREDIT_CARD, expand=True, disabled=True,
            label=languages[lang]['class']
        )
        self.ins_check = ft.Checkbox(
            label=languages[self.lang]['repeater check'],
            label_style=ft.TextStyle(size=14, font_family="PPI", color='grey'),
            active_color="#f0f0f6", check_color=ACCENT_PLUS_COLOR
        )
        self.ins_fees = ft.TextField(
            **login_style, prefix_icon=ft.Icons.MONETIZATION_ON_OUTLINED, expand=True,
            text_align=ft.TextAlign.RIGHT, hint_text=languages[lang]['fees']
        )
        self.tranche_1 = ft.TextField(
            **login_style, expand=True, label=languages[self.lang]['fees part 1'],
            input_filter=ft.NumbersOnlyInputFilter(),
            prefix_icon=ft.Icons.MONETIZATION_ON_OUTLINED,
            text_align=ft.TextAlign.RIGHT, data='fees part 1'
        )
        self.tranche_2 = ft.TextField(
            **login_style, expand=True, label=languages[self.lang]['fees part 2'],
            input_filter=ft.NumbersOnlyInputFilter(),
            prefix_icon=ft.Icons.MONETIZATION_ON_OUTLINED,
            text_align=ft.TextAlign.RIGHT, data='fees part 2'
        )
        self.tranche_3 = ft.TextField(
            **login_style, expand=True, label=languages[self.lang]['fees part 3'],
            input_filter=ft.NumbersOnlyInputFilter(),
            prefix_icon=ft.Icons.MONETIZATION_ON_OUTLINED,
            text_align=ft.TextAlign.RIGHT, data='fees part 3'
        )
        self.switch = ft.Switch(
            **switch_style, on_change=self.changing_pay_off_state
        )

        self.ct_registrations = ft.Container(
            **ct_style,
            content=ft.Container(
                **intern_ct_style,
                width=530, padding=0,
                content=ft.Column(
                    expand=True, scroll=ft.ScrollMode.AUTO,
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
                                            ft.Text(languages[self.lang]['registration'], size=20, font_family='PEB'),
                                        ]
                                    ),
                                    ft.IconButton('close', icon_color='black87', bgcolor=MAIN_COLOR,
                                                  on_click=self.close_ct_registrations),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            padding=20, border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True,
                            bgcolor='white',
                            content=ft.Column(
                                expand=True, scroll=ft.ScrollMode.AUTO,
                                controls=[
                                    self.unregistered, self.ins_class, self.ins_mat, self.ins_fees,
                                    self.ins_check,
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Column(
                                        controls=[
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[self.lang]['school fees'].upper(), size=16,
                                                            font_family="PPB"),
                                                    ft.Divider(
                                                        height=1, thickness=1,
                                                        badge=ft.Badge(text=f"{languages[self.lang]['school fees'].upper()}")
                                                    ),
                                                ], spacing=0
                                            ),
                                            ft.Row([ft.Text(languages[self.lang]['pay off'], size=16,
                                                            font_family="PPM"), self.switch]),
                                            ft.Row([self.tranche_1, self.tranche_2, self.tranche_3, ]),
                                            MyButton(
                                                'Valider', 'check', 150, self.add_registration
                                            ),
                                        ]
                                    ),
                                ]
                            )
                        )
                    ]
                )
            )
        )

        # Nouvel éléve ...
        self.new_nom = ft.TextField(
            **login_style, prefix_icon=ft.Icons.PERSON_OUTLINE_OUTLINED, width=330,
            capitalization=ft.TextCapitalization.CHARACTERS, hint_text=languages[lang]['name']
        )
        self.new_prenom = ft.TextField(
            **login_style, prefix_icon=ft.Icons.PERSON_OUTLINE_OUTLINED, width=330, hint_text=languages[lang]['surname']
        )
        self.new_date = DateSelection(self)
        self.new_sex = ft.Dropdown(
            **drop_style, width=160, hint_text=languages[self.lang]['gender'],
            prefix_icon=ft.Icons.WC_OUTLINED, options=[
                ft.dropdown.Option(gender) for gender in ['M', 'F']
            ]
        )
        self.new_lieu = ft.TextField(
            **login_style, prefix_icon=ft.Icons.PLACE_OUTLINED, width=200, hint_text=languages[lang]['place of birth']
        )
        self.new_pere = ft.TextField(
            **login_style, prefix_icon=ft.Icons.MAN_3_OUTLINED, width=330,
            capitalization=ft.TextCapitalization.CHARACTERS, hint_text=languages[lang]['father']
        )
        self.new_mere = ft.TextField(
            **login_style, prefix_icon=ft.Icons.WOMAN_OUTLINED, width=330,
            capitalization=ft.TextCapitalization.CHARACTERS, hint_text=languages[lang]['mother']
        )
        self.new_contact = ft.TextField(
            **login_style, prefix_icon=ft.Icons.PHONE_ANDROID_OUTLINED, width=200, prefix_text="+237 ",
            input_filter=ft.NumbersOnlyInputFilter(), hint_text=languages[lang]['contact']
        )
        self.new_other = ft.TextField(
            **login_style, prefix_icon=ft.Icons.PHONE_ANDROID_OUTLINED, width=200, prefix_text="+237 ",
            input_filter=ft.NumbersOnlyInputFilter(), hint_text=languages[lang]['contact 2']
        )
        self.new_residence = ft.TextField(
            **login_style, prefix_icon=ft.Icons.LOCATION_ON_OUTLINED, expand=True, hint_text=languages[lang]['residence']
        )
        self.ct_new_student = ft.Container(
            **ct_style,
            content=ft.Container(
                **intern_ct_style,
                width=700, padding=0,
                content=ft.Column(
                    expand=True, scroll=ft.ScrollMode.AUTO,
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
                                            ft.Icon(ft.Icons.PERSON_ADD_OUTLINED, size=24, color="black"),
                                            ft.Text(languages[self.lang]['new student'], size=20, font_family='PEB'),
                                        ]
                                    ),
                                    ft.IconButton('close', icon_color='black87', bgcolor=MAIN_COLOR,
                                                  on_click=self.close_new_student_container),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            padding=20, border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True,
                            bgcolor='white',
                            content=ft.Column(
                                expand=True, scroll=ft.ScrollMode.AUTO,
                                controls=[
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[self.lang]['student info'].upper(), size=16,
                                                    font_family="PPB"),
                                            ft.Divider(height=1, thickness=1)
                                        ], spacing=0
                                    ),
                                    ft.Row([self.new_nom, self.new_prenom]),
                                    ft.Row([self.new_date, self.new_sex, ]),
                                    ft.Row([self.new_lieu, self.new_residence, ]),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[self.lang]['parent info'].upper(), size=16,
                                                    font_family="PPB"),
                                            ft.Divider(height=1, thickness=1)
                                        ], spacing=0
                                    ),
                                    ft.Row([self.new_pere, self.new_mere]),
                                    ft.Row([self.new_contact, self.new_other]),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Row([MyButton(languages[self.lang]['valid'], 'check', 200, self.add_eleve)])
                                ]
                            )
                        )
                    ]
                )
            )
        )

        # Edit student window ______________________________________________________________________________________
        self.edit_id_student = ''
        self.edit_nom = ft.TextField(
            **login_style, prefix_icon=ft.Icons.PERSON_OUTLINE_OUTLINED, width=400, label=languages[self.lang]['name'],
            capitalization=ft.TextCapitalization.CHARACTERS
        )
        self.edit_prenom = ft.TextField(
            **login_style, prefix_icon=ft.Icons.PERSON_OUTLINE_OUTLINED, width=400,
            label=languages[self.lang]['surname'],
        )
        self.edit_mat = ft.TextField(
            **login_style, width=200, disabled=True, label=languages[self.lang]['registration number'],
        )
        self.edit_date = ft.TextField(
            **login_style, width=150, prefix_icon=ft.Icons.CALENDAR_MONTH, label=languages[self.lang]['born in'],
        )
        self.edit_sex = ft.TextField(
            **login_style, width=140, prefix_icon='wc', label=languages[self.lang]['gender'],
        )
        self.edit_lieu = ft.TextField(
            **login_style, prefix_icon=ft.Icons.PLACE_OUTLINED, width=200, label=languages[self.lang]['born at'],
        )
        self.edit_pere = ft.TextField(
            **login_style, prefix_icon=ft.Icons.MAN_3_OUTLINED, width=250,
            capitalization=ft.TextCapitalization.CHARACTERS, label=languages[self.lang]['father'],
        )
        self.edit_mere = ft.TextField(
            **login_style, prefix_icon=ft.Icons.WOMAN_OUTLINED, width=250,
            capitalization=ft.TextCapitalization.CHARACTERS, label=languages[self.lang]['mother'],
        )
        self.edit_contact = ft.TextField(
            **login_style, prefix_icon=ft.Icons.PHONE_ANDROID_OUTLINED, width=200,
            input_filter=ft.NumbersOnlyInputFilter(), label=languages[self.lang]['contact'],
        )
        self.edit_other = ft.TextField(
            **login_style, prefix_icon=ft.Icons.PHONE_ANDROID_OUTLINED, width=200,
            input_filter=ft.NumbersOnlyInputFilter(), label=languages[self.lang]['contact 2'],
        )
        self.edit_residence = ft.TextField(
            **login_style, prefix_icon=ft.Icons.LOCATION_ON_OUTLINED, width=250, label=languages[self.lang]['residence'],
        )
        self.edit_image_url = ft.TextField(
            **login_style, disabled=True, prefix_icon=ft.Icons.PICTURE_IN_PICTURE_OUTLINED,
            label="URL Image",
        )
        self.cp.fp_image_student.on_result = self.set_image_url
        self.image_button = MyButton(
            languages[self.lang]['load image'], ft.Icons.ADD_A_PHOTO_OUTLINED, 200,
            lambda _: self.cp.fp_image_student.pick_files(allow_multiple=False,
                                                          allowed_extensions=['png', 'jpg', 'webp', 'avif'])
        )
        self.image_preview = ft.CircleAvatar(radius=50)
        self.ct_edit_student = ft.Container(
            **ct_style,
            content=ft.Container(
                **intern_ct_style,
                width=650, height=700, padding=0,
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
                                            ft.Icon(ft.Icons.EDIT_OUTLINED, size=24, color="black"),
                                            ft.Text(languages[self.lang]['edit student'], size=20, font_family='PEB'),
                                        ]
                                    ),
                                    ft.IconButton('close', icon_color='black87', bgcolor=MAIN_COLOR,
                                                  on_click=self.close_ct_edit_student),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            padding=20, border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True,
                            bgcolor='white',
                            content=ft.Column(
                                expand=True, scroll=ft.ScrollMode.AUTO,
                                controls=[
                                    ft.Row(
                                        controls=[self.image_preview, ft.Column(controls=[self.edit_nom, self.edit_prenom])]
                                        , spacing=50
                                    ),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Divider(height=1, thickness=1),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Row(controls=[self.edit_sex,self.edit_date,self.edit_lieu]),
                                    ft.Divider(height=2, color=ft.Colors.TRANSPARENT),
                                    ft.Row(controls=[self.edit_pere, self.edit_mere]),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Row(controls=[self.edit_contact, self.edit_other]),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Row(controls=[self.edit_residence, self.edit_mat]),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    self.edit_image_url,
                                    ft.Container(
                                        padding=10, content=ft.Row(
                                            controls=[
                                                ft.Row([self.image_button, ]),
                                                ft.Row(
                                                    controls=[
                                                        MyButton(
                                                            languages[self.lang]['valid'], None, 200,
                                                            self.update_student
                                                        )
                                                    ]
                                                ),
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

        # School fees window ________________________________________________
        self.sc_name = ft.Text(size=24, font_family='PPM')
        self.sc_surname = ft.Text(size=16, font_family='PPM', color='black54')
        self.sc_student_id = ft.Text(size=11, font_family='PPI', color='grey', visible=False)
        self.sc_class = ft.Text(size=16, font_family="PPB")
        self.sc_payment_table = ft.DataTable(
            **datatable_style, columns=[
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.CALENDAR_MONTH, color=ft.Colors.WHITE, size=22),
                            ft.Text("Date")
                        ]
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.REPARTITION_OUTLINED, color=ft.Colors.WHITE, size=22),
                            ft.Text(languages[self.lang]['fees part'])
                        ]
                    )
                ), ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.MONETIZATION_ON_OUTLINED, color=ft.Colors.WHITE, size=22),
                            ft.Text(languages[self.lang]['amount'])
                        ]
                    )
                ),

            ],
        )
        self.sc_amount_paid = ft.TextField(
            **login_style, width=150, read_only=True, label=languages[lang]['amount paid']
        )
        self.sc_amount_expected = ft.TextField(
            **login_style, width=150, read_only=True, label=languages[lang]['amount expected']
        )
        self.sc_amount_due = ft.TextField(
            **login_style, width=150, read_only=True, label=languages[lang]['amount due']
        )

        self.status = ft.Text(size=16, font_family="PPM")
        self.status_icon = ft.Icon(size=16)
        self.status_container = ft.Container(
            alignment=ft.alignment.center, padding=10, border_radius=16,
            content=ft.Row([self.status_icon, self.status], spacing=3)
        )
        self.sc_pay_button = MyButton(
            languages[self.lang]['make a payment'], 'monetization_on_outlined',
            None, self.make_a_payment
        )
        self.pay_print_button = MyButton(
            languages[self.lang]['print receipt'], 'print_outlined',
            200, None
        )
        self.sc_tranche_1 = ft.TextField(
            **login_style, width=150, label=languages[self.lang]['fees part 1'],
            input_filter=ft.NumbersOnlyInputFilter(),
            prefix_icon=ft.Icons.MONETIZATION_ON_OUTLINED,
            text_align=ft.TextAlign.RIGHT, data='fees part 1'
        )
        self.sc_tranche_2 = ft.TextField(
            **login_style, width=150, label=languages[self.lang]['fees part 2'],
            input_filter=ft.NumbersOnlyInputFilter(),
            prefix_icon=ft.Icons.MONETIZATION_ON_OUTLINED,
            text_align=ft.TextAlign.RIGHT, data='fees part 2'
        )
        self.sc_tranche_3 = ft.TextField(
            **login_style, width=150, label=languages[self.lang]['fees part 3'],
            input_filter=ft.NumbersOnlyInputFilter(),
            prefix_icon=ft.Icons.MONETIZATION_ON_OUTLINED,
            text_align=ft.TextAlign.RIGHT, data='fees part 3'
        )
        self.sc_switch = ft.Switch(
            **switch_style, on_change=self.changing_pay_off_state
        )
        self.payment_container = ft.Column(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(languages[self.lang]['make a payment'], size=16,
                                font_family="PPB"),
                        ft.Row(controls=[self.sc_tranche_1, self.sc_tranche_2,
                                         self.sc_tranche_3])
                    ], spacing=5
                ),
                ft.Row([self.sc_pay_button, self.pay_print_button])
            ]
        )
        self.sc_second_container = ft.Column(
            expand=True, alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(languages[self.lang]['loading screen'], size=18, font_family='PPR'),
                        ft.ProgressBar(color=BASE_COLOR)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            ]
        )
        self.school_fees_window = ft.Container(
            **ct_style,
            content=ft.Container(
                **intern_ct_style,
                width=600, padding=0,
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
                                            ft.Icon(ft.Icons.MONETIZATION_ON, size=24, color='black'),
                                            ft.Text(languages[self.lang]['school fees'], size=20, font_family='PPB'),
                                        ]
                                    ),
                                    ft.IconButton('close', icon_color='black87', bgcolor=MAIN_COLOR,
                                                  on_click=self.close_school_fees_window),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            padding=20, border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True,
                            bgcolor='white',
                            content=ft.Column(
                                expand=True, scroll=ft.ScrollMode.AUTO, controls=[self.sc_second_container]
                            )
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            )
        )

        # Discipline window...
        self.dis_student = ft.Dropdown(
            **drop_style, prefix_icon='person_outlined', expand=True, menu_height=200,
            options=[ft.dropdown.Option(key=' ', text=languages[self.lang]['select option'])],
            label=languages[lang]['student']
        )
        self.dis_sequence = ft.TextField(
            **login_style, prefix_icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
            width=200, label=languages[lang]['sequence'], disabled=True
        )
        self.dis_type = ft.Dropdown(
            **drop_style, prefix_icon=ft.Icons.WARNING_AMBER_OUTLINED, menu_height=200,
            options=[
                ft.dropdown.Option(
                    key=choice['key'], text=choice['text']
                ) for choice in [
                    {'key': ' ', 'text': languages[self.lang]['select option']},
                    {'key': 'ban', 'text': languages[self.lang]['ban']},
                    {'key': 'detention', 'text': languages[self.lang]['detention']},
                    {'key': 'justified absence', 'text': languages[self.lang]['justified absence']},
                    {'key': 'late', 'text': languages[self.lang]['late']},
                    {'key': 'permanent ban', 'text': languages[self.lang]['permanent ban']},
                    {'key': 'reprimand', 'text': languages[self.lang]['reprimand']},
                    {'key': 'unjustified absence', 'text': languages[self.lang]['unjustified absence']},
                    {'key': 'warning', 'text': languages[self.lang]['warning']},
                ]
            ], label='type', expand=True
        )
        self.dis_qty = ft.TextField(
            **login_style, width=150, prefix_icon=ft.Icons.ONETWOTHREE, text_align=ft.TextAlign.RIGHT,
            input_filter=ft.NumbersOnlyInputFilter(), label=languages[lang]['quantity']
        )
        self.dis_comment = ft.TextField(
            **ml_style, multiline=True, min_lines=8, expand=True,
            label=languages[lang]['comment']
        )

        self.discipline_window = ft.Container(
            **ct_style,
            content=ft.Container(
                **intern_ct_style,
                width=600, padding=0,
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
                                            ft.Icon(ft.Icons.EMERGENCY, size=24, color='black'),
                                            ft.Text('discipline', size=20, font_family='PPB'),
                                        ]
                                    ),
                                    ft.IconButton('close', icon_color='black87', bgcolor=MAIN_COLOR,
                                                  on_click=self.close_discipline_window),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            padding=20, border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True,
                            bgcolor='white',
                            content=ft.Column(
                                expand=True, scroll=ft.ScrollMode.AUTO,
                                controls=[
                                    self.dis_student,
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    self.dis_type,
                                    ft.Row([self.dis_sequence, self.dis_qty,]),
                                    self.dis_comment,
                                    ft.Container(
                                        padding=10, content=MyButton(
                                            languages[self.lang]['valid'], None, 200,
                                            self.create_new_sanction
                                        )
                                    )
                                ], spacing=10
                            )
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            )
        )

        # discipline report window...
        self.report_name = ft.Text(size=16, font_family='PPM')
        self.report_surname = ft.Text(size=16, font_family='PPM', color='black54')
        self.report_image = ft.CircleAvatar(radius=30)
        self.report_class = ft.Text(size=16, font_family="PPB")
        self.report_table = ft.DataTable(
            **datatable_style, columns=[
                ft.DataColumn(
                    ft.Text(data)
                ) for data in [
                    languages[lang]['sequence'], 'type',
                    languages[lang]['quantity'], languages[lang]['comment']
                ]
            ],
        )
        self.count_unjustified = ft.Text('0', size=16, font_family='PPM', data='unjustified absence')
        self.count_justified = ft.Text('0', size=16, font_family='PPM', data='justified absence')
        self.count_warning = ft.Text('0', size=16, font_family='PPM', data='warning')
        self.count_ban = ft.Text('0', size=16, font_family='PPM', data='ban')
        self.count_permanent_ban = ft.Text('0', size=16, font_family='PPM', data='permanent ban')
        self.count_reprimand= ft.Text('0', size=16, font_family='PPM', data='reprimand')
        self.count_detention = ft.Text('0', size=16, font_family='PPM', data='detention')
        self.count_late = ft.Text('0', size=16, font_family='PPM', data='late')
        self.sub_report_container = ft.Column(
            expand=True, alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(languages[self.lang]['loading screen'], size=18, font_family='PPR'),
                        ft.ProgressBar(color=BASE_COLOR)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            ], spacing=10,
        )
        self.report_window = ft.Container(
            **ct_style,
            content=ft.Container(
                **intern_ct_style,
                width=700, padding=0,
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
                                            ft.Icon(ft.Icons.CONTENT_PASTE_ROUNDED, size=24, color='black'),
                                            ft.Text('discipline report', size=20, font_family='PPB'),
                                        ]
                                    ),
                                    ft.IconButton('close', icon_color='black87', bgcolor=MAIN_COLOR,
                                                  on_click=self.close_report_window),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            padding=20, border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True,
                            bgcolor='white',
                            content=ft.Column(
                                expand=True, scroll=ft.ScrollMode.AUTO,
                                controls=[
                                    self.sub_report_container
                                ], spacing=10
                            )
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            )
        )


        # contenu...
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

        # lancer le chargement des données...
        self.on_mount()

    async def build_main_view(self):
        self.content.controls.clear()

        for widget in (
            self.main_window, self.ct_registrations, self.ct_new_student, self.ct_edit_student,
            self.school_fees_window, self.discipline_window, self.report_window
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
        await self.load_unregistered_students()
        await self.load_classes()

    def on_mount(self):
        self.run_async_in_thread(self.on_init_async())

    async def load_classes(self):
        access_token = self.cp.page.client_storage.get("access_token")
        classes = await get_all_classes_basic_info(access_token)

        for one_class in classes:
            self.ins_class.options.append(
                ft.dropdown.Option(
                    key=one_class['id'], text=f"{one_class['code']}"
                )
            )

        self.ins_class.update()

    async def load_datas(self):
        access_token = self.cp.page.client_storage.get("access_token")
        year_id = self.cp.year_id

        active_sequence = await get_active_sequence(access_token)

        self.active_sequence.value = languages[self.lang][active_sequence['name']]
        self.active_quarter.value = languages[self.lang][active_sequence['quarter']]
        self.active_sequence.data = active_sequence['name']
        self.active_quarter.data = active_sequence['quarter']

        datas = await get_students_with_details_wf(access_token, year_id)

        self.table.controls.clear()

        for student in datas:
            self.table.controls.append(
                OneStudent(self, student)
            )

        self.cp.page.update()

        await self.build_main_view()
        print(self.active_sequence.data)

    async def load_filter_datas(self, e):
        access_token = self.cp.page.client_storage.get("access_token")
        year_id = self.cp.year_id
        datas = await get_students_with_details_wf(access_token, year_id)
        my_search = self.search.value.lower() if self.search else ''
        filtered_datas = list(
            filter(
                lambda x: my_search in x['student_name'].lower() or my_search in x['student_surname'].lower(),
                datas
            )
        )

        self.table.controls.clear()

        for student in filtered_datas:
            self.table.controls.append(
                OneStudent(self, student)
            )

        self.cp.page.update()

    def filter_datas(self, e):
        self.run_async_in_thread(self.load_filter_datas(e))

    async def load_unregistered_students(self):
        access_token = self.cp.page.client_storage.get("access_token")

        students = await get_unregistered_students(access_token)
        self.unregistered.options.clear()

        self.unregistered.options.append(
            ft.dropdown.Option(
                key=' ', text=f"{languages[self.lang]['select option']}"
            )
        )

        for student in students:
            self.unregistered.options.append(
                ft.dropdown.Option(
                    key=student['student_id'], text=f"{student['student_name']} {student['student_surname']}".upper()
                )
            )

        self.unregistered.value = " "
        self.unregistered.update()

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

    def open_registrations_ct(self, e):
        role = self.cp.page.client_storage.get('role')

        if role in ('secrétaire', 'économe'):
            self.show_one_window(self.ct_registrations)
        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.message.value = languages[self.lang]['error rights']
            self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
            self.cp.icon_message.color = ft.Colors.RED
            self.cp.box.open = True
            self.cp.box.update()

    async def set_registration_number(self, e):
        self.ins_mat.value = get_new_registration_number() if self.ins_mat.value in ['', None] else self.ins_mat.value
        self.ins_mat.update()

    def changing_class(self, e):
        self.run_async_in_thread(self.set_registration_number(e))

    async def solder_pension(self, e):
        if self.switch.value:
            access_token = self.cp.page.client_storage.get("access_token")
            year_id = self.cp.year_id

            fees = await get_fees_amount_by_year(access_token, year_id)

            self.tranche_1.value = fees['fees_part_1']
            self.tranche_2.value = fees['fees_part_2']
            self.tranche_3.value = fees['fees_part_3']
            self.cp.page.update()
        else:
            self.tranche_3.value = None
            self.tranche_2.value = None
            self.tranche_1.value = None
            self.cp.page.update()

    def changing_pay_off_state(self, e):
        self.run_async_in_thread(self.solder_pension(e))

    @staticmethod
    def create_pdf_fonts():
        pdfmetrics.registerFont(TTFont('clb', "assets/fonts/calibrib.ttf"))
        pdfmetrics.registerFont(TTFont('cli', "assets/fonts/calibrii.ttf"))
        pdfmetrics.registerFont(TTFont('cal', "assets/fonts/calibri.ttf"))

    async def generate_receipt_pdf(self) -> str:
        selected_student, selected_student_id, selected_class = '', '', ''
        registration_date = datetime.datetime.now().strftime("%d/%m/%Y")
        access_token = self.cp.page.client_storage.get('access_token')

        selected_student = get_student_name_by_id(self.unregistered.value)
        selected_student_id = self.unregistered.value
        selected_class = await get_class_code_by_id_async(self.ins_class.value, access_token)

        print("-------generer reçu__________")
        # print(selected_student, selected_student_id, selected_class, int(self.ins_fees.value))

        # QR Code
        qr_data = (
            f"ID élève"
            f"\nAnnée scolaire: {self.cp.year_label}"
            f"\nID élève: {self.unregistered.value}"
            f"\nNom: {selected_student}"
            f"\nClasse: {selected_class}"
            f"\nMatricule: {self.ins_mat.value}"
            f"\nPar: {self.cp.user_name.value}"
            f"\nLe {registration_date}"
        )
        qr_img = qrcode.make(qr_data)
        qr_img_pil = qr_img.convert("RGB")
        qr_reader = ImageReader(qr_img_pil)

        self.create_pdf_fonts()

        # PDF config
        buffer = io.BytesIO()
        page_width = 7.2 * cm
        page_height = 29.7 * cm
        c = canvas.Canvas(buffer, pagesize=(page_width, page_height))
        c.translate(0.5 * cm, 0)  # Juste une petite marge à gauche

        y = page_height - 1 * cm  # Commence en haut

        def write_centered_line(text, font_size=8, bold=False, space=0.5 * cm, police='cal'):
            nonlocal y
            font = 'cal' if bold else police
            c.setFont(font, font_size)
            c.drawCentredString((page_width - 1 * cm) / 2, y, text)
            y -= space

        # Entête
        write_centered_line("Reçu / Receipt", police='clb', font_size=12, bold=False, space=1 * cm)
        write_centered_line(school_republic_fr, font_size=9, bold=False)
        write_centered_line(national_devise_fr, font_size=9, bold=False)
        write_centered_line(school_delegation_fr, font_size=9, bold=False)
        write_centered_line(school_name_fr, font_size=9, bold=False)
        write_centered_line("", space=0.7 * cm)

        # Infos élève
        write_centered_line(f"Année scolaire : {self.cp.year_label}")
        write_centered_line(f"Nom : {selected_student}")
        write_centered_line(f"Classe : {selected_class}")
        write_centered_line(f"Frais d'inscription : {self.ins_fees.value} FCFA")
        write_centered_line(f"Date d'inscription : {registration_date}")
        write_centered_line("", space=1 * cm)

        # QR Code
        c.drawImage(qr_reader, x=2.1 * cm, y=y - 3 * cm, width=3 * cm, height=3 * cm)
        y -= 3.5 * cm

        # Signature
        write_centered_line("", space=1 * cm)
        write_centered_line("Signature de la Direction")
        write_centered_line("_________________________")

        # Enregistrement
        c.save()
        buffer.seek(0)

        # Upload Supabase
        file_path = f"fiche_{self.unregistered.value}_{uuid.uuid4().hex[:6]}.pdf"

        supabase_client.storage.from_(BUCKET_REGISTRATIONS).upload(
            path=file_path,
            file=buffer.getvalue(),
            file_options={"content-type": "application/pdf"}
        )

        signed_url_response = supabase_client.storage.from_(BUCKET_REGISTRATIONS).create_signed_url(
            file_path, 3600 * 24 * 365
        )
        signed_url = signed_url_response.get("signedURL")
        return signed_url

    async def valider_inscription(self, e):
        if self.ins_class.value:

            # update registration number...
            # try:
            supabase_client.table('students').update(
                {'registration_number': self.ins_mat.value}).eq('id', self.unregistered.value).execute()

            my_url = await self.generate_receipt_pdf()

            # Add a registration...
            repeater = True if self.ins_check.value else False
            supabase_client.table('registrations').insert(
                {'year_id': self.cp.year_id, 'student_id': self.unregistered.value,
                 'class_id': self.ins_class.value, 'receipt_url': my_url,
                 'repeater': repeater, "amount": int(self.ins_fees.value)}
            ).execute()

            self.cp.page.launch_url(my_url)

            # inscription dans la table school_fees...
            supabase_client.table('school_fees').insert(
                {
                    'year_id': self.cp.year_id, 'student_id': self.unregistered.value,
                    "part": "registration", "amount": int(self.ins_fees.value)
                }
            ).execute()

            # add school fees
            for tranche in (self.tranche_1, self.tranche_2, self.tranche_3):
                if tranche.value is None or tranche.value == "":
                    pass
                else:
                    amount_part = int(tranche.value)
                    supabase_client.table('school_fees').insert(
                        {
                            'year_id': self.cp.year_id, 'student_id': self.unregistered.value,
                            'part': tranche.data, 'amount': amount_part,
                        }
                    ).execute()

            self.cp.box.title.value = languages[self.lang]['success']
            self.cp.message.value = languages[self.lang]['student registered']
            self.cp.icon_message.name = ft.Icons.CHECK_CIRCLE
            self.cp.icon_message.color = ft.Colors.LIGHT_GREEN
            self.cp.box.open = True
            self.cp.box.update()

            # empty fields...
            for widget in (
                    self.ins_fees, self.ins_mat, self.ins_check, self.switch,
                    self.tranche_1, self.tranche_2, self.tranche_3, self.unregistered
            ):
                widget.value = None
                widget.update()

            self.ins_class.value = ' '
            await self.load_unregistered_students()
            self.on_mount()


        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.message.value = languages[self.lang]['error msg']
            self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
            self.cp.icon_message.color = ft.Colors.RED
            self.cp.box.open = True
            self.cp.box.update()

    def add_registration(self, e):
        self.run_async_in_thread(self.valider_inscription(e))

    def close_ct_registrations(self, e):
        self.hide_one_window(self.ct_registrations)

    def open_new_student_container(self, e):
        role = self.cp.page.client_storage.get('role')
        if role in ['secrétaire', 'économe']:
            self.show_one_window(self.ct_new_student)
        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.message.value = languages[self.lang]['error rights']
            self.cp.box.open = True
            self.cp.box.update()

    def add_eleve(self, e):
        counter = 0
        for widget in (
            self.new_nom, self.new_prenom, self.new_sex, self.new_lieu, self.new_pere, self.new_mere,
            self.new_date.year, self.new_date.month, self.new_date.day,
            self.new_contact, self.new_date.day, self.new_date.month, self.new_date.year
        ):
            if widget.value is None or widget.value == "":
                counter += 1

        if counter == 0:
            try:
                supabase_client.table('students').insert(
                    {
                        'name': self.new_nom.value, 'surname': self.new_prenom.value, 'gender': self.new_sex.value,
                        'birth_place': self.new_lieu.value,
                        'birth_date': f"{int(self.new_date.day.value)}/{int(self.new_date.month.value)}/{int(self.new_date.year.value)}",
                        'father': self.new_pere.value, 'mother': self.new_mere.value, 'contact': self.new_contact.value,
                        'other_contact': self.new_other.value, 'city': self.new_residence.value
                    }
                ).execute()

                for widget in (
                    self.new_nom, self.new_prenom, self.new_sex, self.new_lieu, self.new_pere, self.new_mere,
                    self.new_date.year, self.new_date.month, self.new_date.day, self.new_other, self.new_residence,
                    self.new_contact, self.new_date.day, self.new_date.month, self.new_date.year
                ):
                    widget.value = None
                    widget.update()

                # Mise à jour de données
                self.run_async_in_thread(self.load_unregistered_students())

                self.cp.box.title.value = languages[self.lang]['success']
                self.cp.message.value = languages[self.lang]['student added']
                self.cp.icon_message.name = ft.Icons.CHECK_CIRCLE
                self.cp.icon_message.color = ft.Colors.LIGHT_GREEN
                self.cp.box.open = True
                self.cp.box.update()


            except Exception as e:
                self.cp.box.title.value = languages[self.lang]['error']
                # print(str(e))
                # print(type(e))
                # self.cp.message.value = f"{e}"
                self.cp.box.open = True
                self.cp.box.update()

        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.message.value = languages[self.lang]['error msg']
            self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
            self.cp.icon_message.color = ft.Colors.RED
            self.cp.box.open = True
            self.cp.box.update()

    def close_new_student_container(self, e):
        self.hide_one_window(self.ct_new_student)

    def close_ct_edit_student(self, e):
        self.hide_one_window(self.ct_edit_student)

    def set_image_url(self, e):
        if e.files:
            file_path = e.files[0].path
            file_name = os.path.basename(file_path)

            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = "application/octet-stream"

            with open(file_path, "rb") as f:
                data = f.read()

            # Upload to Supabase
            try:
                storage_path = f"{self.edit_id_student}{file_name}"
                supabase_client.storage.from_(BUCKET_STUDENTS_PICTURES).upload(
                    path=storage_path,
                    file=data,
                    file_options={"content-type": mime_type}
                )

                signed_url_response = supabase_client.storage.from_(BUCKET_STUDENTS_PICTURES).create_signed_url(storage_path, 60 * 60 * 24 * 365)
                image_url = signed_url_response['signedURL']

                self.edit_image_url.value = image_url
                self.image_preview.background_image_src = image_url
                self.edit_image_url.update()
                self.image_preview.update()

                self.cp.box.title.value = languages[self.lang]['success']
                self.cp.message.value = languages[self.lang]['import image success']
                self.cp.icon_message.name = ft.Icons.CHECK_CIRCLE
                self.cp.icon_message.color = ft.Colors.LIGHT_GREEN
                self.cp.box.open = True
                self.cp.box.update()

            except Exception as e:
                self.cp.box.title.value = languages[self.lang]['error']
                print(f"{e}")
                self.cp.message.value = ''
                self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
                self.cp.icon_message.color = ft.Colors.RED
                self.cp.box.open = True
                self.cp.box.update()

    def update_student(self, e):
        role = self.cp.page.client_storage.get('role')

        if role in ['secrétaire' or 'économe']:
            try:
                supabase_client.table('students').update(
                    {
                        'name': self.edit_nom.value, 'surname': self.edit_prenom.value, 'gender': self.edit_sex.value,
                        'birth_place': self.edit_lieu.value, 'birth_date': self.edit_date.value,
                        'father': self.edit_pere.value, 'mother': self.edit_mere.value, 'contact': self.edit_contact.value,
                        'other_contact': self.edit_other.value, 'city': self.edit_residence.value,
                        'registration_number': self.edit_mat.value, 'image_url': self.edit_image_url.value,
                    }
                ).eq('id', self.edit_id_student).execute()

                self.cp.box.title.value = languages[self.lang]['success']
                self.cp.message.value = languages[self.lang]['student updated']
                self.cp.icon_message.name = ft.Icons.CHECK_CIRCLE
                self.cp.icon_message.color = ft.Colors.LIGHT_GREEN
                self.cp.box.open = True
                self.cp.box.update()

                self.on_mount()

                self.hide_one_window(self.ct_edit_student)

            except Exception as e:
                self.cp.box.title.value = languages[self.lang]['error']
                print(f"{e}")
                self.cp.message.value = f""

                self.cp.box.open = True
                self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
                self.cp.icon_message.color = ft.Colors.RED
                self.cp.box.update()

        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.message.value = languages[self.lang]['error rights']
            self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
            self.cp.icon_message.color = ft.Colors.RED
            self.cp.box.open = True
            self.cp.box.update()

    def close_school_fees_window(self, e):
        self.hide_one_window(self.school_fees_window)
        self.sc_second_container.controls.clear()
        self.sc_second_container.controls = [
            ft.Column(
                controls=[
                    ft.Text(languages[self.lang]['loading screen'], size=18, font_family='PPR'),
                    ft.ProgressBar(color=BASE_COLOR)
                ], alignment = ft.MainAxisAlignment.CENTER,
                horizontal_alignment = ft.CrossAxisAlignment.CENTER

            )
        ]
        self.sc_second_container.alignment = ft.MainAxisAlignment.CENTER
        self.sc_second_container.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.cp.page.update()

    def make_a_payment(self, e):
        role = self.cp.page.client_storage.get('role')

        if role in ['secrétaire', 'économe']:

            for tranche in (self.sc_tranche_1, self.sc_tranche_2, self.sc_tranche_3):
                if tranche.value is None or tranche.value == "":
                    pass
                else:
                    amount_part = int(tranche.value)
                    supabase_client.table('school_fees').insert(
                        {
                            'year_id': self.cp.year_id, 'student_id': self.sc_student_id.value,
                            'part': tranche.label, 'amount': amount_part,
                        }
                    ).execute()

            # update view
            # empty fields...
            for widget in (
                    self.ins_fees, self.ins_mat, self.ins_check, self.switch,
                    self.sc_tranche_1, self.sc_tranche_2, self.sc_tranche_3,
            ):
                widget.value = None
                widget.update()

            total_paid = get_amount_paid_by_student_id(self.sc_student_id.value)
            total_expected = total_school_fees()
            total_due = total_expected - total_paid
            self.sc_student_id.value = self.sc_student_id.value

            if total_due > 0:
                self.sc_amount_due.color = 'red'
                self.status_icon.name = ft.Icons.INDETERMINATE_CHECK_BOX
                self.status_icon.color = 'red'
                self.status.value = languages[self.lang]['on going']
                self.status.color = 'red'
                self.status_container.bgcolor = 'red50'
                self.status_container.border = ft.border.all(1, 'red')
                self.payment_container.visible = True
            else:
                self.sc_amount_due.color = 'green'
                self.status_icon.name = ft.Icons.CHECK_CIRCLE
                self.status_icon.color = 'green'
                self.status.value = languages[self.lang]['sold out']
                self.status.color = 'green'
                self.status_container.bgcolor = 'green50'
                self.status_container.border = ft.border.all(1, 'green')
                self.payment_container.visible = False

            if total_paid < total_due:
                self.sc_amount_paid.color = 'grey'
            else:
                self.sc_amount_paid.color = 'green'

            self.sc_amount_paid.value = add_separator(total_paid)
            self.sc_amount_due.value = add_separator(total_due)
            self.sc_amount_expected.value = add_separator(total_expected)

            self.sc_payment_table.rows.clear()
            for p, payment in enumerate(get_all_payments_by_student(self.sc_student_id.value)):
                line_color = ft.Colors.GREY_100 if p % 2 == 0 else ft.Colors.WHITE
                self.sc_payment_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(payment['date'])[0:10])),
                            ft.DataCell(ft.Text(payment['part'])),
                            ft.DataCell(ft.Text(add_separator(payment['amount'])))
                        ],
                        color=line_color
                    )
                )
            self.sc_payment_table.update()
            self.cp.page.update()

            self.cp.box.title.value = languages[self.lang]['success']
            self.cp.message.value = languages[self.lang]['payment done']
            self.cp.icon_message.name = ft.Icons.CHECK_CIRCLE
            self.cp.icon_message.color = ft.Colors.LIGHT_GREEN
            self.cp.box.open = True
            self.cp.box.update()

            # Generate pdf file

        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.message.value = languages[self.lang]['error rights']
            self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
            self.cp.icon_message.color = ft.Colors.RED
            self.cp.box.open = True
            self.cp.box.update()

    async def build_school_fees_container(self):
        self.sc_second_container.controls.clear()
        self.sc_second_container.controls = [
            ft.Column(
                expand=True,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Column(
                                [self.sc_name, self.sc_surname, self.sc_student_id], spacing=0
                            ),
                            self.status_container
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Divider(height=1, thickness=1),
                    ft.Divider(color=ft.Colors.TRANSPARENT, height=1),
                    ft.Row(
                        controls=[self.sc_amount_paid, self.sc_amount_expected, self.sc_amount_due],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Divider(color=ft.Colors.TRANSPARENT, height=1),
                    ft.Divider(height=1, thickness=1),
                    ft.Divider(color=ft.Colors.TRANSPARENT, height=1),
                    ft.Text(languages[self.lang]['payment history'], size=16,
                            font_family='PPB'),
                    ft.Container(
                        padding=0, border=ft.border.all(1, ft.Colors.GREY_300), border_radius=16,
                        expand=True,
                        content=ft.ListView(expand=True, controls=[self.sc_payment_table]),
                    ),
                    ft.Divider(color=ft.Colors.TRANSPARENT, height=2),
                ]
            ),
            self.payment_container
        ]
        self.sc_second_container.alignment = ft.MainAxisAlignment.CENTER
        self.sc_second_container.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.cp.page.update()

    async def create_new_discipline_entry(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        count = 0
        for widget in (self.dis_student, self.dis_type, self.dis_qty):
            if widget.value is None or widget.value == " ":
                count += 1

        if count > 0:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.message.value = languages[self.lang]['error msg']
            self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
            self.cp.icon_message.color = ft.Colors.RED
            self.cp.box.open = True
            self.cp.box.update()

        else:
            datas = {
                'year_id': self.cp.year_id,
                'student_id': self.dis_student.value,
                'sequence': self.dis_sequence.value,
                'type': self.dis_type.value,
                'quantity': int(self.dis_qty.value),
                "comments": self.dis_comment.value
            }

            await insert_discipline_entry(access_token, datas)

            self.cp.box.title.value = languages[self.lang]['success']
            self.cp.message.value = languages[self.lang]['sanction saved']
            self.cp.icon_message.name = ft.Icons.CHECK_CIRCLE
            self.cp.icon_message.color = ft.Colors.LIGHT_GREEN
            self.cp.box.open = True
            self.cp.box.update()

            self.dis_student.value = ' '
            self.dis_type.value = ' '
            self.dis_qty.value = None
            self.dis_comment.value = None
            self.cp.page.update()

    def create_new_sanction(self, e):
        self.run_async_in_thread(self.create_new_discipline_entry(e))

    def open_discipline_window(self, e):
        self.run_async_in_thread(self.load_discipline_data(e))

    async def load_discipline_data(self, e):
        year_id = self.cp.year_id
        access_token = self.cp.page.client_storage.get('access_token')
        students = await get_registered_students(access_token, year_id)

        for item in students:
            self.dis_student.options.append(
                ft.dropdown.Option(
                    key=item['id'],
                    text=f"{item['name']} {item['surname']}".upper()
                )
            )

        self.dis_sequence.value = self.active_sequence.data

        role = self.cp.page.client_storage.get('role')

        if role in ['secrétaire', "économe", 'professeur', 'principal']:
            self.show_one_window(self.discipline_window)

        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.message.value = languages[self.lang]['error rights']
            self.cp.icon_message.name = ft.Icons.INFO_ROUNDED
            self.cp.icon_message.color = ft.Colors.RED
            self.cp.box.open = True
            self.cp.box.update()

    def close_discipline_window(self, e):
        self.hide_one_window(self.discipline_window)

        self.dis_student.options.clear()
        self.dis_student.options.append(
            ft.dropdown.Option(
                key=' ',
                text=languages[self.lang]['select option']
            )
        )
        self.dis_student.value = ' '
        self.dis_type.value = ' '
        self.dis_qty.value = None
        self.dis_comment.value = None
        self.cp.page.update()

    def build_discipline_report(self):
        self.sub_report_container.controls.clear()
        self.sub_report_container.controls = [
            ft.Row(
                controls=[
                    ft.Row([self.report_name, self.report_surname]),
                    ft.Text(" | "),
                    ft.Row([ft.Icon("roofing", size=20, color='black'), self.report_class])
                ], spacing=20
            ),
            ft.Row(
                [ft.Text(languages[self.lang]['details'].capitalize(), size=16, font_family='PEB')],
                alignment=ft.MainAxisAlignment.START
            ),
            ft.Container(
                padding=0, border=ft.border.all(1, ft.Colors.GREY_300), border_radius=16,
                expand=True,
                content=ft.ListView(expand=True, controls=[self.report_table], height=200,),
            ),
            ft.Row(
                [ft.Text(languages[self.lang]['summary'].capitalize(), size=16, font_family="PEB")],
                alignment=ft.MainAxisAlignment.START
            ),
            ft.Container(
                padding=10, border_radius=16,
                content=ft.Column(
                    controls=[
                        ft.Divider(height=1, thickness=1),
                        ft.Row(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(languages[self.lang]['unjustified absence'].capitalize(), size=16,
                                                font_family="PPM"),
                                        self.count_unjustified
                                    ]
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Text(languages[self.lang]['justified absence'].capitalize(), size=16,
                                                font_family="PPM"),
                                        self.count_justified
                                    ]
                                ),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Divider(height=1, thickness=1),
                        ft.Row(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(languages[self.lang]['ban'].capitalize(), size=16, font_family="PPM"),
                                        self.count_ban
                                    ]
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Text(languages[self.lang]['permanent ban'].capitalize(), size=16,
                                                font_family="PPM"),
                                        self.count_permanent_ban
                                    ]
                                ),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Divider(height=1, thickness=1),
                        ft.Row(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(languages[self.lang]['warning'].capitalize(), size=16,
                                                font_family="PPM"),
                                        self.count_warning
                                    ]
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Text(languages[self.lang]['detention'].capitalize(), size=16,
                                                font_family="PPM"),
                                        self.count_detention
                                    ]
                                ),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Divider(height=1, thickness=1),
                        ft.Row(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(languages[self.lang]['reprimand'].capitalize(), size=16,
                                                font_family="PPM"),
                                        self.count_reprimand
                                    ]
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Text(languages[self.lang]['late'].capitalize(), size=16,
                                                font_family="PPM"),
                                        self.count_late
                                    ], alignment=ft.MainAxisAlignment.CENTER
                                ),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                    ]
                )
            ),

        ]

        self.cp.page.update()

    def close_report_window(self, e):
        for item in (
                self.count_unjustified, self.count_justified, self.count_warning, self.count_ban,
                self.count_permanent_ban, self.count_reprimand, self.count_detention, self.count_late,
        ):
            item.value = 0
            item.color = 'black'

        self.sub_report_container.controls.clear()
        self.sub_report_container.controls.append(
            ft.Column(
                controls=[
                    ft.Text(languages[self.lang]['loading screen'], size=18, font_family='PPR'),
                    ft.ProgressBar(color=BASE_COLOR)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

        self.hide_one_window(self.report_window)





