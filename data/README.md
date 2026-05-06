# Data Folder Structure

This directory contains all data files pulled from Tableau and other data sources.

## Directory Structure

```
data/
├── qa/          # QA audit data from Tableau
├── kpi/         # KPI metrics data from Tableau
├── exports/     # Other exported data files
└── archive/     # Archived/historical data
```

## File Naming Convention

All data files follow a standardized naming convention to clearly indicate:
1. **Data Type**: What kind of data (QA, KPI, etc.)
2. **Date Range**: The time period the data covers

### Format
```
{DATA_TYPE}_{START_DATE}_{END_DATE}.csv
```

### Examples
- `QA_2025-10-12_2025-10-18.csv` - QA audit data from Oct 12-18, 2025 (last week)
- `KPI_2025-10-12_2025-10-18.csv` - KPI metrics data from Oct 12-18, 2025
- `QA_2025-09-21_2025-10-18.csv` - QA audit data covering 4 weeks

### Date Ranges
- Weekly data typically spans **Sunday to Saturday** (configurable in `config.py`)
- Multi-week data uses the start of the first week through the end of the last week
- Dates are in **ISO 8601 format** (YYYY-MM-DD) for easy sorting

## Data Types

### QA (Quality Assurance)
**Source**: Support Agent Audits [Rev3] Tableau workbook
**Location**: `data/qa/`
**Content**: Agent QA audit scores including:
- Agent Name
- Cases (audited)
- Avg Score
- Fail %

**Retrieval**: Use `support_agent_audits.py` to pull QA data

### KPI (Key Performance Indicators)
**Location**: `data/kpi/`
**Content**: Agent KPI metrics (future implementation)

### Exports
**Location**: `data/exports/`
**Content**: Miscellaneous exported data files

### Archive
**Location**: `data/archive/`
**Content**: Historical data files for backup/reference

## Usage

### Pulling QA Data
```python
from support_agent_audits import get_last_week_agent_scores, save_agent_audits_to_csv
from datetime import datetime, timedelta

# Get last week's data
df = get_last_week_agent_scores()

# Auto-saves with proper naming: data/qa/QA_2025-10-12_2025-10-18.csv
# Or manually specify dates:
start = datetime(2025, 10, 12)
end = datetime(2025, 10, 18)
filepath = save_agent_audits_to_csv(df, start_date=start, end_date=end)
```

## Best Practices

1. **Weekly Pulls**: Pull data weekly after the week ends (Sunday morning)
2. **Archiving**: Move old data to `archive/` folder periodically
3. **Naming**: Always use the auto-generated filenames for consistency
4. **Date Accuracy**: Ensure date ranges match the actual data period

## Notes

- All dates use **Sunday-Saturday** week boundaries by default
- Weekend work is included (don't use Mon-Fri ranges)
- Week start/end days can be configured in `config.py` under `GENERAL_DEFALTS`
