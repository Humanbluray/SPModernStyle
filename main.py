import os
import flet as ft
from views.signin import Signin
from views.home import Home
import re, asyncio

SIGNIN_ROUTE = "/"
HOME_ROUTE = '/home'


def main(page: ft.Page):
    page.title = 'School Pilot'
    page.theme_mode = ft.ThemeMode.LIGHT
    page.fonts = {
        "PPR": "/fonts/Figtree-Regular.ttf",
        "PPM": "/fonts/Figtree-Medium.ttf",
        "PPB": "/fonts/Figtree-Bold.ttf",
        "PEB": "/fonts/Figtree-ExtraBold.ttf",
        "PPI": "/fonts/Figtree-Italic.ttf",
        "PME": "/fonts/Poppins-Medium.ttf",
    }

    route_views = {
        "/": Signin,
        "/home": Home
    }

    async def route_change(event: ft.RouteChangeEvent):
        page.views.clear()
        current_route = event.route

        match = re.match(r"^/home/([^/]+)/([^/]+)$", current_route)

        if match:
            language = match.group(1)
            user_uid = match.group(2)
            view = Home(page, language, user_uid)
            page.views.append(view)
            page.update()
            await view.did_mount_async()

        elif current_route in route_views:
            page.views.append(route_views[current_route](page))
            page.update()

        else:
            page.views.append(Signin(page))
            page.update()

    def view_pop(view):
        top_view = page.views[-1]
        page.go(top_view.route)

    def run_async(coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(coro)

    # Ces lignes lient vos fonctions aux événements de la page
    page.on_route_change = lambda e: run_async(route_change(e))
    page.on_view_pop = view_pop
    page.go(page.route)

    # Initialisation de la vue de départ
    page.go(page.route)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    ft.app(
        target=main, assets_dir='assets', route_url_strategy='#', port=port,
    )
