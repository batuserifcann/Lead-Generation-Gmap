"""
Configuration management for Business Lead Automation System
"""
import os
from dotenv import load_dotenv
from pathlib import Path

class Config:
    """Configuration class to manage application settings"""

    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        # Application Settings
        self.APP_NAME = os.getenv('APP_NAME', 'Business Lead Automation')
        self.APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
        self.DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

        # File Paths
        self.DATA_DIR = Path(os.getenv('DATA_DIR', 'data'))
        self.EXCEL_FILE = Path(os.getenv('EXCEL_FILE', 'data/leads.xlsx'))
        self.TEMPLATES_FILE = Path(os.getenv('TEMPLATES_FILE', 'data/templates.json'))
        self.SETTINGS_FILE = Path(os.getenv('SETTINGS_FILE', 'data/settings.json'))
        self.LOG_FILE = Path(os.getenv('LOG_FILE', 'data/logs/app.log'))

        # Rate Limiting Settings
        self.DEFAULT_MESSAGE_DELAY = int(os.getenv('DEFAULT_MESSAGE_DELAY', '30'))
        self.DEFAULT_MAX_MESSAGES_PER_HOUR = int(os.getenv('DEFAULT_MAX_MESSAGES_PER_HOUR', '20'))
        self.DEFAULT_SEARCH_DELAY = int(os.getenv('DEFAULT_SEARCH_DELAY', '2'))

        # Browser Settings
        self.HEADLESS_BROWSER = os.getenv('HEADLESS_BROWSER', 'True').lower() == 'true'
        self.BROWSER_TIMEOUT = int(os.getenv('BROWSER_TIMEOUT', '30'))

        # Logging Settings
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

        # Ensure directories exist
        self._create_directories()

    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.DATA_DIR,
            self.LOG_FILE.parent,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def get_excel_path(self):
        """Get the full path to the Excel file"""
        return str(self.EXCEL_FILE.absolute())

    def get_log_path(self):
        """Get the full path to the log file"""
        return str(self.LOG_FILE.absolute())

    def get_templates_path(self):
        """Get the full path to the templates file"""
        return str(self.TEMPLATES_FILE.absolute())

    def get_settings_path(self):
        """Get the full path to the settings file"""
        return str(self.SETTINGS_FILE.absolute())

# Global configuration instance
config = Config()