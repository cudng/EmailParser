import flet as ft
from flet.core.types import MainAxisAlignment
from imapclient import IMAPClient
from components import AppBar
from utils import validate
from services import EmailConnectionService, is_connected
import threading


class Login(ft.View):

    def __init__(self, page: ft.Page):
        super().__init__(
        padding=0,
        route=page.route,
        appbar=AppBar(page)
        )

        self.page = page

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
            value="imap.gmail.com",
            width=300,
            leading_icon=ft.Icons.ALTERNATE_EMAIL,
            options=[
                ft.DropdownOption(key="imap.gmail.com", text="GMAIL", leading_icon=ft.Icons.ALTERNATE_EMAIL),
                ft.dropdown.Option(key="imap.mail.yahoo.com", text="YAHOO", leading_icon=ft.Icons.ALTERNATE_EMAIL),
            ],
            on_change=lambda e: self.show_value()

        )
        self.email_label = ft.Text("Email:", color=ft.Colors.BLUE_ACCENT, size=20, weight=ft.FontWeight.W_700)
        self.email = ft.TextField(
            value=self.page.client_storage.get("email") if self.page.client_storage.contains_key("email") else "",
            hint_text="Enter your Email",
            color=ft.Colors.BLUE_ACCENT,
            prefix_icon=ft.Icons.EMAIL,
            error_style = ft.TextStyle(size=11)
        )

        # PASSWORD

        self.password_label = ft.Text("Password:", color=ft.Colors.BLUE_ACCENT, size=20, weight=ft.FontWeight.W_700)
        self.password = ft.TextField(
            value=self.page.client_storage.get("pass") if self.page.client_storage.contains_key("pass") else "",
            hint_text="Enter your Password",
            color=ft.Colors.BLUE_ACCENT,
            prefix_icon=ft.Icons.PASSWORD,
            password=True,
            can_reveal_password=True
        )

        # CONNECT BUTTON

        self.connect_button = ft.ElevatedButton(
            text="Connect",
            bgcolor=ft.Colors.BLUE,
            width=300,
            height=50,
            color=ft.Colors.WHITE,
            on_click=lambda e: self.connect(e)
        )

        # CHECK BOX FOR PASSWORD SAVE
        self.checkbox = ft.Checkbox(label="Save Your Password",
                                    value=True if self.page.client_storage.contains_key("pass") else False,
                                    label_position=ft.LabelPosition.LEFT)

        # ERROR
        self.error = ft.SnackBar(
            ft.Text(color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_ACCENT_700,
            padding=20
        )

        # LOADING INDICATOR
        self.loading_indicator = ft.ProgressRing(visible=False)

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
                ft.Row([self.checkbox], alignment=MainAxisAlignment.END),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                ft.Row([self.connect_button], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([self.loading_indicator], alignment=ft.MainAxisAlignment.CENTER),
                self.error
            ])
        )

        self.controls = [self.body]

    def connect(self, e):

        imap_server = self.choose_email_provider.value
        email = self.email.value
        password = self.password.value
        validated_email = validate(email)

        if not is_connected():
            self.error.content.value = "No Internet Connection"
            self.error.open = True
            self.page.update()
            return

        self.loading_indicator.visible = True
        self.body.disabled = True
        self.page.update()

        def perform_connection():
            if validated_email["valid"]:

                service = EmailConnectionService(
                    email=email,
                    password=password,
                    imap_server=imap_server
                )
                conn = service.connect()

                if isinstance(conn, IMAPClient):
                    self.page.client_storage.set("email", email)
                    self.page.session.set("conn", conn)
                    self.loading_indicator.visible = False
                    if self.checkbox.value:
                        self.page.client_storage.set("pass", password)
                    else:
                        self.page.client_storage.remove("pass")
                    self.page.go("/home")

                else:
                    self.error.content.value = conn
                    self.error.open = True
                    self.error.update()
            else:
                self.email.error_text = validated_email["message"]
                self.page.update()

        threading.Thread(target=perform_connection, daemon=True).start()


    def show_value(self):
        ...