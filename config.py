"""
Configuration file for Amplify KPI Calculator Bot
Based on actual KPI system with Export-KPI and Export-QA data sources
"""

# Google Sheets API configuration
GOOGLE_SHEETS_SCOPES = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'  # Full read/write access
]

CREDENTIALS_FILE = 'credentials.json'

# Google Sheets Data Sources
GOOGLE_SHEETS_CONFIG = {
    'sla_cases': {
        'spreadsheet_id': '1isXljGGYWbSgNbpYjVt5rN-3QsGn57frzMfWkdu9eDQ',
        'sheet_name': 'SS Historical Data 3+ Day SLA Post March 2024',
        'description': 'SLA Cases data - daily tracking of cases out of SLA',
        'data_start_row': 2,  # Row where data starts (after headers)
        'agent_column': 'A',  # Column with agent names
        'date_header_row': 1  # Row with date headers
    },
    # Temporary sheets for development
    'temp_kpi_calculator': {
        'spreadsheet_id': '1wT2_W_RO-BTBDTEsVf-NfAAKk9UXkiagsELlqpfGtUU',
        'sheet_name': 'Export - KPI',  # Will be written to
        'description': 'Temporary KPI Calculator for development'
    },
    'temp_agent_info': {
        'spreadsheet_id': '1FmhHKfyPT-LwIyjnMpDfGhRNk45tn9ks1NyxXOSBQpg',
        'sheet_name': 'Agent Info',  # Sheet to read agent metadata from
        'description': 'Temporary Agent Info & Team Distribution for development'
    },
    'sla_tracker': {
        'spreadsheet_id': '1jsQtkP1_yaSsTzWoGsUDF7J_5SyinSBTTuyX6ADMaUE',
        'sheet_name': '3+ Day & 2+ Day SLA Tracker',
        'description': 'SLA Tracker for cases out of SLA'
    }
}

# Google Drive folder configuration
GOOGLE_DRIVE_CONFIG = {
    'salesforce_csvs_folder_id': '1FX8qdAW7K4qzLledkkugbRr0a8oSXv3c',
    'description': 'Folder containing Salesforce CSV exports'
}

# Agent Info Sheet column mappings
AGENT_INFO_COLUMNS = {
    'name': 'Name',  # Agent name
    '_id': '_id',  # Internal ID
    'team_color': 'Team',  # Team color (Orange, Purple, Rose, etc.)
    'emp_fte_status': 'FTE Status',  # Full-time/Part-time status
    'emp_start_date': 'Start Date',  # Employment start date
    'emp_notes': 'Notes'  # Additional notes
}

# KPI Weights (from #Controls sheet)
DEFAULT_WEIGHTS = {
    'time_utilization': 0.15,      # E20
    'cases_per_hour': 0.15,        # E21  
    'initial_chat': 0.05,          # E23
    'initial_phone': 0.025,        # E24
    'initial_email': 0.025,        # E25
    'sla_cases': 0.10,             # E26
    'qa_score': 0.50               # E27
}

# Metric Goals/Targets (from #Controls sheet D column)
METRIC_GOALS = {
    'time_utilization': 0.90,      # D33 - 90% minimum
    'cases_per_hour': 1.21,        # D34 - CPH target
    'csat_score': 0.80,            # D35 - 80% (4+ out of 5)
    'initial_chat': 5.0,           # D36 - 5 minutes max
    'initial_phone': 60.0,         # D37 - 60 seconds max  
    'initial_email': 480.0,        # D38 - 480 minutes (8 hours) max
    'sla_percentage': 0.10,        # D39 - 10% max cases out of SLA
    'qa_score': 90.0,              # D40 - 90% minimum
    'bcf_percentage': 0.05,        # D41 - 5% max BCF rate
    'max_score': 1.0               # D42 - 100% cap
}

GENERAL_DEFAULTS = {
    'normal_working_hours': 40.0,     # Default weekly working hours for Support agents
    'week_start_day': 'Sunday',       # Week start day for calculations
    'week_end_day': 'Saturday'        # Week end day for calculations
}

# CSV Export file patterns for data_importer
EXPORT_FILE_PATTERNS = {
    'time_utilization': 'time_util_export.csv',
    'csat': 'csat_export.csv',
    'initial_chat': 'chat_response_export.csv',
    'initial_phone': 'phone_response_export.csv',
    'initial_email': 'email_response_export.csv',
    'cases_closed': 'cases_closed_export.csv',
    'cases_transferred': 'cases_transferred_export.csv',
    'sla_cases': 'sla_cases_export.csv',
    'qa_scores': 'qa_scores_export.csv',
    'qa_bcf': 'qa_bcf_export.csv',
    'qa_case_count': 'qa_case_count_export.csv'
}

# Data storage paths
DATA_PATHS = {
    'base': 'data',                    # Base data directory
    'qa': 'data/qa',                   # QA audit data from Tableau
    'kpi': 'data/kpi',                 # KPI metrics data from Tableau
    'exports': 'data/exports',         # Other exported data
    'archive': 'data/archive'          # Archived/historical data
}

# Named ranges mapping (from your named_ranges.txt)
NAMED_RANGES = {
    'Agent_Cases_Transferred_To': 'All Agents E9:E151',
    'Agent_CPH': 'All Agents F9:F151', 
    'Agent_Initial_Chat': 'All Agents G9:G151',
    'Agent_Initial_Email': 'All Agents I9:I151',
    'Agent_Initial_Phone': 'All Agents H9:H151',
    'Agent_QA_BCF': 'All Agents L9:L151',
    'Agent_QA_Score': 'All Agents K9:K151',
    'Agent_SLAs': 'All Agents J9:J151', 
    'Agent_Time_Utilization': 'All Agents B9:B151',
    'Agent_Total_Cases_Closed': 'All Agents D9:D151',
    'Agent_Working_Hours': 'All Agents C9:C151',
    'Scores_Final_Weighted': 'All Agents U9:U151'
}

# Export tab column mappings
EXPORT_COLUMNS = {
    'kpi': {
        'agent_name': 'B',
        'time_utilization': 'C', 
        'total_hours': 'D',
        'working_hours': 'E',
        'csat_responses': 'H',
        'csat_positive': 'I', 
        'chat_response': 'N',
        'phone_response': 'R',
        'email_response': 'V',
        'cases_closed': 'AN',
        'cases_transferred': 'AT',
        'sla_cases': 'Z:AE'
    },
    'qa': {
        'agent_name': 'B',
        'bcf_percentage': 'F',
        'qa_score': 'J',
        'cases_audited': 'N'
    }
}

# Team color mappings
TEAM_COLORS = {
    'Orange': '#FF8C00',
    'Purple': '#8E7CC3',
    'Rose': '#FF69B4',
    'Teal': '#008B8B',
    'Yellow': '#FFD700'
}
# Tableau Server Configuration
TABLEAU_CONFIG = {
    'server_url': 'https://10az.online.tableau.com',
    'site_name': 'amplify',
    'api_version': '3.19',  # Tableau REST API version
    'page_size': 100,        # Number of records per page for pagination
    
    # Workbook IDs
    'workbooks': {
        'support_agent_audits': '845f49eb-ec3e-4c25-bd6f-4c39e35a2ad1',
        'kpi_scorecard': '467137c0-5ff5-46b3-bdf8-412e8779c4aa'
    },
    
    # View IDs for data extraction
    'views': {
        # QA/Audit views
        'cs_agent_audits': '614041ff-154f-4aa6-920f-2910355b07a0',
        
        # KPI Scorecard views
        'executive_summary': '70807a32-6065-4a3d-83d2-e4b71cb976c7',
        'csat_talkdesk': 'd89ee56c-5499-4416-8d91-8ed854df519f',
        'csat_chat': '5e2f81aa-e18f-40ac-a070-50fbeef0eaef',
        'response_time_chat': 'd232aee1-6080-46ce-b842-db7ab7b0b0a7',
        'response_time_email': 'fe9d4a04-8eb7-48ac-9bcf-4be41931541d',
        'response_time_phone': 'd212ff54-24d4-419b-995d-30652d534bfa',
        'resolution_time': 'c0fd7131-cca5-4e99-8f14-5fb5c31826fc',
        'escalation_time': '604466ba-f0bc-4c5e-a2be-a52e01adf92d'
    },
    
    # Legacy mappings (kept for backward compatibility)
    'view_mappings': {},
    'view_ids': {}
}

# Performance rating thresholds (for KPI score interpretation)
PERFORMANCE_THRESHOLDS = {
    'excellent': 90,       # 90%+
    'good': 80,            # 80-89%
    'average': 70,         # 70-79%
    'below_average': 60,   # 60-69%
    'needs_improvement': 59, # 50-59%
}
