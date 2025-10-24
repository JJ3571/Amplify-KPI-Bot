# Google Sheets Setup for SLA Data

This document explains how to configure Google Sheets integration for retrieving SLA Cases data.

## Overview

The SLA Cases data is stored in a Google Sheet that tracks daily SLA breaches by agent. The system connects to this sheet to retrieve historical data for specified date ranges.

**Google Sheet:**
- **Spreadsheet ID**: `1isXljGGYWbSgNbpYjVt5rN-3QsGn57frzMfWkdu9eDQ`
- **Sheet Name**: `SS Historical Data 3+ Day SLA Post March 2024`
- **URL**: https://docs.google.com/spreadsheets/d/1isXljGGYWbSgNbpYjVt5rN-3QsGn57frzMfWkdu9eDQ/edit

## Sheet Structure

```
┌─────────────┬──────────┬──────────┬──────────┬─────┐
│ Agent Name  │ 10/12/25 │ 10/13/25 │ 10/14/25 │ ... │
├─────────────┼──────────┼──────────┼──────────┼─────┤
│ Agent 1     │    2     │    1     │    0     │ ... │
│ Agent 2     │    0     │    3     │    1     │ ... │
│ Agent 3     │    1     │    0     │    2     │ ... │
└─────────────┴──────────┴──────────┴──────────┴─────┘
```

- **Column A**: Agent names
- **Columns B+**: Daily SLA breach counts (date headers)
- **Row 1**: Date headers (e.g., "10/12/25", "10/13/2025")
- **Data**: Numeric values representing SLA breaches per day

## Configuration

All Google Sheets settings are stored in `config.py`:

```python
GOOGLE_SHEETS_CONFIG = {
    'sla_cases': {
        'spreadsheet_id': '1isXljGGYWbSgNbpYjVt5rN-3QsGn57frzMfWkdu9eDQ',
        'sheet_name': 'SS Historical Data 3+ Day SLA Post March 2024',
        'description': 'SLA Cases data - daily tracking of cases out of SLA',
        'data_start_row': 2,  # Row where data starts (after headers)
        'agent_column': 'A',  # Column with agent names
        'date_header_row': 1  # Row with date headers
    }
}
```

### Updating Configuration

If the spreadsheet or sheet name changes:

1. Open `config.py`
2. Update the `GOOGLE_SHEETS_CONFIG['sla_cases']` section:
   - `spreadsheet_id`: From the Google Sheets URL
   - `sheet_name`: Exact name of the tab
   - Other fields as needed

## Authentication Setup

### Option 1: Service Account (Recommended)

1. **Create a Service Account** in Google Cloud Console
   - Go to: https://console.cloud.google.com/
   - Create a new project or select existing
   - Enable Google Sheets API
   - Create Service Account credentials
   - Download JSON key file

2. **Share the Google Sheet** with the service account email
   - Open your Google Sheet
   - Click "Share"
   - Add the service account email (e.g., `amplify-kpi@project.iam.gserviceaccount.com`)
   - Grant "Viewer" or "Editor" access

3. **Configure Credentials**
   
   Replace your `credentials.json` with the service account JSON, or add it as a nested object:
   
   ```json
   {
     "type": "service_account",
     "project_id": "your-project",
     "private_key_id": "...",
     "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
     "client_email": "amplify-kpi@your-project.iam.gserviceaccount.com",
     "client_id": "...",
     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
     "token_uri": "https://oauth2.googleapis.com/token",
     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
     "client_x509_cert_url": "..."
   }
   ```

### Option 2: OAuth2 (User Account)

For personal use with your own Google account:

1. Create OAuth 2.0 credentials in Google Cloud Console
2. Download the credentials JSON
3. Run the authentication flow (first time only)
4. Token will be cached for future use

## Usage

### Retrieve Last Week's SLA Data

```python
from sla_cases import get_last_week_sla_data, save_sla_data_to_csv
from datetime import datetime, timedelta

# Get data
sla_df = get_last_week_sla_data()

# Display summary
print(f"Agents: {len(sla_df)}")
print(sla_df[['Agent Name', 'Total SLAs']].head())

# Save to CSV
week_start, week_end = get_week_boundaries(datetime.now() - timedelta(days=7))
filepath = save_sla_data_to_csv(sla_df, week_start, week_end)
```

### Custom Date Range

```python
from sla_cases import get_sla_data
from datetime import datetime

# Define date range
week_start = datetime(2025, 10, 6)   # Sunday
week_end = datetime(2025, 10, 12)     # Saturday

# Retrieve data
sla_df = get_sla_data(week_start, week_end)
```

### Multi-Week Data

```python
from sla_cases import get_multi_week_sla_data

# Get 4 weeks of data
sla_df = get_multi_week_sla_data(num_weeks=4)
```

### Command Line

```bash
# Run the module directly to get last week's data
python sla_cases.py
```

## Output Format

The retrieved data is returned as a pandas DataFrame:

```
┌───────────────┬──────────┬──────────┬──────────┬────────────┐
│ Agent Name    │ 10/12/25 │ 10/13/25 │ 10/14/25 │ Total SLAs │
├───────────────┼──────────┼──────────┼──────────┼────────────┤
│ John Doe      │    2     │    1     │    0     │     3      │
│ Jane Smith    │    0     │    3     │    1     │     4      │
└───────────────┴──────────┴──────────┴──────────┴────────────┘
```

### Saved CSV Files

Files are automatically saved to `data/kpi/` with naming convention:

```
SLA_YYYY-MM-DD_YYYY-MM-DD.csv
```

Example: `SLA_2025-10-12_2025-10-18.csv`

## Troubleshooting

### Authentication Errors

**Error**: `Failed to connect to Google Sheets`

**Solutions**:
1. Verify service account JSON is in `credentials.json`
2. Ensure Google Sheet is shared with service account email
3. Check that Google Sheets API is enabled in Google Cloud Console

### Permission Errors

**Error**: `Failed to open spreadsheet`

**Solutions**:
1. Verify the spreadsheet ID in `config.py` is correct
2. Ensure the service account has access to the sheet
3. Check that the sheet is not set to private/restricted

### Sheet Not Found

**Error**: `Failed to open worksheet 'SS Historical Data...'`

**Solutions**:
1. Verify the exact sheet name in `config.py`
2. Check for typos or extra spaces in the name
3. Sheet names are case-sensitive
4. Run the error output to see available sheet names

### No Data Returned

**Error**: `No date columns found within range`

**Solutions**:
1. Check that date headers in row 1 are in recognizable format
2. Verify the date range matches available data in the sheet
3. Ensure `date_header_row` in config matches actual row with dates
4. Check that date columns contain numeric SLA counts

### Date Parsing Issues

If dates aren't being recognized:

1. Check date format in sheet headers
2. Supported formats:
   - `10/12/2025` (M/D/YYYY)
   - `10/12/25` (M/D/YY)
   - `2025-10-12` (YYYY-MM-DD)
   - `Oct 12, 2025`
3. Update `parse_date_header()` in `sla_cases.py` for custom formats

## Dependencies

Required packages (already in `requirements.txt`):

```
gspread>=5.0.0
google-auth>=2.0.0
google-auth-oauthlib>=0.5.0
pandas>=1.5.0
```

Install with:
```bash
pip install gspread google-auth google-auth-oauthlib
```

## Testing Connection

Test your Google Sheets connection:

```python
from sheets_client import GoogleSheetsClient
from config import GOOGLE_SHEETS_CONFIG

config = GOOGLE_SHEETS_CONFIG['sla_cases']

with GoogleSheetsClient() as client:
    # Test connection
    spreadsheet = client.get_spreadsheet(config['spreadsheet_id'])
    print(f"✅ Connected to: {spreadsheet.title}")
    
    # List available sheets
    print("\nAvailable sheets:")
    for worksheet in spreadsheet.worksheets():
        print(f"  - {worksheet.title}")
```

## Updating the Sheet

If the Google Sheet structure changes:

1. **New Sheet Name**: Update `sheet_name` in `config.py`
2. **Different Spreadsheet**: Update `spreadsheet_id` in `config.py`
3. **Different Header Row**: Update `date_header_row` in `config.py`
4. **Different Agent Column**: Update `agent_column` in `config.py`

No code changes required - just update the configuration!

## Integration with KPI System

The SLA data can be integrated into the overall KPI calculation:

```python
from sla_cases import get_last_week_sla_data
from support_agent_audits import get_last_week_agent_scores
from support_services_kpi import get_csat_scores

# Get all data sources
sla_df = get_last_week_sla_data()
qa_df = get_last_week_agent_scores()
csat_df = get_csat_scores()

# Merge on Agent Name
combined = qa_df.merge(sla_df[['Agent Name', 'Total SLAs']], on='Agent Name', how='left')
```

## Security Notes

- Never commit `credentials.json` to git
- Add to `.gitignore`: `credentials.json`
- Use environment variables for sensitive data in production
- Restrict service account permissions to read-only if possible
- Regularly rotate service account keys

---

**Questions?** Check the main [DOCS.md](../DOCS.md) for complete system documentation.
