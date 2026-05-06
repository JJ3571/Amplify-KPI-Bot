"""
Data import module for KPI Calculator Bot
Handles CSV exports from Tableau, Salesforce, and G-Sheets
"""

import pandas as pd
import glob
import os
from pathlib import Path
import logging
from config import EXPORT_FILE_PATTERNS, EXPORT_COLUMNS

class DataImporter:
    def __init__(self, data_folder="exports"):
        """
        Initialize data importer
        
        Args:
            data_folder (str): Path to folder containing CSV exports
        """
        self.data_folder = Path(data_folder)
        self.data_folder.mkdir(exist_ok=True)
        
        # Storage for loaded data
        self.kpi_data = {}
        self.qa_data = {}
        self.agent_lookup = {}
        
    def load_csv_files(self):
        """
        Load all CSV files from the exports folder based on naming patterns
        
        Returns:
            dict: Dictionary containing all loaded datasets
        """
        logging.info(f"Loading CSV files from {self.data_folder}")
        
        datasets = {}
        
        for data_type, pattern in EXPORT_FILE_PATTERNS.items():
            files = glob.glob(str(self.data_folder / pattern))
            
            if files:
                # Use the most recent file if multiple matches
                latest_file = max(files, key=os.path.getctime)
                try:
                    df = pd.read_csv(latest_file)
                    datasets[data_type] = df
                    logging.info(f"Loaded {data_type}: {latest_file} ({len(df)} rows)")
                except Exception as e:
                    logging.error(f"Error loading {latest_file}: {e}")
            else:
                logging.warning(f"No files found for pattern: {pattern}")
        
        return datasets
    
    def process_time_utilization_data(self, df):
        """
        Process time utilization export data
        
        Args:
            df (pd.DataFrame): Raw time utilization data
            
        Returns:
            pd.DataFrame: Processed data with agent lookup
        """
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Standard columns expected: Agent Name, Time Utilization Percent, Total Hours Worked
        required_cols = ['Name', 'Time Utilization Percent', 'Total Hours Worked']
        
        # Find actual column names (may vary slightly)
        col_mapping = {}
        for req_col in required_cols:
            for actual_col in df.columns:
                if req_col.lower() in actual_col.lower():
                    col_mapping[req_col] = actual_col
                    break
        
        if len(col_mapping) < len(required_cols):
            missing = [col for col in required_cols if col not in col_mapping]
            logging.warning(f"Missing required columns in time utilization data: {missing}")
            logging.warning(f"Found columns: {list(df.columns)}")
            raise ValueError(f"Missing required columns: {missing}")
        
        # Standardize column names
        df_clean = df.rename(columns={v: k for k, v in col_mapping.items()})
        
        # Clean and convert data types
        if 'Time Utilization Percent' in df_clean.columns:
            df_clean['Time Utilization Percent'] = (
                df_clean['Time Utilization Percent']
                .astype(str)
                .str.replace('%', '')
                .str.replace(',', '')
            )
            df_clean['Time Utilization Percent'] = pd.to_numeric(
                df_clean['Time Utilization Percent'], errors='coerce'
            ) / 100
        
        if 'Total Hours Worked' in df_clean.columns:
            df_clean['Total Hours Worked'] = pd.to_numeric(
                df_clean['Total Hours Worked'], errors='coerce'
            )
        
        return df_clean
    
    def process_csat_data(self, df):
        """
        Process CSAT export data
        
        Args:
            df (pd.DataFrame): Raw CSAT data
            
        Returns:
            pd.DataFrame: Processed CSAT data
        """
        # Expected columns: Agent Name, Total Responses, Positive Responses (4-5 rating)
        df.columns = df.columns.str.strip()
        
        # Validate required columns exist
        required_cols = ['Name']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logging.error(f"Missing required columns in CSAT data: {missing_cols}")
            logging.error(f"Available columns: {list(df.columns)}")
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Clean agent names
        if 'Name' in df.columns:
            df['Name'] = df['Name'].str.strip()
        
        # Convert numeric columns
        numeric_cols = ['Total Responses', 'Positive Responses', 'CSAT Score']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def process_response_time_data(self, df, response_type):
        """
        Process initial response time data (Chat/Phone/Email)
        
        Args:
            df (pd.DataFrame): Raw response time data
            response_type (str): Type of response (chat/phone/email)
            
        Returns:
            pd.DataFrame: Processed response time data
        """
        df.columns = df.columns.str.strip()
        
        # Validate Name column exists
        if 'Name' not in df.columns:
            logging.error(f"Missing 'Name' column in {response_type} response time data")
            logging.error(f"Available columns: {list(df.columns)}")
            raise ValueError(f"Missing required 'Name' column in {response_type} response time data")
        
        # Clean agent names
        if 'Name' in df.columns:
            df['Name'] = df['Name'].str.strip()
        
        # Find the response time column
        time_col = None
        for col in df.columns:
            if 'response' in col.lower() or 'time' in col.lower():
                time_col = col
                break
        
        if time_col:
            logging.debug(f"Found {response_type} response time column: {time_col}")
        else:
            logging.warning(f"No response time column found in {response_type} data")
        
        if time_col:
            # Convert to numeric, handling various formats
            df[f'{response_type}_response_time'] = pd.to_numeric(df[time_col], errors='coerce')
            
            # Convert units if needed (phone is in seconds, others in minutes)
            if response_type == 'phone':
                # Phone response should be in seconds
                pass
            else:
                # Chat and email should be in minutes
                pass
        
        return df
    
    def process_cases_data(self, df, case_type):
        """
        Process cases data (closed/transferred)
        
        Args:
            df (pd.DataFrame): Raw cases data
            case_type (str): Type of cases (closed/transferred)
            
        Returns:
            pd.DataFrame: Processed cases data
        """
        df.columns = df.columns.str.strip()
        
        # Cases data typically has Case Owner column
        if 'Case Owner' in df.columns:
            # Count cases by agent
            agent_counts = df['Case Owner'].value_counts().reset_index()
            agent_counts.columns = ['Name', f'{case_type}_cases']
            return agent_counts
        else:
            logging.warning(f"No 'Case Owner' column found in {case_type} cases data")
            return pd.DataFrame()
    
    def process_sla_data(self, df):
        """
        Process SLA cases data
        
        Args:
            df (pd.DataFrame): Raw SLA cases data
            
        Returns:
            pd.DataFrame: Processed SLA data
        """
        df.columns = df.columns.str.strip()
        
        if 'Case Owner' in df.columns:
            # Count SLA violations by agent
            sla_counts = df['Case Owner'].value_counts().reset_index()
            sla_counts.columns = ['Name', 'sla_cases']
            return sla_counts
        else:
            logging.warning("No 'Case Owner' column found in SLA data")
            return pd.DataFrame()
    
    def process_qa_data(self, df, qa_type):
        """
        Process QA export data (scores/BCF/case count)
        
        Args:
            df (pd.DataFrame): Raw QA data
            qa_type (str): Type of QA data (scores/bcf/case_count)
            
        Returns:
            pd.DataFrame: Processed QA data
        """
        df.columns = df.columns.str.strip()
        
        # Clean agent names
        if 'Agent Name' in df.columns:
            df['Name'] = df['Agent Name'].str.strip()
        elif 'Name' in df.columns:
            df['Name'] = df['Name'].str.strip()
        
        # Process based on QA type
        if qa_type == 'scores':
            if 'Avg Score' in df.columns:
                df['qa_score'] = pd.to_numeric(df['Avg Score'], errors='coerce')
        elif qa_type == 'bcf':
            if 'Fail % (BCF percentage)' in df.columns:
                df['bcf_percentage'] = (
                    df['Fail % (BCF percentage)']
                    .astype(str)
                    .str.replace('%', '')
                    .pipe(lambda x: pd.to_numeric(x, errors='coerce') / 100)
                )
        elif qa_type == 'case_count':
            if 'Case Count' in df.columns:
                df['qa_cases_audited'] = pd.to_numeric(df['Case Count'], errors='coerce')
        
        return df
    
    def merge_all_data(self, datasets):
        """
        Merge all datasets into a comprehensive agent dataset
        
        Args:
            datasets (dict): Dictionary of processed datasets
            
        Returns:
            pd.DataFrame: Merged dataset with all KPI metrics per agent
        """
        # Start with a base agent list
        agent_df = None
        
        # Process each dataset and merge
        for data_type, df in datasets.items():
            if df.empty:
                continue
            
            if data_type == 'time_utilization':
                df_processed = self.process_time_utilization_data(df)
            elif data_type == 'csat':
                df_processed = self.process_csat_data(df)
            elif data_type in ['initial_chat', 'initial_phone', 'initial_email']:
                response_type = data_type.replace('initial_', '')
                df_processed = self.process_response_time_data(df, response_type)
            elif data_type in ['cases_closed', 'cases_transferred']:
                case_type = data_type.replace('cases_', '')
                df_processed = self.process_cases_data(df, case_type)
            elif data_type == 'sla_cases':
                df_processed = self.process_sla_data(df)
            elif data_type.startswith('qa_'):
                qa_type = data_type.replace('qa_', '')
                df_processed = self.process_qa_data(df, qa_type)
            else:
                df_processed = df
            
            # Merge with main dataframe
            if agent_df is None:
                agent_df = df_processed
            else:
                agent_df = agent_df.merge(df_processed, on='Name', how='outer')
        
        # Fill NaN values with 0 for numeric columns
        numeric_columns = agent_df.select_dtypes(include=['number']).columns
        agent_df[numeric_columns] = agent_df[numeric_columns].fillna(0)
        
        logging.info(f"Merged data for {len(agent_df)} agents with {len(agent_df.columns)} metrics")
        
        return agent_df
    
    def load_and_process_all(self):
        """
        Complete pipeline to load and process all export data
        
        Returns:
            pd.DataFrame: Complete agent dataset ready for KPI calculation
        """
        # Load all CSV files
        raw_datasets = self.load_csv_files()
        
        if not raw_datasets:
            logging.error("No data files found. Please check the exports folder.")
            return pd.DataFrame()
        
        # Merge and process all data
        merged_data = self.merge_all_data(raw_datasets)
        
        return merged_data