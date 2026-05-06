"""
Dataframe Generator
Generates comprehensive dataframes combining export data, calculated scores, and agent info
"""

import logging
from pathlib import Path
from datetime import datetime
import pandas as pd

from core import AmplifyKPICalculator
from models import AgentInfoManager
from config import DATA_PATHS


class DataframeGenerator:
    """Generates comprehensive dataframes with exports + scores + agent info"""
    
    def __init__(self, sheets_client=None):
        """
        Initialize Dataframe Generator
        
        Args:
            sheets_client: Optional GoogleSheetsClient instance
        """
        self.logger = logging.getLogger(__name__)
        self.agent_info_manager = AgentInfoManager(sheets_client)
        self.output_dir = Path(DATA_PATHS['base']) / 'dataframes'
        self.output_dir.mkdir(exist_ok=True, parents=True)
    
    def generate_comprehensive_dataframe(
        self,
        export_kpi: pd.DataFrame,
        export_qa: pd.DataFrame,
        week_start: datetime,
        week_end: datetime,
        calculator: AmplifyKPICalculator = None
    ) -> pd.DataFrame:
        """
        Generate comprehensive dataframe with all data
        
        Args:
            export_kpi: Export-KPI DataFrame
            export_qa: Export-QA DataFrame
            week_start: Week start date
            week_end: Week end date
            calculator: Optional pre-initialized calculator
            
        Returns:
            Comprehensive DataFrame with agent metadata, export data, and scores
        """
        self.logger.info("Generating comprehensive dataframe...")
        
        # Initialize calculator if not provided
        if calculator is None:
            # Create a merged dataset for calculator
            # First, merge export KPI and QA data
            merged_data = export_kpi.copy()
            
            # Merge QA data by agent name
            agent_col = None
            for col in ['Agent Name', 'Name', 'agent_name']:
                if col in export_qa.columns:
                    agent_col = col
                    break
            
            if agent_col and 'Agent Name' in merged_data.columns:
                # Merge QA columns into KPI data
                qa_merge_cols = [col for col in export_qa.columns if col != agent_col]
                qa_data_to_merge = export_qa[['Agent Name'] + qa_merge_cols] if 'Agent Name' in export_qa.columns else export_qa
                
                merged_data = merged_data.merge(
                    qa_data_to_merge,
                    on='Agent Name',
                    how='left'
                )
            
            calculator = AmplifyKPICalculator(merged_data)
        
        # Calculate scores for all agents
        scores_df = calculator.calculate_all_agents()
        
        if scores_df.empty:
            self.logger.warning("No scores calculated - returning empty dataframe")
            return pd.DataFrame()
        
        # Load agent info
        agent_info = self.agent_info_manager.load_agent_info()
        
        # Merge all data
        comprehensive_df = scores_df.copy()
        
        # Add agent info if available
        if not agent_info.empty:
            # Match agents and add metadata
            agent_info_dict = {}
            for idx, row in agent_info.iterrows():
                agent_name = row.get('name', '')
                agent_info_dict[agent_name] = {
                    'agent_id': row.get('_id', ''),
                    'team_color': row.get('team_color', ''),
                    'emp_fte_status': row.get('emp_fte_status', ''),
                    'emp_start_date': row.get('emp_start_date', ''),
                    'emp_notes': row.get('emp_notes', '')
                }
            
            # Add agent info columns
            for idx, row in comprehensive_df.iterrows():
                agent_name = row.get('agent_name', '')
                if agent_name in agent_info_dict:
                    info = agent_info_dict[agent_name]
                    comprehensive_df.at[idx, 'agent_id'] = info['agent_id']
                    comprehensive_df.at[idx, 'team_color'] = info['team_color']
                    comprehensive_df.at[idx, 'emp_fte_status'] = info['emp_fte_status']
                    comprehensive_df.at[idx, 'emp_start_date'] = info['emp_start_date']
                    comprehensive_df.at[idx, 'emp_notes'] = info['emp_notes']
        
        # Add week information
        week_str = f"{week_start.strftime('%m/%d/%Y')} - {week_end.strftime('%m/%d/%Y')}"
        comprehensive_df['week_start'] = week_start
        comprehensive_df['week_end'] = week_end
        comprehensive_df['week'] = week_str
        
        self.logger.info(
            f"Generated comprehensive dataframe: "
            f"{len(comprehensive_df)} rows, {len(comprehensive_df.columns)} columns"
        )
        
        return comprehensive_df
    
    def save_dataframe_with_timestamp(
        self,
        df: pd.DataFrame,
        week_start: datetime,
        week_end: datetime,
        filename_prefix: str = 'KPI_Comprehensive'
    ) -> Path:
        """
        Save dataframe with timestamp
        
        Args:
            df: DataFrame to save
            week_start: Week start date
            week_end: Week end date
            filename_prefix: Prefix for filename
            
        Returns:
            Path to saved file
        """
        if df.empty:
            self.logger.warning("Cannot save empty dataframe")
            return None
        
        # Generate filename
        start_str = week_start.strftime('%Y-%m-%d')
        end_str = week_end.strftime('%Y-%m-%d')
        filename = f"{filename_prefix}_{start_str}_{end_str}.csv"
        filepath = self.output_dir / filename
        
        # Save to CSV
        df.to_csv(filepath, index=False)
        
        self.logger.info(f"✅ Saved comprehensive dataframe: {filepath}")
        
        return filepath
    
    def generate_and_save(
        self,
        export_kpi: pd.DataFrame,
        export_qa: pd.DataFrame,
        week_start: datetime,
        week_end: datetime
    ) -> tuple:
        """
        Generate comprehensive dataframe and save it
        
        Args:
            export_kpi: Export-KPI DataFrame
            export_qa: Export-QA DataFrame
            week_start: Week start date
            week_end: Week end date
            
        Returns:
            Tuple of (comprehensive_dataframe, filepath)
        """
        # Generate comprehensive dataframe
        comprehensive_df = self.generate_comprehensive_dataframe(
            export_kpi, export_qa, week_start, week_end
        )
        
        # Save it
        filepath = self.save_dataframe_with_timestamp(
            comprehensive_df, week_start, week_end
        )
        
        return comprehensive_df, filepath


# Standalone usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("="*70)
    print("Dataframe Generator - Testing")
    print("="*70)
    print()
    
    # Create sample data
    from datetime import datetime, timedelta
    from main import get_last_week_dates
    
    week_start, week_end = get_last_week_dates()
    
    sample_kpi = pd.DataFrame({
        'Name': ['Test Agent 1', 'Test Agent 2'],
        'Time Utilization Percent': [0.90, 0.85],
        'Total Hours Worked': [40.0, 38.0],
        'Cases Closed': [50, 45]
    })
    
    sample_qa = pd.DataFrame({
        'Agent Name': ['Test Agent 1', 'Test Agent 2'],
        'QA Score': [95.0, 92.0],
        'BCF %': [0.02, 0.05]
    })
    
    print("Testing dataframe generation...")
    
    generator = DataframeGenerator()
    
    # Uncomment to test (requires full setup)
    # comprehensive_df, filepath = generator.generate_and_save(
    #     sample_kpi, sample_qa, week_start, week_end
    # )
    # print(f"Generated: {len(comprehensive_df)} rows")
    # print(f"Saved to: {filepath}")
    
    print("\n" + "="*70)
