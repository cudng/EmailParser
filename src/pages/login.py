import flet as ft
from elements import AppBar # noqa
from email_validator import validate_email, EmailNotValidError


class Login(ft.View):

    def __init__(self, page: ft.Page):
        super().__init__(
        padding=0,
        route=page.route,
        appbar=AppBar(page)
        )

        # TITLE

        self.title = ft.Text("Welcome to your Email Parser!",
                     size=28,
                     color=ft.Colors.BLUE_ACCENT,
                     weight=ft.FontWeight.W_900
                    )

        # EMAIL

        self.email_provider = ft.Text("Email provider:",
                                      color=ft.Colors.BLUE_ACCENT,
                                      size=20,
                                      weight=ft.FontWeight.W_700)
        self.choose_email_provider = ft.Dropdown(
            value="GMAIL",
            width=300,
            options=[
                ft.dropdown.Option("GMAIL"),
                ft.dropdown.Option("YAHOO"),
            ]
        )
        self.email_label = ft.Text("Email:", color=ft.Colors.BLUE_ACCENT, size=20, weight=ft.FontWeight.W_700)
        self.email = ft.TextField(hint_text="Please enter your Email", color=ft.Colors.BLUE_ACCENT)

        # PASSWORD

        self.password_label = ft.Text("Password:", color=ft.Colors.BLUE_ACCENT, size=20,
                                      weight=ft.FontWeight.W_700)
        self.password = ft.TextField(hint_text="Please enter your Password", color=ft.Colors.BLUE_ACCENT)

        # CONNECT BUTTON

        self.connect_button = ft.ElevatedButton("Connect",
                                                bgcolor=ft.Colors.BLUE,
                                                width=300,
                                                height=50,
                                                color=ft.Colors.WHITE,
                                                on_click=lambda e: self.connect(e))


        # ERROR
        self.error = ft.SnackBar(
            ft.Text(color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_ACCENT_700
        )


        # MAIN CONTAINER

        self.body = ft.Container(
            padding=ft.padding.only(40, 20, 40, 20),
            content=ft.Column([
                ft.Divider(height=100, color=ft.Colors.TRANSPARENT),
                ft.Row([self.title], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                ft.Row([self.email_provider, self.choose_email_provider],
                       alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                       ),
                ft.Row([self.email_label, self.email], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([self.password_label, self.password], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                ft.Row([self.connect_button], alignment=ft.MainAxisAlignment.CENTER),
                self.error
            ])
        )

        self.controls = [self.body]

    def connect(self, e):

        try:
            email = validate_email(self.email.value)

        except EmailNotValidError as e:
            self.error.content.value = e
            self.error.open = True
            self.error.update()
            return

        else:
            validated_email = email.normalized
            self.page.client_storage.set("email", validated_email)
            self.page.go("/home")