import flet as ft

class AppBar(ft.AppBar):

    def __init__(self, page: ft.Page):
        super().__init__(
            title=ft.Text("Email Parser"),
            center_title=True,
            toolbar_height=50,
            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/")) if page.route == "/home" else None,
            bgcolor=ft.Colors.BLUE,
            actions=[ft.IconButton(ft.Icons.WB_SUNNY_OUTLINED if page.theme_mode == ft.ThemeMode.DARK else ft.Icons.DARK_MODE,
                                   on_click=lambda e: self.change_theme_mode(e)),
                     ft.Container(width=20)]
        )
    # CHANGING THEME MODE BETWEEN DARK AND LIGHT
    def change_theme_mode(self, e: ft.TapEvent):
        """Changing between DARK and LIGHT theme modes and swapping Icons"""
        if e.control.icon == ft.Icons.WB_SUNNY_OUTLINED:
            self.actions[0].icon = ft.Icons.DARK_MODE  # noqa
            self.page.theme_mode = ft.ThemeMode.LIGHT
        else:
            self.actions[0].icon = ft.Icons.WB_SUNNY_OUTLINED  # noqa
            self.page.theme_mode = ft.ThemeMode.DARK

        self.page.update()