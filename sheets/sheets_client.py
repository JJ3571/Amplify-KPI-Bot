"""
Google Sheets Client
Handles authentication and data retrieval from Google Sheets
"""

import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import pandas as pd

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False
    logging.warning("gspread not installed. Install with: pip install gspread google-auth")

from config import GOOGLE_SHEETS_SCOPES, CREDENTIALS_FILE, GOOGLE_SHEETS_CONFIG


class GoogleSheetsClient:
    """Client for accessing Google Sheets data"""
    
    def __init__(self, credentials_file: str = CREDENTIALS_FILE):
        """
        Initialize Google Sheets client
        
        Args:
            credentials_file: Path to service account credentials JSON file
        """
        if not GSPREAD_AVAILABLE:
            raise ImportError(
                "gspread is required for Google Sheets integration. "
                "Install with: pip install gspread google-auth"
            )
        
        self.credentials_file = credentials_file
        self.client = None
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> bool:
        """
        Authenticate and connect to Google Sheets
        
        Returns:
            bool: True if connection successful
        """
        try:
            # Check if credentials file has Google service account
            with open(self.credentials_file, 'r') as f:
                creds_data = json.load(f)
            
            # Check if it's a service account file
            if 'type' in creds_data and creds_data['type'] == 'service_account':
                # Use service account credentials
                creds = Credentials.from_service_account_file(
                    self.credentials_file,
                    scopes=GOOGLE_SHEETS_SCOPES
                )
                self.client = gspread.authorize(creds)
                self.logger.info("✅ Connected to Google Sheets using service account")
                return True
            else:
                self.logger.error(
                    "credentials.json doesn't contain Google service account credentials. "
                    "Add 'google_service_account' key with service account JSON content."
                )
                return False
                
        except FileNotFoundError:
            self.logger.error(f"Credentials file not found: {self.credentials_file}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to connect to Google Sheets: {e}")
            return False
    
    def get_spreadsheet(self, spreadsheet_id: str):
        """
        Get a spreadsheet by ID
        
        Args:
            spreadsheet_id: The Google Sheets spreadsheet ID
            
        Returns:
            gspread.Spreadsheet object
        """
        if not self.client:
            if not self.connect():
                raise RuntimeError("Failed to connect to Google Sheets")
        
        try:
            return self.client.open_by_key(spreadsheet_id)
        except PermissionError as e:
            # Check for specific API not enabled error
            error_msg = str(e.__cause__) if hasattr(e, '__cause__') else str(e)
            if 'API has not been used' in error_msg or 'is disabled' in error_msg:
                self.logger.error(
                    "Google Sheets API is not enabled. "
                    "Enable it at: https://console.cloud.google.com/apis/library/sheets.googleapis.com"
                )
                raise RuntimeError(
                    "Google Sheets API not enabled. Visit:\n"
                    "https://console.cloud.google.com/apis/library/sheets.googleapis.com\n"
                    "Click 'Enable' and wait a few minutes before retrying."
                ) from e
            elif 'permission' in error_msg.lower():
                self.logger.error(
                    f"Permission denied accessing spreadsheet {spreadsheet_id}. "
                    "Ensure the sheet is shared with your service account."
                )
                raise RuntimeError(
                    f"Permission denied. Please share the Google Sheet with your service account email.\n"
                    f"Spreadsheet ID: {spreadsheet_id}"
                ) from e
            else:
                raise
        except Exception as e:
            self.logger.error(f"Failed to open spreadsheet {spreadsheet_id}: {e}")
            raise
    
    def get_worksheet(self, spreadsheet_id: str, sheet_name: str):
        """
        Get a specific worksheet from a spreadsheet
        
        Args:
            spreadsheet_id: The Google Sheets spreadsheet ID
            sheet_name: Name of the worksheet/tab
            
        Returns:
            gspread.Worksheet object
        """
        spreadsheet = self.get_spreadsheet(spreadsheet_id)
        try:
            return spreadsheet.worksheet(sheet_name)
        except Exception as e:
            self.logger.error(f"Failed to open worksheet '{sheet_name}': {e}")
            self.logger.info(f"Available sheets: {[ws.title for ws in spreadsheet.worksheets()]}")
            raise
    
    def read_sheet_data(
        self, 
        spreadsheet_id: str, 
        sheet_name: str,
        header_row: int = 1
    ) -> pd.DataFrame:
        """
        Read all data from a worksheet into a DataFrame
        
        Args:
            spreadsheet_id: The Google Sheets spreadsheet ID
            sheet_name: Name of the worksheet/tab
            header_row: Row number containing headers (1-indexed)
            
        Returns:
            pd.DataFrame with the sheet data
        """
        worksheet = self.get_worksheet(spreadsheet_id, sheet_name)
        
        # Get all values
        data = worksheet.get_all_values()
        
        if not data:
            return pd.DataFrame()
        
        # Use specified row as header
        headers = data[header_row - 1]
        data_rows = data[header_row:]
        
        df = pd.DataFrame(data_rows, columns=headers)
        
        self.logger.info(
            f"Read {len(df)} rows from '{sheet_name}' "
            f"with {len(df.columns)} columns"
        )
        
        return df
    
    def read_range(
        self, 
        spreadsheet_id: str, 
        sheet_name: str,
        range_notation: str
    ) -> List[List[Any]]:
        """
        Read a specific range from a worksheet
        
        Args:
            spreadsheet_id: The Google Sheets spreadsheet ID
            sheet_name: Name of the worksheet/tab
            range_notation: A1 notation (e.g., 'A1:D10')
            
        Returns:
            List of lists containing cell values
        """
        worksheet = self.get_worksheet(spreadsheet_id, sheet_name)
        return worksheet.get(range_notation)
    
    def write_dataframe_to_sheet(
        self,
        df: pd.DataFrame,
        spreadsheet_id: str,
        sheet_name: str,
        start_cell: str = 'A1',
        clear_existing: bool = True
    ) -> bool:
        """
        Write a DataFrame to a Google Sheet
        
        Args:
            df: DataFrame to write
            spreadsheet_id: The Google Sheets spreadsheet ID
            sheet_name: Name of the worksheet/tab
            start_cell: Starting cell (e.g., 'A1')
            clear_existing: If True, clear all existing data in the sheet first
            
        Returns:
            bool: True if successful
        """
        try:
            worksheet = self.get_worksheet(spreadsheet_id, sheet_name)
            
            # Clear existing data if requested
            if clear_existing:
                self.logger.info(f"Clearing existing data from '{sheet_name}'...")
                worksheet.clear()
            
            # Convert DataFrame to list of lists
            # Include headers
            data = [df.columns.tolist()] + df.values.tolist()
            
            # Write data starting at start_cell
            worksheet.update(start_cell, data)
            
            self.logger.info(
                f"✅ Wrote {len(df)} rows to '{sheet_name}' "
                f"(starting at {start_cell})"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error writing to '{sheet_name}': {e}")
            return False
    
    def write_dict_list_to_sheet(
        self,
        data: List[Dict],
        spreadsheet_id: str,
        sheet_name: str,
        start_cell: str = 'A1',
        clear_existing: bool = True
    ) -> bool:
        """
        Write a list of dictionaries to a Google Sheet
        
        Args:
            data: List of dictionaries to write
            spreadsheet_id: The Google Sheets spreadsheet ID
            sheet_name: Name of the worksheet/tab
            start_cell: Starting cell (e.g., 'A1')
            clear_existing: If True, clear all existing data in the sheet first
            
        Returns:
            bool: True if successful
        """
        if not data:
            self.logger.warning("No data to write")
            return False
        
        # Convert to DataFrame and write
        df = pd.DataFrame(data)
        return self.write_dataframe_to_sheet(
            df, spreadsheet_id, sheet_name, start_cell, clear_existing
        )
    
    def clear_sheet_range(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        range_notation: str
    ) -> bool:
        """
        Clear a range of cells in a worksheet
        
        Args:
            spreadsheet_id: The Google Sheets spreadsheet ID
            sheet_name: Name of the worksheet/tab
            range_notation: A1 notation range (e.g., 'A2:Z100')
            
        Returns:
            bool: True if successful
        """
        try:
            worksheet = self.get_worksheet(spreadsheet_id, sheet_name)
            worksheet.batch_clear([range_notation])
            self.logger.info(f"Cleared range: {range_notation}")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing range: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.client = None
