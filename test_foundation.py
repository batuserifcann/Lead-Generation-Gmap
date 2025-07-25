#!/usr/bin/env python3
"""
Test script to verify the foundation setup
"""
import sys
import os

def test_imports():
    """Test that our basic modules can be imported"""
    print("Testing foundation imports...")

    try:
        from utils.config import config
        print("✅ Config module imported successfully")
        print(f"   App Name: {config.APP_NAME}")
        print(f"   App Version: {config.APP_VERSION}")
        print(f"   Excel Path: {config.get_excel_path()}")
        print(f"   Log Path: {config.get_log_path()}")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False

    try:
        from utils.logger import log_info, log_error, get_logger
        print("✅ Logger module imported successfully")

        # Test logging
        log_info("Test info message from foundation test")
        logger = get_logger('test')
        logger.debug("Test debug message")
        print("   Logging test completed")
    except Exception as e:
        print(f"❌ Logger import failed: {e}")
        return False

    return True

def test_directory_structure():
    """Test that required directories exist"""
    print("\nTesting directory structure...")

    required_dirs = [
        'gui',
        'core',
        'utils',
        'data',
        'data/logs',
        'tests',
        'gui/components'
    ]

    all_exist = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ Directory exists: {dir_path}")
        else:
            print(f"❌ Directory missing: {dir_path}")
            all_exist = False

    return all_exist

def test_files():
    """Test that required files exist"""
    print("\nTesting required files...")

    required_files = [
        'main.py',
        'requirements.txt',
        '.env',
        'utils/__init__.py',
        'utils/config.py',
        'utils/logger.py',
        'gui/__init__.py',
        'gui/main_window.py',
        'core/__init__.py',
        'tests/__init__.py'
    ]

    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ File exists: {file_path}")
        else:
            print(f"❌ File missing: {file_path}")
            all_exist = False

    return all_exist

def main():
    """Run all foundation tests"""
    print("=" * 50)
    print("BUSINESS LEAD AUTOMATION - FOUNDATION TEST")
    print("=" * 50)

    tests = [
        ("Directory Structure", test_directory_structure),
        ("Required Files", test_files),
        ("Module Imports", test_imports),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))

    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)

    all_passed = True
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL FOUNDATION TESTS PASSED!")
        print("Phase 1: Foundation Setup is complete.")
        print("Ready to proceed to Phase 2: Data Management Core")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please fix the issues before proceeding.")
    print("=" * 50)

    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)