"""
Excel Manager for Business Lead Automation System
Handles all Excel file operations including reading, writing, and data management
"""
import pandas as pd
import openpyxl
from pathlib import Path
from datetime import datetime
import uuid
from typing import Dict, List, Optional, Any
import os

from utils.config import config
from utils.logger import get_logger, log_info, log_error, log_warning

class ExcelManager:
    """Manages Excel file operations for business lead data"""

    def __init__(self, filepath: Optional[str] = None):
        self.logger = get_logger('ExcelManager')
        self.filepath = filepath or config.get_excel_path()
        self.data = pd.DataFrame()

        # Define the standard column structure
        self.columns = [
            'id', 'business_name', 'address', 'phone', 'email', 'website',
            'has_website', 'website_status', 'industry', 'location',
            'google_rating', 'contact_status', 'last_contacted', 'notes',
            'created_at', 'updated_at'
        ]

        log_info(f"ExcelManager initialized with file: {self.filepath}")

    def create_new_file(self, filepath: Optional[str] = None) -> bool:
        """Create a new Excel file with the standard structure"""
        try:
            target_path = filepath or self.filepath

            # Create empty DataFrame with standard columns
            df = pd.DataFrame(columns=self.columns)

            # Ensure directory exists
            Path(target_path).parent.mkdir(parents=True, exist_ok=True)

            # Save to Excel with formatting
            with pd.ExcelWriter(target_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Business_Leads', index=False)

                # Get the workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Business_Leads']

                # Set column widths
                column_widths = {
                    'A': 10,  # id
                    'B': 25,  # business_name
                    'C': 30,  # address
                    'D': 15,  # phone
                    'E': 25,  # email
                    'F': 30,  # website
                    'G': 12,  # has_website
                    'H': 15,  # website_status
                    'I': 15,  # industry
                    'J': 15,  # location
                    'K': 12,  # google_rating
                    'L': 15,  # contact_status
                    'M': 18,  # last_contacted
                    'N': 30,  # notes
                    'O': 18,  # created_at
                    'P': 18,  # updated_at
                }

                for col, width in column_widths.items():
                    worksheet.column_dimensions[col].width = width

            log_info(f"Created new Excel file: {target_path}")
            return True

        except Exception as e:
            log_error(f"Failed to create Excel file: {target_path}", e)
            return False

    def load_data(self, filepath: Optional[str] = None) -> bool:
        """Load data from Excel file"""
        try:
            target_path = filepath or self.filepath

            if not os.path.exists(target_path):
                log_warning(f"Excel file not found: {target_path}")
                # Create new file if it doesn't exist
                if self.create_new_file(target_path):
                    self.data = pd.DataFrame(columns=self.columns)
                    return True
                return False

            # Load the Excel file
            self.data = pd.read_excel(target_path, sheet_name='Business_Leads')

            # Ensure all required columns exist
            for col in self.columns:
                if col not in self.data.columns:
                    self.data[col] = None

            # Reorder columns to match standard structure
            self.data = self.data[self.columns]

            log_info(f"Loaded {len(self.data)} records from Excel file: {target_path}")
            return True

        except Exception as e:
            log_error(f"Failed to load Excel file: {target_path}", e)
            return False

    def save_data(self, data: Optional[pd.DataFrame] = None, filepath: Optional[str] = None) -> bool:
        """Save data to Excel file"""
        try:
            target_path = filepath or self.filepath
            df_to_save = data if data is not None else self.data

            # Ensure directory exists
            Path(target_path).parent.mkdir(parents=True, exist_ok=True)

            # Save to Excel
            with pd.ExcelWriter(target_path, engine='openpyxl') as writer:
                df_to_save.to_excel(writer, sheet_name='Business_Leads', index=False)

                # Apply formatting
                workbook = writer.book
                worksheet = writer.sheets['Business_Leads']

                # Set column widths (same as create_new_file)
                column_widths = {
                    'A': 10, 'B': 25, 'C': 30, 'D': 15, 'E': 25, 'F': 30,
                    'G': 12, 'H': 15, 'I': 15, 'J': 15, 'K': 12, 'L': 15,
                    'M': 18, 'N': 30, 'O': 18, 'P': 18
                }

                for col, width in column_widths.items():
                    worksheet.column_dimensions[col].width = width

            log_info(f"Saved {len(df_to_save)} records to Excel file: {target_path}")
            return True

        except Exception as e:
            log_error(f"Failed to save Excel file: {target_path}", e)
            return False

    def append_business(self, business_data: Dict[str, Any]) -> bool:
        """Add a new business to the data"""
        try:
            # Generate unique ID if not provided
            if 'id' not in business_data or not business_data['id']:
                business_data['id'] = str(uuid.uuid4())[:8]

            # Add timestamps
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            business_data['created_at'] = current_time
            business_data['updated_at'] = current_time

            # Set default values for missing fields
            defaults = {
                'has_website': False,
                'website_status': 'Unknown',
                'contact_status': 'Not Contacted',
                'last_contacted': None,
                'notes': '',
                'google_rating': None
            }

            for key, default_value in defaults.items():
                if key not in business_data:
                    business_data[key] = default_value

            # Create new row DataFrame
            new_row = pd.DataFrame([business_data])

            # Ensure all columns are present
            for col in self.columns:
                if col not in new_row.columns:
                    new_row[col] = None

            # Reorder columns
            new_row = new_row[self.columns]

            # Append to existing data
            self.data = pd.concat([self.data, new_row], ignore_index=True)

            log_info(f"Added business: {business_data.get('business_name', 'Unknown')}")
            return True

        except Exception as e:
            log_error(f"Failed to append business data", e)
            return False

    def update_contact_status(self, business_id: str, status: str, notes: str = "") -> bool:
        """Update the contact status of a business"""
        try:
            # Find the business by ID
            mask = self.data['id'] == business_id
            if not mask.any():
                log_warning(f"Business not found with ID: {business_id}")
                return False

            # Update the contact status
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.data.loc[mask, 'contact_status'] = status
            self.data.loc[mask, 'last_contacted'] = current_time
            self.data.loc[mask, 'updated_at'] = current_time

            if notes:
                existing_notes = self.data.loc[mask, 'notes'].iloc[0] or ""
                new_notes = f"{existing_notes}\n{current_time}: {notes}".strip()
                self.data.loc[mask, 'notes'] = new_notes

            business_name = self.data.loc[mask, 'business_name'].iloc[0]
            log_info(f"Updated contact status for {business_name}: {status}")
            return True

        except Exception as e:
            log_error(f"Failed to update contact status for business ID: {business_id}", e)
            return False

    def get_uncontacted_businesses(self) -> pd.DataFrame:
        """Get businesses that haven't been contacted yet"""
        try:
            uncontacted = self.data[
                (self.data['contact_status'] == 'Not Contacted') |
                (self.data['contact_status'].isna())
            ].copy()

            log_info(f"Found {len(uncontacted)} uncontacted businesses")
            return uncontacted

        except Exception as e:
            log_error("Failed to get uncontacted businesses", e)
            return pd.DataFrame()

    def get_businesses_without_websites(self) -> pd.DataFrame:
        """Get businesses that don't have websites"""
        try:
            no_website = self.data[
                (self.data['has_website'] == False) |
                (self.data['has_website'].isna()) |
                (self.data['website_status'] == 'No Website')
            ].copy()

            log_info(f"Found {len(no_website)} businesses without websites")
            return no_website

        except Exception as e:
            log_error("Failed to get businesses without websites", e)
            return pd.DataFrame()

    def export_filtered_data(self, filter_criteria: Dict[str, Any], filepath: str) -> bool:
        """Export filtered data to a new Excel file"""
        try:
            filtered_data = self.data.copy()

            # Apply filters
            for column, value in filter_criteria.items():
                if column in filtered_data.columns:
                    if isinstance(value, list):
                        filtered_data = filtered_data[filtered_data[column].isin(value)]
                    else:
                        filtered_data = filtered_data[filtered_data[column] == value]

            # Save filtered data
            success = self.save_data(filtered_data, filepath)
            if success:
                log_info(f"Exported {len(filtered_data)} filtered records to: {filepath}")

            return success

        except Exception as e:
            log_error(f"Failed to export filtered data to: {filepath}", e)
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the current data"""
        try:
            if self.data.empty:
                return {
                    'total_businesses': 0,
                    'contacted': 0,
                    'not_contacted': 0,
                    'with_websites': 0,
                    'without_websites': 0,
                    'by_industry': {},
                    'by_location': {},
                    'by_contact_status': {}
                }

            # Safe column access with defaults
            contacted_count = 0
            not_contacted_count = 0
            if 'contact_status' in self.data.columns:
                contacted_count = len(self.data[self.data['contact_status'] != 'Not Contacted'])
                not_contacted_count = len(self.data[self.data['contact_status'] == 'Not Contacted'])
            else:
                not_contacted_count = len(self.data)  # Assume all are not contacted if column missing

            with_websites_count = 0
            without_websites_count = 0
            if 'has_website' in self.data.columns:
                with_websites_count = len(self.data[self.data['has_website'] == True])
                without_websites_count = len(self.data[self.data['has_website'] == False])
            else:
                without_websites_count = len(self.data)  # Assume no websites if column missing

            stats = {
                'total_businesses': len(self.data),
                'contacted': contacted_count,
                'not_contacted': not_contacted_count,
                'with_websites': with_websites_count,
                'without_websites': without_websites_count,
                'by_industry': self.data['industry'].value_counts().to_dict() if 'industry' in self.data.columns else {},
                'by_location': self.data['location'].value_counts().to_dict() if 'location' in self.data.columns else {},
                'by_contact_status': self.data['contact_status'].value_counts().to_dict() if 'contact_status' in self.data.columns else {}
            }

            return stats

        except Exception as e:
            log_error("Failed to generate statistics", e)
            return {
                'total_businesses': 0,
                'contacted': 0,
                'not_contacted': 0,
                'with_websites': 0,
                'without_websites': 0,
                'by_industry': {},
                'by_location': {},
                'by_contact_status': {}
            }

    def search_businesses(self, search_term: str, columns: List[str] = None) -> pd.DataFrame:
        """Search for businesses by term in specified columns"""
        try:
            if columns is None:
                columns = ['business_name', 'address', 'industry', 'location']

            # Create search mask
            mask = pd.Series([False] * len(self.data))

            for column in columns:
                if column in self.data.columns:
                    mask |= self.data[column].str.contains(search_term, case=False, na=False)

            results = self.data[mask].copy()
            log_info(f"Search for '{search_term}' returned {len(results)} results")
            return results

        except Exception as e:
            log_error(f"Failed to search for term: {search_term}", e)
            return pd.DataFrame()

    def update_website_status(self, business_id: str, website_data: Dict[str, Any]) -> bool:
        """Update website status for a business"""
        try:
            # Find the business by ID
            mask = self.data['id'] == business_id
            if not mask.any():
                log_warning(f"Business not found with ID: {business_id}")
                return False

            # Update website-related fields
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            self.data.loc[mask, 'has_website'] = website_data.get('exists', False)
            self.data.loc[mask, 'website_status'] = website_data.get('status', 'Unknown')
            self.data.loc[mask, 'updated_at'] = current_time

            # Add website analysis notes
            if 'content_quality' in website_data:
                existing_notes = self.data.loc[mask, 'notes'].iloc[0] or ""
                website_note = f"Website Status: {website_data['status']} - Quality: {website_data['content_quality']}"
                new_notes = f"{existing_notes}\n{current_time}: {website_note}".strip()
                self.data.loc[mask, 'notes'] = new_notes

            business_name = self.data.loc[mask, 'business_name'].iloc[0]
            log_info(f"Updated website status for {business_name}: {website_data['status']}")
            return True

        except Exception as e:
            log_error(f"Failed to update website status for business ID: {business_id}", e)
            return False

    def get_businesses_for_website_check(self) -> pd.DataFrame:
        """Get businesses that need website status checking"""
        try:
            # Get businesses with websites but unknown status
            needs_check = self.data[
                (self.data['website'].notna()) &
                (self.data['website'] != '') &
                (self.data['website_status'].isin(['Unknown', 'Error', '']) |
                 self.data['website_status'].isna())
            ].copy()

            log_info(f"Found {len(needs_check)} businesses needing website check")
            return needs_check

        except Exception as e:
            log_error("Failed to get businesses for website check", e)
            return pd.DataFrame()