"""
Website Detector for Business Lead Automation System
Handles website existence verification and quality assessment
"""
import requests
import time
import random
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse, urljoin
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
import ssl
import socket

from utils.config import config
from utils.logger import get_logger, log_info, log_error, log_warning

class WebsiteDetector:
    """Detects and analyzes website existence and quality"""

    def __init__(self, timeout: int = 10, max_workers: int = 5):
        self.logger = get_logger('WebsiteDetector')
        self.timeout = timeout
        self.max_workers = max_workers

        # Configure session with headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

        # Common indicators of under construction or placeholder sites
        self.construction_indicators = [
            'under construction', 'coming soon', 'site is being built',
            'website is under development', 'page not found', 'default page',
            'apache default page', 'nginx default page', 'iis default page',
            'domain parked', 'this domain is for sale', 'godaddy',
            'yapım aşamasında', 'hazırlanıyor', 'çok yakında'
        ]

        log_info("WebsiteDetector initialized")

    def check_website_exists(self, url: str) -> Dict[str, Any]:
        """Check if a website exists and analyze its status"""
        if not url:
            return {
                'exists': False,
                'status': 'No Website',
                'status_code': None,
                'response_time': None,
                'ssl_valid': False,
                'content_quality': 'Unknown',
                'error': 'No URL provided'
            }

        # Normalize URL
        normalized_url = self._normalize_url(url)

        try:
            start_time = time.time()

            # Make request with timeout
            response = self.session.get(
                normalized_url,
                timeout=self.timeout,
                allow_redirects=True,
                verify=False  # Skip SSL verification for problematic sites
            )

            response_time = time.time() - start_time

            # Analyze response
            result = self._analyze_response(response, normalized_url, response_time)

            log_info(f"Website check completed for {url}: {result['status']}")
            return result

        except requests.exceptions.Timeout:
            return {
                'exists': False,
                'status': 'Timeout',
                'status_code': None,
                'response_time': self.timeout,
                'ssl_valid': False,
                'content_quality': 'Unknown',
                'error': 'Request timeout'
            }

        except requests.exceptions.ConnectionError:
            return {
                'exists': False,
                'status': 'Connection Error',
                'status_code': None,
                'response_time': None,
                'ssl_valid': False,
                'content_quality': 'Unknown',
                'error': 'Connection failed'
            }

        except requests.exceptions.SSLError:
            # Try without SSL
            try:
                http_url = normalized_url.replace('https://', 'http://')
                response = self.session.get(http_url, timeout=self.timeout, allow_redirects=True)
                result = self._analyze_response(response, http_url, time.time() - start_time)
                result['ssl_valid'] = False
                return result
            except:
                return {
                    'exists': False,
                    'status': 'SSL Error',
                    'status_code': None,
                    'response_time': None,
                    'ssl_valid': False,
                    'content_quality': 'Unknown',
                    'error': 'SSL certificate error'
                }

        except Exception as e:
            log_warning(f"Error checking website {url}: {e}")
            return {
                'exists': False,
                'status': 'Error',
                'status_code': None,
                'response_time': None,
                'ssl_valid': False,
                'content_quality': 'Unknown',
                'error': str(e)
            }

    def _normalize_url(self, url: str) -> str:
        """Normalize URL format"""
        url = url.strip().lower()

        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # Remove trailing slash
        url = url.rstrip('/')

        return url

    def _analyze_response(self, response: requests.Response, url: str, response_time: float) -> Dict[str, Any]:
        """Analyze HTTP response and determine website status"""
        result = {
            'exists': True,
            'status_code': response.status_code,
            'response_time': round(response_time, 2),
            'ssl_valid': url.startswith('https://'),
            'final_url': response.url
        }

        # Check status code
        if response.status_code == 200:
            # Analyze content
            content_analysis = self._analyze_content(response.text, response.headers)
            result.update(content_analysis)

        elif response.status_code in [301, 302, 303, 307, 308]:
            result['status'] = 'Redirect'
            result['content_quality'] = 'Unknown'

        elif response.status_code == 404:
            result['exists'] = False
            result['status'] = 'Not Found'
            result['content_quality'] = 'Unknown'

        elif response.status_code in [500, 502, 503, 504]:
            result['status'] = 'Server Error'
            result['content_quality'] = 'Unknown'

        else:
            result['status'] = f'HTTP {response.status_code}'
            result['content_quality'] = 'Unknown'

        return result

    def _analyze_content(self, html_content: str, headers: Dict) -> Dict[str, Any]:
        """Analyze website content to determine quality and status"""
        try:
            # Parse HTML content
            soup = BeautifulSoup(html_content, 'html.parser')

            # Get page title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ''

            # Get page text content
            page_text = soup.get_text().lower()

            # Check for construction indicators
            is_under_construction = any(
                indicator in page_text or indicator in title_text.lower()
                for indicator in self.construction_indicators
            )

            if is_under_construction:
                return {
                    'status': 'Under Construction',
                    'content_quality': 'Under Construction',
                    'title': title_text,
                    'content_length': len(html_content)
                }

            # Analyze content quality
            content_quality = self._assess_content_quality(soup, html_content)

            return {
                'status': 'Active',
                'content_quality': content_quality,
                'title': title_text,
                'content_length': len(html_content)
            }

        except Exception as e:
            log_warning(f"Error analyzing content: {e}")
            return {
                'status': 'Active',
                'content_quality': 'Unknown',
                'title': '',
                'content_length': len(html_content) if html_content else 0
            }

    def _assess_content_quality(self, soup: BeautifulSoup, html_content: str) -> str:
        """Assess the quality of website content"""
        try:
            # Count various elements
            text_length = len(soup.get_text().strip())
            image_count = len(soup.find_all('img'))
            link_count = len(soup.find_all('a'))
            form_count = len(soup.find_all('form'))

            # Check for common CMS indicators
            cms_indicators = ['wordpress', 'joomla', 'drupal', 'wix', 'squarespace']
            has_cms = any(indicator in html_content.lower() for indicator in cms_indicators)

            # Check for business-related content
            business_keywords = [
                'contact', 'about', 'services', 'products', 'phone', 'email',
                'address', 'location', 'hours', 'business', 'company'
            ]
            business_content_score = sum(
                1 for keyword in business_keywords
                if keyword in soup.get_text().lower()
            )

            # Determine quality based on various factors
            if text_length < 100:
                return 'Minimal Content'
            elif text_length < 500:
                return 'Basic'
            elif business_content_score >= 3 and (image_count > 0 or form_count > 0):
                return 'Professional'
            elif business_content_score >= 2:
                return 'Good'
            else:
                return 'Basic'

        except Exception as e:
            log_warning(f"Error assessing content quality: {e}")
            return 'Unknown'

    def batch_check_websites(self, urls: List[str], progress_callback: Optional[callable] = None) -> Dict[str, Dict[str, Any]]:
        """Check multiple websites concurrently"""
        results = {}

        if not urls:
            return results

        log_info(f"Starting batch website check for {len(urls)} URLs")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_url = {
                executor.submit(self.check_website_exists, url): url
                for url in urls if url
            }

            completed = 0
            total = len(future_to_url)

            # Process completed tasks
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                completed += 1

                try:
                    result = future.result()
                    results[url] = result

                    if progress_callback:
                        progress_callback(completed, total, url, result['status'])

                    # Small delay to avoid overwhelming servers
                    time.sleep(random.uniform(0.1, 0.3))

                except Exception as e:
                    log_error(f"Error checking website {url}", e)
                    results[url] = {
                        'exists': False,
                        'status': 'Error',
                        'error': str(e)
                    }

        log_info(f"Batch website check completed: {len(results)} results")
        return results

    def validate_website_quality(self, url: str) -> Dict[str, Any]:
        """Perform detailed website quality validation"""
        basic_check = self.check_website_exists(url)

        if not basic_check['exists'] or basic_check['status'] != 'Active':
            return basic_check

        # Additional quality checks
        try:
            response = self.session.get(url, timeout=self.timeout)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Check for mobile responsiveness
            viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
            is_mobile_friendly = viewport_meta is not None

            # Check for SSL
            has_ssl = url.startswith('https://')

            # Check loading speed (basic)
            load_time = basic_check.get('response_time', 0)
            speed_rating = 'Fast' if load_time < 2 else 'Moderate' if load_time < 5 else 'Slow'

            # Update result with quality metrics
            basic_check.update({
                'mobile_friendly': is_mobile_friendly,
                'has_ssl': has_ssl,
                'speed_rating': speed_rating,
                'seo_title_length': len(basic_check.get('title', '')),
                'has_meta_description': bool(soup.find('meta', attrs={'name': 'description'}))
            })

        except Exception as e:
            log_warning(f"Error in detailed quality check for {url}: {e}")

        return basic_check

    def is_under_construction(self, url: str) -> bool:
        """Quick check if website is under construction"""
        result = self.check_website_exists(url)
        return result.get('content_quality') == 'Under Construction'

    def extract_website_info(self, url: str) -> Dict[str, Any]:
        """Extract detailed information from website"""
        result = self.check_website_exists(url)

        if not result['exists'] or result['status'] != 'Active':
            return result

        try:
            response = self.session.get(url, timeout=self.timeout)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract contact information
            contact_info = self._extract_contact_info(soup)

            # Extract business information
            business_info = self._extract_business_info(soup)

            result.update({
                'contact_info': contact_info,
                'business_info': business_info
            })

        except Exception as e:
            log_warning(f"Error extracting website info from {url}: {e}")

        return result

    def _extract_contact_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract contact information from website"""
        contact_info = {
            'emails': [],
            'phones': [],
            'addresses': []
        }

        try:
            page_text = soup.get_text()

            # Extract emails
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, page_text)
            contact_info['emails'] = list(set(emails))

            # Extract phone numbers (Turkish format)
            phone_patterns = [
                r'\+90\s?\d{3}\s?\d{3}\s?\d{2}\s?\d{2}',
                r'0\d{3}\s?\d{3}\s?\d{2}\s?\d{2}',
                r'\(\d{3}\)\s?\d{3}\s?\d{2}\s?\d{2}'
            ]

            phones = []
            for pattern in phone_patterns:
                phones.extend(re.findall(pattern, page_text))
            contact_info['phones'] = list(set(phones))

        except Exception as e:
            log_warning(f"Error extracting contact info: {e}")

        return contact_info

    def _extract_business_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract business information from website"""
        business_info = {
            'description': '',
            'services': [],
            'social_media': []
        }

        try:
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                business_info['description'] = meta_desc.get('content', '')

            # Extract social media links
            social_patterns = {
                'facebook': r'facebook\.com/[^/\s]+',
                'instagram': r'instagram\.com/[^/\s]+',
                'twitter': r'twitter\.com/[^/\s]+',
                'linkedin': r'linkedin\.com/[^/\s]+'
            }

            page_html = str(soup)
            for platform, pattern in social_patterns.items():
                matches = re.findall(pattern, page_html)
                if matches:
                    business_info['social_media'].extend([
                        {'platform': platform, 'url': f"https://{match}"}
                        for match in matches
                    ])

        except Exception as e:
            log_warning(f"Error extracting business info: {e}")

        return business_info