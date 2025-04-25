# config.py
from dotenv import load_dotenv
import flet as ft

# Load environment variables from a .env file
load_dotenv()

# Application Metadata
APP_NAME = "My Flet App"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "A sample Flet application."

# UI Settings
WINDOW_WIDTH = 650
WINDOW_HEIGHT = 1100
THEME_MODE = ft.ThemeMode.LIGHT  # Options: LIGHT or DARK

