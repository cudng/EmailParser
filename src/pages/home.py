import flet as ft
from elements import AppBar # noqa

RESULTS = [
        {
            "Subject": "Invoice for March 2024",
            "From": "billing@company.com",
            "Date": "Mon, 01 Apr 2024 10:35:22 +0000",
            "Body": "Hi John, Please find attached the invoice for March 2024. Total: $1,250.00"
        },
        {
            "Subject": "Payment Reminder",
            "From": "billing@company.com",
            "Date": "Tue, 05 Mar 2024 15:48:30 +0000",
            "Body": "Dear John, This is a friendly reminder that payment for February's invoice is still pending."
        },
        {
            "Subject": "Payment Reminder",
            "From": "billing@company.com",
            "Date": "Tue, 05 Mar 2024 15:48:30 +0000",
            "Body": "Dear John, This is a friendly reminder that payment for February's invoice is still pending. Please make the payment at your earliest convenience."
        },
        {
            "Subject": "Your Receipt from Purchase",
            "From": "noreply@store.com",
            "Date": "Sun, 24 Mar 2024 11:02:00 +0000",
            "Body": "Thanks for your purchase! Here is your receipt. Total: $45.99. Order ID: 123456"
        },
        {
            "Subject": "Meeting Notes",
            "From": "teamlead@company.com",
            "Date": "Wed, 03 Apr 2024 14:00:00 +0000",
            "Body": "Attached are the notes from today’s meeting. Action items: 1. Update client report, 2. Fix email export bug."
        },
    ]


class Home(ft.View):

    def __init__(self, page: ft.Page):
        super().__init__(
            padding=0,
            route=page.route,
            appbar=AppBar(page)
        )
        self.page = page

        # EMAIL
        self.email = ft.Text(value=f"{self.page.client_storage.get("email")}", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_ACCENT)
        self.green_circle = ft.Container(bgcolor=ft.Colors.GREEN_ACCENT_700, width=15, height=15, border_radius=20, offset=ft.Offset(-0.2, 0.1))

        # SEARCH SECTION

        #sender field
        self.specific_sender_label = ft.Text("Pick a specific sender:", size=18, color=ft.Colors.BLUE_ACCENT, weight=ft.FontWeight.W_700)
        self.specific_sender = ft.TextField(hint_text="Enter sender")

        #subject_field
        self.subject_label = ft.Text("Pick a Subject:", size=18, color=ft.Colors.BLUE_ACCENT, weight=ft.FontWeight.W_700)
        self.subject = ft.TextField(hint_text='Enter Subject(e.g "Invoice")')

        #since_a_date field
        self.since_a_date_label = ft.Text("Pick since a date:", size=18, color=ft.Colors.BLUE_ACCENT, weight=ft.FontWeight.W_700)
        self.since_a_date = ft.TextField(hint_text="Enter a date (DD-Mon-YYY)")

        #before_a_date field
        self.before_a_date_label = ft.Text("Pick before a date:", size=18, color=ft.Colors.BLUE_ACCENT, weight=ft.FontWeight.W_700)
        self.before_a_date = ft.TextField(hint_text="Enter a date(DD-Mon-YYY)")

        #by_word field
        self.by_word_label = ft.Text("Search by word:", size=18, color=ft.Colors.BLUE_ACCENT, weight=ft.FontWeight.W_700)
        self.by_word = ft.TextField(hint_text="Enter search word")

        #search_button
        self.search_button = ft.ElevatedButton("Search", bgcolor=ft.Colors.BLUE, width=200, height=40)

        # END OF SEARCH SECTION

        # ERROR
        self.validate_error = ft.SnackBar(
            ft.Text(color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_ACCENT_700)


        # RESULTS SECTION

        #results label
        self.results_label = ft.Text("📧 Parsed Email Results", size=25, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_ACCENT)

        self.table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Subject")),
            ft.DataColumn(ft.Text("From")),
            ft.DataColumn(ft.Text("Date")),
            ft.DataColumn(ft.Text("Body (Preview)")),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(email["Subject"])),
                    ft.DataCell(ft.Text(email["From"])),
                    ft.DataCell(ft.Text(email["Date"])),
                    ft.DataCell(ft.Text(email["Body"][:40] + "...")),
                ]
            )
            for email in RESULTS
        ],
        divider_thickness=2,  # adds space between rows
        heading_row_color=ft.Colors.BLUE,
        column_spacing=20,
    )

        #save button
        self.save_button = ft.ElevatedButton("Save", bgcolor=ft.Colors.GREEN, width=200, height=40)

        # END OF RESULT SECTION

        # BODY

        self.body = ft.Container(
            padding=20,
            content=ft.Column([
                ft.Row([self.email, self.green_circle], alignment=ft.MainAxisAlignment.START),
                ft.Divider(height=10),
                ft.Row([self.specific_sender_label, self.specific_sender], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([self.subject_label, self.subject], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([self.before_a_date_label, self.before_a_date], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([self.since_a_date_label, self.since_a_date], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([self.by_word_label, self.by_word], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=10),
                ft.Row([self.search_button], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Row([self.results_label], alignment=ft.MainAxisAlignment.CENTER),
                self.table,
                ft.Divider(height=10),
                ft.Row([self.save_button], alignment=ft.MainAxisAlignment.CENTER),
            ])
        )

        # CONTENT
        self.controls = [self.body]