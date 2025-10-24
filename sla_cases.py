"""
SLA Cases Data Retrieval from Google Sheets
Retrieves daily SLA breach data from the SS Historical Data sheet
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple
import pandas as pd

from sheets_client import GoogleSheetsClient
from config import GOOGLE_SHEETS_CONFIG, DATA_PATHS, GENERAL_DEFALTS


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_week_boundaries(
    reference_date: Optional[datetime] = None,
    week_start: str = GENERAL_DEFALTS['week_start_day'],
    week_end: str = GENERAL_DEFALTS['week_end_day']
) -> Tuple[datetime, datetime]:
    """
    Get the start and end dates for a week
    
    Args:
        reference_date: Date to calculate week for (defaults to today)
        week_start: Day of week that starts the week (e.g., 'Sunday')
        week_end: Day of week that ends the week (e.g., 'Saturday')
    
    Returns:
        Tuple of (week_start_date, week_end_date)
    """
    if reference_date is None:
        reference_date = datetime.now()
    
    # Map day names to weekday numbers (0=Monday, 6=Sunday)
    day_map = {
        'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
        'Friday': 4, 'Saturday': 5, 'Sunday': 6
    }
    
    start_day_num = day_map[week_start]
    end_day_num = day_map[week_end]
    
    # Get current weekday (0=Monday, 6=Sunday)
    current_weekday = reference_date.weekday()
    
    # Calculate days to subtract to get to week start
    days_to_start = (current_weekday - start_day_num) % 7
    week_start_date = reference_date - timedelta(days=days_to_start)
    
    # Calculate days to add to get to week end
    days_to_end = (end_day_num - start_day_num) % 7
    week_end_date = week_start_date + timedelta(days=days_to_end)
    
    return week_start_date, week_end_date


def parse_date_header(header_value: str) -> Optional[datetime]:
    """
    Parse a date from a column header
    
    Common formats:
    - "10/12/2025" (M/D/YYYY)
    - "2025-10-12" (YYYY-MM-DD)
    - "Oct 12, 2025"
    
    Args:
        header_value: The header string to parse
    
    Returns:
        datetime object or None if parsing fails
    """
    if not header_value or not isinstance(header_value, str):
        return None
    
    # Try common date formats
    formats = [
        '%m/%d/%Y',      # 10/12/2025
        '%m/%d/%y',      # 10/12/25
        '%Y-%m-%d',      # 2025-10-12
        '%m-%d-%Y',      # 10-12-2025
        '%b %d, %Y',     # Oct 12, 2025
        '%B %d, %Y',     # October 12, 2025
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(header_value.strip(), fmt)
        except (ValueError, AttributeError):
            continue
    
    return None


def get_sla_data(
    week_start: datetime,
    week_end: datetime,
    spreadsheet_id: Optional[str] = None,
    sheet_name: Optional[str] = None
) -> pd.DataFrame:
    """
    Get SLA cases data for a specific date range
    
    Args:
        week_start: Start date for data retrieval
        week_end: End date for data retrieval
        spreadsheet_id: Google Sheets ID (defaults to config)
        sheet_name: Sheet name (defaults to config)
    
    Returns:
        DataFrame with columns: Agent Name, Date columns (one per day), Total
    """
    # Use config defaults if not specified
    config = GOOGLE_SHEETS_CONFIG['sla_cases']
    if spreadsheet_id is None:
        spreadsheet_id = config['spreadsheet_id']
    if sheet_name is None:
        sheet_name = config['sheet_name']
    
    logger.info(f"Retrieving SLA data from {week_start.date()} to {week_end.date()}")
    
    try:
        with GoogleSheetsClient() as client:
            # Read all data from the sheet
            df = client.read_sheet_data(
                spreadsheet_id=spreadsheet_id,
                sheet_name=sheet_name,
                header_row=config['date_header_row']
            )
            
            if df.empty:
                logger.warning("No data found in SLA sheet")
                return pd.DataFrame()
            
            # First column should be agent names
            agent_col = df.columns[0]
            
            # Parse date columns
            date_columns = {}
            for col in df.columns[1:]:  # Skip agent name column
                parsed_date = parse_date_header(col)
                if parsed_date:
                    # Only include dates within our range
                    if week_start <= parsed_date <= week_end:
                        date_columns[col] = parsed_date
            
            logger.info(f"Found {len(date_columns)} date columns in range")
            
            if not date_columns:
                logger.warning(
                    f"No date columns found within range "
                    f"{week_start.date()} to {week_end.date()}"
                )
                return pd.DataFrame()
            
            # Select agent column and date columns within range
            columns_to_keep = [agent_col] + list(date_columns.keys())
            filtered_df = df[columns_to_keep].copy()
            
            # Rename agent column to standard name
            filtered_df.rename(columns={agent_col: 'Agent Name'}, inplace=True)
            
            # Convert date columns to numeric (SLA counts)
            for col in date_columns.keys():
                filtered_df[col] = pd.to_numeric(
                    filtered_df[col], 
                    errors='coerce'
                ).fillna(0)
            
            # Calculate total SLAs for the period
            date_cols = [col for col in filtered_df.columns if col != 'Agent Name']
            filtered_df['Total SLAs'] = filtered_df[date_cols].sum(axis=1)
            
            # Remove rows with no agent name
            filtered_df = filtered_df[
                filtered_df['Agent Name'].notna() & 
                (filtered_df['Agent Name'] != '')
            ]
            
            logger.info(
                f"Retrieved SLA data for {len(filtered_df)} agents, "
                f"{len(date_cols)} days"
            )
            
            return filtered_df
            
    except Exception as e:
        logger.error(f"Error retrieving SLA data: {e}")
        raise


def get_last_week_sla_data() -> pd.DataFrame:
    """
    Get SLA data for last week (most recent complete week)
    
    Returns:
        DataFrame with SLA data for last week
    """
    # Get last week's boundaries
    today = datetime.now()
    last_week_ref = today - timedelta(days=7)
    week_start, week_end = get_week_boundaries(last_week_ref)
    
    logger.info(f"Getting last week's SLA data: {week_start.date()} to {week_end.date()}")
    
    return get_sla_data(week_start, week_end)


def get_multi_week_sla_data(num_weeks: int = 4) -> pd.DataFrame:
    """
    Get SLA data for multiple weeks
    
    Args:
        num_weeks: Number of weeks to retrieve (default: 4)
    
    Returns:
        DataFrame with SLA data spanning multiple weeks
    """
    today = datetime.now()
    
    # Get the end of the most recent complete week
    last_week_ref = today - timedelta(days=7)
    _, week_end = get_week_boundaries(last_week_ref)
    
    # Calculate start date (num_weeks ago from week_end)
    week_start = week_end - timedelta(days=(num_weeks * 7 - 1))
    
    logger.info(
        f"Getting {num_weeks} weeks of SLA data: "
        f"{week_start.date()} to {week_end.date()}"
    )
    
    return get_sla_data(week_start, week_end)


def save_sla_data_to_csv(
    df: pd.DataFrame,
    week_start: datetime,
    week_end: datetime,
    output_dir: Optional[str] = None
) -> str:
    """
    Save SLA data to CSV with standardized naming
    
    Args:
        df: DataFrame to save
        week_start: Start date of the data
        week_end: End date of the data
        output_dir: Output directory (defaults to data/kpi/)
    
    Returns:
        Path to saved CSV file
    """
    if output_dir is None:
        output_dir = DATA_PATHS['kpi']
    
    # Create output directory if it doesn't exist
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # Format filename: SLA_YYYY-MM-DD_YYYY-MM-DD.csv
    start_str = week_start.strftime('%Y-%m-%d')
    end_str = week_end.strftime('%Y-%m-%d')
    filename = f"SLA_{start_str}_{end_str}.csv"
    filepath = os.path.join(output_dir, filename)
    
    # Save to CSV
    df.to_csv(filepath, index=False)
    logger.info(f"✅ Saved SLA data to: {filepath}")
    
    return filepath


if __name__ == "__main__":
    """
    Example usage: Retrieve and save last week's SLA data
    """
    print("SLA Cases Data Retrieval")
    print("=" * 60)
    
    try:
        # Get last week's data
        print("\n📊 Retrieving last week's SLA data...")
        sla_df = get_last_week_sla_data()
        
        if not sla_df.empty:
            print(f"\n✅ Retrieved data for {len(sla_df)} agents")
            print(f"   Columns: {list(sla_df.columns)}")
            print(f"\nTotal SLAs by agent (top 10):")
            print(
                sla_df[['Agent Name', 'Total SLAs']]
                .sort_values('Total SLAs', ascending=False)
                .head(10)
                .to_string(index=False)
            )
            
            # Save to CSV
            week_start, week_end = get_week_boundaries(
                datetime.now() - timedelta(days=7)
            )
            filepath = save_sla_data_to_csv(sla_df, week_start, week_end)
            print(f"\n💾 Data saved to: {filepath}")
            
        else:
            print("❌ No data retrieved")
    
    except RuntimeError as e:
        # User-friendly error messages
        print(f"\n❌ Setup Error: {e}")
        print("\n💡 Next Steps:")
        if "API not enabled" in str(e):
            print("   1. Visit the URL above to enable Google Sheets API")
            print("   2. Click the 'Enable' button")
            print("   3. Wait 2-3 minutes for changes to propagate")
            print("   4. Run this script again")
        elif "Permission denied" in str(e):
            print("   1. Open the Google Sheet in your browser")
            print("   2. Click 'Share' button")
            print("   3. Add your service account email")
            print("   4. Grant 'Viewer' or 'Editor' access")
        else:
            print("   See data/GOOGLE_SHEETS_SETUP.md for detailed setup instructions")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.exception("Failed to retrieve SLA data")
        print("\n💡 For help, see: data/GOOGLE_SHEETS_SETUP.md")
