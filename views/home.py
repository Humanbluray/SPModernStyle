from components import *
from translations.translations import languages
from services.supabase_client import supabase_client
import asyncio
from services.async_functions.general_functions import get_active_quarter, get_active_sequence, get_current_year_id, get_current_year_label, get_current_year_short
from views.tabs.students import Students
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


class Home(ft.View):
    def __init__(self, page: ft.Page, language: str, user_id:str):
        super().__init__(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            padding=0, bgcolor='white', route=f"/home/{language}/{user_id}"
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
        self.user_image = ft.CircleAvatar(radius=30)

        # Notifications...
        self.nb_notifications = ft.Text("2", size=10, font_family="PPB", color="white")
        self.notifications_cloud = ft.Container(
            visible=True, alignment=ft.alignment.center, shape=ft.BoxShape.CIRCLE, width=20,
            content=self.nb_notifications, bgcolor='red', padding=3
        )
        self.notifs_container = ft.Stack(
            controls=[
                ft.Container(
                    bgcolor='#f0f0f6', alignment=ft.alignment.center, shape=ft.BoxShape.CIRCLE,
                    content=ft.Icon(ft.Icons.NOTIFICATIONS, color='black', size=20), height=45,
                    padding=10,
                    on_click=None
                ),
                self.notifications_cloud
            ], alignment=ft.alignment.top_right
        )

        for i in range(10): # juste pour garder à portée de main
            role = self.page.client_storage.get('role')
            # Menus utilisateurs en fonction du rôle...
            self.board_menu = ft.NavigationDrawerDestination(
                label=languages[self.language]['menu board'],
                icon=ft.Icon(ft.Icons.DASHBOARD_OUTLINED, size=24, color="grey"),
                selected_icon=ft.Icon(ft.Icons.DASHBOARD, size=24, color="black"),
                visible=roles['board'][role]
            )
            self.students_menu = ft.NavigationDrawerDestination(
                label=languages[self.language]['menu students'],
                icon=ft.Icon(ft.Icons.PERSON_OUTLINE_OUTLINED, size=24, color="grey"),
                selected_icon=ft.Icon(ft.Icons.PERSON, size=24, color="black"),
                visible=roles['students'][role]
            )
            self.classes_menu = ft.NavigationDrawerDestination(
                label=languages[self.language]['menu classes'],
                icon=ft.Icon(ft.Icons.ROOFING, size=24, color="grey"),
                selected_icon=ft.Icon(ft.Icons.ROOFING, size=24, color="black"),
                visible=roles['classes'][role]
            )
            self.teachers_menu = ft.NavigationDrawerDestination(
                label=languages[self.language]['menu teachers'],
                icon=ft.Icon(ft.Icons.SUPERVISOR_ACCOUNT_OUTLINED, size=24, color="grey"),
                selected_icon=ft.Icon(ft.Icons.SUPERVISOR_ACCOUNT, size=24, color="black"),
                visible=roles['teachers'][role]
            )
            self.schedule_menu = ft.NavigationDrawerDestination(
                label=languages[self.language]['menu time table'],
                icon=ft.Icon(ft.Icons.EVENT_AVAILABLE_OUTLINED, size=24, color="grey"),
                selected_icon=ft.Icon(ft.Icons.EVENT_AVAILABLE_ROUNDED, size=24, color="black"),
                visible=roles['timetable'][role]
            )
            self.fees_menu = ft.NavigationDrawerDestination(
                label=languages[self.language]['menu school fees'],
                icon=ft.Icon(ft.Icons.ATTACH_MONEY_OUTLINED, size=24, color="grey"),
                selected_icon=ft.Icon(ft.Icons.ATTACH_MONEY_ROUNDED, size=24, color="black"),
                visible=roles['school_fees'][role]
            )
            self.menu_notes = ft.NavigationDrawerDestination(
                label=languages[self.language]['menu notes'],
                icon=ft.Icon(ft.Icons.CONTENT_COPY_OUTLINED, size=24, color="grey"),
                selected_icon=ft.Icon(ft.Icons.CONTENT_COPY_ROUNDED, size=24, color="black"),
                visible=roles['notes'][role]
            )
            self.report_menu = ft.NavigationDrawerDestination(
                label=languages[self.language]['menu report book'],
                icon=ft.Icon(ft.Icons.SCHOOL_OUTLINED, size=24, color="grey"),
                selected_icon=ft.Icon(ft.Icons.SCHOOL_ROUNDED, size=24, color="black"),
                visible=roles['report_book'][role]
            )
            self.years_menu = ft.NavigationDrawerDestination(
                label=languages[self.language]['menu academic years'],
                icon=ft.Icon(ft.Icons.CALENDAR_TODAY_OUTLINED, size=24, color="grey"),
                selected_icon=ft.Icon(ft.Icons.CALENDAR_TODAY_ROUNDED, size=24, color="black"),
                visible=roles['years'][role]
            )
            self.users_menu = ft.NavigationDrawerDestination(
                label=languages[self.language]['menu users'],
                icon=ft.Icon(ft.Icons.SETTINGS_OUTLINED, size=24, color="grey"),
                selected_icon=ft.Icon(ft.Icons.SETTINGS_ROUNDED, size=24, color="black"),
                visible=roles['users'][role]
            )

        # Navigation drawer...
        self.drawer = ft.NavigationDrawer(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Row(
                                controls=[
                                    self.user_image,
                                    ft.Column([self.user_name, self.user_surname], spacing=0)
                                ]
                            ),
                            ft.Row(
                                controls=[
                                    self.notifs_container,
                                    ft.IconButton(
                                        ft.Icons.LOGOUT_OUTLINED, icon_size=24, icon_color='black',
                                        on_click=self.logout
                                    )
                                ]
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    padding=10,
                ),
                ft.Divider(height=1, thickness=1),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                NavBar(self)
                # self.board_menu, self.students_menu, self.classes_menu,
                # self.teachers_menu, self.schedule_menu, self.fees_menu,
                # self.menu_notes, self.report_menu, self.years_menu,
                # self.users_menu
            ],
            indicator_color=BASE_COLOR, selected_index=-1,
            tile_padding=5,
        )

        self.my_content = ft.Column(
            expand=True,
                controls=[
                    ft.Text(languages[language]['loading screen'], size=18, font_family='PPR'),
                    ft.ProgressRing(color=BASE_COLOR)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )

        self.controls = [
            self.my_content
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

        # Remplacement du ProgressRing par l'UI principale
        self.my_content.controls.clear()
        self.my_content.controls.append(
            ft.Row(
                controls=[
                    ft.IconButton(
                        ft.Icons.MENU, icon_size=24, icon_color='black', on_click=lambda e: self.page.open(self.drawer)
                    ),
                    ft.Container(
                        border_radius=16, border=ft.border.all(1, ACCENT_PLUS_COLOR),
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
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








