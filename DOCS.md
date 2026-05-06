# Amplify KPI Bot - Complete Documentation

> **Comprehensive guide for the Amplify KPI Calculator Bot with Tableau API integration**

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Project Structure](#project-structure)
4. [Data Sources](#data-sources)
5. [Usage Guide](#usage-guide)
6. [Tableau Integration](#tableau-integration)
7. [Configuration](#configuration)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The Amplify KPI Bot is a sophisticated Python application that:
- **Processes KPI data** from multiple sources (Tableau, Salesforce, Google Sheets)
- **Calculates weighted scores** using configurable formulas
- **Generates performance reports** for agents and teams
- **Integrates with Tableau** for automated data retrieval

### Key Features
✅ **Tableau API Integration** - Direct data pulls from Tableau workbooks  
✅ **Automated Data Processing** - CSV and API-based data handling  
✅ **Weighted KPI Scoring** - Sophisticated scoring with conditional weight redistribution  
✅ **Agent Scorecards** - Individual performance reports  
✅ **Team Analytics** - Comprehensive team performance analysis  
✅ **Flexible Configuration** - Easy to modify weights, goals, and metrics  

---

## Quick Start

### 1. Environment Setup
```bash
# Clone and navigate to project
cd Amplify-KPI-Bot

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Credentials
Create `credentials.json` in the project root:
```json
{
  "tableau_token_name": "AmplifyKPIBot",
  "tableau_api_key": "your_token_secret_here",
  "type": "service_account",
  "project_id": "your_project",
  "private_key_id": "key_id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "your_service_account@project.iam.gserviceaccount.com"
}
```

### 3. Test Tableau Connection
```bash
python main.py --test-tableau
```

### 4. Pull Data from Tableau
```python
# QA Data (Agent Audits)
from core import get_last_week_agent_scores

qa_data = get_last_week_agent_scores()
# Saves to: data/qa/QA_2025-10-12_2025-10-18.csv

# KPI Data (Response Times, CSAT, etc.)
from core import get_csat_scores, get_response_times

csat = get_csat_scores()
email_response = get_response_times('email')
phone_response = get_response_times('phone')
# Saves to: data/kpi/KPI_{metric}_{dates}.csv
```

---

## Project Structure

```
Amplify-KPI-Bot/
├── 📁 clients/                     # API clients & integrations
│   ├── tableau_client.py           # Tableau REST API client
│   ├── salesforce_client.py        # Salesforce client
│   ├── gdrive_importer.py          # Google Drive CSV importer
│   └── connection_checker.py       # Connection health checker
│
├── 📁 sheets/                      # Google Sheets integration
│   ├── sheets_client.py            # Google Sheets API client
│   ├── sheets_updater.py           # Sheets data writer
│   └── sla_cases.py                # SLA data from Sheets
│
├── 📁 core/                        # Core business logic
│   ├── kpi_calculator.py           # KPI scoring engine
│   ├── kpi_aggregator.py           # Data aggregation
│   ├── named_functions.py          # Excel formula equivalents
│   ├── support_agent_audits.py     # QA data retrieval
│   ├── support_services_kpi.py     # KPI data retrieval
│   └── data_importer.py            # CSV data processing
│
├── 📁 models/                      # Data models
│   └── agent_info_manager.py       # Agent metadata manager
│
├── 📁 exporters/                   # Output generation
│   ├── excel_generator.py          # Excel workbook generator
│   ├── scorecard_generator.py      # Agent scorecard generator
│   └── dataframe_generator.py      # Comprehensive dataframes
│
├── 📁 data/                        # Data storage
│   ├── qa/                         # QA audit data from Tableau
│   ├── kpi/                        # KPI metrics data
│   ├── exports/                    # Other exported data
│   ├── archive/                    # Historical/archived data
│   └── README.md                   # Data documentation
│
├── 📁 scripts/                     # Utility scripts
│   ├── tableau_tools.py            # Unified Tableau testing/diagnostics
│   ├── find_tableau_content.py    # Search workbooks/views
│   ├── setup_helper.py             # Setup and dependency checker
│   ├── validate_system.py          # System validation
│   └── README.md                   # Scripts documentation
│
├── 📁 examples/                    # Example files
├── 📁 exports/                     # Export output directory
│
├── � Root Files (Entry Points & Config)
│   ├── app.py                      # Streamlit web interface (ENTRY POINT)
│   ├── main.py                     # CLI entry point (ENTRY POINT)
│   ├── update_kpi_sheets.py        # Workflow orchestrator
│   ├── config.py                   # Global configuration & settings
│   ├── utils.py                    # General utilities
│   ├── README.md                   # Main documentation
│   ├── DOCS.md                     # Detailed technical docs
│   ├── credentials.json            # API credentials (gitignored)
│   ├── requirements.txt            # Python dependencies
│   └── .gitignore                  # Git ignore rules
```

---

## Data Sources

### Tableau Workbooks

#### 1. Support Agent Audits [Rev3]
**Purpose**: QA audit scores  
**Workbook ID**: `845f49eb-ec3e-4c25-bd6f-4c39e35a2ad1`  
**Module**: `support_agent_audits.py`

**Available Data**:
- Agent Name
- Cases (audited)
- Avg Score
- Fail %

**Retrieval**:
```python
from core import get_last_week_agent_scores

# Last week's data (Sunday-Saturday)
df = get_last_week_agent_scores()

# Multi-week data
df = get_multi_week_agent_scores(num_weeks=4)
```

**Output**: `data/qa/QA_{start}_{end}.csv`

---

#### 2. Support Services KPI Scorecard
**Purpose**: Response times, CSAT, resolution times  
**Workbook ID**: `467137c0-5ff5-46b3-bdf8-412e8779c4aa`  
**Module**: `support_services_kpi.py`

**Available Data**:

| Metric | Records | Columns |
|--------|---------|---------|
| **CSAT Scores** | Individual responses | Agent, Score (1-5), Date |
| **Email Response** | Individual cases | Agent, Time (hours), Case ID |
| **Phone Response** | Individual calls | Agent, Time (seconds), Call ID |
| **Resolution Time** | Individual cases | Agent, Time (hours), Case details |

**Retrieval**:
```python
from core import (
    get_csat_scores,
    get_response_times,
    get_resolution_time_data
)

# Last week's data
csat = get_csat_scores()
email = get_response_times('email')
phone = get_response_times('phone')
resolution = get_resolution_time_data()
```

**Output**: `data/kpi/KPI_{metric}_{start}_{end}.csv`

---

#### 3. SLA Cases (Google Sheets)
**Purpose**: Daily SLA breach tracking by agent  
**Spreadsheet ID**: `1isXljGGYWbSgNbpYjVt5rN-3QsGn57frzMfWkdu9eDQ`  
**Sheet**: `SS Historical Data 3+ Day SLA Post March 2024`  
**Module**: `sla_cases.py`

**Available Data**:
- Agent Name
- Daily SLA counts (one column per date)
- Total SLAs (aggregated for date range)

**Sheet Structure**:
```
┌─────────────┬──────────┬──────────┬──────────┬─────┐
│ Agent Name  │ 10/12/25 │ 10/13/25 │ 10/14/25 │ ... │
├─────────────┼──────────┼──────────┼──────────┼─────┤
│ Agent 1     │    2     │    1     │    0     │ ... │
│ Agent 2     │    0     │    3     │    1     │ ... │
└─────────────┴──────────┴──────────┴──────────┴─────┘
```

**Retrieval**:
```python
from sla_cases import get_last_week_sla_data, get_multi_week_sla_data

# Last week's data (Sunday-Saturday)
df = get_last_week_sla_data()

# Multi-week data
df = get_multi_week_sla_data(num_weeks=4)

# Custom date range
from datetime import datetime
df = get_sla_data(
    week_start=datetime(2025, 10, 6),
    week_end=datetime(2025, 10, 12)
)
```

**Authentication**: Requires Google service account credentials in `credentials.json`

**Output**: `data/kpi/SLA_{start}_{end}.csv`

**Setup Guide**: See [data/GOOGLE_SHEETS_SETUP.md](data/GOOGLE_SHEETS_SETUP.md)

---

### File Naming Convention

**Format**: `{TYPE}_{START_DATE}_{END_DATE}.csv`

**Examples**:
- `QA_2025-10-12_2025-10-18.csv` - Last week's QA data
- `KPI_CSAT_2025-10-12_2025-10-18.csv` - CSAT scores
- `KPI_ResponseTime_Email_2025-10-12_2025-10-18.csv` - Email response times

**Benefits**:
- ✅ Clear data type identification
- ✅ Easy to see date range at a glance
- ✅ Files sort chronologically
- ✅ No timestamp ambiguity

---

## Usage Guide

### Command Line Interface

```bash
# Test Tableau connection
python main.py --test-tableau

# Process CSV exports
python main.py --exports-folder exports --output results.xlsx

# Generate scorecards
python main.py --exports-folder exports --output results.xlsx --generate-scorecards

# Single agent scorecard
python main.py --exports-folder exports --agent "Agent Name" --scorecard output.csv

# Use Tableau instead of CSV
python main.py --use-tableau --output results.xlsx

# Debug mode
python main.py --exports-folder exports --output results.xlsx --debug
```

### Python API

#### Pull QA Data
```python
from core import get_last_week_agent_scores, get_agent_audits_data, get_multi_week_agent_scores
from datetime import datetime, timedelta

# Last week (automatic)
qa_df = get_last_week_agent_scores()

# Custom date range
start = datetime(2025, 9, 1)
end = datetime(2025, 9, 30)
qa_df = get_agent_audits_data(week_start=start, week_end=end)

# Multi-week
qa_df = get_multi_week_agent_scores(num_weeks=4)
```

#### Pull KPI Data
```python
from core import (
    get_csat_scores,
    get_response_times,
    get_resolution_time_data
)

# Get individual metrics
csat_df = get_csat_scores()
email_df = get_response_times('email')
phone_df = get_response_times('phone')
resolution_df = get_resolution_time_data()

# Calculate agent averages
import pandas as pd
avg_csat = csat_df.groupby('Name')['CSAT Score'].mean()
avg_email = email_df.groupby('Name')['Time to First Response Email (hours)'].mean()
```

#### Calculate KPIs
```python
from main import AmplifyKPIBot

# Initialize bot
bot = AmplifyKPIBot(exports_folder="exports")

# Load and process data
bot.load_and_process_data()

# Calculate KPIs
results = bot.calculate_kpis()

# Generate scorecards
bot.generate_scorecards(output_folder="scorecards")
```

---

## Tableau Integration

### Setup

1. **Create Personal Access Token** in Tableau:
   - Go to Tableau Server → My Account Settings
   - Create new Personal Access Token
   - Name: `AmplifyKPIBot`
   - Copy the token name and secret

2. **Update credentials.json**:
```json
{
  "tableau_token_name": "AmplifyKPIBot",
  "tableau_api_key": "your_secret_here"
}
```

3. **Test connection**:
```bash
python main.py --test-tableau
```

### Configured Workbooks

| Workbook | Purpose | Status |
|----------|---------|--------|
| **Support Agent Audits [Rev3]** | QA audit scores | ✅ Working |
| **Support Services KPI Scorecard** | Response times, CSAT | ✅ Working |

### Available Tools

**Unified Testing Tool**: `scripts/tableau_tools.py`
```bash
python scripts/tableau_tools.py

# Interactive menu:
# 1. Quick Connection Test
# 2. Diagnose Credentials
# 3. List All Workbooks and Views
# 4. Explore Specific Workbook
# 5. Test View Data Retrieval
# 6. Exit
```

**Search Tool**: `scripts/find_tableau_content.py`
```bash
# Search for workbooks/views by name
python scripts/find_tableau_content.py "Agent"
python scripts/find_tableau_content.py "KPI"
```

### API Features

✅ **Pagination** - Retrieves ALL workbooks/views (not just first 100)  
✅ **Authentication** - Personal Access Token support  
✅ **Data Export** - CSV data retrieval from views  
✅ **Context Manager** - Automatic sign-out  
✅ **Error Handling** - Comprehensive logging  
✅ **XML Namespace** - Proper Tableau API response parsing  

---

## Configuration

### config.py Overview

```python
# KPI Weights (total must equal 1.0)
DEFAULT_WEIGHTS = {
    'time_utilization': 0.15,      # 15%
    'cases_per_hour': 0.15,        # 15%
    'initial_chat': 0.05,          # 5%
    'initial_phone': 0.025,        # 2.5%
    'initial_email': 0.025,        # 2.5%
    'sla_cases': 0.10,             # 10%
    'qa_score': 0.50               # 50%
}

# Metric Goals/Targets
METRIC_GOALS = {
    'time_utilization': 0.90,      # 90% minimum
    'cases_per_hour': 1.21,        # CPH target
    'csat_score': 0.80,            # 80% (4+ out of 5)
    'initial_chat': 5.0,           # 5 minutes max
    'initial_phone': 60.0,         # 60 seconds max
    'initial_email': 480.0,        # 480 minutes (8 hours) max
    'sla_percentage': 0.10,        # 10% max cases out of SLA
    'qa_score': 90.0,              # 90% minimum
    'bcf_percentage': 0.05,        # 5% max BCF rate
}

# General Defaults
GENERAL_DEFALTS = {
    'normal_working_hours': 40.0,     # Default weekly hours
    'week_start_day': 'Sunday',      # Week start for calculations
    'week_end_day': 'Saturday'        # Week end for calculations
}

# Data Paths
DATA_PATHS = {
    'base': 'data',
    'qa': 'data/qa',
    'kpi': 'data/kpi',
    'exports': 'data/exports',
    'archive': 'data/archive'
}

# Google Sheets Configuration
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

# Tableau Configuration
TABLEAU_CONFIG = {
    'server_url': 'https://10az.online.tableau.com',
    'site_name': 'amplify',
    'workbooks': {
        'support_agent_audits': '845f49eb-ec3e-4c25-bd6f-4c39e35a2ad1',
        'kpi_scorecard': '467137c0-5ff5-46b3-bdf8-412e8779c4aa'
    },
    'views': {
        'cs_agent_audits': '614041ff-154f-4aa6-920f-2910355b07a0',
        'csat_talkdesk': 'd89ee56c-5499-4416-8d91-8ed854df519f',
        'response_time_email': 'fe9d4a04-8eb7-48ac-9bcf-4be41931541d',
        'response_time_phone': 'd212ff54-24d4-419b-995d-30652d534bfa',
        'resolution_time': 'c0fd7131-cca5-4e99-8f14-5fb5c31826fc'
    }
}
```

### Customizing Weights

```python
from config import DEFAULT_WEIGHTS

# Modify weights
custom_weights = DEFAULT_WEIGHTS.copy()
custom_weights['qa_score'] = 0.60  # Increase QA to 60%
custom_weights['cases_per_hour'] = 0.10  # Decrease CPH to 10%

# Use with bot
bot = AmplifyKPIBot(custom_weights=custom_weights)
```

### Week Boundaries

All data follows **Sunday-Saturday** week boundaries by default.
- Includes weekend work
- Configurable in `config.py` under `GENERAL_DEFALTS`

---

## Troubleshooting

### Tableau Connection Issues

**Problem**: `Authentication failed`  
**Solution**:
1. Verify token name matches exactly: `AmplifyKPIBot`
2. Check token secret is correct in `credentials.json`
3. Ensure token hasn't expired
4. Test with: `python scripts/tableau_tools.py` → Option 2 (Diagnose Credentials)

**Problem**: `No workbooks/views found`  
**Solution**:
1. Check permissions on Tableau Server
2. Verify site name is correct: `amplify`
3. Confirm you have access to the workbooks

**Problem**: `Empty data returned from view`  
**Solution**:
1. Some views are dashboards and don't support data export
2. Try individual metric views instead of summary views
3. Check if view has filters that might exclude all data

### Data Issues

**Problem**: `No date column found`  
**Solution**:
- This is expected for some Tableau views
- Data is already filtered in the view itself
- Filter warning can be ignored if data looks correct

**Problem**: `File not found` errors  
**Solution**:
1. Check file paths are absolute
2. Verify data folders exist: `data/qa/`, `data/kpi/`
3. Run the data retrieval scripts to create folders

### Performance

**Problem**: Slow data retrieval  
**Solution**:
- Large views (1000+ rows) take 20-30 seconds
- This is normal for Tableau API
- Use `max_age` parameter to cache data:
  ```python
  df = client.query_view(view_id, max_age=60)  # Cache for 60 min
  ```

### Google Sheets Issues

**Problem**: `Failed to connect to Google Sheets`  
**Solution**:
1. Verify service account credentials in `credentials.json`
2. Ensure Google Sheet is shared with service account email
3. Check Google Sheets API is enabled in Google Cloud Console
4. See [data/GOOGLE_SHEETS_SETUP.md](data/GOOGLE_SHEETS_SETUP.md) for detailed setup

**Problem**: `Failed to open worksheet`  
**Solution**:
1. Verify sheet name in `config.py` matches exactly (case-sensitive)
2. Check for typos or extra spaces
3. Run error to see list of available sheets

**Problem**: `No date columns found within range`  
**Solution**:
1. Check date format in sheet headers (Row 1)
2. Supported: `10/12/2025`, `2025-10-12`, `Oct 12, 2025`
3. Verify date range matches available data in sheet
4. Update `date_header_row` in config if dates are in different row

---

## KPI Scoring Logic

### Calculation Order

1. **Load Data** - From Tableau or CSV exports
2. **Calculate Base Metrics**:
   - Time Utilization %
   - Cases Per Hour
   - Response Times (Chat, Phone, Email)
   - SLA Breach %
   - QA Score
   - BCF %
   - CSAT Score

3. **Apply Conditional Logic**:
   - Score each metric (0-1 scale)
   - Apply weight redistribution if needed
   - Calculate weighted total

4. **Generate Output**:
   - Individual agent scores
   - Team aggregates
   - Performance ratings

### Performance Ratings

| Rating | Score Range |
|--------|-------------|
| **Excellent** | 95%+ |
| **Outstanding** | 90-94% |
| **Good** | 80-89% |
| **Average** | 70-79% |
| **Below Average** | <70% |

---

## Data Visualization & Future Enhancements

### Current Capabilities
✅ **Raw data extraction** - Individual records from Tableau  
✅ **Agent-level aggregation** - Can be calculated from raw data  
✅ **Time-series data** - Multiple weeks for trend analysis  
✅ **Multi-metric tracking** - QA, CSAT, response times, resolution times  

### Future Opportunities

1. **Agent Performance Dashboards**
   - Week-over-week trends
   - Comparison against team averages
   - Identify top performers

2. **Predictive Analytics**
   - Correlation between metrics (e.g., response time vs CSAT)
   - Performance trajectory predictions
   - Training effectiveness tracking

3. **Growth & Retention Tracking**
   - Agent skill development over time
   - Performance improvement patterns
   - Early warning indicators for retention risk

4. **Team Analytics**
   - Channel-specific performance (email vs phone vs chat)
   - Workload distribution analysis
   - Seasonal patterns and staffing optimization

---

## Support & Resources

### Documentation Locations

| Topic | Location |
|-------|----------|
| **General Overview** | This file (README.md) |
| **Data Folder** | `data/README.md` |
| **QA Data Details** | `data/qa/` (in main data README) |
| **KPI Data Details** | `data/kpi/README.md` |
| **Scripts** | `scripts/README.md` |
| **Technical Docs** | `DOCS.md` |

### Helper Commands

```bash
# Validate system setup
python scripts/final_validation.py

# Check dependencies
python scripts/setup_helper.py

# Explore Tableau content
python scripts/tableau_tools.py

# Search for specific workbooks/views
python scripts/find_tableau_content.py "search term"

# Test Tableau connection
python main.py --test-tableau
```

### Common Tasks

**Weekly Data Pull**:
```bash
# Pull QA and KPI data for last week
python support_agent_audits.py
python support_services_kpi.py

# Files saved to:
# data/qa/QA_2025-10-12_2025-10-18.csv
# data/kpi/KPI_CSAT_2025-10-12_2025-10-18.csv
# data/kpi/KPI_ResponseTime_Email_2025-10-12_2025-10-18.csv
# data/kpi/KPI_ResponseTime_Phone_2025-10-12_2025-10-18.csv
# data/kpi/KPI_ResolutionTime_2025-10-12_2025-10-18.csv
```

**Archive Old Data**:
```bash
# Move old files to archive folder
mv data/qa/QA_2025-09-*.csv data/archive/
mv data/kpi/KPI_*_2025-09-*.csv data/archive/
```

---

## Version History

### Current Version
- ✅ Tableau API integration complete
- ✅ QA data retrieval (Support Agent Audits)
- ✅ KPI data retrieval (CSAT, Response Times, Resolution Times)
- ✅ Automated file naming with date ranges
- ✅ Organized data folder structure
- ✅ Pagination support for large datasets
- ✅ Consolidated testing tools

### Roadmap
- 🔄 Agent-level aggregation functions
- 🔄 Time Utilization data source identification
- 🔄 SLA data extraction
- 🔄 Automated weekly scheduling
- 🔄 Dashboard visualizations
- 🔄 Historical trend analysis

---

**Built to automate KPI tracking and performance analysis for Amplify Support Services** 🚀

For questions or issues, check the troubleshooting section or run diagnostic tools in `scripts/`.
