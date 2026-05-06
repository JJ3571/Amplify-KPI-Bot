"""
Support Services KPI Data Retrieval
Helper functions for pulling KPI metrics from Tableau Support Services KPI Scorecard
"""

from clients import TableauClient
from config import TABLEAU_CONFIG, DATA_PATHS
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import logging
from utils import get_last_week_dates

# Workbook and View IDs
KPI_SCORECARD_WORKBOOK_ID = TABLEAU_CONFIG['workbooks']['kpi_scorecard']

# Individual metric view IDs
VIEW_IDS = {
    'csat_talkdesk': TABLEAU_CONFIG['views']['csat_talkdesk'],
    'csat_chat': TABLEAU_CONFIG['views']['csat_chat'],
    'response_time_chat': TABLEAU_CONFIG['views']['response_time_chat'],
    'response_time_email': TABLEAU_CONFIG['views']['response_time_email'],
    'response_time_phone': TABLEAU_CONFIG['views']['response_time_phone'],
    'resolution_time': TABLEAU_CONFIG['views']['resolution_time'],
    'escalation_time': TABLEAU_CONFIG['views']['escalation_time']
}

# Ensure data directories exist
Path(DATA_PATHS['kpi']).mkdir(parents=True, exist_ok=True)


def get_csat_scores(week_start=None, week_end=None, max_age=-1):
    """
    Retrieve CSAT scores from Tableau (Talkdesk data)
    
    Args:
        week_start (datetime): Start of week filter
        week_end (datetime): End of week filter
        max_age (int): Maximum age of cached data in minutes (-1 for live)
    
    Returns:
        pd.DataFrame: CSAT data with columns: Day, Agent Name, CSAT Score, etc.
    """
    if week_start is None or week_end is None:
        week_start, week_end = get_last_week_dates()
    
    logging.info(f"Retrieving CSAT scores")
    logging.info(f"Week: {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}")
    
    with TableauClient() as client:
        if not client.connect(TABLEAU_CONFIG['server_url'], TABLEAU_CONFIG['site_name']):
            logging.error("Failed to connect to Tableau")
            return None
        
        df = client.query_view(VIEW_IDS['csat_talkdesk'], max_age=max_age)
        
        if df is None:
            logging.error("Failed to retrieve CSAT data")
            return None
        
        logging.info(f"Retrieved {len(df)} CSAT records")
        return df


def get_response_times(metric_type='email', week_start=None, week_end=None, max_age=-1):
    """
    Retrieve response time data for chat, email, or phone
    
    Args:
        metric_type (str): Type of metric - 'chat', 'email', or 'phone'
        week_start (datetime): Start of week filter
        week_end (datetime): End of week filter
        max_age (int): Maximum age of cached data in minutes (-1 for live)
    
    Returns:
        pd.DataFrame: Response time data
    """
    if week_start is None or week_end is None:
        week_start, week_end = get_last_week_dates()
    
    view_key = f'response_time_{metric_type}'
    
    if view_key not in VIEW_IDS:
        logging.error(f"Invalid metric type: {metric_type}")
        return None
    
    logging.info(f"Retrieving {metric_type} response times")
    logging.info(f"Week: {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}")
    
    with TableauClient() as client:
        if not client.connect(TABLEAU_CONFIG['server_url'], TABLEAU_CONFIG['site_name']):
            logging.error("Failed to connect to Tableau")
            return None
        
        df = client.query_view(VIEW_IDS[view_key], max_age=max_age)
        
        if df is None:
            logging.error(f"Failed to retrieve {metric_type} response time data")
            return None
        
        logging.info(f"Retrieved {len(df)} {metric_type} response time records")
        return df


def get_resolution_time_data(week_start=None, week_end=None, max_age=-1):
    """
    Retrieve case resolution time data
    
    Args:
        week_start (datetime): Start of week filter
        week_end (datetime): End of week filter
        max_age (int): Maximum age of cached data in minutes (-1 for live)
    
    Returns:
        pd.DataFrame: Resolution time data with case details
    """
    if week_start is None or week_end is None:
        week_start, week_end = get_last_week_dates()
    
    logging.info(f"Retrieving case resolution time data")
    logging.info(f"Week: {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}")
    
    with TableauClient() as client:
        if not client.connect(TABLEAU_CONFIG['server_url'], TABLEAU_CONFIG['site_name']):
            logging.error("Failed to connect to Tableau")
            return None
        
        df = client.query_view(VIEW_IDS['resolution_time'], max_age=max_age)
        
        if df is None:
            logging.error("Failed to retrieve resolution time data")
            return None
        
        logging.info(f"Retrieved {len(df)} case resolution records")
        return df


def aggregate_agent_kpis(week_start=None, week_end=None):
    """
    Aggregate all KPI metrics by agent for a given week
    
    Args:
        week_start (datetime): Start of week
        week_end (datetime): End of week
    
    Returns:
        pd.DataFrame: Aggregated KPI data by agent
    """
    if week_start is None or week_end is None:
        week_start, week_end = get_last_week_dates()
    
    logging.info(f"Aggregating KPI data by agent")
    logging.info(f"Week: {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}")
    
    all_data = {}
    
    # Get CSAT scores
    csat_df = get_csat_scores(week_start, week_end)
    if csat_df is not None and len(csat_df) > 0:
        all_data['csat'] = csat_df
    
    # Get response times
    for metric_type in ['email', 'phone']:  # Chat data seems unavailable
        response_df = get_response_times(metric_type, week_start, week_end)
        if response_df is not None and len(response_df) > 0:
            all_data[f'response_{metric_type}'] = response_df
    
    # Get resolution times
    resolution_df = get_resolution_time_data(week_start, week_end)
    if resolution_df is not None and len(resolution_df) > 0:
        all_data['resolution'] = resolution_df
    
    if not all_data:
        logging.warning("No data retrieved from any views")
        return None
    
    logging.info(f"Retrieved data from {len(all_data)} metric views")
    
    # TODO: Aggregate by agent name
    # This would require joining/grouping the data by agent
    # For now, return the raw data dictionary
    
    return all_data


def save_kpi_data_to_csv(df, metric_name, start_date=None, end_date=None, filename=None):
    """
    Save KPI data to CSV with proper naming
    
    Args:
        df (pd.DataFrame): KPI data
        metric_name (str): Name of the metric (e.g., 'CSAT', 'ResponseTime_Email')
        start_date (datetime): Start date for filename
        end_date (datetime): End date for filename
        filename (str): Optional custom filename
    
    Returns:
        str: Path to saved file
    """
    if filename is None:
        if start_date is None or end_date is None:
            start_date, end_date = get_last_week_dates()
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        filename = f"KPI_{metric_name}_{start_str}_{end_str}.csv"
    
    # Save to kpi data folder
    filepath = Path(DATA_PATHS['kpi']) / filename
    df.to_csv(filepath, index=False)
    logging.info(f"Saved to {filepath}")
    
    return str(filepath)


def get_last_week_kpi_data():
    """
    Get last week's KPI data (most common use case)
    
    Returns:
        dict: Dictionary of DataFrames for each metric
    """
    week_start, week_end = get_last_week_dates()
    return aggregate_agent_kpis(week_start, week_end)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("="*70)
    print("Support Services KPI - Data Retrieval")
    print("="*70)
    print()
    
    week_start, week_end = get_last_week_dates()
    print(f"Week: {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}\n")
    
    # Test 1: Get CSAT scores
    print("📊 Retrieving CSAT scores...")
    csat_df = get_csat_scores()
    
    if csat_df is not None:
        print(f"✅ Retrieved {len(csat_df)} CSAT records")
        print(f"Columns: {list(csat_df.columns)}")
        print(f"\nFirst few rows:")
        print(csat_df.head(10))
        
        filepath = save_kpi_data_to_csv(csat_df, 'CSAT', week_start, week_end)
        print(f"\n💾 Saved to: {filepath}")
    else:
        print("❌ Failed to retrieve CSAT data")
    
    print("\n" + "="*70 + "\n")
    
    # Test 2: Get email response times
    print("📊 Retrieving email response times...")
    email_df = get_response_times('email')
    
    if email_df is not None:
        print(f"✅ Retrieved {len(email_df)} email response records")
        print(f"Columns: {list(email_df.columns)}")
        print(f"\nFirst few rows:")
        print(email_df.head())
        
        filepath = save_kpi_data_to_csv(email_df, 'ResponseTime_Email', week_start, week_end)
        print(f"\n💾 Saved to: {filepath}")
    else:
        print("❌ Failed to retrieve email response data")
    
    print("\n" + "="*70 + "\n")
    
    # Test 3: Get phone response times
    print("📊 Retrieving phone response times...")
    phone_df = get_response_times('phone')
    
    if phone_df is not None:
        print(f"✅ Retrieved {len(phone_df)} phone response records")
        print(f"Columns: {list(phone_df.columns)}")
        print(f"\nFirst few rows:")
        print(phone_df.head())
        
        filepath = save_kpi_data_to_csv(phone_df, 'ResponseTime_Phone', week_start, week_end)
        print(f"\n💾 Saved to: {filepath}")
    else:
        print("❌ Failed to retrieve phone response data")
    
    print("\n" + "="*70 + "\n")
    
    # Test 4: Get resolution time data
    print("📊 Retrieving case resolution time data...")
    resolution_df = get_resolution_time_data()
    
    if resolution_df is not None:
        print(f"✅ Retrieved {len(resolution_df)} resolution records")
        print(f"Columns: {list(resolution_df.columns)}")
        print(f"\nFirst few rows:")
        print(resolution_df.head())
        
        filepath = save_kpi_data_to_csv(resolution_df, 'ResolutionTime', week_start, week_end)
        print(f"\n💾 Saved to: {filepath}")
    else:
        print("❌ Failed to retrieve resolution time data")
    
    print("\n" + "="*70)
