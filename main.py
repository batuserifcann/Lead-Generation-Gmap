#!/usr/bin/env python3
"""
Business Lead Automation System
Main application entry point
"""
import sys
import tkinter as tk
from tkinter import messagebox
import traceback

# Import configuration and logging
from utils.config import config
from utils.logger import log_info, log_error, get_logger

def main():
    """Main application entry point"""
    logger = get_logger('main')

    try:
        log_info(f"Starting {config.APP_NAME} v{config.APP_VERSION}")

        # Create the main Tkinter root window
        root = tk.Tk()
        root.withdraw()  # Hide the root window initially

        # Import and create the main application window
        try:
            from gui.main_window import MainWindow
            app = MainWindow(root)
            log_info("Main application window created successfully")
        except ImportError as e:
            log_error("Failed to import main window", e)
            messagebox.showerror(
                "Import Error",
                f"Failed to load the main application window.\n\nError: {str(e)}\n\nPlease ensure all required modules are installed."
            )
            return 1

        # Show the root window and start the main loop
        root.deiconify()
        log_info("Starting GUI main loop")
        root.mainloop()

        log_info("Application closed normally")
        return 0

    except Exception as e:
        error_msg = f"Unexpected error in main application: {str(e)}"
        log_error(error_msg, e)

        # Show error dialog if possible
        try:
            messagebox.showerror(
                "Application Error",
                f"An unexpected error occurred:\n\n{str(e)}\n\nCheck the log file for more details."
            )
        except:
            # If we can't show a dialog, print to console
            print(f"FATAL ERROR: {error_msg}")
            traceback.print_exc()

        return 1

def setup_exception_handler():
    """Setup global exception handler for unhandled exceptions"""
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Allow Ctrl+C to work normally
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        error_msg = f"Unhandled exception: {exc_type.__name__}: {exc_value}"
        log_error(error_msg)

        # Log the full traceback
        logger = get_logger('exception_handler')
        logger.error("Full traceback:", exc_info=(exc_type, exc_value, exc_traceback))

        # Show error dialog
        try:
            messagebox.showerror(
                "Unhandled Error",
                f"An unhandled error occurred:\n\n{exc_type.__name__}: {exc_value}\n\nThe application will continue running, but some features may not work correctly.\n\nCheck the log file for more details."
            )
        except:
            print(f"UNHANDLED ERROR: {error_msg}")

    sys.excepthook = handle_exception

if __name__ == "__main__":
    # Setup global exception handling
    setup_exception_handler()

    # Run the main application
    exit_code = main()
    sys.exit(exit_code)