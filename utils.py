"""
Shared utility functions for Amplify KPI Bot
Consolidates common functionality used across multiple modules
"""

import logging
from datetime import datetime, timedelta
from config import GENERAL_DEFAULTS


def setup_logging(level=logging.INFO, log_file='kpi_bot.log'):
    """
    Configure logging for the application
    
    Args:
        level: Logging level (default: INFO)
        log_file: Path to log file (default: kpi_bot.log)
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


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


def get_week_boundaries(
    reference_date=None,
    week_start=None,
    week_end=None
):
    """
    Get the start and end dates for a week
    
    Args:
        reference_date: Date to calculate week for (defaults to today)
        week_start: Day of week that starts the week (defaults to GENERAL_DEFAULTS)
        week_end: Day of week that ends the week (defaults to GENERAL_DEFAULTS)
    
    Returns:
        Tuple of (week_start_date, week_end_date)
    """
    if reference_date is None:
        reference_date = datetime.now()
    
    # Use defaults from config if not specified
    if week_start is None:
        week_start = GENERAL_DEFAULTS['week_start_day']
    if week_end is None:
        week_end = GENERAL_DEFAULTS['week_end_day']
    
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

