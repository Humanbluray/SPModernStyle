import flet as ft
from translations.translations import languages
from utils.styles import login_style, password_style, drop_style
from utils.couleurs import ACCENT_PLUS_COLOR, PAGE_BG_COLOR, BASE_COLOR
from components import MyButton
from services.supabase_client import supabase_client

SP_LOGO_URL = 'https://nppwkqytgqlqijpeulfj.supabase.co/storage/v1/object/public/logo_school_pilot/logo%20mini.png'


class Signin(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            bgcolor=PAGE_BG_COLOR, route='/'
        )
        self.page = page
        self.lang_button = ft.Dropdown(
            **drop_style, options=[
                ft.dropdown.Option(
                    key=choice['value'], text=f"{choice['text']}"
                )
                for choice in [
                    {'value': 'fr', "text": 'Français'}, {'value': 'en', "text": 'Anglais'}
                ]
            ], value="fr", on_change=self.change_language,
            filled=True, fill_color=PAGE_BG_COLOR,
        )
        self.email = ft.TextField(
            **login_style, prefix_icon=ft.Icons.PERSON_OUTLINE_OUTLINED,
            label=languages[self.lang_button.value]['email'],
        )
        self.password = ft.TextField(
            **password_style, prefix_icon=ft.Icons.LOCK_OUTLINE_ROUNDED,
            label=languages[self.lang_button.value]['password'],
        )
        self.connect_button = MyButton(
            languages[self.lang_button.value]['sign in'], None, None,
            self.authenticate_user
        )

        self.choose_text = ft.Text(
            languages[self.lang_button.value]['choose language'], size=16, font_family='PPM'
        )
        self.login_text = ft.Text(
            languages[self.lang_button.value]['login'].capitalize(),
            size=30, font_family="PEB"
        )
        self.info_text =  ft.Text(
            languages[self.lang_button.value]['enter informations'], size=13, font_family="PPM"
        )
        self.welcome_text = ft.Text(
            languages[self.lang_button.value]['welcome to SP'],
            size=48, font_family='PEB'
        )

        self.page_container = ft.Container(
            content=ft.Column(
                [
                    # En-tête avec le logo et le titre
                    ft.Row(
                        controls=[
                            ft.Text("S", size=72, font_family='PEB', color=BASE_COLOR),
                            ft.Text("P", size=72, font_family='PEB')
                        ], spacing=0, alignment=ft.MainAxisAlignment.CENTER
                    ),
                    self.login_text,
                    self.info_text,
                    ft.Divider(height=10, color="transparent"),
                    self.email, self.password,
                    ft.Divider(height=1, color="transparent"),
                    self.connect_button,
                    ft.Divider(height=40, color="transparent"),

                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            padding=ft.padding.all(40),
            border_radius=ft.border_radius.all(20),
            bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.WHITE),
            width=400,
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            )
        )
        self.controls = [
            ft.Stack(
                alignment=ft.alignment.center,
                controls=[
                    ft.Container(
                        expand=True, bgcolor=PAGE_BG_COLOR
                    ),
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Column(
                                        controls=[self.welcome_text],
                                        spacing=0,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER

                                    ),
                                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                                    ft.Column(
                                        controls=[
                                            self.choose_text,
                                            self.lang_button
                                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                    )
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            self.page_container
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=200
                    )
                ]
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
        self.page.overlay.append(self.box)

    def change_language(self, e):
        lang = self.lang_button.value
        self.choose_text.value = languages[lang]['choose language']
        self.connect_button.content.controls[1].value = languages[lang]['sign in']
        self.login_text.value =  languages[lang]['login'].capitalize()
        self.password.label = languages[lang]['password']
        self.info_text.value = languages[self.lang_button.value]['enter informations']
        self.welcome_text.value = languages[self.lang_button.value]['welcome to SP']
        self.page.update()

    def authenticate_user(self, e):
        language = self.lang_button.value
        email = self.email.value
        password = self.password.value

        if email and password:
            try:
                result = supabase_client.auth.sign_in_with_password({"email": email, "password": password})
                session = result.session
                user = result.user

                if session and user:
                    access_token = session.access_token
                    refresh_token = session.refresh_token
                    user_id = user.id

                    self.page.client_storage.set("access_token", access_token)
                    self.page.client_storage.set("refresh_token", refresh_token)
                    self.page.client_storage.set("user_id", user_id)
                    self.page.client_storage.set("lang", language)

                    user_data = supabase_client.table("users").select("role").eq("id", user_id).execute()
                    if user_data.data:
                        role = user_data.data[0]["role"]
                        print(f"role: {role}")
                        self.page.client_storage.set("role", role)

                    self.page.go(f"/home/{language}/{user_id}")
                    return

                # Si pas de session ou d'utilisateur
                self.show_error_dialog(language, "invalid_credentials")
                return

            except Exception as e:
                error_message = str(e).lower()
                print("[ERREUR AUTH] :", e)

                if "network" in error_message or "connection" in error_message or "timeout" in error_message:
                    self.show_error_dialog(language, "network_error")
                elif "invalid" in error_message or "credentials" in error_message or "email" in error_message:
                    self.show_error_dialog(language, "invalid_credentials")
                else:
                    self.show_error_dialog(language, "general_error")

        else:
            self.show_error_dialog(language, "empty_fields")

    def close_box(self, e):
        self.box.open = False
        self.box.update()

    def show_error_dialog(self, lang, error_type):
        messages = {
            "network_error": {
                "title": languages[lang]['network error title'],
                "message": languages[lang]['network error msg']
            },
            "invalid_credentials": {
                "title": languages[lang]['error'],
                "message": languages[lang]['invalid credentials']
            },
            "empty_fields": {
                "title": languages[lang]['error'],
                "message": languages[lang]['error msg']
            },
            "general_error": {
                "title": languages[lang]['error'],
                "message": languages[lang]['unexpected error']
            }
        }

        self.box.title.value = messages[error_type]["title"]
        self.message.value = messages[error_type]["message"]
        self.icon_message.name = ft.Icons.INFO
        self.icon_message.color = ft.Colors.RED
        self.box.open = True
        self.box.update()


