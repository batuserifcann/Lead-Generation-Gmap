"""
WhatsApp Web Automation for Business Lead Automation System
Handles automated messaging through WhatsApp Web interface
"""
import time
import random
from typing import Dict, List, Optional, Callable, Any
import re
from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from utils.config import config
from utils.logger import get_logger, log_info, log_error, log_warning
from core.rate_limiter import RateLimiter

class WhatsAppAutomation:
    """Automates WhatsApp Web messaging"""

    def __init__(self, headless: bool = False, progress_callback: Optional[Callable] = None):
        self.logger = get_logger('WhatsAppAutomation')
        self.driver = None
        self.headless = headless  # WhatsApp Web usually requires non-headless mode for QR scanning
        self.progress_callback = progress_callback
        self.is_running = False
        self.is_logged_in = False

        # Rate limiter
        self.rate_limiter = RateLimiter(
            max_per_hour=config.DEFAULT_MAX_MESSAGES_PER_HOUR,
            delay_between=config.DEFAULT_MESSAGE_DELAY
        )

        # WhatsApp Web selectors (may need updates if WhatsApp changes their interface)
        self.selectors = {
            'qr_code': '[data-testid="qr-code"]',
            'search_box': '[data-testid="chat-list-search"]',
            'message_box': '[data-testid="conversation-compose-box-input"]',
            'send_button': '[data-testid="compose-btn-send"]',
            'chat_list': '[data-testid="chat-list"]',
            'message_status': '[data-testid="msg-check"]',
            'new_chat_button': '[data-testid="new-chat-button"]',
            'contact_search': '[data-testid="contact-search-input"]'
        }

        log_info("WhatsAppAutomation initialized")

    def initialize_driver(self) -> bool:
        """Initialize Chrome WebDriver for WhatsApp Web"""
        try:
            chrome_options = Options()

            # WhatsApp Web specific options
            if self.headless:
                log_warning("WhatsApp Web may not work properly in headless mode")
                chrome_options.add_argument('--headless')

            # Basic options
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            # User agent
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            # Window size
            chrome_options.add_argument('--window-size=1200,800')

            # Disable notifications
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0
            }
            chrome_options.add_experimental_option("prefs", prefs)

            # Initialize driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            # Set timeouts
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(60)

            log_info("Chrome WebDriver initialized for WhatsApp Web")
            return True

        except Exception as e:
            log_error("Failed to initialize Chrome WebDriver for WhatsApp", e)
            return False

    def start_whatsapp_session(self) -> bool:
        """Start WhatsApp Web session and wait for QR code scan"""
        if not self.initialize_driver():
            return False

        try:
            log_info("Opening WhatsApp Web...")
            if self.progress_callback:
                self.progress_callback("Opening WhatsApp Web...")

            # Navigate to WhatsApp Web
            self.driver.get("https://web.whatsapp.com")

            # Wait for QR code or main interface
            if self.progress_callback:
                self.progress_callback("Waiting for QR code scan...")

            success = self.wait_for_qr_scan()

            if success:
                self.is_logged_in = True
                log_info("WhatsApp Web session started successfully")
                if self.progress_callback:
                    self.progress_callback("WhatsApp Web ready for messaging")
                return True
            else:
                log_error("Failed to establish WhatsApp Web session")
                return False

        except Exception as e:
            log_error("Error starting WhatsApp Web session", e)
            return False

    def wait_for_qr_scan(self, timeout: int = 120) -> bool:
        """Wait for user to scan QR code"""
        try:
            # Check if already logged in
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['search_box']))
                )
                log_info("Already logged in to WhatsApp Web")
                return True
            except TimeoutException:
                pass

            # Wait for QR code to appear
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['qr_code']))
                )
                log_info("QR code displayed - waiting for scan")
                if self.progress_callback:
                    self.progress_callback("Please scan the QR code with your phone...")
            except TimeoutException:
                log_warning("QR code not found - may already be logged in")

            # Wait for successful login (search box appears)
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['search_box']))
            )

            # Additional wait for interface to fully load
            time.sleep(3)

            log_info("Successfully logged in to WhatsApp Web")
            return True

        except TimeoutException:
            log_error(f"Timeout waiting for QR code scan ({timeout}s)")
            if self.progress_callback:
                self.progress_callback("Timeout waiting for QR code scan")
            return False
        except Exception as e:
            log_error("Error waiting for QR code scan", e)
            return False

    def send_message(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Send a message to a phone number"""
        if not self.is_logged_in:
            return {
                'success': False,
                'error': 'Not logged in to WhatsApp Web',
                'status': 'Not Logged In'
            }

        # Check rate limiting
        if not self.rate_limiter.can_send_message():
            wait_time = self.rate_limiter.get_next_available_time()
            return {
                'success': False,
                'error': f'Rate limit exceeded. Wait {wait_time} seconds',
                'status': 'Rate Limited',
                'wait_time': wait_time
            }

        try:
            # Clean phone number
            clean_phone = self._clean_phone_number(phone_number)
            if not clean_phone:
                return {
                    'success': False,
                    'error': 'Invalid phone number format',
                    'status': 'Invalid Phone'
                }

            log_info(f"Sending message to {clean_phone}")
            if self.progress_callback:
                self.progress_callback(f"Sending message to {clean_phone}...")

            # Open chat using WhatsApp Web URL
            chat_url = f"https://web.whatsapp.com/send?phone={clean_phone}&text={quote(message)}"
            self.driver.get(chat_url)

            # Wait for chat to load
            time.sleep(3)

            # Check if chat opened successfully
            try:
                # Wait for message box to appear
                message_box = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['message_box']))
                )

                # Clear any existing text and type message
                message_box.clear()
                time.sleep(1)
                message_box.send_keys(message)
                time.sleep(1)

                # Send message
                send_button = self.driver.find_element(By.CSS_SELECTOR, self.selectors['send_button'])
                send_button.click()

                # Wait a moment for message to be sent
                time.sleep(2)

                # Record successful send
                self.rate_limiter.record_message_sent()

                log_info(f"Message sent successfully to {clean_phone}")
                return {
                    'success': True,
                    'status': 'Sent',
                    'phone': clean_phone,
                    'timestamp': time.time()
                }

            except TimeoutException:
                # Check if it's an invalid number error
                try:
                    error_element = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Phone number shared via url is invalid')]")
                    return {
                        'success': False,
                        'error': 'Invalid phone number',
                        'status': 'Invalid Phone',
                        'phone': clean_phone
                    }
                except NoSuchElementException:
                    return {
                        'success': False,
                        'error': 'Chat failed to load',
                        'status': 'Chat Load Failed',
                        'phone': clean_phone
                    }

        except Exception as e:
            log_error(f"Error sending message to {phone_number}", e)
            return {
                'success': False,
                'error': str(e),
                'status': 'Error',
                'phone': phone_number
            }

    def _clean_phone_number(self, phone: str) -> str:
        """Clean and format phone number for WhatsApp"""
        if not phone:
            return ""

        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)

        # Handle Turkish phone numbers
        if cleaned.startswith('0'):
            cleaned = '90' + cleaned[1:]
        elif cleaned.startswith('+90'):
            cleaned = cleaned[1:]
        elif cleaned.startswith('90') and len(cleaned) == 12:
            pass  # Already in correct format
        elif not cleaned.startswith('90'):
            # Assume Turkish number if no country code
            if len(cleaned) == 10:
                cleaned = '90' + cleaned

        return cleaned



    def send_bulk_messages(self, recipients: List[Dict[str, str]], progress_callback: Optional[Callable] = None) -> List[Dict[str, Any]]:
        """Send messages to multiple recipients"""
        if not self.is_logged_in:
            log_error("Not logged in to WhatsApp Web")
            return []

        results = []
        self.is_running = True

        log_info(f"Starting bulk message sending to {len(recipients)} recipients")

        for i, recipient in enumerate(recipients):
            if not self.is_running:
                log_info("Bulk messaging stopped by user")
                break

            phone = recipient.get('phone', '')
            message = recipient.get('message', '')
            business_name = recipient.get('business_name', 'Unknown')

            if not phone or not message:
                log_warning(f"Skipping recipient {i+1}: missing phone or message")
                continue

            # Send message
            result = self.send_message(phone, message)
            result['business_name'] = business_name
            result['index'] = i + 1
            results.append(result)

            # Update progress
            if progress_callback:
                progress_callback(i + 1, len(recipients), result)

            # Wait between messages (rate limiting)
            if result['success'] and i < len(recipients) - 1:  # Don't wait after last message
                wait_time = self.rate_limiter.get_next_available_time()
                if wait_time > 0:
                    log_info(f"Rate limiting: waiting {wait_time} seconds before next message...")

                    for _ in range(wait_time):
                        if not self.is_running:
                            break
                        time.sleep(1)

                # Add small random delay for human-like behavior
                random_delay = random.uniform(1, 3)
                time.sleep(random_delay)

        self.is_running = False
        log_info(f"Bulk messaging completed. Sent {sum(1 for r in results if r['success'])} out of {len(results)} messages")

        return results

    def stop_messaging(self):
        """Stop the messaging process"""
        self.is_running = False
        log_info("WhatsApp messaging stop requested")

    def check_message_status(self, phone_number: str) -> str:
        """Check the delivery status of the last message to a phone number"""
        # This is a simplified implementation
        # In practice, you'd need to navigate to the chat and check message status
        try:
            # Navigate to chat
            clean_phone = self._clean_phone_number(phone_number)
            chat_url = f"https://web.whatsapp.com/send?phone={clean_phone}"
            self.driver.get(chat_url)

            time.sleep(3)

            # Look for message status indicators
            try:
                # Check for delivered/read status (this is simplified)
                status_elements = self.driver.find_elements(By.CSS_SELECTOR, self.selectors['message_status'])
                if status_elements:
                    return "Delivered"
                else:
                    return "Sent"
            except:
                return "Unknown"

        except Exception as e:
            log_error(f"Error checking message status for {phone_number}", e)
            return "Error"

    def close_session(self):
        """Close WhatsApp Web session"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.is_logged_in = False
                log_info("WhatsApp Web session closed")
        except Exception as e:
            log_error("Error closing WhatsApp Web session", e)

    def __del__(self):
        """Cleanup when object is destroyed"""
        self.close_session()