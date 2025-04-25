import flet as ft

class NotFoundPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            padding=0, route=page.route
        )

        self.main_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text("404 Not Found", size=30, weight=ft.FontWeight.BOLD, color="blue"),
                    ft.ElevatedButton("Go Home", on_click=lambda _: page.go("/login"))
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
            expand=True)

        self.controls = [self.main_container]