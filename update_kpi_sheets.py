"""
Update KPI Sheets Workflow
Main function to update the KPI Calculator Google Sheets with data for last week
"""

import logging
from datetime import datetime
from typing import Dict, Optional
import pandas as pd

from clients import ConnectionChecker
from core import KPIAggregator, AmplifyKPICalculator
from exporters import DataframeGenerator
from sheets import SheetsUpdater, GoogleSheetsClient
from utils import get_last_week_dates


def update_kpi_calculator_for_last_week(
    update_sheets: bool = True,
    save_dataframe: bool = True
) -> Dict:
    """
    Update KPI Calculator with last week's data
    
    Args:
        update_sheets: If True, update Google Sheets
        save_dataframe: If True, save comprehensive dataframe locally
        
    Returns:
        Dictionary with update results and summary
    """
    logger = logging.getLogger(__name__)
    
    results = {
        'success': False,
        'week_start': None,
        'week_end': None,
        'agents_updated': 0,
        'data_sources_used': [],
        'sheets_updated': False,
        'dataframe_saved': False,
        'dataframe_path': None,
        'message': ''
    }
    
    try:
        # Get last week dates
        week_start, week_end = get_last_week_dates()
        results['week_start'] = week_start.isoformat()
        results['week_end'] = week_end.isoformat()
        
        logger.info(f"Updating KPI Calculator for week: {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}")
        
        # Check connections
        checker = ConnectionChecker()
        connection_results = checker.check_all_connections()
        
        # Track available data sources
        data_sources = []
        if connection_results['tableau']['available']:
            data_sources.append('Tableau')
        if connection_results['google_sheets']['available']:
            data_sources.append('Google Sheets')
        if connection_results['salesforce']['available']:
            data_sources.append('Salesforce')
        else:
            # Try Google Drive as fallback
            try:
                from clients import GoogleDriveImporter
                importer = GoogleDriveImporter()
                if importer.connect():
                    data_sources.append('Google Drive (Salesforce CSV)')
            except:
                pass
        
        results['data_sources_used'] = data_sources
        
        if not data_sources:
            logger.error("No data sources available")
            results['message'] = 'No data sources available'
            return results
        
        # Initialize aggregator
        aggregator = KPIAggregator(week_start, week_end)
        
        # Load data from available sources
        logger.info("Loading data from available sources...")
        
        data_loaded = False
        
        # Load Tableau QA data
        if connection_results['tableau']['available']:
            if aggregator.load_tableau_qa_data():
                logger.info("✅ Tableau QA data loaded")
                data_loaded = True
        
        # Load Tableau KPI data
        if connection_results['tableau']['available']:
            if aggregator.load_tableau_kpi_data():
                logger.info("✅ Tableau KPI data loaded")
                data_loaded = True
        
        # Load Google Sheets SLA data
        if connection_results['google_sheets']['available']:
            if aggregator.load_google_sheets_sla_data():
                logger.info("✅ Google Sheets SLA data loaded")
                data_loaded = True
        
        # Load Salesforce data (or Google Drive CSVs)
        if connection_results['salesforce']['available'] or 'Google Drive' in str(data_sources):
            if aggregator.load_salesforce_data():
                logger.info("✅ Salesforce/Drive data loaded")
                data_loaded = True
        
        if not data_loaded:
            logger.error("Failed to load data from any source")
            results['message'] = 'Failed to load data from any source'
            return results
        
        # Generate Export-KPI and Export-QA tabs
        logger.info("Generating Export tabs...")
        export_kpi = aggregator.generate_export_kpi_tab()
        export_qa = aggregator.generate_export_qa_tab()
        
        if export_kpi is None and export_qa is None:
            logger.error("Failed to generate export tabs")
            results['message'] = 'Failed to generate export tabs'
            return results
        
        if export_kpi is not None:
            results['agents_updated'] = len(export_kpi)
        
        # Update Google Sheets if requested
        if update_sheets and (export_kpi is not None or export_qa is not None):
            logger.info("Updating Google Sheets...")
            
            sheets_client = GoogleSheetsClient()
            updater = SheetsUpdater(sheets_client)
            
            update_results = updater.update_both_sheets(export_kpi, export_qa)
            
            if update_results['kpi'] or update_results['qa']:
                results['sheets_updated'] = True
                logger.info("✅ Google Sheets updated successfully")
            else:
                logger.warning("⚠️  Failed to update Google Sheets")
                results['message'] = 'Failed to update Google Sheets'
        
        # Generate comprehensive dataframe if requested
        if save_dataframe and (export_kpi is not None or export_qa is not None):
            logger.info("Generating comprehensive dataframe...")
            
            # Initialize calculator
            if export_kpi is not None:
                calculator = AmplifyKPICalculator(export_kpi)
                
                # Initialize dataframe generator
                dataframe_gen = DataframeGenerator(sheets_client)
                
                # Generate and save comprehensive dataframe
                comprehensive_df, filepath = dataframe_gen.generate_and_save(
                    export_kpi, export_qa, week_start, week_end
                )
                
                if filepath:
                    results['dataframe_saved'] = True
                    results['dataframe_path'] = str(filepath)
                    logger.info(f"✅ Comprehensive dataframe saved: {filepath}")
        
        results['success'] = True
        results['message'] = f'Successfully updated {len(export_kpi) if export_kpi is not None else 0} agents'
        
        logger.info("✅ KPI Calculator update complete")
        
        return results
        
    except Exception as e:
        logger.error(f"Error updating KPI Calculator: {e}")
        results['message'] = f'Error: {str(e)}'
        return results


# Standalone usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("="*70)
    print("Update KPI Sheets - Running")
    print("="*70)
    print()
    
    # Run update
    results = update_kpi_calculator_for_last_week(
        update_sheets=True,
        save_dataframe=True
    )
    
    # Display results
    print("\n" + "="*70)
    print("UPDATE RESULTS")
    print("="*70)
    
    if results['success']:
        print("✅ Success!")
        print(f"\nWeek: {results['week_start']} to {results['week_end']}")
        print(f"Agents Updated: {results['agents_updated']}")
        print(f"Data Sources: {', '.join(results['data_sources_used'])}")
        print(f"Sheets Updated: {results['sheets_updated']}")
        print(f"Dataframe Saved: {results['dataframe_saved']}")
        
        if results['dataframe_path']:
            print(f"\nDataframe saved to: {results['dataframe_path']}")
    else:
        print("❌ Failed!")
        print(f"Error: {results['message']}")
    
    print("\n" + "="*70)
