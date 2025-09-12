from components import MyButton, MyMiniIcon, SingleOption, EditSingleOption, ColoredIcon, MyTextButton
from utils.styles import drop_style, datatable_style, login_style, ct_style, intern_ct_style, top_ct_style, bottom_ct_style
from utils.couleurs import *
from translations.translations import languages
import os, mimetypes, asyncio, threading, json
from services.async_functions.users_functions import *
from utils.useful_functions import add_separator, format_number
from services.async_functions.general_functions import get_active_sequence
from services.supabase_client import supabase_client


class Users(ft.Container):
    def __init__(self, cp: object):
        super().__init__(
            expand=True
        )
        # parent container (Home) ___________________________________________________________
        self.cp = cp
        lang = self.cp.language
        self.lang = lang

        # KPI _________________________________________________
        self.nb_users = ft.Text(size=28, font_family="PPM", weight=ft.FontWeight.BOLD)

        self.ct_nb_users = ft.Container(
            width=170, height=120, padding=10, border_radius=24,
            bgcolor='white', content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ColoredIcon(ft.Icons.PIE_CHART_SHARP, 'indigo', 'indigo50'),
                            ft.Text(languages[lang]['total'].upper(), size=12, font_family='PPI', color='indigo')
                        ], alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Column(
                        controls=[
                            self.nb_users,
                            ft.Text(languages[lang]['nb users'], size=11, font_family='PPI', color='grey')
                        ], spacing=0
                    )
                ]
            )
        )

        # Main window...
        self.search = ft.TextField(
            **login_style, width=300, label=f"{languages[lang]['search']}", prefix_icon='search',
            on_change=self.on_search_change
        )
        self.table = ft.DataTable(
            **datatable_style, columns=[
                ft.DataColumn(ft.Text(menu)) for menu in [
                    languages[lang]['name'].capitalize(), languages[lang]['email'].capitalize(),
                    languages[lang]['role'].capitalize(), languages[lang]['contact'].capitalize(),
                    languages[lang]['active'].capitalize(), 'Actions'
                ]
            ], expand=True
        )
        self.active_sequence = ft.Text(size=14, font_family='PPB')
        self.active_quarter = ft.Text(size=14, font_family='PPB')
        self.sequence_ct = ft.Chip(
            label=self.active_sequence,
            leading=ft.Icon(ft.Icons.CALENDAR_MONTH_OUTLINED, size=16, color='black87'),
            shape=ft.RoundedRectangleBorder(radius=16)
        )
        self.menu_button = ft.IconButton(
            ft.Icons.MENU, icon_size=24, icon_color='black',
            on_click=lambda e: self.cp.page.open(self.cp.drawer)
        )
        self.top_menu = ft.Container(
            padding=10, content=ft.Row(
                controls=[
                    ft.Row(
                        controls=[
                            self.menu_button,
                            ft.Row(
                                controls=[
                                    ft.Text(languages[self.lang]['menu users'].capitalize(), size=24,
                                            font_family="PEB"),
                                ], spacing=0
                            )
                        ]
                    ),
                    self.sequence_ct
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        )

        self.main_window = ft.Container(
            expand=True, padding=20, border_radius=16,
            content=ft.Column(
                expand=True,
                controls=[
                    self.top_menu,
                    ft.Row(
                        controls=[
                            ft.Row(
                                controls=[
                                    MyTextButton(languages[lang]['new user'], self.open_new_user_window),
                                ]
                            ),
                            self.search
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Container(
                        padding=0, border_radius=16, border=ft.border.all(1, MAIN_COLOR),
                        expand=True, content=ft.ListView(
                            [self.table], expand=True
                        )
                    )
                ]
            )
        )

        # new user window...
        self.new_name = ft.TextField(
            **login_style, width=300, label=languages[lang]['name'], prefix_icon=ft.Icons.PERSON_OUTLINED
        )
        self.new_surname = ft.TextField(
            **login_style, width=300, label=languages[lang]['surname'], prefix_icon=ft.Icons.PERSON_OUTLINED
        )
        self.new_email = ft.TextField(
            **login_style, width=300, label='email', prefix_icon=ft.Icons.MAIL_OUTLINED
        )
        self.new_contact = ft.TextField(
            **login_style, width=200, prefix_icon=ft.Icons.PHONE_ANDROID_OUTLINED, prefix_text='+237 ',
            label=languages[lang]['contact']
        )
        self.new_function = ft.TextField(
            **login_style, width=300, label=languages[lang]['function'], prefix_icon=ft.Icons.FUNCTIONS_OUTLINED
        )
        self.new_role = ft.Dropdown(
            **drop_style, width=170, label=languages[lang]['role'],
            options=[
                ft.dropdown.Option(
                    text=role['label'], key=role['value']
                ) for role in [
                    {'label': languages[lang]['bursar'], 'value': 'économe'},
                    {'label': languages[lang]['secretary'], 'value': 'secrétaire'},
                    {'label': languages[lang]['teacher'], 'value': 'professeur'},
                    {'label': languages[lang]['principal'], 'value': 'principal'},
                    {'label': languages[lang]['prefect of studies'], 'value': 'préfet'},
                    {'label': languages[lang]['administrator'], 'value': 'admin'},
                ]
            ]
        )
        self.new_user_container = ft.Container(
            **ct_style, content=ft.Container(
                **intern_ct_style, width=700, content=ft.Column(
                    expand=True, scroll=ft.ScrollMode.AUTO, spacing=0,
                    controls=[
                        ft.Container(
                            **top_ct_style, content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['new user'], size=20, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=MAIN_COLOR,
                                        on_click=self.close_new_user_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            **bottom_ct_style, content=ft.Column(
                                controls=[
                                    ft.Row(controls=[self.new_name, self.new_surname]),
                                    ft.Row(controls=[self.new_email, self.new_contact]),
                                    self.new_function,
                                    self.new_role,
                                    ft.Container(
                                        padding=10,
                                        content=ft.Row(
                                            controls=[
                                                MyButton(languages[lang]['valid'], 'check', None, self.create_new_user)
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

    def build_main_view(self):
        self.content.controls.clear()
        self.content.controls = [
            self.main_window, self.new_user_container
        ]
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
        access_token = self.cp.page.client_storage.get('access_token')
        datas = await get_all_users(access_token)
        active_sequence = await get_active_sequence(access_token)
        self.active_sequence.value = languages[self.lang][active_sequence['name']]
        self.active_quarter.value = languages[self.lang][active_sequence['quarter']]
        self.active_sequence.data = active_sequence['name']
        self.active_quarter.data = active_sequence['quarter']

        self.table.rows.clear()

        for d, data in enumerate(datas):
            line_color = "grey100" if d % 2 == 0 else 'white'

            if data['role'] == "secrétaire":
                role_color = "lightblue"
                role_icon = ft.Icons.FOLDER_OUTLINED

            elif data['role'] == 'professeur':
                role_color = 'brown'
                role_icon = ft.Icons.ASSIGNMENT_IND_OUTLINED

            elif data['role'] == 'admin':
                role_color = 'amber'
                role_icon = ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED

            elif data['role'] == 'principal':
                role_color = "red"
                role_icon = ft.Icons.SUPERVISOR_ACCOUNT_OUTLINED

            elif data['role'] == "préfet":
                role_color = "deeppurple"
                role_icon = "school"

            else:
                role_color = "deeporange"
                role_icon = ft.Icons.REAL_ESTATE_AGENT_OUTLINED

            if data['active']:
                active_status = languages[self.lang]['active']
                active_icon = ft.Icons.CHECK_CIRCLE
                active_color = ft.Colors.GREEN
            else:
                active_status = languages[self.lang]['inactive']
                active_icon = ft.Icons.INFO_ROUNDED
                active_color = ft.Colors.RED

            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(f"{data['name']} {data['surname']}".upper())),
                        ft.DataCell(ft.Text(f"{data['email']}")),
                        ft.DataCell(
                            ft.Chip(
                                label=ft.Text(f"{data['role']}", size=13, font_family='FTB'),
                                leading=ft.Icon(role_icon, size=18, color=role_color),
                                shape=ft.RoundedRectangleBorder(radius=16)
                            )
                        ),
                        ft.DataCell(ft.Text(f"{data['contact']}")),
                        ft.DataCell(
                            ft.Chip(
                                label=ft.Text(f"{active_status}", size=13, font_family='FTB'),
                                leading=ft.Icon(active_icon, size=18, color=active_color),
                                shape=ft.RoundedRectangleBorder(radius=16)
                            )
                        ),
                        ft.DataCell(ft.Row(
                            controls=[
                                MyMiniIcon(ft.Icons.DELETE_SWEEP_OUTLINED, '', 'red', data, self.delete_user),
                            ], spacing=0
                        )),
                    ], color=line_color
                )
            )

        self.build_main_view()

    def on_search_change(self, e):
        self.run_async_in_thread(self.filter_datas(e))

    async def filter_datas(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        datas = await get_all_users(access_token)
        search = self.search.value if self.search.value else ''

        filtered_datas = list(filter(lambda x: search in x['name'] or search in x['surname'], datas))
        self.table.rows.clear()

        for d, data in enumerate(filtered_datas):
            line_color = "grey100" if d % 2 == 0 else 'white'

            if data['role'] == "secrétaire":
                role_color = "lightblue"
                role_icon = ft.Icons.FOLDER_OUTLINED

            elif data['role'] == 'professeur':
                role_color = 'brown'
                role_icon = ft.Icons.ASSIGNMENT_IND_OUTLINED

            elif data['role'] == 'admin':
                role_color = 'amber'
                role_icon = ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED

            elif data['role'] == 'principal':
                role_color = "red"
                role_icon = ft.Icons.SUPERVISOR_ACCOUNT_OUTLINED

            elif data['role'] == "préfet":
                role_color = "deeppurple"
                role_icon = "school"

            else:
                role_color = "deeporange"
                role_icon = ft.Icons.REAL_ESTATE_AGENT_OUTLINED

            if data['active']:
                active_status = languages[self.lang]['active']
                active_icon = ft.Icons.CHECK_CIRCLE
                active_color = ft.Colors.GREEN
            else:
                active_status = languages[self.lang]['inactive']
                active_icon = ft.Icons.INFO_ROUNDED
                active_color = ft.Colors.RED

            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(f"{data['name']} {data['surname']}".upper())),
                        ft.DataCell(ft.Text(f"{data['email']}")),
                        ft.DataCell(
                            ft.Chip(
                                label=ft.Text(f"{data['role']}", size=13, font_family='FTB'),
                                leading=ft.Icon(role_icon, size=18, color=role_color),
                                shape=ft.RoundedRectangleBorder(radius=16)
                            )
                        ),
                        ft.DataCell(ft.Text(f"{data['contact']}")),
                        ft.DataCell(
                            ft.Chip(
                                label=ft.Text(f"{active_status}", size=13, font_family='FTB'),
                                leading=ft.Icon(active_icon, size=18, color=active_color),
                                shape=ft.RoundedRectangleBorder(radius=16)
                            )
                        ),
                        ft.DataCell(ft.Row(
                            controls=[
                                MyMiniIcon(ft.Icons.DELETE_SWEEP_OUTLINED, '', 'red', data, self.delete_user),
                            ], spacing=0
                        )),
                    ], color=line_color
                )
            )

        self.cp.page.update()

    def open_new_user_window(self, e):
        self.show_one_window(self.new_user_container)

    def close_new_user_window(self, e):
        self.hide_one_window(self.new_user_container)

        for widget in (self.new_name, self.new_surname, self.new_function, self.new_contact,
                       self.new_email, self.new_role):
            widget.value = None
            widget.update()

    def create_new_user(self, e):
        try:
            # send invitation
            response = supabase_client.auth.admin.invite_user_by_email(
                email=self.new_email.value,
                redirect_to=app_url
            )
            user = response.user

            if user:
                print("Invitation envoyée avec succès.")
                print("ID de l'utilisateur :", user.id)

                # 2. Créer un profil lié dans la table `users`
                data = {
                    "id": user.id,  # correspond à auth.users.id
                    "email": self.new_email.value,
                    "name": self.new_name.value,
                    "surname": self.new_surname.value,
                    "role": self.new_role.value,
                    'function': self.new_function.value,
                    'contact': self.new_contact.value
                }

                # On ajoute dans la table users...
                insert_response = supabase_client.table("users").insert(data).execute()

                if insert_response.data:
                    print("Profil utilisateur ajouté dans la table users.")

                    # on cherche son id et l'ajoute dans la table prof si c'est un professeur...
                    if self.new_role.value == "professeur":
                        prof_id_response = supabase_client.table('users').select("id").eq(
                            'name', self.new_name.value).eq('surname', self.new_surname.value).execute()

                        prof_id = prof_id_response.data[0]['id']

                        datas_to_teacher = {
                            "id": prof_id,
                            "name": self.new_name.value,
                            "surname": self.new_surname.value,
                            "gender": self.new_gender.value,
                            "contact": self.new_contact.value
                        }
                        supabase_client.table('teachers').insert(datas_to_teacher).execute()


                    # email invitation...
                    try:
                        response = supabase_client.auth.admin.invite_user_by_email(
                            self.new_email.value, {
                                "data": {"redirect_to": app_url}
                            }
                        )

                        if response.user:
                            print(f"L'utilisateur {response.user.email} a été invité avec succès.")

                            self.cp.box.title.value = languages[self.lang]['success']
                            self.cp.message.value = languages[self.lang]['user added']
                            self.cp.icon_message.name = ft.Icons.CHECK_CIRCLE
                            self.cp.icon_message.color = ft.Colors.LIGHT_GREEN
                            self.cp.box.open = True
                            self.cp.box.update()

                            return {"user": response.user, "error": None}


                        else:
                            print(f"Erreur lors de l'invitation de l'utilisateur: {response.error.message}")
                            return {"user": None, "error": response.error}

                    except Exception as e:
                        print(f"Une erreur inattendue est survenue: {e}")
                        return {"user": None, "error": str(e)}

                else:
                    print("Erreur lors de l'insertion dans la table users.")
                    return False



        except Exception as e:
            print("Erreur lors de l'invitation :", e)
            return False

    def delete_user(self, e):
        user_id = e.control.data['id']
        new_status = False

        try:
            response = supabase_client.auth.admin.delete_user(user_id)

            supabase_client.table('users').update({'active': False}).eq('id', user_id).execute()

            if response.data:
                print(f"Le statut de l'utilisateur {user_id} a été mis à jour avec succès à '{new_status}'.")

                self.cp.box.title.value = languages[self.lang]['success']
                self.cp.message.value = languages[self.lang]['user disabled']
                self.cp.icon_message.name = ft.Icons.CHECK_CIRCLE
                self.cp.icon_message.color = ft.Colors.LIGHT_GREEN
                self.cp.box.open = True
                self.cp.box.update()

                self.load_datas()

                return response.data
            else:
                print(f"Erreur lors de la mise à jour du statut: {response.error.message}")
                return response.error

        except Exception as e:
            print(f"Une erreur inattendue est survenue: {e}")
            return str(e)







