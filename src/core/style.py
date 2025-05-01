import flet as ft
from components import AppBar



class Style:

    # LOGIN PAGE START

    @staticmethod
    def login_view(page) -> dict:
        return {
            "padding": 0,
            "route": page.route,
            "appbar": AppBar(page)
        }

    @staticmethod
    def title() -> dict:
        return {
            "value": "Welcome to your Email Parser!",
            "size": 28,
            "color": ft.Colors.BLUE_ACCENT,
            "weight": ft.FontWeight.W_900
        }

    @staticmethod
    def email_provider_label() -> dict:
        return {
            "value": "Email provider:",
            "color": ft.Colors.BLUE_ACCENT,
            "size": 20,
            "weight": ft.FontWeight.W_700
        }

    @staticmethod
    def password_field(page) -> dict:
        return {
            "value": page.client_storage.get("pass") if page.client_storage.contains_key("pass") else "",
            "hint_text": "Enter your Password",
            "color": ft.Colors.BLUE_ACCENT,
            "prefix_icon": ft.Icons.PASSWORD,
            "password": True,
            "can_reveal_password": True
        }

    @staticmethod
    def email_field(page) -> dict:
        return {
            "value": page.client_storage.get("email") if page.client_storage.contains_key("email") else "",
            "hint_text": "Enter your Email",
            "color": ft.Colors.BLUE_ACCENT,
            "prefix_icon": ft.Icons.EMAIL,
            "error_style": ft.TextStyle(size=11)
        }

    @staticmethod
    def connect_button() -> dict:
        return {
            "text": "Connect",
            "bgcolor": ft.Colors.BLUE,
            "width": 300,
            "height": 50,
            "color": ft.Colors.WHITE,
        }

    @staticmethod
    def checkbox(page) -> dict:
        return {
            "label": "Save Your Password",
            "value": True if page.client_storage.contains_key("pass") else False,
            "label_position": ft.LabelPosition.LEFT
        }

    @staticmethod # noqa
    def error_snackbar() -> dict:
        return {
            "content": ft.Text(color=ft.Colors.WHITE),
            "bgcolor": ft.Colors.RED_ACCENT_700,
            "padding": 20
}


    @staticmethod
    def function() -> dict:
        return {

        }

    @staticmethod
    def choose_email_provider() -> dict:
        return {
            "value": "imap.gmail.com",
            "width": 300,
            "leading_icon": ft.Icons.ALTERNATE_EMAIL,
            "options": [
                ft.DropdownOption(key="imap.gmail.com", text="GMAIL", leading_icon=ft.Icons.ALTERNATE_EMAIL),
                ft.dropdown.Option(key="imap.mail.yahoo.com", text="YAHOO", leading_icon=ft.Icons.ALTERNATE_EMAIL),
            ]
        }


    # LOGIN PAGE END


    # HOME PAGE START
    @staticmethod
    def email_textfield() -> dict:
        return {
            "size": 22,
            "weight": ft.FontWeight.BOLD,
        }

    @staticmethod
    def online_indicator() -> dict:
        return {
            "bgcolor": ft.Colors.GREEN_ACCENT_700,
            "width":  12,
            "height":  12,
            "border_radius":  20,
            "offset":  ft.Offset(-0.2, 0.1)
        }

    @staticmethod
    def label() -> dict:
        return {
            "size": 18,
            "color": ft.Colors.BLUE_ACCENT,
            "weight": ft.FontWeight.W_700
        }


    @staticmethod
    def search_button() -> dict:
        return {
            "bgcolor": ft.Colors.BLUE,
            "width" : 200,
            "height" : 40,
            "icon" : ft.Icons.SEARCH_OUTLINED,
        }

    @staticmethod
    def more_fields() -> dict:
        return {
            "spans": [
                ft.TextSpan(
                    text="More filters...",
                    style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
                    on_click=lambda e: ...
            )]
        }

    @staticmethod
    def lv() -> dict:
        return {
            "expand": 1,
            "spacing": 10,
            "padding": 20,
            "divider_thickness": 1
        }

    @staticmethod
    def table_container() -> dict:
        return {
            "height": 350,
            "expand": True,
            "expand_loose": True,
        }

    @staticmethod
    def save_button() -> dict:
        return {
            "text": "💾 Save",
            "bgcolor": ft.Colors.GREY,
            "width": 200,
            "height": 40,
            "disabled": True,
        }

    @staticmethod
    def delete_button() -> dict:
        return {
            "text": "🗑️Bin",
            "bgcolor": ft.Colors.GREY,
            "width": 200,
            "height": 40,
            "disabled": True
        }

    @staticmethod
    def results_label() -> dict:
        return {
            "value": "📧 Parsed Email Results",
            "size": 25,
            "weight": ft.FontWeight.BOLD,
            "color": ft.Colors.BLUE_ACCENT
        }

    @staticmethod
    def results_text_span() -> dict:
        return {
            "style": ft.TextStyle(
                weight=ft.FontWeight.W_500,
                color=ft.Colors.BLUE_ACCENT_700,
            )
        }

    @staticmethod
    def file_picker() -> dict:
        return {
            "dialog_title": "Save email results as...",
            "file_type": ft.FilePickerFileType.CUSTOM,
            "allowed_extensions": ["csv"],
            "file_name": "email_results.csv"
        }

    @staticmethod
    def choose_folder() -> dict:
        return {
            "width": 300,
        }

    @staticmethod
    def function() -> dict:
        return {

        }

    # HOME PAGE END

