"""
Test Google Maps Scraper functionality
"""
import unittest
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.google_maps_scraper import GoogleMapsScraper

class TestGoogleMapsScraper(unittest.TestCase):
    """Test cases for GoogleMapsScraper"""

    def setUp(self):
        """Set up test environment"""
        self.scraper = GoogleMapsScraper(headless=True)

    def tearDown(self):
        """Clean up test environment"""
        if self.scraper:
            self.scraper.close_driver()

    def test_scraper_initialization(self):
        """Test scraper initialization"""
        self.assertIsNotNone(self.scraper)
        self.assertTrue(self.scraper.headless)
        self.assertFalse(self.scraper.is_running)

    def test_driver_initialization(self):
        """Test WebDriver initialization"""
        # This test requires Chrome to be installed
        try:
            success = self.scraper.initialize_driver()
            if success:
                self.assertIsNotNone(self.scraper.driver)
                self.scraper.close_driver()
            else:
                self.skipTest("Chrome WebDriver not available")
        except Exception as e:
            self.skipTest(f"Chrome WebDriver initialization failed: {e}")

    def test_avoid_detection(self):
        """Test anti-detection measures"""
        # This should not raise any exceptions
        try:
            self.scraper.avoid_detection()
        except Exception as e:
            self.fail(f"avoid_detection raised an exception: {e}")

    def test_stop_scraping(self):
        """Test stopping scraping process"""
        self.scraper.is_running = True
        self.scraper.stop_scraping()
        self.assertFalse(self.scraper.is_running)

    @unittest.skip("Requires actual web scraping - use for manual testing only")
    def test_search_businesses_manual(self):
        """Manual test for business search (skipped by default)"""
        # This test is skipped by default as it requires actual web scraping
        # Uncomment @unittest.skip to run manually

        results = self.scraper.search_businesses("restaurant", "İzmir", max_results=5)

        self.assertIsInstance(results, list)
        if results:  # If we got results
            self.assertGreater(len(results), 0)

            # Check first result structure
            first_result = results[0]
            self.assertIn('business_name', first_result)
            self.assertIsInstance(first_result['business_name'], str)

if __name__ == '__main__':
    unittest.main()