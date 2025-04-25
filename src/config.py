# config.py
import os
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

# Environment Variables
API_KEY = os.getenv("API_KEY", "default_api_key")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///default.db")

# File Paths
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
LOG_FILE = os.path.join(os.path.dirname(__file__), "app.log")
