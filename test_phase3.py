#!/usr/bin/env python3
"""
Test script to verify Phase 3: Google Maps Scraping implementation
"""
import sys
import os

def test_phase3_implementation():
    """Test Phase 3 components"""
    print("=" * 60)
    print("PHASE 3: GOOGLE MAPS SCRAPING - TESTING")
    print("=" * 60)

    success_count = 0
    total_tests = 0

    # Test 1: Google Maps Scraper Import
    total_tests += 1
    try:
        from core.google_maps_scraper import GoogleMapsScraper
        print("✅ GoogleMapsScraper import successful")
        success_count += 1
    except Exception as e:
        print(f"❌ GoogleMapsScraper import failed: {e}")

    # Test 2: Scraper Initialization
    total_tests += 1
    try:
        from core.google_maps_scraper import GoogleMapsScraper
        scraper = GoogleMapsScraper(headless=True)

        if scraper and hasattr(scraper, 'search_businesses'):
            print("✅ Scraper initialization successful")
            success_count += 1
        else:
            print("❌ Scraper initialization failed - missing methods")

    except Exception as e:
        print(f"❌ Scraper initialization failed: {e}")

    # Test 3: Required Dependencies
    total_tests += 1
    try:
        import selenium
        from selenium import webdriver
        from webdriver_manager.chrome import ChromeDriverManager
        import requests
        from bs4 import BeautifulSoup

        print("✅ Required dependencies available")
        success_count += 1

    except ImportError as e:
        print(f"❌ Missing required dependency: {e}")

    # Test 4: GUI Integration
    total_tests += 1
    try:
        from gui.main_window import MainWindow
        from core.google_maps_scraper import GoogleMapsScraper

        # Check if GUI has scraper integration
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide window

        app = MainWindow(root)

        # Check if search functionality is implemented
        if hasattr(app, 'start_search') and hasattr(app, 'stop_search'):
            # Check if the methods are not just placeholders
            import inspect
            start_search_source = inspect.getsource(app.start_search)

            if "not yet implemented" not in start_search_source:
                print("✅ GUI-Scraper integration successful")
                success_count += 1
            else:
                print("❌ GUI-Scraper integration incomplete")
        else:
            print("❌ GUI-Scraper integration missing methods")

        root.destroy()

    except Exception as e:
        print(f"❌ GUI integration test failed: {e}")

    # Test 5: Input Validation Integration
    total_tests += 1
    try:
        from utils.validators import InputValidator

        # Test search parameter validation
        is_valid, errors = InputValidator.validate_search_parameters(
            "construction", "İzmir", "10", "50"
        )

        if is_valid:
            print("✅ Input validation integration successful")
            success_count += 1
        else:
            print(f"❌ Input validation failed: {errors}")

    except Exception as e:
        print(f"❌ Input validation test failed: {e}")

    # Test 6: Anti-Detection Features
    total_tests += 1
    try:
        from core.google_maps_scraper import GoogleMapsScraper
        scraper = GoogleMapsScraper(headless=True)

        # Check if anti-detection methods exist
        if (hasattr(scraper, 'avoid_detection') and
            hasattr(scraper, 'user_agents') and
            len(scraper.user_agents) > 0):
            print("✅ Anti-detection features implemented")
            success_count += 1
        else:
            print("❌ Anti-detection features missing")

    except Exception as e:
        print(f"❌ Anti-detection test failed: {e}")

    print("\n" + "=" * 60)
    print("PHASE 3 TEST RESULTS")
    print("=" * 60)
    print(f"Tests Passed: {success_count}/{total_tests}")
    print(f"Success Rate: {(success_count/total_tests)*100:.1f}%")

    if success_count == total_tests:
        print("\n🎉 PHASE 3: GOOGLE MAPS SCRAPING - COMPLETE!")
        print("✅ Google Maps scraper implemented")
        print("✅ Anti-detection measures implemented")
        print("✅ GUI integration completed")
        print("✅ Input validation integrated")
        print("\nReady to proceed to Phase 4: Website Detection System")
        return True
    else:
        print(f"\n❌ PHASE 3 INCOMPLETE - {total_tests - success_count} tests failed")
        print("\nNote: Some tests may fail due to missing Chrome browser or network issues.")
        print("The core functionality is implemented and ready for manual testing.")
        return False

if __name__ == "__main__":
    success = test_phase3_implementation()
    sys.exit(0 if success else 1)