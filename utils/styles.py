from utils.couleurs import *

# _____Style pour les champs de connexion_____
login_style: dict = dict(
    border_radius=ft.border_radius.all(10),
    border_color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
    focused_border_color=BASE_COLOR,
    height=50,
    autofocus=True, content_padding=12, cursor_color=BASE_COLOR,
    hint_style=ft.TextStyle(size=16, font_family='PPM', color="black"),
    text_style=ft.TextStyle(size=16, font_family='PPM', color='black'),
    label_style=ft.TextStyle(size=16, font_family="PPM", color='black'),
)

# _____Style pour les champs multiline_____
ml_style: dict = dict(
    border_radius=ft.border_radius.all(10),
    border_color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
    focused_border_color=BASE_COLOR,
    autofocus=True, content_padding=12, cursor_color=BASE_COLOR,
    hint_style=ft.TextStyle(size=16, font_family='PPM', color="black"),
    text_style=ft.TextStyle(size=16, font_family='PPM', color='black'),
    label_style=ft.TextStyle(size=16, font_family="PPM", color='black'),
)

# _____Style pour outline_____
outline_style: dict = dict(
    border_radius=ft.border_radius.all(10),
    border_color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
    focused_border_color=BASE_COLOR, border=ft.InputBorder.NONE,
    height=50,
    autofocus=True, content_padding=12, cursor_color=BASE_COLOR, read_only=True,
    hint_style=ft.TextStyle(size=16, font_family='PPM', color="black"),
    text_style=ft.TextStyle(size=16, font_family='PPM', color='black'),
    label_style=ft.TextStyle(size=16, font_family="PPM", color='black'),
)



# _____style pour les mots de passe_____
password_style: dict = dict(
    border_radius=ft.border_radius.all(10),
    border_color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
    focused_border_color=BASE_COLOR, content_padding=12, cursor_color=BASE_COLOR,
    height=50,
    autofocus=True, password=True, can_reveal_password=True,
    hint_style=ft.TextStyle(size=16, font_family='PPM', color="black"),
    text_style=ft.TextStyle(size=16, font_family='PPM', color='black'),
    label_style=ft.TextStyle(size=16, font_family="PPM", color='black'),
)

# _____Style pour dropdown_____
drop_style: dict = dict(
    border_radius=10, border_color=BASE_COLOR,
    label_style=ft.TextStyle(size=16, font_family="PPM", color='black'),
    text_style=ft.TextStyle(size=16, font_family="PPM", color="black"),
    hint_style=ft.TextStyle(size=16, font_family="PPM", color="black"),
    border_width=1, content_padding=12,
    editable=True, enable_filter=True, enable_search=True, max_menu_height=200,
    selected_trailing_icon=ft.Icons.KEYBOARD_ARROW_UP_OUTLINED,
    trailing_icon=ft.Icons.KEYBOARD_ARROW_DOWN_OUTLINED
)

# _____style pour les switch_____
switch_style: dict = dict(
    active_color=BASE_COLOR,
    inactive_track_color=ft.Colors.GREY_100,
    thumb_color={
        ft.ControlState.SELECTED: BASE_COLOR,
        ft.ControlState.DEFAULT: ft.Colors.WHITE,
    },
    track_color={
        ft.ControlState.SELECTED: THUMB_COLOR,
        ft.ControlState.DEFAULT: ft.Colors.GREY,
    },
)

# _____style pour les containers_____
ct_style: dict = dict(
    visible=False,
    alignment=ft.alignment.center,
    padding=0,
    bgcolor=ft.Colors.with_opacity(0.4, ft.Colors.BLACK),  # Surcouche semi-transparente
    blur=ft.Blur(sigma_x=10, sigma_y=10, tile_mode=ft.BlurTileMode.CLAMP),  # Le flou est sur la surcouche
    animate_opacity=300,
)

# _____style pour les containers internes_____
intern_ct_style: dict = dict(
    bgcolor="white", border_radius=16,
    shadow=ft.BoxShadow(
        spread_radius=1, blur_radius=10, offset=ft.Offset(0, 5),
        color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
    )
)

# _____style pour les top containers_____
top_ct_style: dict = dict(
    bgcolor="white", padding=20, border=ft.border.only(
        bottom=ft.BorderSide(1, MAIN_COLOR)
    ),
    border_radius=ft.border_radius.only(top_left=8, top_right=8),
)

# _____style pour les bottom containers_____
bottom_ct_style: dict = dict(
    bgcolor="white", padding=20, border=ft.border.only(
        top=ft.BorderSide(1, MAIN_COLOR)
    ), expand=True,
    border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
)

# _____sequence container style_____
seq_ct_style: dict = dict(
    padding=5, border_radius=16, border=ft.border.all(1, BASE_COLOR),
    alignment=ft.alignment.center,
)

# _____Style pour les datatables_____
datatable_style: dict = dict(
    heading_row_color=ACCENT_PLUS_COLOR,
    horizontal_margin=20,
    column_spacing=20,
    data_text_style=ft.TextStyle(size=16, font_family='PPM'),
    heading_text_style=ft.TextStyle(size=16, font_family='PPR', color='white'),

)
