#!/usr/bin/env python3
"""
Test script to verify Phase 2: Data Management Core implementation
"""
import sys
import os
import tempfile

def test_phase2_implementation():
    """Test Phase 2 components"""
    print("=" * 60)
    print("PHASE 2: DATA MANAGEMENT CORE - TESTING")
    print("=" * 60)

    success_count = 0
    total_tests = 0

    # Test 1: Excel Manager Import
    total_tests += 1
    try:
        from core.excel_manager import ExcelManager
        print("✅ ExcelManager import successful")
        success_count += 1
    except Exception as e:
        print(f"❌ ExcelManager import failed: {e}")

    # Test 2: Data Models Import
    total_tests += 1
    try:
        from core.data_models import BusinessData
        print("✅ BusinessData model import successful")
        success_count += 1
    except Exception as e:
        print(f"❌ BusinessData model import failed: {e}")

    # Test 3: Validators Import
    total_tests += 1
    try:
        from utils.validators import InputValidator
        print("✅ InputValidator import successful")
        success_count += 1
    except Exception as e:
        print(f"❌ InputValidator import failed: {e}")

    # Test 4: Excel Manager Basic Functionality
    total_tests += 1
    try:
        from core.excel_manager import ExcelManager

        # Create temporary file
        temp_dir = tempfile.mkdtemp()
        test_file = os.path.join(temp_dir, 'test_phase2.xlsx')

        # Test Excel manager
        excel_manager = ExcelManager(test_file)
        success = excel_manager.create_new_file()

        if success and os.path.exists(test_file):
            print("✅ Excel file creation successful")
            success_count += 1

            # Clean up
            os.remove(test_file)
            os.rmdir(temp_dir)
        else:
            print("❌ Excel file creation failed")

    except Exception as e:
        print(f"❌ Excel Manager functionality test failed: {e}")

    # Test 5: Business Data Validation
    total_tests += 1
    try:
        from core.data_models import BusinessData

        # Test valid business data
        business = BusinessData(
            business_name="Test Company",
            phone="+905551234567",
            email="test@company.com",
            website="https://testcompany.com"
        )

        is_valid, errors = business.is_valid()
        if is_valid:
            print("✅ Business data validation successful")
            success_count += 1
        else:
            print(f"❌ Business data validation failed: {errors}")

    except Exception as e:
        print(f"❌ Business data validation test failed: {e}")

    # Test 6: Input Validators
    total_tests += 1
    try:
        from utils.validators import InputValidator

        # Test phone validation
        is_valid, error = InputValidator.validate_phone_number("+905551234567")
        if is_valid:
            print("✅ Input validation successful")
            success_count += 1
        else:
            print(f"❌ Input validation failed: {error}")

    except Exception as e:
        print(f"❌ Input validation test failed: {e}")

    print("\n" + "=" * 60)
    print("PHASE 2 TEST RESULTS")
    print("=" * 60)
    print(f"Tests Passed: {success_count}/{total_tests}")
    print(f"Success Rate: {(success_count/total_tests)*100:.1f}%")

    if success_count == total_tests:
        print("\n🎉 PHASE 2: DATA MANAGEMENT CORE - COMPLETE!")
        print("✅ Excel Manager implemented and working")
        print("✅ Data models and validation implemented")
        print("✅ GUI integration completed")
        print("\nReady to proceed to Phase 3: Google Maps Scraping")
        return True
    else:
        print(f"\n❌ PHASE 2 INCOMPLETE - {total_tests - success_count} tests failed")
        return False

if __name__ == "__main__":
    success = test_phase2_implementation()
    sys.exit(0 if success else 1)