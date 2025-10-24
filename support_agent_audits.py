"""
Support Agent Audits Data Retrieval
Helper functions for pulling CS Agent QA data from Tableau
"""

from tableau_client import TableauClient
from config import TABLEAU_CONFIG, DATA_PATHS, GENERAL_DEFALTS
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Workbook and View IDs
SUPPORT_AUDITS_WORKBOOK_ID = TABLEAU_CONFIG['workbooks']['support_agent_audits']
CS_AGENT_AUDITS_VIEW_ID = TABLEAU_CONFIG['views']['cs_agent_audits']

# Ensure data directories exist
Path(DATA_PATHS['qa']).mkdir(parents=True, exist_ok=True)


def get_last_week_dates():
    """
    Get the start and end dates for last week (Sunday to Saturday)
    
    Returns:
        tuple: (start_date, end_date) as datetime objects
    """
    today = datetime.now()
    # Find last Sunday
    days_since_sunday = (today.weekday() + 1) % 7  # Monday = 0, Sunday = 6
    last_sunday = today - timedelta(days=days_since_sunday + 7)
    last_saturday = last_sunday + timedelta(days=6)
    
    return last_sunday, last_saturday


def get_agent_audits_data(week_start=None, week_end=None, max_age=-1):
    """
    Retrieve CS Agent Audits data from Tableau
    
    Args:
        week_start (datetime): Start of week filter (defaults to last week)
        week_end (datetime): End of week filter (defaults to last week)
        max_age (int): Maximum age of cached data in minutes (-1 for live data)
    
    Returns:
        pd.DataFrame: Agent audit data with columns: Agent Name, Cases, Avg Score, Fail %
    
    Note:
        Tableau REST API v3.19 has limited filter support via the API.
        Filters must be applied in the view definition or via URL parameters.
        The data is returned in "long" format and will be pivoted to "wide" format.
    """
    # Default to last week if not specified
    if week_start is None or week_end is None:
        week_start, week_end = get_last_week_dates()
    
    logging.info(f"Retrieving agent audit data")
    logging.info(f"Week: {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}")
    
    with TableauClient() as client:
        # Connect to Tableau
        if not client.connect(TABLEAU_CONFIG['server_url'], TABLEAU_CONFIG['site_name']):
            logging.error("Failed to connect to Tableau")
            return None
        
        # Query the view
        df = client.query_view(CS_AGENT_AUDITS_VIEW_ID, max_age=max_age)
        
        if df is None:
            logging.error("Failed to retrieve data from view")
            return None
        
        logging.info(f"Retrieved {len(df)} rows with {len(df.columns)} columns")
        logging.info(f"Columns: {list(df.columns)}")
        
        # Pivot the data from long to wide format
        # Long format: Agent Name | Measure Names | Measure Values
        # Wide format: Agent Name | Cases | Avg Score | Fail %
        if 'Measure Names' in df.columns and 'Measure Values' in df.columns:
            logging.info("Pivoting data from long to wide format...")
            df_wide = df.pivot(index='Agent Name', columns='Measure Names', values='Measure Values')
            df_wide = df_wide.reset_index()
            logging.info(f"Pivoted to {len(df_wide)} rows with columns: {list(df_wide.columns)}")
            return df_wide
        else:
            # Data is already in wide format
            return df


def filter_agent_audits_by_week(df, week_start, week_end):
    """
    Filter agent audits DataFrame by week
    
    Args:
        df (pd.DataFrame): Agent audits data
        week_start (datetime): Start of week
        week_end (datetime): End of week
    
    Returns:
        pd.DataFrame: Filtered data
    """
    # Try to find date column (might be named differently)
    date_columns = [col for col in df.columns if 'date' in col.lower() or 'week' in col.lower()]
    
    if not date_columns:
        logging.warning("No date column found - returning unfiltered data")
        return df
    
    date_col = date_columns[0]
    logging.info(f"Filtering by date column: {date_col}")
    
    # Convert to datetime if not already
    df[date_col] = pd.to_datetime(df[date_col])
    
    # Filter to week range
    mask = (df[date_col] >= week_start) & (df[date_col] <= week_end)
    filtered_df = df[mask]
    
    logging.info(f"Filtered from {len(df)} to {len(filtered_df)} rows")
    
    return filtered_df


def get_last_week_agent_scores():
    """
    Get last week's agent audit scores (most common use case)
    
    Returns:
        pd.DataFrame: Agent scores for last week with columns:
                     - Agent Name
                     - Cases
                     - Avg Score
                     - Fail %
    """
    df = get_agent_audits_data()
    
    if df is None:
        return None
    
    # Filter to last week
    week_start, week_end = get_last_week_dates()
    df_filtered = filter_agent_audits_by_week(df, week_start, week_end)
    
    return df_filtered


def get_multi_week_agent_scores(num_weeks=4):
    """
    Get agent audit scores for multiple weeks
    
    Args:
        num_weeks (int): Number of weeks to retrieve (going back from last week)
    
    Returns:
        pd.DataFrame: Agent scores for the specified number of weeks
    """
    df = get_agent_audits_data()
    
    if df is None:
        return None
    
    # Calculate date range
    today = datetime.now()
    days_since_sunday = (today.weekday() + 1) % 7
    last_sunday = today - timedelta(days=days_since_sunday + 7)
    
    # Go back num_weeks
    start_date = last_sunday - timedelta(weeks=num_weeks - 1)
    end_date = last_sunday + timedelta(days=6)  # Last Saturday
    
    logging.info(f"Retrieving {num_weeks} weeks of data")
    logging.info(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Filter data
    df_filtered = filter_agent_audits_by_week(df, start_date, end_date)
    
    return df_filtered


def save_agent_audits_to_csv(df, filename=None, start_date=None, end_date=None):
    """
    Save agent audits data to CSV with date range in filename
    
    Args:
        df (pd.DataFrame): Agent audits data
        filename (str): Output filename (if None, auto-generates with date range)
        start_date (datetime): Start date for filename
        end_date (datetime): End date for filename
    
    Returns:
        str: Path to saved file
    """
    if filename is None:
        # Auto-generate filename with date range
        if start_date is None or end_date is None:
            start_date, end_date = get_last_week_dates()
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        filename = f"QA_{start_str}_{end_str}.csv"
    
    # Save to qa data folder
    filepath = Path(DATA_PATHS['qa']) / filename
    df.to_csv(filepath, index=False)
    logging.info(f"Saved to {filepath}")
    
    return str(filepath)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("="*70)
    print("Support Agent Audits - Data Retrieval")
    print("="*70)
    print()
    
    # Test 1: Get last week's data
    print("📊 Retrieving last week's agent audit scores...")
    week_start, week_end = get_last_week_dates()
    df = get_last_week_agent_scores()
    
    if df is not None:
        print(f"\n✅ Retrieved {len(df)} rows")
        print(f"   Date range: {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}")
        print(f"\nColumns: {list(df.columns)}")
        print(f"\nFirst few rows:")
        print(df.head(10))
        
        # Save to CSV with date range in filename
        filepath = save_agent_audits_to_csv(df, start_date=week_start, end_date=week_end)
        print(f"\n💾 Saved to: {filepath}")
    else:
        print("\n❌ Failed to retrieve data")
    
    print("\n" + "="*70)
    
    # Test 2: Get multi-week data
    print("\n📊 Retrieving 4 weeks of agent audit data...")
    num_weeks = 4
    
    # Calculate date range for multi-week
    today = datetime.now()
    days_since_sunday = (today.weekday() + 1) % 7
    last_sunday = today - timedelta(days=days_since_sunday + 7)
    multi_start = last_sunday - timedelta(weeks=num_weeks - 1)
    multi_end = last_sunday + timedelta(days=6)
    
    df_multi = get_multi_week_agent_scores(num_weeks=num_weeks)
    
    if df_multi is not None:
        print(f"\n✅ Retrieved {len(df_multi)} rows")
        print(f"   Date range: {multi_start.strftime('%Y-%m-%d')} to {multi_end.strftime('%Y-%m-%d')}")
        print(f"\nFirst few rows:")
        print(df_multi.head())
        
        # Save to CSV with date range in filename
        filepath = save_agent_audits_to_csv(df_multi, start_date=multi_start, end_date=multi_end)
        print(f"\n💾 Saved to: {filepath}")
    else:
        print("\n❌ Failed to retrieve data")
    
    print("\n" + "="*70)
