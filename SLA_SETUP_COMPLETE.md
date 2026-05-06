# SLA Cases Setup Complete ✅

**Date**: October 21, 2025

---

## What Was Configured

### 1. Google Sheets Integration (New)

Created complete integration for retrieving SLA Cases data from Google Sheets.

**Google Sheet Details:**
- **Spreadsheet ID**: `1isXljGGYWbSgNbpYjVt5rN-3QsGn57frzMfWkdu9eDQ`
- **Sheet Name**: `SS Historical Data 3+ Day SLA Post March 2024`
- **URL**: https://docs.google.com/spreadsheets/d/1isXljGGYWbSgNbpYjVt5rN-3QsGn57frzMfWkdu9eDQ/edit

**Data Structure:**
```
Column A: Agent Names
Columns B+: Daily SLA counts (date headers in row 1)
Each cell: Number of SLA breaches for that agent on that date
```

---

## Files Created

### Core Modules

1. **`sheets_client.py`** - Google Sheets API client
   - Service account authentication
   - Spreadsheet and worksheet access
   - Data retrieval with pandas
   - Context manager support
   - Error handling and logging

2. **`sla_cases.py`** - SLA data retrieval module
   - `get_sla_data(week_start, week_end)` - Custom date range
   - `get_last_week_sla_data()` - Last week's data
   - `get_multi_week_sla_data(num_weeks)` - Multi-week data
   - `save_sla_data_to_csv()` - Automatic CSV saving
   - Date parsing for multiple formats
   - Automatic totaling across date range

### Documentation

3. **`data/GOOGLE_SHEETS_SETUP.md`** - Comprehensive setup guide
   - Authentication setup (service account + OAuth2)
   - Sheet structure documentation
   - Configuration instructions
   - Usage examples
   - Troubleshooting guide
   - Security best practices

---

## Configuration Updates

### `config.py`

Added new section for Google Sheets:

```python
# Google Sheets API configuration
GOOGLE_SHEETS_SCOPES = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets.readonly'
]

# Google Sheets Data Sources
GOOGLE_SHEETS_CONFIG = {
    'sla_cases': {
        'spreadsheet_id': '1isXljGGYWbSgNbpYjVt5rN-3QsGn57frzMfWkdu9eDQ',
        'sheet_name': 'SS Historical Data 3+ Day SLA Post March 2024',
        'description': 'SLA Cases data - daily tracking of cases out of SLA',
        'data_start_row': 2,
        'agent_column': 'A',
        'date_header_row': 1
    }
}
```

**Benefits:**
- ✅ Easy to update if sheet name changes
- ✅ Spreadsheet ID stored centrally
- ✅ Sheet structure documented in config
- ✅ No code changes needed for updates

---

## Documentation Updates

### `DOCS.md`
- Added SLA Cases (Google Sheets) as Data Source #3
- Included sheet structure diagram
- Added Google Sheets configuration section
- Added Google Sheets troubleshooting section

### `README.md`
- Added Google Sheets Integration feature
- Added SLA data to Quick Start commands
- Added `sla_cases.py` to data outputs
- Added link to Google Sheets setup guide

---

## Usage Examples

### Retrieve Last Week's SLA Data

```python
from sla_cases import get_last_week_sla_data, save_sla_data_to_csv
from datetime import datetime, timedelta

# Get data
sla_df = get_last_week_sla_data()

# Display summary
print(f"Agents: {len(sla_df)}")
print(sla_df[['Agent Name', 'Total SLAs']].head())

# Auto-save with date range in filename
from sla_cases import get_week_boundaries
week_start, week_end = get_week_boundaries(datetime.now() - timedelta(days=7))
save_sla_data_to_csv(sla_df, week_start, week_end)
# Saves to: data/kpi/SLA_2025-10-12_2025-10-18.csv
```

### Command Line

```bash
# Run directly to get last week's data
python sla_cases.py

# Output:
# - Displays top 10 agents by SLA count
# - Auto-saves to data/kpi/SLA_{dates}.csv
```

### Custom Date Range

```python
from sla_cases import get_sla_data
from datetime import datetime

week_start = datetime(2025, 10, 6)   # Sunday
week_end = datetime(2025, 10, 12)     # Saturday

sla_df = get_sla_data(week_start, week_end)
```

### Multi-Week Trends

```python
from sla_cases import get_multi_week_sla_data

# Get 4 weeks of SLA data
sla_df = get_multi_week_sla_data(num_weeks=4)
```

---

## Authentication Setup Required

To use the Google Sheets integration, you need to set up authentication:

### Option 1: Service Account (Recommended)

1. **Create Service Account** in Google Cloud Console
2. **Download credentials JSON**
3. **Share Google Sheet** with service account email
4. **Update credentials.json** with service account details

### Option 2: OAuth2 (User Account)

For personal use with your own Google account.

**See**: `data/GOOGLE_SHEETS_SETUP.md` for detailed setup instructions

---

## Output Format

### DataFrame Structure

```python
┌───────────────┬──────────┬──────────┬──────────┬────────────┐
│ Agent Name    │ 10/12/25 │ 10/13/25 │ 10/14/25 │ Total SLAs │
├───────────────┼──────────┼──────────┼──────────┼────────────┤
│ John Doe      │    2     │    1     │    0     │     3      │
│ Jane Smith    │    0     │    3     │    1     │     4      │
└───────────────┴──────────┴──────────┴──────────┴────────────┘
```

### CSV Files

Saved to: `data/kpi/SLA_{START}_{END}.csv`

**Naming Convention**: `SLA_YYYY-MM-DD_YYYY-MM-DD.csv`

**Examples**:
- `SLA_2025-10-12_2025-10-18.csv` - Last week
- `SLA_2025-09-21_2025-10-18.csv` - 4 weeks

---

## Features

### Automatic Date Filtering
- Reads all columns from Google Sheet
- Parses date headers automatically
- Filters to only include dates in specified range
- Supports multiple date formats

### Supported Date Formats
- `10/12/2025` (M/D/YYYY)
- `10/12/25` (M/D/YY)
- `2025-10-12` (YYYY-MM-DD)
- `Oct 12, 2025` (Month Day, Year)
- `October 12, 2025` (Full month)

### Automatic Totaling
- Sums SLA counts across all date columns in range
- Creates "Total SLAs" column
- Filters out empty/invalid agent names

### Week Boundary Alignment
- Uses Sunday-Saturday weeks (configurable)
- Matches Tableau data boundaries
- Consistent with other data sources

---

## Next Steps

### To Use This Integration:

1. **Setup Authentication**
   - Follow guide in `data/GOOGLE_SHEETS_SETUP.md`
   - Create service account or use OAuth2
   - Share Google Sheet with credentials

2. **Test Connection**
   ```python
   from sheets_client import GoogleSheetsClient
   from config import GOOGLE_SHEETS_CONFIG
   
   config = GOOGLE_SHEETS_CONFIG['sla_cases']
   with GoogleSheetsClient() as client:
       spreadsheet = client.get_spreadsheet(config['spreadsheet_id'])
       print(f"✅ Connected to: {spreadsheet.title}")
   ```

3. **Retrieve Data**
   ```bash
   python sla_cases.py
   ```

### Integration with KPI System

Combine with other data sources:

```python
from sla_cases import get_last_week_sla_data
from support_agent_audits import get_last_week_agent_scores
from support_services_kpi import get_csat_scores

# Get all data
sla_df = get_last_week_sla_data()
qa_df = get_last_week_agent_scores()
csat_df = get_csat_scores()

# Merge on Agent Name
combined = qa_df.merge(
    sla_df[['Agent Name', 'Total SLAs']], 
    on='Agent Name', 
    how='left'
)
```

---

## Configuration Flexibility

### If Sheet Structure Changes

All settings are in `config.py`, no code changes needed:

```python
GOOGLE_SHEETS_CONFIG = {
    'sla_cases': {
        'spreadsheet_id': '...',        # Update if moved to new sheet
        'sheet_name': '...',            # Update if tab renamed
        'data_start_row': 2,            # Update if header rows change
        'agent_column': 'A',            # Update if agents move
        'date_header_row': 1            # Update if dates move
    }
}
```

---

## Summary

✅ **Complete Google Sheets integration for SLA data**  
✅ **Flexible configuration in `config.py`**  
✅ **Automatic date filtering and totaling**  
✅ **Consistent file naming with other data sources**  
✅ **Comprehensive documentation and setup guide**  
✅ **Multiple retrieval methods (last week, multi-week, custom range)**  
✅ **Service account support for automated access**  

---

**Status**: Ready to use once authentication is configured!

See `data/GOOGLE_SHEETS_SETUP.md` for authentication setup instructions.
