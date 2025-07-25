"""
Google Maps Scraper for Business Lead Automation System
Handles scraping business information from Google Maps
"""
import time
import random
import re
from typing import List, Dict, Any, Optional, Callable
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from utils.config import config
from utils.logger import get_logger, log_info, log_error, log_warning
from core.data_models import BusinessData

class GoogleMapsScraper:
    """Scrapes business information from Google Maps"""

    def __init__(self, headless: bool = None, progress_callback: Optional[Callable] = None):
        self.logger = get_logger('GoogleMapsScraper')
        self.driver = None
        self.headless = headless if headless is not None else config.HEADLESS_BROWSER
        self.progress_callback = progress_callback
        self.is_running = False

        # Anti-detection settings
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]

        log_info("GoogleMapsScraper initialized")

    def initialize_driver(self) -> bool:
        """Initialize the Chrome WebDriver with anti-detection measures"""
        try:
            chrome_options = Options()

            # Basic options
            if self.headless:
                chrome_options.add_argument('--headless')

            # Anti-detection measures
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            # Random user agent
            user_agent = random.choice(self.user_agents)
            chrome_options.add_argument(f'--user-agent={user_agent}')

            # Window size
            chrome_options.add_argument('--window-size=1920,1080')

            # Disable images for faster loading
            prefs = {"profile.managed_default_content_settings.images": 2}
            chrome_options.add_experimental_option("prefs", prefs)

            # Initialize driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            # Set timeouts
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)

            log_info("Chrome WebDriver initialized successfully")
            return True

        except Exception as e:
            log_error("Failed to initialize Chrome WebDriver", e)
            return False

    def search_businesses(self, query: str, location: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search for businesses on Google Maps"""
        if not self.initialize_driver():
            return []

        try:
            self.is_running = True
            businesses = []

            # Construct search URL
            search_term = f"{query} {location}"
            encoded_search = quote_plus(search_term)
            url = f"https://www.google.com/maps/search/{encoded_search}"

            log_info(f"Starting Google Maps search: {search_term}")
            if self.progress_callback:
                self.progress_callback(f"Searching for: {search_term}")

            # Navigate to Google Maps
            self.driver.get(url)
            self.avoid_detection()

            # Wait for results to load
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[role="main"]'))
                )
            except TimeoutException:
                log_error("Timeout waiting for Google Maps to load")
                return []

            # Scroll to load more results
            self._scroll_to_load_results(max_results)

            # Extract business information
            businesses = self._extract_business_details()

            # Limit results
            if len(businesses) > max_results:
                businesses = businesses[:max_results]

            log_info(f"Successfully scraped {len(businesses)} businesses")
            return businesses

        except Exception as e:
            log_error("Error during Google Maps search", e)
            return []

        finally:
            self.is_running = False
            self.close_driver()

    def _scroll_to_load_results(self, max_results: int):
        """Scroll through the results panel to load more businesses"""
        try:
            # Find the scrollable results panel
            results_panel = self.driver.find_element(By.CSS_SELECTOR, '[role="main"]')

            last_height = 0
            scroll_attempts = 0
            max_scroll_attempts = 20

            while scroll_attempts < max_scroll_attempts:
                if not self.is_running:
                    break

                # Scroll down in the results panel
                self.driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight",
                    results_panel
                )

                # Wait for new content to load
                time.sleep(random.uniform(2, 4))

                # Check if we've loaded enough results
                current_results = len(self.driver.find_elements(By.CSS_SELECTOR, '[data-result-index]'))
                if current_results >= max_results:
                    log_info(f"Loaded {current_results} results, stopping scroll")
                    break

                # Check if we've reached the bottom
                new_height = self.driver.execute_script(
                    "return arguments[0].scrollHeight",
                    results_panel
                )

                if new_height == last_height:
                    scroll_attempts += 1
                    if scroll_attempts >= 3:  # No new content after 3 attempts
                        log_info("No more results to load")
                        break
                else:
                    scroll_attempts = 0
                    last_height = new_height

                if self.progress_callback:
                    self.progress_callback(f"Loading results... ({current_results} found)")

                self.avoid_detection()

        except Exception as e:
            log_error("Error scrolling to load results", e)

    def _extract_business_details(self) -> List[Dict[str, Any]]:
        """Extract business details from the current page"""
        businesses = []

        try:
            # Find all business result elements
            business_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-result-index]')

            log_info(f"Found {len(business_elements)} business elements to process")

            for i, element in enumerate(business_elements):
                if not self.is_running:
                    break

                try:
                    business_data = self._extract_single_business(element, i)
                    if business_data:
                        businesses.append(business_data)

                        if self.progress_callback:
                            self.progress_callback(f"Processed {len(businesses)} businesses...")

                    # Small delay between extractions
                    time.sleep(random.uniform(0.5, 1.5))

                except Exception as e:
                    log_warning(f"Error extracting business {i}: {e}")
                    continue

            return businesses

        except Exception as e:
            log_error("Error extracting business details", e)
            return businesses

    def _extract_single_business(self, element, index: int) -> Optional[Dict[str, Any]]:
        """Extract details from a single business element"""
        try:
            business_data = {}

            # Business name
            try:
                name_element = element.find_element(By.CSS_SELECTOR, '[role="button"] > div > div:nth-child(2) > div:nth-child(1)')
                business_data['business_name'] = name_element.text.strip()
            except:
                # Try alternative selector
                try:
                    name_element = element.find_element(By.CSS_SELECTOR, 'h3, [data-value="Name"]')
                    business_data['business_name'] = name_element.text.strip()
                except:
                    log_warning(f"Could not extract business name for element {index}")
                    return None

            # Address
            try:
                address_elements = element.find_elements(By.CSS_SELECTOR, '[data-value="Address"]')
                if address_elements:
                    business_data['address'] = address_elements[0].text.strip()
                else:
                    # Try alternative approach
                    text_content = element.text
                    address_match = re.search(r'[\w\s,]+(?:Cd\.|Sk\.|Mh\.|İl\.|İlçe)', text_content)
                    if address_match:
                        business_data['address'] = address_match.group().strip()
            except:
                business_data['address'] = None

            # Phone number
            try:
                phone_elements = element.find_elements(By.CSS_SELECTOR, '[data-value="Phone number"]')
                if phone_elements:
                    phone_text = phone_elements[0].text.strip()
                    # Clean phone number
                    phone_clean = re.sub(r'[^\d+]', '', phone_text)
                    if phone_clean:
                        business_data['phone'] = phone_clean
                else:
                    business_data['phone'] = None
            except:
                business_data['phone'] = None

            # Website
            try:
                website_elements = element.find_elements(By.CSS_SELECTOR, '[data-value="Website"]')
                if website_elements:
                    business_data['website'] = website_elements[0].get_attribute('href')
                else:
                    business_data['website'] = None
            except:
                business_data['website'] = None

            # Rating
            try:
                rating_elements = element.find_elements(By.CSS_SELECTOR, '[role="img"][aria-label*="star"]')
                if rating_elements:
                    rating_text = rating_elements[0].get_attribute('aria-label')
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        business_data['google_rating'] = float(rating_match.group(1))
                else:
                    business_data['google_rating'] = None
            except:
                business_data['google_rating'] = None

            # Set default values
            business_data['has_website'] = bool(business_data.get('website'))
            business_data['website_status'] = 'Unknown'
            business_data['contact_status'] = 'Not Contacted'

            return business_data

        except Exception as e:
            log_error(f"Error extracting single business {index}", e)
            return None

    def avoid_detection(self):
        """Implement anti-detection measures"""
        try:
            # Random delay
            delay = random.uniform(1, 3)
            time.sleep(delay)

            # Random mouse movements (simulate human behavior)
            if self.driver and not self.headless:
                try:
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(self.driver)

                    # Random small movements
                    for _ in range(random.randint(1, 3)):
                        x_offset = random.randint(-50, 50)
                        y_offset = random.randint(-50, 50)
                        actions.move_by_offset(x_offset, y_offset)

                    actions.perform()
                except:
                    pass  # Ignore if action chains fail

        except Exception as e:
            log_warning(f"Error in avoid_detection: {e}")

    def stop_scraping(self):
        """Stop the scraping process"""
        self.is_running = False
        log_info("Scraping stop requested")

    def close_driver(self):
        """Close the WebDriver"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                log_info("WebDriver closed successfully")
        except Exception as e:
            log_error("Error closing WebDriver", e)

    def __del__(self):
        """Cleanup when object is destroyed"""
        self.close_driver()