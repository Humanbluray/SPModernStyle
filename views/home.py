import ftplib

from utils.styles import dash_style
from components import *
from translations.translations import languages
from services.supabase_client import supabase_client
import asyncio
from services.async_functions.general_functions import (get_active_quarter, get_active_sequence,
                                                        get_current_year_id, get_current_year_label, get_current_year_short)
from views.tabs.students import Students
from services.async_functions.dashboard_functions import *
from components.menu import NavBar
from utils.useful_functions import *
from components.menu import NavBar

roles = {
    'board' : {'admin': True, 'principal': True, 'préfet': False, 'secrétaire': False, 'économe': False, 'professeur': False},
    'students' : {'admin': True, 'principal': True, 'préfet': True, 'secrétaire': True, 'économe': True, 'professeur': True},
    'classes' : {'admin': True, 'principal': True, 'préfet': True, 'secrétaire': False, 'économe': False, 'professeur': False},
    'teachers' : {'admin': True, 'principal': True, 'préfet': False, 'secrétaire': True, 'économe': False, 'professeur': False},
    'timetable' : {'admin': True, 'principal': True, 'préfet': True, 'secrétaire': True, 'économe': True, 'professeur': True},
    'school_fees' : {'admin': False, 'principal': True, 'préfet': False, 'secrétaire': False, 'économe': True, 'professeur': False},
    'notes' : {'admin': True, 'principal': True, 'préfet': True, 'secrétaire': True, 'économe': True, 'professeur': True},
    'report_book' : {'admin': True, 'principal': True, 'préfet': True, 'secrétaire': True, 'économe': True, 'professeur': True},
    'users' : {'admin': True, 'principal': False, 'préfet': False, 'secrétaire': False, 'économe': False, 'professeur': False},
    'years' : {'admin': False, 'principal': True, 'préfet': False, 'secrétaire': False, 'économe': False, 'professeur': False},
}

couleurs = {
    'red': {'icon_color': 'red', 'bg_color': 'red50'},
    'green': {'icon_color': 'green', 'bg_color': 'green50'},
    'amber': {'icon_color': 'amber', 'bg_color': 'amber50'},
    'deeppurple': {'icon_color': 'deeppurple', 'bg_color': 'deeppurple50'},
    'deeporange': {'icon_color': 'deeporange', 'bg_color': 'deeporange50'},
    'orange': {'icon_color': 'orange', 'bg_color': 'orange50'},
    'pink': {'icon_color': 'pink', 'bg_color': 'pink50'},
    'purple': {'icon_color': 'purple', 'bg_color': 'purple50'},
    'blue': {'icon_color': 'blue', 'bg_color': 'blue50'},
    'indigo': {'icon_color':    'indigo', 'bg_color':   'indigo50'},
    'brown': {'icon_color': 'brown', 'bg_color': 'brown50'},
    'lime': {'icon_color': 'lime', 'bg_color': 'lime50'},
    'teal': {'icon_color': 'teal', 'bg_color': 'teal50'},
}


class Home(ft.View):
    def __init__(self, page: ft.Page, language: str, user_id:str):
        super().__init__(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            padding=0, bgcolor=MAIN_COLOR, route=f"/home/{language}/{user_id}"
        )
        # paramètres de la classe...
        self.page = page
        self.language = language
        self.user_id = user_id
        self.year_id = get_current_year_id()
        self.year_label = get_current_year_label()
        self.year_short = get_current_year_short()
        self.role = ''

        # infos user...
        self.user_name = ft.Text("", size=18, font_family='PPB')
        self.user_surname = ft.Text("", size=16, font_family='PPM')
        self.user_image = ft.CircleAvatar(radius=20)

        # Notifications...
        self.nb_notifications = 2
        self.notif_badge = ft.Badge(
            text_color="white", text=f"{self.nb_notifications}", bgcolor='red',
            label_visible=True if self.nb_notifications > 0 else False
        )
        self.ct_notifs = ft.Container(
            alignment=ft.alignment.center,
            bgcolor=MAIN_COLOR,
            padding=10,
            shape=ft.BoxShape.CIRCLE,
            width=50,
            on_click=lambda e: print('view notifications'),
            badge=self.notif_badge,
            content=ft.Icon(ft.Icons.NOTIFICATIONS, color='black87', size=18),
        )

        self.top_menu = ft.Container(
            bgcolor="white", padding=ft.padding.only(10, 8, 10, 8),
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.15, "black")),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text("School", size=24, font_family="PEB", color=BASE_COLOR),
                            ft.Text("Pilot", size=24, font_family="PEB")
                        ], spacing=0
                    ),
                    NavBar(self),
                    ft.Row(
                        controls=[

                            ft.Container(
                                content=self.user_image,
                                on_click=None
                            ),
                            self.ct_notifs
                        ], spacing=2
                    )
                ]
            )
        )
        
        self.active_sequence = ft.Text(size=14, font_family='PPB')
        self.active_quarter = ft.Text(size=14, font_family='PPB')
        self.sequence_ct = ft.Chip(
            label=self.active_sequence,
            leading=ft.Icon(ft.Icons.CALENDAR_MONTH_OUTLINED, size=16, color='black87'),
            shape=ft.RoundedRectangleBorder(radius=16)
        )

        self.my_content = ft.Column(
            expand=True,
                controls=[
                    ft.Text(languages[language]['loading screen'], size=18, font_family='PPR'),
                    ft.ProgressRing(color=BASE_COLOR)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER

            )

        # Kpi________________________________________
        self.nb_students = ft.Text(size=30, font_family="PEB")
        self.nb_classes = ft.Text(size=30, font_family="PEB")
        self.fill_rate = ft.Text(size=30, font_family="PEB")

        # professeurs et affectations...
        self.nb_affected_hours = ft.Text(size=30, font_family="PEB")
        self.nb_teachers = ft.Text(size=30, font_family="PEB")
        self.nb_hours_non_affected = ft.Text(size=30, font_family="PEB")
        self.nb_affectations_rate = ft.Text(size=30, font_family="PEB")

        self.bloc_profs = ft.Container(
            padding=20, bgcolor='white', border_radius=24,
            content=ft.Row(
                controls=[
                    DashContainer(
                        ft.Icons.GROUP_OUTLINED, couleurs['deeppurple'], languages[self.language]['head count'],
                        self.nb_students
                    ),
                    ft.VerticalDivider(width=50, thickness=1),
                    DashContainer(
                        ft.Icons.ROOFING, couleurs['orange'], 'nb classes',
                        self.nb_classes
                    ),
                    ft.VerticalDivider(width=50, thickness=1),
                    DashContainer(
                        ft.Icons.PIE_CHART_OUTLINE_OUTLINED, couleurs['blue'],
                        languages[self.language]['fill rate'],
                        self.fill_rate
                    ),
                    ft.VerticalDivider(width=50, thickness=1),
                    DashContainer(
                        ft.Icons.SUPERVISOR_ACCOUNT_OUTLINED, couleurs['green'],
                        languages[self.language]['menu teachers'], self.nb_teachers
                    ),
                    ft.VerticalDivider(width=30, thickness=1),
                    DashContainer(
                        ft.Icons.TIMER_OUTLINED, couleurs['red'],
                        languages[self.language]['nb hours affected'], self.nb_affected_hours
                    ),
                    ft.VerticalDivider(width=30, thickness=1),
                    DashContainer(
                        ft.Icons.WATCH_LATER_OUTLINED, couleurs['teal'],
                        languages[self.language]['free hours'], self.nb_hours_non_affected
                    ),
                    ft.VerticalDivider(width=30, thickness=1),
                    DashContainer(
                        ft.Icons.PIE_CHART_OUTLINE_OUTLINED, couleurs['amber'],
                        languages[self.language]['affectation rate'], self.nb_affectations_rate
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_AROUND
            )
        )

        # notes....
        self.nb_notes = ft.Text()
        self.nb_notes_success = ft.Text()
        self.note_rate_success = ft.Text()

        # General average...
        self.general_average = ft.Text(size=30, font_family="PEB")
        # graphique par sequence...

        # finances...
        self.expected = ft.Text()
        self.recovered = ft.Text()
        self.due = ft.Text()
        self.recovery_rate = ft.Text()

        # Discipline...
        self.count_abs_unjustified = ft.Text()
        self.count_abs_justified = ft.Text()
        self.count_late = ft.Text()
        self.count_ban = ft.Text()
        self.count_reprimand = ft.Text()
        self.count_detention = ft.Text()
        self.count_warning = ft.Text()
        self.count_permanent_ban = ft.Text()

        # fin KPI____________________________________

        self.controls = [
            ft.Column(
                expand=True,
                controls=[
                    self.top_menu,
                    ft.Container(
                        alignment=ft.alignment.center, expand=True,
                        content=self.my_content
                    )
                ], spacing=0
            )
        ]

        # Overlays...
        self.message = ft.Text("", size=16, font_family='PPM')
        self.icon_message = ft.Icon(size=36)
        self.box = ft.AlertDialog(
            title=ft.Text(size=24, font_family='PPB'),
            content=ft.Row(
                controls=[
                    self.icon_message, self.message
                ], alignment=ft.MainAxisAlignment.CENTER
            )
        )
        self.fp_image_student = ft.FilePicker()
        self.fp_import_notes = ft.FilePicker()

        for widget in (
                self.fp_image_student, self.box, self.fp_import_notes
        ):
            self.page.overlay.append(widget)


    def logout(self, e):
        try:
            supabase_client.auth.sign_out()
        except Exception as e:
            print(f"Erreur lors de la déconnexion : {e}")
        self.page.client_storage.clear()
        self.page.go('/')

    async def did_mount_async(self):
        print("[DEBUG] Vue montée : appel check_auth()")
        await self.check_auth()

    async def check_auth(self):
        access_token = self.page.client_storage.get("access_token")
        role = self.page.client_storage.get("access_token")
        self.role = role
        print(f"[DEBUG] role: {role}")
        print("[DEBUG] Access token :", access_token)

        if not access_token:
            self.page.go('/')
            return

        try:
            user_response = await asyncio.to_thread(supabase_client.auth.get_user, access_token)
            print("[DEBUG] Réponse utilisateur :", user_response)

            if not user_response or not user_response.user:
                raise Exception("Utilisateur non trouvé ou token invalide.")

            await self.build_main_view()  # Interface
            await self.load_user_data(user_response.user)  # Données utilisateur


        except Exception as e:
            print(f"[ERREUR AUTHENTIFICATION] {e}")
            import traceback;
            traceback.print_exc()
            self.page.client_storage.clear()
            self.page.go('/')

    async def build_main_view(self):
        print("[DEBUG] Construction de la vue principale")

        access_token = self.page.client_storage.get("access_token")
        active_sequence = await get_active_sequence(access_token)
        self.active_sequence.value = languages[self.language][active_sequence['name']]
        self.active_quarter.value = languages[self.language][active_sequence['quarter']]
        self.active_sequence.data = active_sequence['name']
        self.active_quarter.data = active_sequence['quarter']

        dash_datas = await get_dashboard_stats(access_token, self.year_id)
        # remplissage des datas dans le dashboard...

        own_data = dash_datas[0]

        self.nb_students.value = own_data['nombre_eleves_inscrits']
        self.nb_classes.value = own_data['nombre_classes']
        self.fill_rate.value = f"{write_number(own_data['taux_remplissage_global'])}%"

        self.nb_teachers.value = own_data['nombre_professeurs']
        self.nb_affected_hours.value = own_data['nombre_heures_affectees']
        self.nb_hours_non_affected.value = own_data['nombre_heures_a_affecter']
        total_heures = own_data['nombre_heures_affectees'] + own_data['nombre_heures_a_affecter']
        self.nb_affectations_rate.value = f"{write_number(own_data['nombre_heures_affectees'] * 100 / total_heures)}%"

        self.general_average.value = write_number(own_data['moyenne_generale_etablissement'])

        graphic = BarGraphic(
            infos=[
                {
                    'value': write_number(own_data['moyenne_sequence_1']),
                    'color': 'blue', 'bg_color': 'blue50',
                    'label': f"S1 ({write_number(own_data['moyenne_sequence_1'])})"
                },
                {
                    'value': write_number(own_data['moyenne_sequence_2']),
                    'color': 'blue', 'bg_color': 'blue50',
                    'label': f"S2 ({write_number(own_data['moyenne_sequence_2'])})"
                },
                {
                    'value': write_number(own_data['moyenne_sequence_3']),
                    'color': 'blue', 'bg_color': 'blue50',
                    'label': f"S3 ({write_number(own_data['moyenne_sequence_3'])})"
                },
                {
                    'value': write_number(own_data['moyenne_sequence_4']),
                    'color': 'blue', 'bg_color': 'blue50',
                    'label': f"S4 ({write_number(own_data['moyenne_sequence_4'])})"
                },
                {
                    'value': write_number(own_data['moyenne_sequence_5']),
                    'color': 'blue', 'bg_color': 'blue50',
                    'label': f"S5 ({write_number(own_data['moyenne_sequence_5'])})"
                },
                {
                    'value': write_number(own_data['moyenne_sequence_6']),
                    'color': 'blue', 'bg_color': 'blue50',
                    'label': f"S6 ({write_number(own_data['moyenne_sequence_6'])})"
                },
            ],
            max_value=12, title=languages[self.language]['overall average']
        )

        # Remplacement du ProgressRing par l'UI principale
        self.my_content.controls.clear()
        self.my_content.controls.append(
            ft.Column(
                controls=[
                    ft.Container(
                        padding=10, content=ft.Row(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.IconButton(
                                            ft.Icons.MENU, icon_size=24, icon_color='black',
                                            on_click=lambda e: self.page.open(self.drawer)
                                        ),
                                        ft.Text(languages[self.language]['menu board'], size=18, font_family='PPB')
                                    ]
                                ),
                                self.sequence_ct
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        )
                    ),
                    ft.Divider(height=5, thickness=1),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.DATA_ARRAY_OUTLINED, size=24, color='black'),
                                        ft.Text(
                                            f"{languages[self.language]['menu students']} and {languages[self.language]['menu teachers']}",
                                            size=16, font_family='PPI'
                                        )
                                    ]
                                ),
                                self.bloc_profs
                            ]
                        ),
                        padding=10
                    ),
                    ft.Row(
                        controls=[
                            ft.Container(
                                padding=10, border_radius=16, bgcolor="white",
                                margin=ft.margin.only(10, 0, 10, 0),
                                content=DashContainer(
                                    ft.Icons.DATA_ARRAY_OUTLINED, couleurs['blue'],
                                    languages[self.language]['overall average'],
                                    self.general_average
                                ),
                            ),
                            ft.Container(
                                padding=10, border_radius=16, bgcolor="white", width=800,
                                height=300, content=ft.Column(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(ft.Icons.DATA_EXPLORATION_OUTLINED, size=24, color='black'),
                                                ft.Text(
                                                    languages[self.language]['general average trend'],
                                                    size=16, font_family='PEB'
                                                ),
                                            ], alignment=ft.MainAxisAlignment.CENTER
                                        ),
                                        ft.Divider(height=1, thickness=1),
                                        ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                        graphic
                                    ]
                                )
                            )
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START
                    )
                ]
            )
        )
        self.page.update()

    async def load_user_data(self, user):
        print("[DEBUG] Chargement des infos utilisateur")
        resp = supabase_client.table('users').select('*').eq('id', self.user_id).execute()
        self.user_name.value = f"{resp.data[0]['name']}"
        self.user_surname.value = f"{resp.data[0]['surname']}"
        self.user_image.foreground_image_src = resp.data[0]['image_url']
        self.role = resp.data[0]['role']
        self.page.update()








