"""
KPI Data Aggregator - Combine data from multiple sources
Aggregates Tableau (QA + KPI), Google Sheets (SLA), and Salesforce data
into Export-KPI and Export-QA format matching the KPI Calculator structure
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

from support_agent_audits import get_last_week_agent_scores, get_last_week_dates
from support_services_kpi import (
    get_csat_scores, get_response_times, get_resolution_time_data
)
from sla_cases import get_last_week_sla_data
from config import METRIC_GOALS


class KPIAggregator:
    """Aggregate KPI data from multiple sources into standardized format"""
    
    def __init__(self, week_start=None, week_end=None):
        """
        Initialize KPI aggregator
        
        Args:
            week_start (datetime): Start of week (defaults to last Sunday)
            week_end (datetime): End of week (defaults to last Saturday)
        """
        if week_start is None or week_end is None:
            self.week_start, self.week_end = get_last_week_dates()
        else:
            self.week_start = week_start
            self.week_end = week_end
        
        self.data = {
            'qa': None,
            'kpi': None,
            'sla': None,
            'salesforce': None
        }
        
        logging.info(f"KPI Aggregator initialized for week: {self.week_start.strftime('%Y-%m-%d')} to {self.week_end.strftime('%Y-%m-%d')}")
    
    def load_tableau_qa_data(self) -> bool:
        """
        Load QA audit data from Tableau
        
        Returns:
            bool: True if successful
        """
        try:
            logging.info("Loading QA audit data from Tableau...")
            df = get_last_week_agent_scores()
            
            if df is None or len(df) == 0:
                logging.warning("No QA data retrieved from Tableau")
                return False
            
            self.data['qa'] = df
            logging.info(f"Loaded QA data for {len(df)} agents")
            return True
            
        except Exception as e:
            logging.error(f"Failed to load QA data: {e}")
            return False
    
    def load_tableau_kpi_data(self) -> bool:
        """
        Load KPI metrics from Tableau (CSAT, response times, cases)
        
        Returns:
            bool: True if successful
        """
        try:
            logging.info("Loading KPI metrics from Tableau...")
            
            kpi_data = {}
            
            # Load CSAT data
            try:
                csat_df = get_csat_scores(self.week_start, self.week_end)
                if csat_df is not None and len(csat_df) > 0:
                    kpi_data['csat'] = csat_df
                    logging.info(f"  Loaded CSAT data: {len(csat_df)} records")
            except Exception as e:
                logging.warning(f"  Could not load CSAT data: {e}")
            
            # Load response time data
            for metric_type in ['chat', 'phone', 'email']:
                try:
                    response_df = get_response_times(metric_type, self.week_start, self.week_end)
                    if response_df is not None and len(response_df) > 0:
                        kpi_data[f'response_{metric_type}'] = response_df
                        logging.info(f"  Loaded {metric_type} response times: {len(response_df)} records")
                except Exception as e:
                    logging.warning(f"  Could not load {metric_type} response times: {e}")
            
            # Load resolution time data
            try:
                resolution_df = get_resolution_time_data(self.week_start, self.week_end)
                if resolution_df is not None and len(resolution_df) > 0:
                    kpi_data['resolution'] = resolution_df
                    logging.info(f"  Loaded resolution times: {len(resolution_df)} records")
            except Exception as e:
                logging.warning(f"  Could not load resolution times: {e}")
            
            if not kpi_data:
                logging.warning("No KPI data retrieved from Tableau")
                return False
            
            self.data['kpi'] = kpi_data
            logging.info(f"Loaded {len(kpi_data)} KPI metric types from Tableau")
            return True
            
        except Exception as e:
            logging.error(f"Failed to load KPI data: {e}")
            return False
    
    def load_google_sheets_sla_data(self) -> bool:
        """
        Load SLA cases data from Google Sheets
        
        Returns:
            bool: True if successful
        """
        try:
            logging.info("Loading SLA data from Google Sheets...")
            df = get_last_week_sla_data()
            
            if df is None or len(df) == 0:
                logging.warning("No SLA data retrieved from Google Sheets")
                return False
            
            self.data['sla'] = df
            logging.info(f"Loaded SLA data for {len(df)} agents")
            return True
            
        except Exception as e:
            logging.error(f"Failed to load SLA data: {e}")
            return False
    
    def load_salesforce_data(self) -> bool:
        """
        Load case data from Salesforce
        
        Returns:
            bool: True if successful
        """
        # TODO: Implement when Salesforce connection is available
        logging.info("Salesforce data loading not yet implemented")
        return False
    
    def generate_export_qa_tab(self) -> Optional[pd.DataFrame]:
        """
        Generate Export-QA tab data
        
        Structure matches: examples/[v2.4] KPI Calculator.xlsx - Export - QA tab
        Columns: Week, Agent Name, Team, BCF %, QA Score %, Cases Audited
        
        Returns:
            pd.DataFrame: QA export data or None if insufficient data
        """
        if self.data['qa'] is None:
            logging.error("Cannot generate Export-QA: No QA data loaded")
            return None
        
        try:
            df = self.data['qa'].copy()
            
            # Create base structure
            export_qa = pd.DataFrame()
            
            # Week column (formatted as "MM/DD/YYYY - MM/DD/YYYY")
            week_str = f"{self.week_start.strftime('%m/%d/%Y')} - {self.week_end.strftime('%m/%d/%Y')}"
            export_qa['Week'] = week_str
            
            # Agent Name - try multiple possible column names
            agent_col = None
            for possible_name in ['Agent Name', 'agent_name', 'Agent', 'Name']:
                if possible_name in df.columns:
                    agent_col = possible_name
                    break
            
            if agent_col is None:
                logging.error(f"Cannot find agent name column in QA data. Columns: {list(df.columns)}")
                return None
            
            export_qa['Agent Name'] = df[agent_col]
            
            # Team - if available in source data, otherwise leave blank
            if 'Team' in df.columns:
                export_qa['Team'] = df['Team']
            else:
                export_qa['Team'] = ''
            
            # BCF % - try multiple possible column names
            bcf_col = None
            for possible_name in ['Fail %', 'BCF %', 'BCF Percentage', 'Fail Percentage']:
                if possible_name in df.columns:
                    bcf_col = possible_name
                    break
            
            if bcf_col:
                # Convert to decimal if needed (e.g., 5% -> 0.05)
                bcf_values = pd.to_numeric(df[bcf_col], errors='coerce')
                if bcf_values.max() > 1:  # If values are like 5 instead of 0.05
                    bcf_values = bcf_values / 100
                export_qa['BCF %'] = bcf_values
            else:
                export_qa['BCF %'] = 0.0
                logging.warning("BCF % column not found in QA data")
            
            # QA Score % - try multiple possible column names
            score_col = None
            for possible_name in ['Avg Score', 'QA Score', 'Score', 'Average Score']:
                if possible_name in df.columns:
                    score_col = possible_name
                    break
            
            if score_col:
                # Convert to decimal if needed (e.g., 95 -> 0.95)
                score_values = pd.to_numeric(df[score_col], errors='coerce')
                if score_values.max() > 1:  # If values are like 95 instead of 0.95
                    score_values = score_values / 100
                export_qa['QA Score %'] = score_values
            else:
                export_qa['QA Score %'] = 0.0
                logging.warning("QA Score column not found in QA data")
            
            # Cases Audited - try multiple possible column names
            cases_col = None
            for possible_name in ['Cases', 'Cases Audited', 'Total Cases', '# Cases']:
                if possible_name in df.columns:
                    cases_col = possible_name
                    break
            
            if cases_col:
                export_qa['Cases Audited'] = pd.to_numeric(df[cases_col], errors='coerce').fillna(0).astype(int)
            else:
                export_qa['Cases Audited'] = 0
                logging.warning("Cases column not found in QA data")
            
            logging.info(f"Generated Export-QA tab with {len(export_qa)} agents")
            return export_qa
            
        except Exception as e:
            logging.error(f"Error generating Export-QA tab: {e}")
            return None
    
    def generate_export_kpi_tab(self) -> Optional[pd.DataFrame]:
        """
        Generate Export-KPI tab data
        
        Structure matches: examples/[v2.4] KPI Calculator.xlsx - Export - KPI tab
        Columns: Week, Agent Name, Time Utilization %, Total Hours, Working Hours,
                CSAT Responses, CSAT Positive, Chat Response (min), Phone Response (sec),
                Email Response (min), Cases Closed, Cases Transferred, SLA Cases (by day)
        
        Returns:
            pd.DataFrame: KPI export data or None if insufficient data
        """
        if self.data['kpi'] is None and self.data['qa'] is None:
            logging.error("Cannot generate Export-KPI: No KPI or QA data loaded")
            return None
        
        try:
            # Start with agent list from QA data or create from KPI data
            if self.data['qa'] is not None:
                agent_col = self._find_column(self.data['qa'], ['Agent Name', 'agent_name', 'Agent'])
                if agent_col:
                    agents = self.data['qa'][agent_col].unique()
                else:
                    agents = []
            else:
                agents = []
            
            # Create base structure
            export_kpi = pd.DataFrame()
            
            # Week column
            week_str = f"{self.week_start.strftime('%m/%d/%Y')} - {self.week_end.strftime('%m/%d/%Y')}"
            export_kpi['Week'] = week_str
            export_kpi['Agent Name'] = agents if len(agents) > 0 else ['No agents found']
            
            # Initialize all columns with default values
            export_kpi['Time Utilization %'] = 0.0
            export_kpi['Total Hours'] = 0.0
            export_kpi['Working Hours'] = 40.0  # Default to 40 hours/week
            export_kpi['CSAT Responses'] = 0
            export_kpi['CSAT Positive'] = 0
            export_kpi['Chat Response (min)'] = 0.0
            export_kpi['Phone Response (sec)'] = 0.0
            export_kpi['Email Response (min)'] = 0.0
            export_kpi['Cases Closed'] = 0
            export_kpi['Cases Transferred'] = 0
            
            # Add SLA columns for each day of the week
            days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            for day in days:
                export_kpi[f'SLA {day}'] = 0
            
            # Populate CSAT data if available
            if self.data['kpi'] and 'csat' in self.data['kpi']:
                export_kpi = self._merge_csat_data(export_kpi, self.data['kpi']['csat'])
            
            # Populate response time data if available
            if self.data['kpi']:
                for metric in ['chat', 'phone', 'email']:
                    key = f'response_{metric}'
                    if key in self.data['kpi']:
                        export_kpi = self._merge_response_time_data(
                            export_kpi, self.data['kpi'][key], metric
                        )
            
            # Populate SLA data if available
            if self.data['sla'] is not None:
                export_kpi = self._merge_sla_data(export_kpi, self.data['sla'])
            
            # Populate Salesforce case data if available
            if self.data['salesforce'] is not None:
                export_kpi = self._merge_salesforce_data(export_kpi, self.data['salesforce'])
            
            logging.info(f"Generated Export-KPI tab with {len(export_kpi)} agents")
            return export_kpi
            
        except Exception as e:
            logging.error(f"Error generating Export-KPI tab: {e}")
            return None
    
    def _find_column(self, df: pd.DataFrame, possible_names: list) -> Optional[str]:
        """Find a column by trying multiple possible names"""
        for name in possible_names:
            if name in df.columns:
                return name
        return None
    
    def _merge_csat_data(self, export_kpi: pd.DataFrame, csat_df: pd.DataFrame) -> pd.DataFrame:
        """Merge CSAT data into export_kpi DataFrame"""
        try:
            agent_col = self._find_column(csat_df, ['Agent Name', 'agent_name', 'Agent'])
            if not agent_col:
                logging.warning("Cannot find agent column in CSAT data")
                return export_kpi
            
            # Aggregate CSAT by agent
            csat_agg = csat_df.groupby(agent_col).agg({
                # Find response count column
                **{col: 'count' for col in ['CSAT Score', 'Rating', 'Score'] if col in csat_df.columns}
            }).reset_index()
            
            # Count positive responses (assuming 4+ out of 5 is positive, or 0.8+ if decimal)
            score_col = self._find_column(csat_df, ['CSAT Score', 'Rating', 'Score'])
            if score_col:
                csat_df['is_positive'] = pd.to_numeric(csat_df[score_col], errors='coerce') >= 0.8
                positive_counts = csat_df.groupby(agent_col)['is_positive'].sum().reset_index()
                positive_counts.columns = [agent_col, 'CSAT Positive']
                
                csat_agg = csat_agg.merge(positive_counts, on=agent_col, how='left')
            
            # Merge into export_kpi
            export_kpi = export_kpi.merge(
                csat_agg, left_on='Agent Name', right_on=agent_col, how='left', suffixes=('', '_csat')
            )
            
            # Update CSAT columns
            if 'CSAT Positive' in csat_agg.columns:
                export_kpi['CSAT Positive'] = export_kpi['CSAT Positive_csat'].fillna(0).astype(int)
            
            logging.info("Merged CSAT data")
            
        except Exception as e:
            logging.warning(f"Could not merge CSAT data: {e}")
        
        return export_kpi
    
    def _merge_response_time_data(self, export_kpi: pd.DataFrame, response_df: pd.DataFrame, 
                                  metric_type: str) -> pd.DataFrame:
        """Merge response time data into export_kpi DataFrame"""
        try:
            agent_col = self._find_column(response_df, ['Agent Name', 'agent_name', 'Agent'])
            time_col = self._find_column(response_df, ['Response Time', 'Avg Response Time', 'Time'])
            
            if not agent_col or not time_col:
                logging.warning(f"Cannot find required columns in {metric_type} response data")
                return export_kpi
            
            # Aggregate by agent (average response time)
            agg_df = response_df.groupby(agent_col)[time_col].mean().reset_index()
            agg_df.columns = ['Agent', f'{metric_type}_response']
            
            # Merge into export_kpi
            export_kpi = export_kpi.merge(agg_df, left_on='Agent Name', right_on='Agent', how='left')
            
            # Update appropriate column
            if metric_type == 'chat':
                export_kpi['Chat Response (min)'] = export_kpi['chat_response'].fillna(0)
            elif metric_type == 'phone':
                export_kpi['Phone Response (sec)'] = export_kpi['phone_response'].fillna(0)
            elif metric_type == 'email':
                export_kpi['Email Response (min)'] = export_kpi['email_response'].fillna(0)
            
            logging.info(f"Merged {metric_type} response time data")
            
        except Exception as e:
            logging.warning(f"Could not merge {metric_type} response time data: {e}")
        
        return export_kpi
    
    def _merge_sla_data(self, export_kpi: pd.DataFrame, sla_df: pd.DataFrame) -> pd.DataFrame:
        """Merge SLA cases data into export_kpi DataFrame"""
        try:
            agent_col = self._find_column(sla_df, ['Agent Name', 'agent_name', 'Agent'])
            if not agent_col:
                logging.warning("Cannot find agent column in SLA data")
                return export_kpi
            
            # SLA data should have columns for each day
            days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            
            for day in days:
                if day in sla_df.columns:
                    # Merge day data
                    day_data = sla_df[[agent_col, day]].copy()
                    day_data.columns = ['Agent', f'SLA {day}']
                    
                    export_kpi = export_kpi.merge(
                        day_data, left_on='Agent Name', right_on='Agent', 
                        how='left', suffixes=('', f'_{day}')
                    )
                    
                    # Update SLA column
                    if f'SLA {day}_{day}' in export_kpi.columns:
                        export_kpi[f'SLA {day}'] = export_kpi[f'SLA {day}_{day}'].fillna(0).astype(int)
            
            logging.info("Merged SLA data")
            
        except Exception as e:
            logging.warning(f"Could not merge SLA data: {e}")
        
        return export_kpi
    
    def _merge_salesforce_data(self, export_kpi: pd.DataFrame, sf_data: Dict) -> pd.DataFrame:
        """Merge Salesforce case data into export_kpi DataFrame"""
        # TODO: Implement when Salesforce data is available
        logging.info("Salesforce data merging not yet implemented")
        return export_kpi


# Standalone usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("="*70)
    print("KPI Data Aggregator - Testing")
    print("="*70)
    print()
    
    # Initialize aggregator for last week
    aggregator = KPIAggregator()
    
    # Load Tableau data
    print("📊 Loading Tableau data...")
    qa_success = aggregator.load_tableau_qa_data()
    kpi_success = aggregator.load_tableau_kpi_data()
    
    if qa_success:
        print(f"✅ QA data loaded: {len(aggregator.data['qa'])} agents")
    else:
        print("❌ Failed to load QA data")
    
    if kpi_success:
        kpi_types = len(aggregator.data['kpi'])
        print(f"✅ KPI data loaded: {kpi_types} metric types")
    else:
        print("❌ Failed to load KPI data")
    
    # Load Google Sheets SLA data
    print("\n📊 Loading Google Sheets SLA data...")
    sla_success = aggregator.load_google_sheets_sla_data()
    
    if sla_success:
        print(f"✅ SLA data loaded: {len(aggregator.data['sla'])} agents")
    else:
        print("❌ Failed to load SLA data (may not have permissions yet)")
    
    # Generate Export-QA tab
    print("\n📋 Generating Export-QA tab...")
    export_qa = aggregator.generate_export_qa_tab()
    
    if export_qa is not None:
        print(f"✅ Export-QA generated: {len(export_qa)} rows")
        print("\nPreview:")
        print(export_qa.head())
    else:
        print("❌ Failed to generate Export-QA tab")
    
    # Generate Export-KPI tab
    print("\n📋 Generating Export-KPI tab...")
    export_kpi = aggregator.generate_export_kpi_tab()
    
    if export_kpi is not None:
        print(f"✅ Export-KPI generated: {len(export_kpi)} rows, {len(export_kpi.columns)} columns")
        print("\nColumns:", list(export_kpi.columns))
        print("\nPreview:")
        print(export_kpi.head())
    else:
        print("❌ Failed to generate Export-KPI tab")
    
    print("\n" + "="*70)
