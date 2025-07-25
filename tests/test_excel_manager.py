"""
Test Excel Manager functionality
"""
import unittest
import os
import tempfile
import pandas as pd
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.excel_manager import ExcelManager
from core.data_models import BusinessData

class TestExcelManager(unittest.TestCase):
    """Test cases for ExcelManager"""

    def setUp(self):
        """Set up test environment"""
        # Create temporary file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test_leads.xlsx')
        self.excel_manager = ExcelManager(self.test_file)

    def tearDown(self):
        """Clean up test environment"""
        # Remove test file if it exists
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

        # Remove temp directory
        os.rmdir(self.temp_dir)

    def test_create_new_file(self):
        """Test creating a new Excel file"""
        success = self.excel_manager.create_new_file()

        self.assertTrue(success)
        self.assertTrue(os.path.exists(self.test_file))

        # Verify file structure
        df = pd.read_excel(self.test_file, sheet_name='Business_Leads')
        expected_columns = [
            'id', 'business_name', 'address', 'phone', 'email', 'website',
            'has_website', 'website_status', 'industry', 'location',
            'google_rating', 'contact_status', 'last_contacted', 'notes',
            'created_at', 'updated_at'
        ]

        self.assertEqual(list(df.columns), expected_columns)
        self.assertEqual(len(df), 0)  # Should be empty initially

    def test_load_data_new_file(self):
        """Test loading data when file doesn't exist"""
        success = self.excel_manager.load_data()

        self.assertTrue(success)
        self.assertTrue(os.path.exists(self.test_file))
        self.assertEqual(len(self.excel_manager.data), 0)

    def test_append_business(self):
        """Test adding a business to the data"""
        # Create file first
        self.excel_manager.load_data()

        business_data = {
            'business_name': 'Test Construction Company',
            'address': 'İzmir, Turkey',
            'phone': '+905551234567',
            'email': 'info@testcompany.com',
            'website': 'https://testcompany.com',
            'industry': 'construction',
            'location': 'İzmir',
            'google_rating': 4.5
        }

        success = self.excel_manager.append_business(business_data)

        self.assertTrue(success)
        self.assertEqual(len(self.excel_manager.data), 1)

        # Check data integrity
        added_business = self.excel_manager.data.iloc[0]
        self.assertEqual(added_business['business_name'], 'Test Construction Company')
        self.assertEqual(added_business['contact_status'], 'Not Contacted')
        self.assertIsNotNone(added_business['id'])
        self.assertIsNotNone(added_business['created_at'])

    def test_save_and_load_data(self):
        """Test saving and loading data"""
        # Create and add test data
        self.excel_manager.load_data()

        business_data = {
            'business_name': 'Save Test Company',
            'industry': 'construction',
            'location': 'İzmir'
        }

        self.excel_manager.append_business(business_data)

        # Save data
        save_success = self.excel_manager.save_data()
        self.assertTrue(save_success)

        # Create new manager and load data
        new_manager = ExcelManager(self.test_file)
        load_success = new_manager.load_data()

        self.assertTrue(load_success)
        self.assertEqual(len(new_manager.data), 1)
        self.assertEqual(new_manager.data.iloc[0]['business_name'], 'Save Test Company')

    def test_update_contact_status(self):
        """Test updating contact status"""
        # Create and add test data
        self.excel_manager.load_data()

        business_data = {
            'business_name': 'Contact Test Company',
            'industry': 'construction'
        }

        self.excel_manager.append_business(business_data)
        business_id = self.excel_manager.data.iloc[0]['id']

        # Update contact status
        success = self.excel_manager.update_contact_status(
            business_id,
            'Contacted',
            'Initial contact made'
        )

        self.assertTrue(success)

        # Verify update
        updated_business = self.excel_manager.data.iloc[0]
        self.assertEqual(updated_business['contact_status'], 'Contacted')
        self.assertIsNotNone(updated_business['last_contacted'])
        self.assertIn('Initial contact made', updated_business['notes'])

    def test_get_uncontacted_businesses(self):
        """Test getting uncontacted businesses"""
        self.excel_manager.load_data()

        # Add test businesses
        businesses = [
            {'business_name': 'Uncontacted 1', 'contact_status': 'Not Contacted'},
            {'business_name': 'Contacted 1', 'contact_status': 'Contacted'},
            {'business_name': 'Uncontacted 2', 'contact_status': 'Not Contacted'}
        ]

        for business in businesses:
            self.excel_manager.append_business(business)

        uncontacted = self.excel_manager.get_uncontacted_businesses()

        self.assertEqual(len(uncontacted), 2)
        self.assertTrue(all(row['contact_status'] == 'Not Contacted' for _, row in uncontacted.iterrows()))

    def test_get_statistics(self):
        """Test getting data statistics"""
        self.excel_manager.load_data()

        # Add test businesses
        businesses = [
            {'business_name': 'Company 1', 'industry': 'construction', 'has_website': True, 'contact_status': 'Contacted'},
            {'business_name': 'Company 2', 'industry': 'construction', 'has_website': False, 'contact_status': 'Not Contacted'},
            {'business_name': 'Company 3', 'industry': 'restaurant', 'has_website': True, 'contact_status': 'Contacted'}
        ]

        for business in businesses:
            self.excel_manager.append_business(business)

        stats = self.excel_manager.get_statistics()

        self.assertEqual(stats['total_businesses'], 3)
        self.assertEqual(stats['contacted'], 2)
        self.assertEqual(stats['not_contacted'], 1)
        self.assertEqual(stats['with_websites'], 2)
        self.assertEqual(stats['without_websites'], 1)
        self.assertEqual(stats['by_industry']['construction'], 2)
        self.assertEqual(stats['by_industry']['restaurant'], 1)

if __name__ == '__main__':
    unittest.main()