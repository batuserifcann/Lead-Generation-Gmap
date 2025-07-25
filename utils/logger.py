"""
Logging configuration for Business Lead Automation System
"""
import logging
import logging.handlers
from pathlib import Path
from .config import config

class Logger:
    """Logger class to manage application logging"""

    def __init__(self):
        self.logger = None
        self._setup_logger()

    def _setup_logger(self):
        """Setup the main application logger"""
        # Create logger
        self.logger = logging.getLogger(config.APP_NAME)
        self.logger.setLevel(getattr(logging, config.LOG_LEVEL.upper()))

        # Prevent duplicate handlers
        if self.logger.handlers:
            return

        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )

        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            config.get_log_path(),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO if not config.DEBUG else logging.DEBUG)
        console_handler.setFormatter(simple_formatter)

        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get_logger(self, name=None):
        """Get a logger instance"""
        if name:
            return logging.getLogger(f"{config.APP_NAME}.{name}")
        return self.logger

    def log_error(self, message, exception=None):
        """Log an error with optional exception details"""
        if exception:
            self.logger.error(f"{message}: {str(exception)}", exc_info=True)
        else:
            self.logger.error(message)

    def log_info(self, message):
        """Log an info message"""
        self.logger.info(message)

    def log_warning(self, message):
        """Log a warning message"""
        self.logger.warning(message)

    def log_debug(self, message):
        """Log a debug message"""
        self.logger.debug(message)

# Global logger instance
app_logger = Logger()

# Convenience functions
def get_logger(name=None):
    """Get a logger instance"""
    return app_logger.get_logger(name)

def log_error(message, exception=None):
    """Log an error"""
    app_logger.log_error(message, exception)

def log_info(message):
    """Log info"""
    app_logger.log_info(message)

def log_warning(message):
    """Log warning"""
    app_logger.log_warning(message)

def log_debug(message):
    """Log debug"""
    app_logger.log_debug(message)