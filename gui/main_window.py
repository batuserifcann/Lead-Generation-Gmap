"""
Main application window for Business Lead Automation System
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import pandas as pd
from datetime import datetime
from datetime import datetime
import os
from typing import List, Dict

from utils.config import config
from utils.logger import get_logger, log_info, log_error, log_warning
from core.excel_manager import ExcelManager
from core.data_models import BusinessData
from core.google_maps_scraper import GoogleMapsScraper
from core.website_detector import WebsiteDetector
from core.whatsapp_automation import WhatsAppAutomation
from core.message_templates import MessageTemplateManager
from utils.validators import InputValidator

class MainWindow:
    """Main application window with tabbed interface"""

    def __init__(self, root):
        self.root = root
        self.logger = get_logger('MainWindow')

        # Initialize variables
        self.is_running = False
        self.current_data = pd.DataFrame()

        # Initialize Excel manager
        self.excel_manager = ExcelManager()

        # Initialize scraper and website detector
        self.scraper = None
        self.scraper_thread = None
        self.website_detector = WebsiteDetector()
        self.website_check_thread = None

        # Initialize WhatsApp automation and message templates
        self.whatsapp = None
        self.whatsapp_thread = None
        self.template_manager = MessageTemplateManager()

        # Initialize filtering
        self.filtered_data = pd.DataFrame()
        self.sort_column = None
        self.sort_reverse = False

        # Configure the main window
        self.setup_window()

        # Create the user interface
        self.setup_ui()

        # Load existing data if available
        self.load_existing_data()

        log_info("Main window initialized successfully")

    def setup_window(self):
        """Configure the main window properties"""
        self.root.title(f"{config.APP_NAME} v{config.APP_VERSION}")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)

        # Center the window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1200x800+{x}+{y}")

        # Configure window closing behavior
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        """Create the main user interface"""
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tabs
        self.create_search_tab()
        self.create_data_tab()
        self.create_messaging_tab()
        self.create_settings_tab()
        self.create_analytics_tab()

        # Create status bar
        self.create_status_bar()

    def create_search_tab(self):
        """Create the business search tab"""
        self.search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="🔍 Business Search")

        # Search Parameters Frame
        params_frame = ttk.LabelFrame(self.search_frame, text="Search Parameters", padding=10)
        params_frame.pack(fill=tk.X, padx=10, pady=5)

        # Industry input
        ttk.Label(params_frame, text="Industry/Business Type:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.industry_var = tk.StringVar(value="construction")
        ttk.Entry(params_frame, textvariable=self.industry_var, width=30).grid(row=0, column=1, padx=5, pady=2)

        # Location input
        ttk.Label(params_frame, text="Location:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.location_var = tk.StringVar(value="İzmir")
        ttk.Entry(params_frame, textvariable=self.location_var, width=30).grid(row=1, column=1, padx=5, pady=2)

        # Search radius
        ttk.Label(params_frame, text="Search Radius (km):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.radius_var = tk.StringVar(value="10")
        ttk.Entry(params_frame, textvariable=self.radius_var, width=30).grid(row=2, column=1, padx=5, pady=2)

        # Max results
        ttk.Label(params_frame, text="Max Results:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.max_results_var = tk.StringVar(value="50")
        ttk.Entry(params_frame, textvariable=self.max_results_var, width=30).grid(row=3, column=1, padx=5, pady=2)

        # Control buttons
        control_frame = ttk.Frame(self.search_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        self.start_search_btn = ttk.Button(control_frame, text="🚀 Start Search", command=self.start_search)
        self.start_search_btn.pack(side=tk.LEFT, padx=5)

        self.stop_search_btn = ttk.Button(control_frame, text="⏹️ Stop Search", command=self.stop_search, state=tk.DISABLED)
        self.stop_search_btn.pack(side=tk.LEFT, padx=5)

        # Progress frame
        progress_frame = ttk.LabelFrame(self.search_frame, text="Progress", padding=10)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)

        self.progress_var = tk.StringVar(value="Ready to start search...")
        ttk.Label(progress_frame, textvariable=self.progress_var).pack(anchor=tk.W)

        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=5)

        # Results preview
        results_frame = ttk.LabelFrame(self.search_frame, text="Search Results Preview", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Treeview for results
        columns = ('Name', 'Address', 'Phone', 'Website Status')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=10)

        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=200)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        h_scrollbar = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_data_tab(self):
        """Create the data review tab"""
        self.data_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.data_frame, text="📊 Data Review")

        # Data management controls
        controls_frame = ttk.Frame(self.data_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(controls_frame, text="📂 Load Excel File", command=self.load_excel_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="💾 Save to Excel", command=self.save_to_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="📤 Export Selected", command=self.export_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="🔄 Refresh Data", command=self.refresh_data_view).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="🌐 Check Websites", command=self.start_website_check).pack(side=tk.LEFT, padx=5)

        # Add filter controls
        filter_frame = ttk.Frame(self.data_frame)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT, padx=5)

        # Industry filter
        ttk.Label(filter_frame, text="Industry:").pack(side=tk.LEFT, padx=(10, 5))
        self.industry_filter_var = tk.StringVar()
        self.industry_filter_combo = ttk.Combobox(filter_frame, textvariable=self.industry_filter_var, width=15)
        self.industry_filter_combo.pack(side=tk.LEFT, padx=5)
        self.industry_filter_combo.bind('<<ComboboxSelected>>', self.apply_filters)

        # Contact status filter
        ttk.Label(filter_frame, text="Status:").pack(side=tk.LEFT, padx=(10, 5))
        self.status_filter_var = tk.StringVar()
        self.status_filter_combo = ttk.Combobox(filter_frame, textvariable=self.status_filter_var, width=15)
        self.status_filter_combo['values'] = ('All', 'Not Contacted', 'Contacted', 'Responded', 'Interested', 'Not Interested')
        self.status_filter_combo.set('All')
        self.status_filter_combo.pack(side=tk.LEFT, padx=5)
        self.status_filter_combo.bind('<<ComboboxSelected>>', self.apply_filters)

        # Website filter
        ttk.Label(filter_frame, text="Website:").pack(side=tk.LEFT, padx=(10, 5))
        self.website_filter_var = tk.StringVar()
        self.website_filter_combo = ttk.Combobox(filter_frame, textvariable=self.website_filter_var, width=15)
        self.website_filter_combo['values'] = ('All', 'Has Website', 'No Website', 'Under Construction')
        self.website_filter_combo.set('All')
        self.website_filter_combo.pack(side=tk.LEFT, padx=5)
        self.website_filter_combo.bind('<<ComboboxSelected>>', self.apply_filters)

        # Search box
        ttk.Label(filter_frame, text="Search:").pack(side=tk.LEFT, padx=(10, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self.apply_filters)

        # Clear filters button
        ttk.Button(filter_frame, text="Clear Filters", command=self.clear_filters).pack(side=tk.LEFT, padx=10)

        # Data table
        data_frame = ttk.LabelFrame(self.data_frame, text="Business Data", padding=10)
        data_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create treeview for data editing
        data_columns = ('Select', 'Name', 'Address', 'Phone', 'Email', 'Website', 'Has Website', 'Contact Status', 'Last Contacted')
        self.data_tree = ttk.Treeview(data_frame, columns=data_columns, show='headings', height=15)

        # Column mapping for sorting
        self.column_mapping = {
            'Name': 'business_name',
            'Address': 'address',
            'Phone': 'phone',
            'Email': 'email',
            'Website': 'website',
            'Has Website': 'has_website',
            'Contact Status': 'contact_status',
            'Last Contacted': 'last_contacted'
        }

        for col in data_columns:
            # Add sorting functionality to column headers
            if col in self.column_mapping:
                self.data_tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(self.column_mapping[c]))
            else:
                self.data_tree.heading(col, text=col)

            if col == 'Select':
                self.data_tree.column(col, width=50)
            elif col in ['Name', 'Address']:
                self.data_tree.column(col, width=150)
            else:
                self.data_tree.column(col, width=100)

        # Scrollbars for data table
        data_v_scrollbar = ttk.Scrollbar(data_frame, orient=tk.VERTICAL, command=self.data_tree.yview)
        data_h_scrollbar = ttk.Scrollbar(data_frame, orient=tk.HORIZONTAL, command=self.data_tree.xview)
        self.data_tree.configure(yscrollcommand=data_v_scrollbar.set, xscrollcommand=data_h_scrollbar.set)

        self.data_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        data_v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        data_h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Statistics frame
        stats_frame = ttk.LabelFrame(self.data_frame, text="Statistics", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)

        self.stats_var = tk.StringVar(value="No data loaded")
        ttk.Label(stats_frame, textvariable=self.stats_var).pack(anchor=tk.W)

    def create_messaging_tab(self):
        """Create the WhatsApp messaging tab"""
        self.messaging_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.messaging_frame, text="💬 WhatsApp Messaging")

        # Messaging controls
        msg_controls_frame = ttk.Frame(self.messaging_frame)
        msg_controls_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(msg_controls_frame, text="📱 Start WhatsApp", command=self.start_whatsapp).pack(side=tk.LEFT, padx=5)
        ttk.Button(msg_controls_frame, text="🚀 Send Messages", command=self.start_messaging).pack(side=tk.LEFT, padx=5)
        ttk.Button(msg_controls_frame, text="⏹️ Stop Messaging", command=self.stop_messaging).pack(side=tk.LEFT, padx=5)

        # Message template frame
        template_frame = ttk.LabelFrame(self.messaging_frame, text="Message Template", padding=10)
        template_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.message_template = tk.Text(template_frame, height=10, wrap=tk.WORD)
        self.message_template.pack(fill=tk.BOTH, expand=True)

        # Default template
        default_template = """Merhaba {business_name},

{location} bölgesinde faaliyet gösteren işletmeniz için profesyonel bir web sitesi hazırlayabiliriz.

Dijital varlığınızı güçlendirerek daha fazla müşteriye ulaşmanıza yardımcı olalım.

Ücretsiz görüşme için mesaj atabilirsiniz.

İyi çalışmalar,
[Your Agency Name]"""

        self.message_template.insert(tk.END, default_template)

        # Messaging progress
        msg_progress_frame = ttk.LabelFrame(self.messaging_frame, text="Messaging Progress", padding=10)
        msg_progress_frame.pack(fill=tk.X, padx=10, pady=5)

        self.msg_progress_var = tk.StringVar(value="Ready to send messages...")
        ttk.Label(msg_progress_frame, textvariable=self.msg_progress_var).pack(anchor=tk.W)

        self.msg_progress_bar = ttk.Progressbar(msg_progress_frame, mode='determinate')
        self.msg_progress_bar.pack(fill=tk.X, pady=5)

    def create_settings_tab(self):
        """Create the settings tab"""
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="⚙️ Settings")

        # Rate limiting settings
        rate_frame = ttk.LabelFrame(self.settings_frame, text="Rate Limiting", padding=10)
        rate_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(rate_frame, text="Delay between messages (seconds):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.message_delay_var = tk.StringVar(value=str(config.DEFAULT_MESSAGE_DELAY))
        ttk.Entry(rate_frame, textvariable=self.message_delay_var, width=10).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(rate_frame, text="Max messages per hour:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.max_messages_hour_var = tk.StringVar(value=str(config.DEFAULT_MAX_MESSAGES_PER_HOUR))
        ttk.Entry(rate_frame, textvariable=self.max_messages_hour_var, width=10).grid(row=1, column=1, padx=5, pady=2)

        # File paths
        paths_frame = ttk.LabelFrame(self.settings_frame, text="File Paths", padding=10)
        paths_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(paths_frame, text="Excel Data File:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.excel_path_var = tk.StringVar(value=config.get_excel_path())
        ttk.Entry(paths_frame, textvariable=self.excel_path_var, width=50).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(paths_frame, text="Browse", command=self.browse_excel_file).grid(row=0, column=2, padx=5, pady=2)

        # Browser settings
        browser_frame = ttk.LabelFrame(self.settings_frame, text="Browser Settings", padding=10)
        browser_frame.pack(fill=tk.X, padx=10, pady=5)

        self.headless_var = tk.BooleanVar(value=config.HEADLESS_BROWSER)
        ttk.Checkbutton(browser_frame, text="Run browser in headless mode", variable=self.headless_var).pack(anchor=tk.W)

        ttk.Label(browser_frame, text="Browser timeout (seconds):").pack(anchor=tk.W, pady=(10, 0))
        self.browser_timeout_var = tk.StringVar(value=str(config.BROWSER_TIMEOUT))
        ttk.Entry(browser_frame, textvariable=self.browser_timeout_var, width=10).pack(anchor=tk.W, pady=2)

    def create_analytics_tab(self):
        """Create the analytics and statistics tab"""
        self.analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_frame, text="📊 Analytics")

        # Refresh button
        refresh_frame = ttk.Frame(self.analytics_frame)
        refresh_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(refresh_frame, text="🔄 Refresh Analytics", command=self.refresh_analytics).pack(side=tk.LEFT)

        # Create main analytics container
        main_container = ttk.Frame(self.analytics_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left column - Summary statistics
        left_frame = ttk.LabelFrame(main_container, text="Summary Statistics", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.summary_text = tk.Text(left_frame, height=15, width=40, wrap=tk.WORD, state=tk.DISABLED)
        summary_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.summary_text.yview)
        self.summary_text.configure(yscrollcommand=summary_scroll.set)

        self.summary_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        summary_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Right column - Detailed breakdowns
        right_frame = ttk.LabelFrame(main_container, text="Detailed Breakdowns", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Industry breakdown
        industry_frame = ttk.LabelFrame(right_frame, text="By Industry", padding=5)
        industry_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        self.industry_tree = ttk.Treeview(industry_frame, columns=('Count', 'Percentage'), show='tree headings', height=6)
        self.industry_tree.heading('#0', text='Industry')
        self.industry_tree.heading('Count', text='Count')
        self.industry_tree.heading('Percentage', text='%')
        self.industry_tree.column('#0', width=120)
        self.industry_tree.column('Count', width=60)
        self.industry_tree.column('Percentage', width=60)
        self.industry_tree.pack(fill=tk.BOTH, expand=True)

        # Location breakdown
        location_frame = ttk.LabelFrame(right_frame, text="By Location", padding=5)
        location_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.location_tree = ttk.Treeview(location_frame, columns=('Count', 'Percentage'), show='tree headings', height=6)
        self.location_tree.heading('#0', text='Location')
        self.location_tree.heading('Count', text='Count')
        self.location_tree.heading('Percentage', text='%')
        self.location_tree.column('#0', width=120)
        self.location_tree.column('Count', width=60)
        self.location_tree.column('Percentage', width=60)
        self.location_tree.pack(fill=tk.BOTH, expand=True)

        # Contact status breakdown
        status_frame = ttk.LabelFrame(right_frame, text="By Contact Status", padding=5)
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        self.status_tree = ttk.Treeview(status_frame, columns=('Count', 'Percentage'), show='tree headings', height=6)
        self.status_tree.heading('#0', text='Status')
        self.status_tree.heading('Count', text='Count')
        self.status_tree.heading('Percentage', text='%')
        self.status_tree.column('#0', width=120)
        self.status_tree.column('Count', width=60)
        self.status_tree.column('Percentage', width=60)
        self.status_tree.pack(fill=tk.BOTH, expand=True)

    def create_status_bar(self):
        """Create the status bar at the bottom of the window"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.status_frame, textvariable=self.status_var).pack(side=tk.LEFT)

        # Add separator
        ttk.Separator(self.status_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Add current time
        self.time_var = tk.StringVar()
        ttk.Label(self.status_frame, textvariable=self.time_var).pack(side=tk.RIGHT)
        self.update_time()

    def update_time(self):
        """Update the time display in the status bar"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_var.set(current_time)
        self.root.after(1000, self.update_time)  # Update every second

    def update_status(self, message):
        """Update the status bar message"""
        self.status_var.set(message)
        log_info(f"Status: {message}")

    # Event handlers (placeholder implementations)
    def start_search(self):
        """Start the business search process"""
        # Validate input parameters
        industry = self.industry_var.get().strip()
        location = self.location_var.get().strip()
        radius = self.radius_var.get().strip()
        max_results = self.max_results_var.get().strip()

        # Validate inputs
        is_valid, errors = InputValidator.validate_search_parameters(
            industry, location, radius, max_results
        )

        if not is_valid:
            error_message = "\n".join(errors)
            messagebox.showerror("Invalid Input", f"Please fix the following errors:\n\n{error_message}")
            return

        # Disable search button and enable stop button
        self.start_search_btn.config(state=tk.DISABLED)
        self.stop_search_btn.config(state=tk.NORMAL)

        # Start progress bar
        self.progress_bar.config(mode='indeterminate')
        self.progress_bar.start()

        # Start search in a separate thread
        self.scraper_thread = threading.Thread(
            target=self._run_search_thread,
            args=(industry, location, int(max_results)),
            daemon=True
        )
        self.scraper_thread.start()

        self.update_status("Starting business search...")
        log_info(f"Started search for {industry} in {location}")

    def _run_search_thread(self, industry: str, location: str, max_results: int):
        """Run the search in a separate thread"""
        try:
            # Create scraper with progress callback
            self.scraper = GoogleMapsScraper(
                headless=self.headless_var.get(),
                progress_callback=self._update_search_progress
            )

            # Perform search
            results = self.scraper.search_businesses(industry, location, max_results)

            # Process results on main thread
            self.root.after(0, self._process_search_results, results, industry, location)

        except Exception as e:
            log_error("Error in search thread", e)
            self.root.after(0, self._handle_search_error, str(e))

    def _update_search_progress(self, message: str):
        """Update search progress (called from scraper thread)"""
        self.root.after(0, lambda: self.progress_var.set(message))

    def _process_search_results(self, results: List[Dict], industry: str, location: str):
        """Process search results on the main thread"""
        try:
            # Clear existing results
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)

            # Add results to Excel and display
            added_count = 0
            for result in results:
                try:
                    # Add industry and location info
                    result['industry'] = industry
                    result['location'] = location

                    # Add to Excel
                    success = self.excel_manager.append_business(result)
                    if success:
                        added_count += 1

                        # Add to results tree
                        values = [
                            result.get('business_name', ''),
                            result.get('address', ''),
                            result.get('phone', ''),
                            "✓" if result.get('has_website', False) else "✗"
                        ]
                        self.results_tree.insert('', 'end', values=values)

                except Exception as e:
                    log_warning(f"Error processing result: {e}")
                    continue

            # Save data
            self.excel_manager.save_data()

            # Refresh data view
            self.refresh_data_view()

            # Update status
            self.progress_var.set(f"Search completed! Found {len(results)} businesses, added {added_count} new records")
            self.update_status(f"Search completed: {added_count} businesses added")

            log_info(f"Search completed: {len(results)} found, {added_count} added")

        except Exception as e:
            log_error("Error processing search results", e)
            self.progress_var.set("Error processing search results")

        finally:
            self._finish_search()

    def _handle_search_error(self, error_message: str):
        """Handle search errors on the main thread"""
        self.progress_var.set(f"Search failed: {error_message}")
        self.update_status("Search failed")
        messagebox.showerror("Search Error", f"Search failed:\n\n{error_message}")
        self._finish_search()

    def _finish_search(self):
        """Clean up after search completion"""
        # Stop progress bar
        self.progress_bar.stop()
        self.progress_bar.config(mode='determinate')

        # Re-enable buttons
        self.start_search_btn.config(state=tk.NORMAL)
        self.stop_search_btn.config(state=tk.DISABLED)

        # Clean up scraper
        if self.scraper:
            self.scraper.close_driver()
            self.scraper = None

    def stop_search(self):
        """Stop the business search process"""
        if self.scraper:
            self.scraper.stop_scraping()

        self.progress_var.set("Stopping search...")
        self.update_status("Search stopped by user")
        log_info("Search stop requested by user")

    def start_website_check(self):
        """Start checking websites for businesses"""
        # Get businesses that need website checking
        businesses_to_check = self.excel_manager.get_businesses_for_website_check()

        if businesses_to_check.empty:
            messagebox.showinfo("No Websites to Check", "No businesses with websites found that need checking.")
            return

        # Confirm with user
        count = len(businesses_to_check)
        if not messagebox.askyesno(
            "Check Websites",
            f"This will check {count} websites. This may take several minutes. Continue?"
        ):
            return

        # Start website checking in a separate thread
        self.website_check_thread = threading.Thread(
            target=self._run_website_check_thread,
            args=(businesses_to_check,),
            daemon=True
        )
        self.website_check_thread.start()

        self.update_status(f"Starting website check for {count} businesses...")
        log_info(f"Started website check for {count} businesses")

    def _run_website_check_thread(self, businesses_df):
        """Run website checking in a separate thread"""
        try:
            # Extract URLs and IDs
            url_to_id = {}
            urls_to_check = []

            for _, business in businesses_df.iterrows():
                website = business.get('website')
                if website and website.strip():
                    urls_to_check.append(website.strip())
                    url_to_id[website.strip()] = business['id']

            if not urls_to_check:
                self.root.after(0, lambda: self.update_status("No valid websites to check"))
                return

            # Check websites with progress callback
            def progress_callback(completed, total, url, status):
                progress_msg = f"Checking websites... {completed}/{total} - {status}"
                self.root.after(0, lambda: self.update_status(progress_msg))

            results = self.website_detector.batch_check_websites(urls_to_check, progress_callback)

            # Update database with results
            updated_count = 0
            for url, result in results.items():
                business_id = url_to_id.get(url)
                if business_id:
                    success = self.excel_manager.update_website_status(business_id, result)
                    if success:
                        updated_count += 1

            # Save changes
            self.excel_manager.save_data()

            # Update GUI on main thread
            self.root.after(0, self._finish_website_check, updated_count, len(results))

        except Exception as e:
            log_error("Error in website check thread", e)
            self.root.after(0, lambda: self._handle_website_check_error(str(e)))

    def _finish_website_check(self, updated_count: int, total_checked: int):
        """Finish website checking on main thread"""
        # Refresh data view
        self.refresh_data_view()

        # Update status
        self.update_status(f"Website check completed: {updated_count}/{total_checked} updated")

        # Show completion message
        messagebox.showinfo(
            "Website Check Complete",
            f"Checked {total_checked} websites.\nUpdated {updated_count} business records."
        )

        log_info(f"Website check completed: {updated_count}/{total_checked} updated")

    def _handle_website_check_error(self, error_message: str):
        """Handle website check errors on main thread"""
        self.update_status("Website check failed")
        messagebox.showerror("Website Check Error", f"Website check failed:\n\n{error_message}")
        log_error(f"Website check failed: {error_message}")

    def load_excel_file(self):
        """Load data from an Excel file"""
        filename = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )

        if filename:
            try:
                # Create new Excel manager with selected file
                temp_manager = ExcelManager(filename)
                success = temp_manager.load_data()

                if success:
                    self.excel_manager = temp_manager
                    self.current_data = self.excel_manager.data.copy()
                    self.refresh_data_view()
                    self.update_status(f"Loaded {len(self.current_data)} records from {filename}")
                    messagebox.showinfo("Success", f"Successfully loaded {len(self.current_data)} records")
                else:
                    messagebox.showerror("Error", "Failed to load Excel file")

            except Exception as e:
                log_error(f"Error loading Excel file: {filename}", e)
                messagebox.showerror("Error", f"Error loading file: {str(e)}")
        else:
            self.update_status("File selection cancelled")

    def save_to_excel(self):
        """Save current data to Excel file"""
        try:
            success = self.excel_manager.save_data()

            if success:
                self.update_status(f"Saved {len(self.excel_manager.data)} records to Excel file")
                messagebox.showinfo("Success", "Data saved successfully")
            else:
                messagebox.showerror("Error", "Failed to save data to Excel file")

        except Exception as e:
            log_error("Error saving Excel file", e)
            messagebox.showerror("Error", f"Error saving file: {str(e)}")

    def export_selected(self):
        """Export selected data to a new file"""
        self.update_status("Export functionality not yet implemented")
        log_warning("export_selected called but not yet implemented")

    def refresh_data_view(self):
        """Refresh the data view"""
        try:
            # Clear existing data in the tree
            for item in self.data_tree.get_children():
                self.data_tree.delete(item)

            # Use filtered data if available, otherwise use all data
            data_to_display = self.filtered_data if not self.filtered_data.empty else self.excel_manager.data

            # Populate with current data
            if not data_to_display.empty:
                for index, row in data_to_display.iterrows():
                    values = [
                        "☐",  # Select checkbox placeholder
                        row.get('business_name', ''),
                        row.get('address', ''),
                        row.get('phone', ''),
                        row.get('email', ''),
                        row.get('website', ''),
                        "✓" if row.get('has_website', False) else "✗",
                        row.get('contact_status', ''),
                        row.get('last_contacted', '')
                    ]
                    self.data_tree.insert('', 'end', values=values)

            # Update statistics (use all data for stats, not filtered)
            stats = self.excel_manager.get_statistics()
            filtered_count = len(data_to_display)
            total_count = stats['total_businesses']

            if filtered_count < total_count:
                stats_text = f"Showing: {filtered_count}/{total_count} | Contacted: {stats['contacted']} | Not Contacted: {stats['not_contacted']} | With Websites: {stats['with_websites']} | Without Websites: {stats['without_websites']}"
            else:
                stats_text = f"Total: {stats['total_businesses']} | Contacted: {stats['contacted']} | Not Contacted: {stats['not_contacted']} | With Websites: {stats['with_websites']} | Without Websites: {stats['without_websites']}"

            self.stats_var.set(stats_text)

            # Update filter options
            self.update_filter_options()

            self.update_status("Data view refreshed")
            log_info("Data view refreshed")

        except Exception as e:
            log_error("Error refreshing data view", e)
            self.update_status("Error refreshing data view")

    def start_whatsapp(self):
        """Start WhatsApp Web automation"""
        try:
            if self.whatsapp and self.whatsapp.is_logged_in:
                messagebox.showinfo("Already Connected", "WhatsApp Web is already connected and ready.")
                return

            # Create WhatsApp automation instance
            self.whatsapp = WhatsAppAutomation(
                headless=False,  # WhatsApp Web needs to be visible for QR scanning
                progress_callback=self._update_whatsapp_progress
            )

            # Start WhatsApp session in a separate thread
            self.whatsapp_thread = threading.Thread(
                target=self._start_whatsapp_thread,
                daemon=True
            )
            self.whatsapp_thread.start()

            self.update_status("Starting WhatsApp Web...")
            log_info("Starting WhatsApp Web session")

        except Exception as e:
            log_error("Error starting WhatsApp Web", e)
            messagebox.showerror("WhatsApp Error", f"Failed to start WhatsApp Web:\n\n{str(e)}")

    def _start_whatsapp_thread(self):
        """Start WhatsApp Web in a separate thread"""
        try:
            success = self.whatsapp.start_whatsapp_session()

            if success:
                self.root.after(0, lambda: self._whatsapp_session_ready())
            else:
                self.root.after(0, lambda: self._whatsapp_session_failed())

        except Exception as e:
            log_error("Error in WhatsApp thread", e)
            self.root.after(0, lambda: self._whatsapp_session_failed(str(e)))

    def _update_whatsapp_progress(self, message: str):
        """Update WhatsApp progress (called from WhatsApp thread)"""
        self.root.after(0, lambda: self.msg_progress_var.set(message))

    def _whatsapp_session_ready(self):
        """Handle WhatsApp session ready on main thread"""
        self.msg_progress_var.set("WhatsApp Web connected and ready!")
        self.update_status("WhatsApp Web ready for messaging")
        messagebox.showinfo("WhatsApp Ready", "WhatsApp Web is connected and ready for messaging!")
        log_info("WhatsApp Web session ready")

    def _whatsapp_session_failed(self, error: str = None):
        """Handle WhatsApp session failure on main thread"""
        error_msg = f"Failed to connect to WhatsApp Web"
        if error:
            error_msg += f": {error}"

        self.msg_progress_var.set(error_msg)
        self.update_status("WhatsApp Web connection failed")
        messagebox.showerror("WhatsApp Error", error_msg)
        log_error("WhatsApp Web session failed")

    def start_messaging(self):
        """Start sending messages"""
        if not self.whatsapp or not self.whatsapp.is_logged_in:
            messagebox.showerror("Not Connected", "Please connect to WhatsApp Web first.")
            return

        # Get businesses without websites (potential targets)
        target_businesses = self.excel_manager.get_businesses_without_websites()

        if target_businesses.empty:
            messagebox.showinfo("No Targets", "No businesses without websites found to message.")
            return

        # Get message template
        template_content = self.message_template.get("1.0", tk.END).strip()
        if not template_content:
            messagebox.showerror("No Template", "Please enter a message template.")
            return

        # Validate template
        is_valid, errors = self.template_manager.validate_template(template_content)
        if not is_valid:
            error_message = "\n".join(errors)
            messagebox.showerror("Invalid Template", f"Template validation failed:\n\n{error_message}")
            return

        # Confirm with user
        count = len(target_businesses)
        if not messagebox.askyesno(
            "Start Messaging",
            f"This will send messages to {count} businesses. Continue?"
        ):
            return

        # Prepare recipients
        recipients = []
        for _, business in target_businesses.iterrows():
            if business.get('phone'):
                personalized_message = self.template_manager.personalize_message_content(
                    template_content, business.to_dict()
                )

                recipients.append({
                    'phone': business['phone'],
                    'message': personalized_message,
                    'business_name': business.get('business_name', 'Unknown'),
                    'business_id': business['id']
                })

        if not recipients:
            messagebox.showinfo("No Recipients", "No businesses with phone numbers found.")
            return

        # Start messaging in a separate thread
        self.whatsapp_thread = threading.Thread(
            target=self._run_messaging_thread,
            args=(recipients,),
            daemon=True
        )
        self.whatsapp_thread.start()

        self.update_status(f"Starting to send messages to {len(recipients)} businesses...")
        log_info(f"Started messaging to {len(recipients)} businesses")

    def _run_messaging_thread(self, recipients):
        """Run messaging in a separate thread"""
        try:
            def progress_callback(current, total, result):
                progress_msg = f"Sending messages... {current}/{total} - {result['status']}"
                self.root.after(0, lambda: self.msg_progress_var.set(progress_msg))

            # Send bulk messages
            results = self.whatsapp.send_bulk_messages(recipients, progress_callback)

            # Update database with results
            self._update_contact_status_from_results(results)

            # Process results on main thread
            self.root.after(0, self._finish_messaging, results)

        except Exception as e:
            log_error("Error in messaging thread", e)
            self.root.after(0, lambda: self._handle_messaging_error(str(e)))

    def _update_contact_status_from_results(self, results):
        """Update contact status in database based on messaging results"""
        for result in results:
            business_id = result.get('business_id')
            if business_id:
                if result['success']:
                    status = 'Contacted'
                    notes = f"WhatsApp message sent successfully"
                else:
                    status = 'Contact Failed'
                    notes = f"WhatsApp message failed: {result.get('error', 'Unknown error')}"

                self.excel_manager.update_contact_status(business_id, status, notes)

        # Save changes
        self.excel_manager.save_data()

    def _finish_messaging(self, results):
        """Finish messaging on main thread"""
        successful = sum(1 for r in results if r['success'])
        total = len(results)

        # Refresh data view
        self.refresh_data_view()

        # Update progress
        self.msg_progress_var.set(f"Messaging completed: {successful}/{total} sent successfully")
        self.update_status(f"Messaging completed: {successful}/{total} messages sent")

        # Show completion message
        messagebox.showinfo(
            "Messaging Complete",
            f"Sent {successful} out of {total} messages successfully."
        )

        log_info(f"Messaging completed: {successful}/{total} messages sent")

    def _handle_messaging_error(self, error_message: str):
        """Handle messaging errors on main thread"""
        self.msg_progress_var.set("Messaging failed")
        self.update_status("Messaging failed")
        messagebox.showerror("Messaging Error", f"Messaging failed:\n\n{error_message}")
        log_error(f"Messaging failed: {error_message}")

    def stop_messaging(self):
        """Stop sending messages"""
        if self.whatsapp:
            self.whatsapp.stop_messaging()

        self.msg_progress_var.set("Stopping messaging...")
        self.update_status("Messaging stopped by user")
        log_info("Messaging stop requested by user")

    def browse_excel_file(self):
        """Browse for Excel file location"""
        filename = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if filename:
            self.excel_path_var.set(filename)
            self.update_status(f"Excel file path updated: {filename}")

    def load_existing_data(self):
        """Load existing data if available"""
        try:
            success = self.excel_manager.load_data()
            if success:
                self.current_data = self.excel_manager.data.copy()
                self.refresh_data_view()

                if len(self.excel_manager.data) > 0:
                    self.update_status(f"Loaded {len(self.excel_manager.data)} existing records")
                    log_info(f"Loaded {len(self.excel_manager.data)} existing records from Excel file")
                else:
                    self.update_status("Excel file created - ready to add data")
                    log_info("New Excel file created")
            else:
                self.update_status("Error loading existing data")
                log_error("Failed to load existing Excel data")
        except Exception as e:
            log_error("Error loading existing data", e)
            self.update_status("Error loading existing data")

    def on_closing(self):
        """Handle window closing event"""
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            log_info("Application closing by user request")

            # Clean up WhatsApp session
            if self.whatsapp:
                try:
                    self.whatsapp.close_session()
                except Exception as e:
                    log_error("Error closing WhatsApp session", e)

            self.root.destroy()

    def apply_filters(self, event=None):
        """Apply filters to the data table"""
        try:
            # Start with all data
            filtered_data = self.excel_manager.data.copy()

            if filtered_data.empty:
                self.filtered_data = filtered_data
                self.refresh_data_view()
                return

            # Apply industry filter
            industry_filter = self.industry_filter_var.get()
            if industry_filter and industry_filter != 'All':
                filtered_data = filtered_data[filtered_data['industry'] == industry_filter]

            # Apply contact status filter
            status_filter = self.status_filter_var.get()
            if status_filter and status_filter != 'All':
                filtered_data = filtered_data[filtered_data['contact_status'] == status_filter]

            # Apply website filter
            website_filter = self.website_filter_var.get()
            if website_filter and website_filter != 'All':
                if website_filter == 'Has Website':
                    filtered_data = filtered_data[filtered_data['has_website'] == True]
                elif website_filter == 'No Website':
                    filtered_data = filtered_data[filtered_data['has_website'] == False]
                elif website_filter == 'Under Construction':
                    filtered_data = filtered_data[filtered_data['website_status'] == 'Under Construction']

            # Apply search filter
            search_term = self.search_var.get().strip().lower()
            if search_term:
                search_mask = (
                    filtered_data['business_name'].str.lower().str.contains(search_term, na=False) |
                    filtered_data['address'].str.lower().str.contains(search_term, na=False) |
                    filtered_data['industry'].str.lower().str.contains(search_term, na=False) |
                    filtered_data['location'].str.lower().str.contains(search_term, na=False)
                )
                filtered_data = filtered_data[search_mask]

            # Apply sorting if set
            if self.sort_column and self.sort_column in filtered_data.columns:
                filtered_data = filtered_data.sort_values(
                    by=self.sort_column,
                    ascending=not self.sort_reverse,
                    na_position='last'
                )

            self.filtered_data = filtered_data
            self.refresh_data_view()

        except Exception as e:
            log_error("Error applying filters", e)

    def clear_filters(self):
        """Clear all filters"""
        self.industry_filter_var.set('')
        self.status_filter_var.set('All')
        self.website_filter_var.set('All')
        self.search_var.set('')
        self.sort_column = None
        self.sort_reverse = False
        self.apply_filters()

    def sort_by_column(self, column: str):
        """Sort data by column"""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        self.apply_filters()

    def update_filter_options(self):
        """Update filter dropdown options based on current data"""
        try:
            if not self.excel_manager.data.empty:
                # Update industry filter options
                industries = ['All'] + sorted(self.excel_manager.data['industry'].dropna().unique().tolist())
                self.industry_filter_combo['values'] = industries

                # Set current value if it's still valid
                current_industry = self.industry_filter_var.get()
                if current_industry not in industries:
                    self.industry_filter_var.set('All')

        except Exception as e:
            log_error("Error updating filter options", e)

    def refresh_analytics(self):
        """Refresh the analytics dashboard"""
        try:
            stats = self.excel_manager.get_statistics()

            # Update summary statistics
            self.summary_text.config(state=tk.NORMAL)
            self.summary_text.delete(1.0, tk.END)

            summary_content = f"""📊 BUSINESS LEAD ANALYTICS
{'='*40}

📈 OVERVIEW
Total Businesses: {stats['total_businesses']}
Contacted: {stats['contacted']}
Not Contacted: {stats['not_contacted']}
Response Rate: {(stats['contacted']/max(stats['total_businesses'], 1)*100):.1f}%

🌐 WEBSITE STATUS
With Websites: {stats['with_websites']}
Without Websites: {stats['without_websites']}
Website Coverage: {(stats['with_websites']/max(stats['total_businesses'], 1)*100):.1f}%

📞 CONTACT ANALYSIS
Contact Success Rate: {(stats['contacted']/max(stats['total_businesses'], 1)*100):.1f}%
Remaining Prospects: {stats['not_contacted']}

📊 DATA QUALITY
Complete Records: {self._count_complete_records()}
Missing Phone Numbers: {self._count_missing_phones()}
Missing Emails: {self._count_missing_emails()}

🎯 TARGETING OPPORTUNITIES
Businesses without websites: {stats['without_websites']}
Uncontacted with phones: {self._count_uncontacted_with_phones()}
High-value prospects: {self._count_high_value_prospects()}

📅 LAST UPDATED
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            self.summary_text.insert(1.0, summary_content)
            self.summary_text.config(state=tk.DISABLED)

            # Update industry breakdown
            self._update_breakdown_tree(self.industry_tree, stats['by_industry'], stats['total_businesses'])

            # Update location breakdown
            self._update_breakdown_tree(self.location_tree, stats['by_location'], stats['total_businesses'])

            # Update contact status breakdown
            self._update_breakdown_tree(self.status_tree, stats['by_contact_status'], stats['total_businesses'])

            self.update_status("Analytics refreshed")
            log_info("Analytics dashboard refreshed")

        except Exception as e:
            log_error("Error refreshing analytics", e)
            self.update_status("Error refreshing analytics")

    def _update_breakdown_tree(self, tree, data_dict, total):
        """Update a breakdown tree with data"""
        try:
            # Clear existing items
            for item in tree.get_children():
                tree.delete(item)

            # Sort by count (descending)
            sorted_items = sorted(data_dict.items(), key=lambda x: x[1], reverse=True)

            for category, count in sorted_items:
                if count > 0:  # Only show categories with data
                    percentage = (count / max(total, 1)) * 100
                    tree.insert('', 'end', text=category or 'Unknown',
                               values=(count, f"{percentage:.1f}%"))

        except Exception as e:
            log_error("Error updating breakdown tree", e)

    def _count_complete_records(self) -> int:
        """Count records with all essential fields"""
        try:
            if self.excel_manager.data.empty:
                return 0

            complete_mask = (
                self.excel_manager.data['business_name'].notna() &
                self.excel_manager.data['phone'].notna() &
                self.excel_manager.data['address'].notna()
            )
            return complete_mask.sum()
        except:
            return 0

    def _count_missing_phones(self) -> int:
        """Count records missing phone numbers"""
        try:
            if self.excel_manager.data.empty:
                return 0
            return self.excel_manager.data['phone'].isna().sum()
        except:
            return 0

    def _count_missing_emails(self) -> int:
        """Count records missing email addresses"""
        try:
            if self.excel_manager.data.empty:
                return 0
            return self.excel_manager.data['email'].isna().sum()
        except:
            return 0

    def _count_uncontacted_with_phones(self) -> int:
        """Count uncontacted businesses with phone numbers"""
        try:
            if self.excel_manager.data.empty:
                return 0

            mask = (
                (self.excel_manager.data['contact_status'] == 'Not Contacted') &
                self.excel_manager.data['phone'].notna()
            )
            return mask.sum()
        except:
            return 0

    def _count_high_value_prospects(self) -> int:
        """Count high-value prospects (uncontacted, no website, has phone)"""
        try:
            if self.excel_manager.data.empty:
                return 0

            mask = (
                (self.excel_manager.data['contact_status'] == 'Not Contacted') &
                (self.excel_manager.data['has_website'] == False) &
                self.excel_manager.data['phone'].notna()
            )
            return mask.sum()
        except:
            return 0