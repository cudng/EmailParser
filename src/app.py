import flet as ft
import pages
import config


def main(page: ft.Page):

    page.window.height = config.WINDOW_HEIGHT
    page.window.width = config.WINDOW_WIDTH
    page.theme_mode = config.THEME_MODE
    page.window.always_on_top = True
    page.scroll = ft.ScrollMode.AUTO


    def on_route_change(route): # noqa

        page.views.clear()

        match page.route:

            case "/":
                page.views.append(pages.Login(page))

            case "/home":
                page.views.append(pages.Home(page))

            case _ :
                page.views.append(pages.NotFoundPage(page))

        page.update()


    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)


    def on_app_close(e):
        conn = page.session.get("conn")
        if conn:
            conn.logout()


    page.on_close = on_app_close
    page.on_route_change = on_route_change
    page.on_view_pop = view_pop

    page.go(page.route)
    # page.go("/home")

ft.app(main)