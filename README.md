# Emailparser app

📧 Email Parser App (Built with Flet + IMAPClient)
A clean, fast, and user-friendly email parsing tool built with the Flet framework. This app allows users to log in with their Gmail account, filter emails using multiple criteria, preview them, and take further actions like exporting or deleting—all from a sleek cross-platform interface.

🔑 Key Features:
Login System: Secure sign-in using Gmail credentials.

Smart Filtering: Search emails by:

Sender

Subject

Keywords

Date range (since/before)

Email Preview: Instantly view filtered results inside the app.

CSV Export: Save selected emails to a downloadable CSV file.

Bin Function: Bulk move found emails to trash directly.

Gmail Supported (Yahoo support coming soon!)

Cross-platform: Works on desktop, mobile, and web.

💡 Built With:
Flet for frontend (Flutter-like UI in Python)

IMAPClient for secure and reliable email communication


## Run the app

### uv

Run as a desktop app:

```
uv run flet run
```

Run as a web app:

```
uv run flet run --web
```

### Poetry

Install dependencies from `pyproject.toml`:

```
poetry install
```

Run as a desktop app:

```
poetry run flet run
```

Run as a web app:

```
poetry run flet run --web
```

For more details on running the app, refer to the [Getting Started Guide](https://flet.dev/docs/getting-started/).

## Build the app

### Android

```
flet build apk -v
```

For more details on building and signing `.apk` or `.aab`, refer to the [Android Packaging Guide](https://flet.dev/docs/publish/android/).

### iOS


```
flet build ipa -v
```

For more details on building and signing `.ipa`, refer to the [iOS Packaging Guide](https://flet.dev/docs/publish/ios/).

### macOS

```
flet build macos -v
```

For more details on building macOS package, refer to the [macOS Packaging Guide](https://flet.dev/docs/publish/macos/).

### Linux

```
flet build linux -v
```

For more details on building Linux package, refer to the [Linux Packaging Guide](https://flet.dev/docs/publish/linux/).

### Windows

```
flet build windows -v
```

For more details on building Windows package, refer to the [Windows Packaging Guide](https://flet.dev/docs/publish/windows/).