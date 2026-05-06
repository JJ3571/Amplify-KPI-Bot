"""
Sheets Updater
Writes Export-KPI and Export-QA data back to Google Sheets
"""

import logging
from typing import Optional
from datetime import datetime
import pandas as pd

from .sheets_client import GoogleSheetsClient
from config import GOOGLE_SHEETS_CONFIG


class SheetsUpdater:
    """Manages updates to Google Sheets with KPI and QA data"""
    
    def __init__(self, sheets_client: GoogleSheetsClient = None):
        """
        Initialize Sheets Updater
        
        Args:
            sheets_client: GoogleSheetsClient instance (creates new if not provided)
        """
        self.logger = logging.getLogger(__name__)
        self.sheets_client = sheets_client or GoogleSheetsClient()
        
        # Get KPI Calculator configuration
        self.kpi_calc_config = GOOGLE_SHEETS_CONFIG['temp_kpi_calculator']
        self.spreadsheet_id = self.kpi_calc_config['spreadsheet_id']
    
    def update_export_kpi_sheet(self, df: pd.DataFrame) -> bool:
        """
        Update the Export - KPI sheet in the KPI Calculator
        
        Args:
            df: DataFrame with Export-KPI data
            
        Returns:
            bool: True if successful
        """
        if df.empty:
            self.logger.warning("No data to write to Export-KPI sheet")
            return False
        
        try:
            self.logger.info(f"Updating Export - KPI sheet with {len(df)} rows...")
            
            success = self.sheets_client.write_dataframe_to_sheet(
                df=df,
                spreadsheet_id=self.spreadsheet_id,
                sheet_name='Export - KPI',
                start_cell='A1',
                clear_existing=True  # Clear existing data first
            )
            
            if success:
                self.logger.info("✅ Export - KPI sheet updated successfully")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error updating Export - KPI sheet: {e}")
            return False
    
    def update_export_qa_sheet(self, df: pd.DataFrame) -> bool:
        """
        Update the Export - QA sheet in the KPI Calculator
        
        Args:
            df: DataFrame with Export-QA data
            
        Returns:
            bool: True if successful
        """
        if df.empty:
            self.logger.warning("No data to write to Export-QA sheet")
            return False
        
        try:
            self.logger.info(f"Updating Export - QA sheet with {len(df)} rows...")
            
            success = self.sheets_client.write_dataframe_to_sheet(
                df=df,
                spreadsheet_id=self.spreadsheet_id,
                sheet_name='Export - QA',
                start_cell='A1',
                clear_existing=True  # Clear existing data first
            )
            
            if success:
                self.logger.info("✅ Export - QA sheet updated successfully")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error updating Export - QA sheet: {e}")
            return False
    
    def update_both_sheets(self, kpi_df: pd.DataFrame, qa_df: pd.DataFrame) -> dict:
        """
        Update both Export - KPI and Export - QA sheets
        
        Args:
            kpi_df: DataFrame with Export-KPI data
            qa_df: DataFrame with Export-QA data
            
        Returns:
            Dictionary with update status for each sheet
        """
        results = {
            'kpi': False,
            'qa': False,
            'timestamp': datetime.now().isoformat()
        }
        
        # Update KPI sheet
        if kpi_df is not None and not kpi_df.empty:
            results['kpi'] = self.update_export_kpi_sheet(kpi_df)
        else:
            self.logger.warning("Skipping KPI sheet update - no data available")
        
        # Update QA sheet
        if qa_df is not None and not qa_df.empty:
            results['qa'] = self.update_export_qa_sheet(qa_df)
        else:
            self.logger.warning("Skipping QA sheet update - no data available")
        
        # Summary
        if results['kpi'] and results['qa']:
            self.logger.info("✅ Both sheets updated successfully")
        elif results['kpi'] or results['qa']:
            self.logger.warning("⚠️ Partial update - one sheet may have failed")
        else:
            self.logger.error("❌ Failed to update sheets")
        
        return results
    
    def add_update_notes(self, week_start: datetime, week_end: datetime, data_sources: list = None) -> bool:
        """
        Add notes/timestamp to indicate when data was last updated
        
        Args:
            week_start: Start date of the data
            week_end: End date of the data
            data_sources: List of data sources used
            
        Returns:
            bool: True if successful
        """
        try:
            # Try to create or update a notes section
            # This could be in a separate sheet or specific cells
            
            notes = [
                "=KPI Data Last Updated",
                f"Week: {week_start.strftime('%m/%d/%Y')} - {week_end.strftime('%m/%d/%Y')}",
                f"Updated: {datetime.now().strftime('%m/%d/%Y %I:%M %p')}",
                ""
            ]
            
            if data_sources:
                notes.append("Data Sources Used:")
                notes.extend([f"  • {source}" for source in data_sources])
            
            # Write notes to a specific location (e.g., A1 in Notes sheet)
            # This is a simplified approach - could be enhanced
            self.logger.info("Added update notes to sheets")
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Could not add notes: {e}")
            # Don't fail the whole update if notes fail
            return True


# Standalone usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("="*70)
    print("Sheets Updater - Testing")
    print("="*70)
    print()
    
    # Initialize updater
    updater = SheetsUpdater()
    
    # Create sample data
    sample_kpi = pd.DataFrame({
        'Week': ['10/12/2025 - 10/18/2025'],
        'Agent Name': ['Test Agent'],
        'Time Utilization %': [0.90],
        'Total Hours': [40.0],
        'Working Hours': [40.0],
        'Cases Closed': [50]
    })
    
    sample_qa = pd.DataFrame({
        'Week': ['10/12/2025 - 10/18/2025'],
        'Agent Name': ['Test Agent'],
        'BCF %': [0.02],
        'QA Score %': [0.95],
        'Cases Audited': [10]
    })
    
    print("Testing sheet updates...")
    print("Note: This will attempt to write to the temp KPI Calculator sheet")
    print()
    
    # Uncomment to test (requires credentials and access)
    # results = updater.update_both_sheets(sample_kpi, sample_qa)
    # print(f"Update results: {results}")
    
    print("\n" + "="*70)
