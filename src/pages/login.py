import flet as ft
from imapclient import IMAPClient
from utils import validate
from services import EmailConnectionService, is_connected, get_folders
import threading
from core import Style


class Login(ft.View):

    def __init__(self, page: ft.Page):
        super().__init__(**Style.login_view(page))

        self.page = page

        # TITLE

        self.title = ft.Text(**Style.title())

        # EMAIL

        self.email_provider = ft.Text(**Style.email_provider_label())
        self.choose_email_provider = ft.Dropdown(**Style.choose_email_provider())
        self.email_label = ft.Text(**Style.label(), value="Email:")
        self.email = ft.TextField(**Style.email_field(page))

        # PASSWORD

        self.password_label = ft.Text(**Style.label(), value="Password:")
        self.password = ft.TextField(**Style.password_field(page))

        # CONNECT BUTTON

        self.connect_button = ft.ElevatedButton(
            **Style.connect_button(),
            on_click=lambda e: self.connect(e)
        )

        # CHECK BOX FOR PASSWORD SAVE
        self.checkbox = ft.Checkbox(**Style.password_checkbox(page))

        # ERROR
        self.error = ft.SnackBar(**Style.error_snackbar())

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
                ft.Row([self.checkbox], alignment=ft.MainAxisAlignment.END),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                ft.Row([self.connect_button], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([self.loading_indicator], alignment=ft.MainAxisAlignment.CENTER),
                self.error
            ])
        )

        self.controls = [self.body]

    def get_connection(self) -> IMAPClient | str:

        imap_server = self.choose_email_provider.value
        password = self.password.value
        email = self.email.value

        validated_email = validate(email)

        if validated_email["valid"]:
            service = EmailConnectionService(
                email=email,
                password=password,
                imap_server=imap_server
            )
            return service.connect()
        else:
            return validated_email["message"]

    def save_password(self):
        if self.checkbox.value:
            self.page.client_storage.set("pass", self.password.value)
        else:
            self.page.client_storage.remove("pass")

    def connect(self, e):

        if not is_connected():
            self.error.content.value = "No Internet Connection"
            self.error.open = True
            self.page.update()
            return

        self.loading_indicator.visible = True
        self.body.disabled = True
        self.page.update()

        def perform_connection():

            conn = self.get_connection()

            if isinstance(conn, IMAPClient):
                folders = get_folders(conn)
                self.page.client_storage.set("email", self.email.value)
                self.page.session.set("conn", conn)
                self.page.client_storage.set("folders", folders) if not self.page.client_storage.contains_key("folders") else ...
                self.loading_indicator.visible = False
                self.save_password()
                self.page.go("/home")

            else:
                self.email.error_text = conn
                self.error.open = True
                self.page.update()

        threading.Thread(target=perform_connection, daemon=True).start()

