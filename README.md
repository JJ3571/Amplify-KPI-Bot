# Amplify KPI Bot

> Automated KPI tracking and performance analysis for Amplify Support Services

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tableau API](https://img.shields.io/badge/Tableau-API%20v3.19-orange.svg)](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api.htm)

---

## 🚀 Quick Start

```bash
# 1. Setup environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# 2. Test Tableau connection
python main.py --test-tableau

# 3. Pull last week's data
python support_agent_audits.py      # QA data
python support_services_kpi.py      # KPI metrics
python sla_cases.py                 # SLA data from Google Sheets
```

**📊 Data automatically saved to:**
- `data/qa/QA_2025-10-12_2025-10-18.csv`
- `data/kpi/KPI_CSAT_2025-10-12_2025-10-18.csv`
- `data/kpi/KPI_ResponseTime_Email_2025-10-12_2025-10-18.csv`
- `data/kpi/KPI_ResponseTime_Phone_2025-10-12_2025-10-18.csv`
- `data/kpi/KPI_ResolutionTime_2025-10-12_2025-10-18.csv`
- `data/kpi/SLA_2025-10-12_2025-10-18.csv`

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| **[DOCS.md](DOCS.md)** | 📚 **Complete documentation** - Setup, usage, API guide, troubleshooting |
| **[data/README.md](data/README.md)** | 💾 Data folder structure and file naming conventions |
| **[data/kpi/README.md](data/kpi/README.md)** | 📊 KPI metrics details and usage |
| **[data/GOOGLE_SHEETS_SETUP.md](data/GOOGLE_SHEETS_SETUP.md)** | 📋 Google Sheets SLA data setup guide |
| **[scripts/README.md](scripts/README.md)** | 🔧 Helper scripts and utilities |

---

## ✨ Features

### 🔗 Tableau Integration
- **Direct API access** to Tableau Server
- **Automated data pulls** from configured workbooks
- **Pagination support** for large datasets (100+ records)
- **Proper date-based file naming** for easy tracking

### � Google Sheets Integration
- **SLA Cases data** from live Google Sheet
- **Service account authentication** for secure access
- **Automatic date range filtering** for specified weeks
- **Daily SLA breach tracking** by agent

### �📊 Data Sources
| Source | Type | Status |
|--------|------|--------|
| **Support Agent Audits** | QA scores | ✅ Working |
| **Support Services KPI Scorecard** | Response times, CSAT, resolution | ✅ Working |
| **SS Historical Data (G-Sheet)** | SLA cases by agent/date | ✅ Working |

### 📁 Organized Data Storage
```
data/
├── qa/          # QA audit scores by agent
├── kpi/         # Response times, CSAT, resolution times
├── exports/     # Other exports
└── archive/     # Historical data
```

### 📝 Smart File Naming
Format: `{TYPE}_{START_DATE}_{END_DATE}.csv`
- Example: `QA_2025-10-12_2025-10-18.csv`
- Clear date ranges (Sunday-Saturday)
- Chronological sorting
- Easy identification


---

## 💻 Usage

### Command Line

```bash
# Test Tableau connection
python main.py --test-tableau

# Pull data from Tableau
python support_agent_audits.py      # QA data
python support_services_kpi.py      # KPI metrics

# Process CSV exports (legacy)
python main.py --exports-folder exports --output results.xlsx
```

### Python API

```python
# QA Data
from support_agent_audits import get_last_week_agent_scores
qa_df = get_last_week_agent_scores()

# KPI Data
from support_services_kpi import get_csat_scores, get_response_times
csat_df = get_csat_scores()
email_df = get_response_times('email')
phone_df = get_response_times('phone')
```

**See [DOCS.md](DOCS.md) for detailed usage examples and API reference.**

---

## 🛠️ Available Tools

### Tableau Tools
```bash
# Interactive testing menu
python scripts/tableau_tools.py

# Search for workbooks/views
python scripts/find_tableau_content.py "KPI"
```

### System Validation
```bash
# Validate setup
python scripts/final_validation.py

# Check dependencies
python scripts/setup_helper.py
```

---

## ⚙️ Configuration

Key settings in `config.py`:

```python
# KPI Weights (must total 1.0)
DEFAULT_WEIGHTS = {
    'time_utilization': 0.15,
    'cases_per_hour': 0.15,
    'initial_chat': 0.05,
    'initial_phone': 0.025,
    'initial_email': 0.025,
    'sla_cases': 0.10,
    'qa_score': 0.50
}

# Week boundaries (Sunday-Saturday)
GENERAL_DEFALTS = {
    'week_start_day': 'Sunday',
    'week_end_day': 'Saturday'
}

# Tableau Server
TABLEAU_CONFIG = {
    'server_url': 'https://10az.online.tableau.com',
    'site_name': 'amplify'
}
```

---

## 📊 Available Metrics

### QA Data (from Support Agent Audits)
- Agent Name
- Cases (audited)
- Avg Score
- Fail %

### KPI Data (from KPI Scorecard)
- **CSAT Scores** - Customer satisfaction ratings
- **Email Response Times** - Time to first response (hours)
- **Phone Response Times** - Speed to answer (seconds)
- **Case Resolution Times** - Time to resolve (business hours)

---

## 🔍 Data Retrieval Examples

### Last Week's Data
```python
from support_agent_audits import get_last_week_agent_scores
from support_services_kpi import get_csat_scores, get_response_times

# QA scores
qa = get_last_week_agent_scores()

# KPI metrics
csat = get_csat_scores()
email = get_response_times('email')
phone = get_response_times('phone')
```

### Multi-Week Trends
```python
from support_agent_audits import get_multi_week_agent_scores

# Get 4 weeks of QA data
qa_4weeks = get_multi_week_agent_scores(num_weeks=4)
```

### Custom Date Range
```python
from support_agent_audits import get_agent_audits_data
from datetime import datetime

start = datetime(2025, 9, 1)
end = datetime(2025, 9, 30)
qa_september = get_agent_audits_data(week_start=start, week_end=end)
```

---

## 🗂️ Project Structure

```
Amplify-KPI-Bot/
├── data/                           # All data storage
│   ├── qa/                         # QA audit data
│   ├── kpi/                        # KPI metrics
│   ├── exports/                    # Other exports
│   └── archive/                    # Historical data
│
├── scripts/                        # Utility scripts
│   ├── tableau_tools.py            # Unified Tableau testing
│   ├── find_tableau_content.py     # Search tool
│   └── ...
│
├── Core Modules
│   ├── main.py                     # Main application
│   ├── config.py                   # Configuration
│   ├── tableau_client.py           # Tableau API client
│   ├── support_agent_audits.py     # QA data retrieval
│   ├── support_services_kpi.py     # KPI data retrieval
│   └── ...
│
└── Documentation
    ├── README.md                   # This file
    ├── DOCS.md                     # Complete documentation
    └── requirements.txt            # Dependencies
```

---

## 🐛 Troubleshooting

### Tableau Connection Issues
```bash
# Diagnose credentials
python scripts/tableau_tools.py
# Choose option 2: Diagnose Credentials
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Authentication failed | Verify token name is "AmplifyKPIBot" in credentials.json |
| No data returned | Check view permissions in Tableau |
| Slow retrieval | Normal for large views (1000+ rows takes 20-30 sec) |

**See [DOCS.md](DOCS.md) for detailed troubleshooting guide.**

---

## 📈 KPI Scoring

### Performance Ratings
- **Excellent**: 95%+
- **Outstanding**: 90-94%
- **Good**: 80-89%
- **Average**: 70-79%
- **Below Average**: <70%

### Metric Targets
- **Time Utilization**: 90% minimum
- **Cases Per Hour**: 1.21 target
- **CSAT Score**: 80% (4+ out of 5)
- **Email Response**: 8 hours max
- **Phone Response**: 60 seconds max
- **QA Score**: 90% minimum

---

## 🎯 Future Enhancements

- 🔄 Agent-level aggregation functions
- 🔄 Time Utilization data source
- 🔄 SLA data extraction
- 🔄 Automated weekly scheduling
- 🔄 Dashboard visualizations
- 🔄 Historical trend analysis
- 🔄 Performance predictions
- 🔄 Growth tracking over time

---

## 📞 Support

For detailed information:
- **📚 Full Documentation**: See [DOCS.md](DOCS.md)
- **💾 Data Information**: See [data/README.md](data/README.md)
- **🔧 Script Help**: See [scripts/README.md](scripts/README.md)

---

**Built to automate KPI tracking and performance analysis** 🚀

*Questions? Check [DOCS.md](DOCS.md) for comprehensive guides and troubleshooting.*

