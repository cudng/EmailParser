import logging

from imapclient import IMAPClient
import flet as ft
from components import AppBar
from utils import auto_format_and_validate_date_input, on_change
import threading  # Recommended for non-blocking UI during long tasks
from services import SearchEmails, EmailSearchError,is_connected, save_emails_to_csv, move_to_trash, get_folders, sorted_emails
from pathlib import Path
from core import Style


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
        self.emails_count = 0
        self.home_dir = str(Path.home())


        # GET THE IMAP4_SSL OBJECT FROM SESSION
        self.connection = self.page.session.get("conn")

        self.folders = self.page.client_storage.get("folders")

        # EMAIL
        self.email = ft.Text(**Style.email_textfield(), value=f"{self.page.client_storage.get("email")}")
        self.online_indicator = ft.Container(**Style.online_indicator())
        self.group_checkbox = ft.Checkbox(
            **Style.group_checkbox(),
            on_change=lambda e: self.checked(e)
        )

        # SEARCH SECTION

        #folder selection
        self.folders_label = ft.Text(**Style.label(), value="Please choose folder:")
        self.choose_folder = ft.Dropdown(
            **Style.choose_folder(),
            value=self.page.client_storage.get("folder") if self.page.client_storage.contains_key("folder") else self.folders[0][0],
            options=[ft.DropdownOption(key=folder[0], text=folder[1]) for folder in self.folders],
            on_change=lambda e: self.dropdown_changed(e)
        )

        #sender field
        self.sender_label = ft.Text("Pick sender:", **Style.label())
        self.sender = ft.TextField(hint_text="Enter sender", on_change=lambda e: on_change(e))

        #subject_field
        self.subject_label = ft.Text("Pick a Subject:", **Style.label())
        self.subject = ft.TextField(hint_text='Enter Subject(e.g Invoice)', on_change=lambda e: on_change(e))

        #since_a_date field
        self.since_a_date_label = ft.Text("Pick since a date:", **Style.label())
        self.since_a_date = ft.TextField(
            hint_text="Enter a date (DD-Mon-YYY)",
            on_change=lambda e: auto_format_and_validate_date_input(e)
        )

        #before_a_date field
        self.before_a_date_label = ft.Text("Pick before a date:", **Style.label())
        self.before_a_date = ft.TextField(
            hint_text="Enter a date(DD-Mon-YYY)",
            on_change=lambda e: auto_format_and_validate_date_input(e)
        )

        #by_word field
        self.by_word_label = ft.Text("Search by word:", **Style.label())
        self.by_word = ft.TextField(hint_text="Enter search word", on_change=lambda e: on_change(e))

        #search_button
        self.search_button = ft.FilledButton(
            "Search",
            on_click=lambda e: self.search_emails(e),
            **Style.search_button()
        )

        # more fields
        self.more_fields = ft.TextButton(
            icon=ft.Icons.ARROW_DROP_DOWN,
            text="More filters"
        )

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
        self.results_label = ft.Text(**Style.results_label())

        self.lv = ft.ListView(**Style.lv())

        self.table_container = ft.Container(
            **Style.table_container(),
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
                ft.TextButton("Yes", on_click=lambda e: self.delete_emails()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: page.add(
                ft.Text("Modal dialog dismissed"),
            ),
        )

        # Save button
        self.save_button = ft.FilledButton(
            **Style.save_button(),
            on_click=lambda e: self.save_to_csv(e)
        )

        # Delete button
        self.delete_button = ft.FilledButton(
            **Style.delete_button(),
            on_click=lambda e: self.open_dlg_delete(e)
        )

        # Number of Emails Found
        self.emails_found = ft.Text(f"Emails found: {self.emails_count}")
        # END OF RESULT SECTION


        # FILTERS AREA

        self.filters_column = ft.Column([
            ft.Row([self.folders_label, self.choose_folder], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([self.sender_label, self.sender], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([self.subject_label, self.subject], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([self.before_a_date_label, self.before_a_date], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([self.since_a_date_label, self.since_a_date], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([self.by_word_label, self.by_word], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([self.more_fields], alignment=ft.MainAxisAlignment.CENTER)
        ])

        # BODY

        self.body = ft.Container(
            padding=20,
            content=ft.Column([
                ft.Row([self.email, self.online_indicator, ft.VerticalDivider(width=50), self.group_checkbox], alignment=ft.MainAxisAlignment.START),
                ft.Divider(height=10),
                self.filters_column,
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
                ], scroll=ft.ScrollMode.AUTO
            )
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
        sender = self.sender.value.strip()
        subject = self.subject.value.strip()
        since = self.since_a_date.value.strip()
        before = self.before_a_date.value.strip()
        text = self.by_word.value.strip()

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
                self.email_ids = search.get_email_ids(self.choose_folder.value)

                get_emails: dict = {
                    False: lambda : search.get_email_data("ALL"),
                    True: lambda: search.get_email_data("CURTAIN")
                }
                self.emails = get_emails[self.group_checkbox.value]()

                self.lv.controls = self.get_lv_controls()
                self.emails_count = len(self.emails)
                self.emails_found.value = f"Emails found: {self.emails_count}"

                if not self.group_checkbox.value:
                    self.activate_buttons()

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
            **Style.file_picker(),
            initial_directory=self.home_dir,
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

    def delete_all_found_emails(self) -> tuple:
        result, info = move_to_trash(conn=self.connection, ids=self.email_ids)
        # Clear previous results
        self.lv.controls.clear()
        self.emails_count = 0
        self.emails_found.value = f"Emails found: {self.emails_count}"
        return result, info

    def delete_emails_by_sender(self)-> tuple:
        result, info = move_to_trash(conn=self.connection, ids=self.delete_dlg_modal.data.data)  # self.delete_dlg_modal.data.data = list of uids saved for found emails per sender
        # Clear the row
        self.lv.controls.remove(self.delete_dlg_modal.data)
        self.emails_count = int(self.emails_count) - len(self.delete_dlg_modal.data.data)

        self.emails_found.value = f"Emails found: {self.emails_count}"
        return result, info

    def delete_emails(self) -> None:
        # Show the loading indicator
        self.page.close(self.delete_dlg_modal)
        self.loading_indicator.visible = True
        self.body.disabled = True
        self.page.update()

        def perform_delete():
            if self.group_checkbox.value:
                result, info = self.delete_emails_by_sender()
            else:
                result, info = self.delete_all_found_emails()

            self.loading_indicator.visible = False
            self.body.disabled = False

            if result:
                self.show_success(info)
            else:
                self.show_error(info)

            self.page.update()

        threading.Thread(target=perform_delete, daemon=True).start()


    def get_lv_controls(self) -> list:
        logging.warning(self.group_checkbox.value)
        sorted_senders = sorted_emails(self.emails)
        # builds different outcome depends on user choice to Group item True or False( checkbox )
        choice: dict = {
            True: lambda : [
                ft.ResponsiveRow([
                    ft.Text(
                        spans=[
                            ft.TextSpan(
                                "From: ",
                                **Style.results_text_span()
                            ),
                            ft.TextSpan(f"{sender}: {data["count"]}")
                        ]
                    ),

                    ft.IconButton(**Style.delete_icon_button(), on_click=lambda e: self.icon_button_clicked(e), data=data["count"])
                ], data=data["uids"]
            ) for sender, data in sorted_senders],
            False: lambda : [
                ft.ResponsiveRow([
                    ft.Text(
                        spans=[
                            ft.TextSpan(
                                "Subject: ",
                                **Style.results_text_span()
                            ),
                            ft.TextSpan(f"{email["subject"]}", )
                        ]
                    ),
                    ft.Text(
                        spans=[
                            ft.TextSpan(
                                "From: ",
                                **Style.results_text_span()
                            ),
                            ft.TextSpan(f"{email["from"]}")
                        ]
                    ),
                    ft.Text(
                        spans=[
                            ft.TextSpan(
                                "Date: ",
                                **Style.results_text_span()
                            ),
                            ft.TextSpan(f"{email["date"]}")
                        ]
                    ),
                    ft.Text(
                        spans=[
                            ft.TextSpan(
                                "Body: ",
                                **Style.results_text_span()
                            ),
                            ft.TextSpan(f"{email["body"][:200] + "..."}")
                        ]
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_EVENLY
                )
                for email in self.emails
            ]
        }

        return choice[self.group_checkbox.value]()

    def icon_button_clicked(self, e: ft.ControlEvent):
        self.delete_dlg_modal.content.value = f"Do you really want to move {e.control.data} emails to Bin?"
        self.delete_dlg_modal.data = e.control.parent  # sets data for dialog modal as Responsive Row , parent of button clicked
        self.page.open(self.delete_dlg_modal)
        self.delete_dlg_modal.update()

    def checked(self, e: ft.ControlEvent):
        chosen_folder: dict = {
            True: self.folders[1][0],
            False: self.page.client_storage.get("folder")  if self.page.client_storage.contains_key("folder") else self.folders[0][0]
        }
        self.clear_filter_fields()
        self.filters_column.disabled = e.control.value
        self.choose_folder.value = chosen_folder[e.control.value]
        self.filters_column.update()

    def clear_filter_fields(self) -> None:
        self.by_word.value = ""
        self.since_a_date.value = ""
        self.before_a_date.value = ""
        self.subject.value = ""
        self.sender.value = ""

    def dropdown_changed(self, e: ft.ControlEvent):
        self.page.client_storage.set("folder", e.control.value)

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

    def activate_buttons(self):
        self.save_button.bgcolor = ft.Colors.GREEN_ACCENT_700
        self.delete_button.bgcolor = ft.Colors.RED_ACCENT_700
        self.save_button.disabled = False
        self.delete_button.disabled = False