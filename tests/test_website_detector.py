"""
Test Website Detector functionality
"""
import unittest
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.website_detector import WebsiteDetector

class TestWebsiteDetector(unittest.TestCase):
    """Test cases for WebsiteDetector"""

    def setUp(self):
        """Set up test environment"""
        self.detector = WebsiteDetector(timeout=5)

    def test_detector_initialization(self):
        """Test detector initialization"""
        self.assertIsNotNone(self.detector)
        self.assertEqual(self.detector.timeout, 5)
        self.assertIsNotNone(self.detector.session)
        self.assertGreater(len(self.detector.construction_indicators), 0)

    def test_normalize_url(self):
        """Test URL normalization"""
        test_cases = [
            ("google.com", "https://google.com"),
            ("http://example.com", "http://example.com"),
            ("https://test.com/", "https://test.com"),
            ("EXAMPLE.COM", "https://example.com"),
        ]

        for input_url, expected in test_cases:
            result = self.detector._normalize_url(input_url)
            self.assertEqual(result, expected)

    def test_check_website_exists_no_url(self):
        """Test website check with no URL"""
        result = self.detector.check_website_exists("")

        self.assertFalse(result['exists'])
        self.assertEqual(result['status'], 'No Website')
        self.assertEqual(result['error'], 'No URL provided')

    def test_check_website_exists_invalid_url(self):
        """Test website check with invalid URL"""
        result = self.detector.check_website_exists("invalid-url-that-does-not-exist.com")

        self.assertFalse(result['exists'])
        self.assertIn(result['status'], ['Connection Error', 'Error', 'Timeout'])

    @unittest.skip("Requires internet connection - use for manual testing only")
    def test_check_website_exists_valid_url(self):
        """Test website check with valid URL (manual test)"""
        # This test is skipped by default as it requires internet connection
        result = self.detector.check_website_exists("https://www.google.com")

        self.assertTrue(result['exists'])
        self.assertEqual(result['status_code'], 200)
        self.assertIsNotNone(result['response_time'])

    def test_assess_content_quality(self):
        """Test content quality assessment"""
        from bs4 import BeautifulSoup

        # Test minimal content
        minimal_html = "<html><body>Test</body></html>"
        soup = BeautifulSoup(minimal_html, 'html.parser')
        quality = self.detector._assess_content_quality(soup, minimal_html)
        self.assertEqual(quality, 'Minimal Content')

        # Test professional content
        professional_html = """
        <html>
        <body>
            <h1>Professional Business</h1>
            <p>We provide excellent services to our customers. Contact us for more information.</p>
            <p>Our address is downtown. Phone: 123-456-7890. Email: info@business.com</p>
            <img src="logo.jpg" alt="Logo">
            <form>
                <input type="text" name="contact">
                <button>Submit</button>
            </form>
        </body>
        </html>
        """
        soup = BeautifulSoup(professional_html, 'html.parser')
        quality = self.detector._assess_content_quality(soup, professional_html)
        self.assertIn(quality, ['Professional', 'Good'])

    def test_analyze_content_construction(self):
        """Test content analysis for under construction sites"""
        construction_html = """
        <html>
        <head><title>Under Construction</title></head>
        <body>
            <h1>Site Under Construction</h1>
            <p>Coming soon!</p>
        </body>
        </html>
        """

        result = self.detector._analyze_content(construction_html, {})

        self.assertEqual(result['status'], 'Under Construction')
        self.assertEqual(result['content_quality'], 'Under Construction')
        self.assertEqual(result['title'], 'Under Construction')

    def test_batch_check_websites_empty(self):
        """Test batch checking with empty URL list"""
        results = self.detector.batch_check_websites([])
        self.assertEqual(len(results), 0)

    def test_batch_check_websites_invalid(self):
        """Test batch checking with invalid URLs"""
        urls = ["invalid-url-1.com", "invalid-url-2.com"]
        results = self.detector.batch_check_websites(urls)

        self.assertEqual(len(results), 2)
        for url in urls:
            self.assertIn(url, results)
            self.assertFalse(results[url]['exists'])

    def test_is_under_construction(self):
        """Test under construction detection"""
        # Mock the check_website_exists method for testing
        original_method = self.detector.check_website_exists

        def mock_check(url):
            return {'content_quality': 'Under Construction'}

        self.detector.check_website_exists = mock_check

        result = self.detector.is_under_construction("test.com")
        self.assertTrue(result)

        # Restore original method
        self.detector.check_website_exists = original_method

    def test_extract_contact_info(self):
        """Test contact information extraction"""
        from bs4 import BeautifulSoup

        html_with_contact = """
        <html>
        <body>
            <p>Contact us at info@company.com or call +90 555 123 45 67</p>
            <p>Alternative: (212) 555 12 34</p>
        </body>
        </html>
        """

        soup = BeautifulSoup(html_with_contact, 'html.parser')
        contact_info = self.detector._extract_contact_info(soup)

        self.assertGreater(len(contact_info['emails']), 0)
        self.assertIn('info@company.com', contact_info['emails'])
        self.assertGreater(len(contact_info['phones']), 0)

if __name__ == '__main__':
    unittest.main()