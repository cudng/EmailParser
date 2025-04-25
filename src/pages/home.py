from imapclient import IMAPClient
import flet as ft
from components import AppBar
from utils import auto_format_and_validate_date_input, on_change
import threading  # Recommended for non-blocking UI during long tasks
from services import SearchEmails, EmailSearchError,is_connected, save_emails_to_csv, DeleteEmails
from pathlib import Path


class Home(ft.View):

    def __init__(self, page: ft.Page):
        super().__init__(
            padding=0,
            route=page.route,
            appbar=AppBar(page)
        )
        self.page = page
        self.email_ids = []
        self.emails = []
        self.home_dir = str(Path.home())

        # GET THE IMAP4_SSL OBJECT FROM SESSION
        self.connection = self.page.session.get("conn")

        # EMAIL
        self.email = ft.Text(value=f"{self.page.client_storage.get("email")}", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_ACCENT_700)
        self.online_indicator = ft.Container(bgcolor=ft.Colors.GREEN_ACCENT_700, width=12, height=12, border_radius=20, offset=ft.Offset(-0.2, 0.1))

        # SEARCH SECTION

        #sender field
        self.specific_sender_label = ft.Text("Pick a specific sender:", size=18, color=ft.Colors.BLUE_ACCENT, weight=ft.FontWeight.W_700)
        self.specific_sender = ft.TextField(hint_text="Enter sender", on_change=lambda e: on_change(e))

        #subject_field
        self.subject_label = ft.Text("Pick a Subject:", size=18, color=ft.Colors.BLUE_ACCENT, weight=ft.FontWeight.W_700)
        self.subject = ft.TextField(hint_text='Enter Subject(e.g Invoice)', on_change=lambda e: on_change(e))

        #since_a_date field
        self.since_a_date_label = ft.Text("Pick since a date:", size=18, color=ft.Colors.BLUE_ACCENT, weight=ft.FontWeight.W_700)
        self.since_a_date = ft.TextField(
            hint_text="Enter a date (DD-Mon-YYY)",
            on_change=lambda e: auto_format_and_validate_date_input(e)
        )

        #before_a_date field
        self.before_a_date_label = ft.Text(
            "Pick before a date:",
            size=18, color=ft.Colors.BLUE_ACCENT,
            weight=ft.FontWeight.W_700
        )
        self.before_a_date = ft.TextField(
            hint_text="Enter a date(DD-Mon-YYY)",
            on_change=lambda e: auto_format_and_validate_date_input(e)
        )

        #by_word field
        self.by_word_label = ft.Text(
            "Search by word:",
            size=18, color=ft.Colors.BLUE_ACCENT,
            weight=ft.FontWeight.W_700,
        )
        self.by_word = ft.TextField(hint_text="Enter search word", on_change=lambda e: on_change(e))

        #search_button
        self.search_button = ft.FilledButton(
            "Search", bgcolor=ft.Colors.BLUE,
            width=200, height=40, icon=ft.Icons.SEARCH_OUTLINED,
            on_click=lambda e: self.search_emails(e)
        )

        # more fields
        self.more_fields = ft.Text(spans=[ft.TextSpan(
            text="More filters...",
            style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
            on_click=lambda e: ...
        )])

        # END OF SEARCH SECTION

        # ERROR
        self.snack_bar = ft.SnackBar(
            ft.Text(),
            padding=20
        )

        # LOADING INDICATOR
        self.loading_indicator = ft.ProgressRing(visible=False)

        # RESULTS SECTION

        #results label
        self.results_label = ft.Text("📧 Parsed Email Results", size=25, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_ACCENT)

        self.lv = ft.ListView(expand=1,
                              spacing=10,
                              padding=20,
                              divider_thickness=1
                              )

        self.table_container = ft.Container(
            height=350,
            expand=True,
            expand_loose=True,
            content=self.lv
        )

        # File picker
        self.file_picker = ft.FilePicker()
        self.page.overlay.append(self.file_picker)
        self.file_picker.on_result = self.file_save_result

        # Open modal dialog
        self.delete_dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Please confirm"),
            content=ft.Text(""),
            actions=[
                ft.TextButton("No", on_click=lambda e: self.page.close(self.delete_dlg_modal)),
                ft.TextButton("Yes", on_click=lambda e: self.delete_emails(e)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: page.add(
                ft.Text("Modal dialog dismissed"),
            ),
        )

        # Save button
        self.save_button = ft.FilledButton(
            text="💾 Save",
            bgcolor=ft.Colors.GREY,
            width=200,
            height=40,
            disabled=True,
            on_click=lambda e: self.save_to_csv(e)
        )

        # Delete button
        self.delete_button = ft.FilledButton(
            text="🗑️Bin",
            bgcolor=ft.Colors.GREY,
            width=200,
            height=40,
            disabled=True,
            on_click=lambda e: self.open_dlg_delete(e)
        )
        # Number of Emails Found
        self.emails_found = ft.Text(f"Emails found: {len(self.emails)}")
        # END OF RESULT SECTION


        # BODY

        self.body = ft.Container(
            padding=20,
            content=ft.Column([
                ft.Row([self.email, self.online_indicator], alignment=ft.MainAxisAlignment.START),
                ft.Divider(height=10),
                ft.Row([self.specific_sender_label, self.specific_sender], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([self.subject_label, self.subject], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([self.before_a_date_label, self.before_a_date], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([self.since_a_date_label, self.since_a_date], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([self.by_word_label, self.by_word], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([self.more_fields], alignment=ft.MainAxisAlignment.END),
                ft.Divider(height=10),
                ft.Row([self.search_button], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([self.loading_indicator,], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Row([self.results_label], alignment=ft.MainAxisAlignment.CENTER),
                self.emails_found,
                ft.Divider(height=5),
                self.table_container,
                ft.Divider(height=10),
                ft.Row([self.save_button, self.delete_button], alignment=ft.MainAxisAlignment.CENTER),
                self.snack_bar
            ])
        )

        # CONTENT
        self.controls = [self.body]

    def check_internet(self):

        if not is_connected():
            self.show_error("No Internet Connection")
            return False
        else:
            return True

    def check_session(self):
        if not isinstance(self.connection, IMAPClient):
            self.show_error("Your session is Expired! Please Log in first.")
            self.online_indicator.bgcolor = ft.Colors.RED_ACCENT_700
            return False
        else:
            return True

    def get_filter_values(self):
        sender = self.specific_sender.value.strip()
        subject = self.subject.value.strip()
        since = self.since_a_date.value.strip()
        before = self.before_a_date.value.strip()
        text = self.by_word.value.strip()

        # Check if all fields are empty
        if not any([sender, subject, since, before, text]):
            self.show_error("Please enter at least one filter value.")
            return

        filter_values = {
            "sender": sender or None,
            "subject": subject or None,
            "since": since or None,
            "before": before or None,
            "text": text or None
        }

        return filter_values

    def search_emails(self, e) -> None: # noqa

        if not self.check_session():
            return
        if not self.check_internet():
            return

        filter_values = self.get_filter_values()

        # Show the loading indicator
        self.loading_indicator.visible = True
        self.lv.controls.clear()  # Clear previous results
        self.body.disabled = True
        self.page.update()

        def perform_search(filters: dict[str, str], conn: IMAPClient):
            try:
                search = SearchEmails(filters, conn)
                self.email_ids = search.get_email_ids()
                self.emails = search.get_email_data()
                self.lv.controls = [
                    ft.ResponsiveRow([
                        ft.Text(
                                spans=[
                                    ft.TextSpan(
                                       "Subject: ",
                                        style=ft.TextStyle(
                                            weight=ft.FontWeight.W_500,
                                            color=ft.Colors.BLUE_ACCENT_700,
                                        )),
                                    ft.TextSpan(f"{email["subject"]}",)
                                ]),
                        ft.Text(
                                spans=[
                                    ft.TextSpan(
                                        "From: ",
                                        style=ft.TextStyle(
                                            weight=ft.FontWeight.W_500,
                                            color=ft.Colors.BLUE_ACCENT_700,
                                        )
                                    ),
                                    ft.TextSpan(f"{email["from"]}")
                                ]
                                ),
                        ft.Text(
                                spans=[
                                    ft.TextSpan(
                                        "Date: ",
                                        style=ft.TextStyle(
                                            weight=ft.FontWeight.W_500,
                                            color=ft.Colors.BLUE_ACCENT_700,
                                        )),
                                    ft.TextSpan(f"{email["date"]}")
                                ]
                                ),
                        ft.Text(
                                spans=[
                                    ft.TextSpan(
                                        "Body: ",
                                        style=ft.TextStyle(
                                            weight=ft.FontWeight.W_500,
                                            color=ft.Colors.BLUE_ACCENT_700,
                                        )),
                                    ft.TextSpan(f"{email["body"][:200] + "..."}")
                                ]
                                ),
                    ], alignment=ft.MainAxisAlignment.SPACE_EVENLY
                    )
                        for email in self.emails
                    ]
                self.save_button.bgcolor = ft.Colors.GREEN_ACCENT_700
                self.delete_button.bgcolor = ft.Colors.RED_ACCENT_700
                self.save_button.disabled = False
                self.delete_button.disabled = False
                self.emails_found.value = f"Emails found: {len(self.emails)}"

            except EmailSearchError as Error:
                # Show error to user in UI
                self.show_error(Error)

            finally:
                # Hide the loading indicator after search is complete
                self.loading_indicator.visible = False
                self.body.disabled = False
                self.page.update()

        # Run the search in a separate thread so the UI remains responsive.
        threading.Thread(target=perform_search, args=(filter_values, self.connection), daemon=True).start()


    def save_to_csv(self, e) -> None:
        if len(self.emails) == 0:
            self.show_error("There Are no Search Results")
            return

        self.file_picker.save_file(
            dialog_title="Save email results as...",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["csv"],
            initial_directory=self.home_dir,
            file_name="email_results.csv"
        )

    def file_save_result(self, e) -> None:
        if e.path:
            if not e.path.endswith(".csv"):
                e.path += ".csv"  # force correct extension
            save_emails_to_csv(e.path, self.emails)
            self.snack_bar.content.value = f"✅ Emails saved successfully into: {e.path}"
            self.snack_bar.bgcolor = ft.Colors.GREEN_ACCENT_700
            self.snack_bar.open = True
            self.page.update()

    def open_dlg_delete(self, e) -> None:

        self.delete_dlg_modal.content.value = f"Do you really want to move {len(self.email_ids)} emails to Bin?"
        self.page.open(self.delete_dlg_modal)
        self.delete_dlg_modal.update()

    def delete_emails(self, e) -> None:
        # Show the loading indicator
        self.page.close(self.delete_dlg_modal)
        self.loading_indicator.visible = True
        self.body.disabled = True
        self.page.update()

        def perform_delete():
            delete_service = DeleteEmails(conn=self.connection, ids=self.email_ids)
            result, info = delete_service.move_to_trash()

            # Clear previous results
            self.lv.controls.clear()
            self.emails_found.value = "0"
            self.loading_indicator.visible = False
            self.body.disabled = False

            if result:
                self.show_success(info)
            else:
                self.show_error(info)

            self.page.update()

        threading.Thread(target=perform_delete, daemon=True).start()


    def show_success(self, message) -> None:
        self.snack_bar.content.value = message
        self.snack_bar.bgcolor = ft.Colors.GREEN_ACCENT_700
        self.snack_bar.open = True
        self.snack_bar.update()

    def show_error(self, message):
        self.snack_bar.bgcolor = ft.Colors.RED_ACCENT_700
        self.snack_bar.content.value = message
        self.snack_bar.open = True
        self.snack_bar.update()