"""
Agent Info Manager
Loads and caches agent metadata from Google Sheets (Agent Info & Team Distribution)
"""

import logging
from typing import Optional, Dict, List
from datetime import datetime
import pandas as pd

from sheets import GoogleSheetsClient
from config import GOOGLE_SHEETS_CONFIG, AGENT_INFO_COLUMNS


class AgentInfoManager:
    """Manages agent metadata loaded from Google Sheets"""
    
    def __init__(self, sheets_client: GoogleSheetsClient = None):
        """
        Initialize Agent Info Manager
        
        Args:
            sheets_client: GoogleSheetsClient instance (creates new if not provided)
        """
        self.logger = logging.getLogger(__name__)
        self.sheets_client = sheets_client or GoogleSheetsClient()
        
        # Cache for loaded agent info
        self.agent_info_cache = None
        self.last_load_time = None
    
    def load_agent_info(self, force_reload: bool = False) -> pd.DataFrame:
        """
        Load agent info from Google Sheets
        
        Args:
            force_reload: If True, reload even if cached data exists
            
        Returns:
            DataFrame with agent information
        """
        # Return cached data if available and not forcing reload
        if not force_reload and self.agent_info_cache is not None:
            self.logger.info("Using cached agent info")
            return self.agent_info_cache
        
        try:
            # Connect to Google Sheets
            if not self.sheets_client.client:
                if not self.sheets_client.connect():
                    self.logger.error("Failed to connect to Google Sheets")
                    return pd.DataFrame()
            
            # Get spreadsheet ID and sheet name
            config = GOOGLE_SHEETS_CONFIG['temp_agent_info']
            spreadsheet_id = config['spreadsheet_id']
            sheet_name = config['sheet_name']
            
            self.logger.info(f"Loading agent info from sheet: {sheet_name}")
            
            # Read the sheet
            df = self.sheets_client.read_sheet_data(spreadsheet_id, sheet_name)
            
            if df.empty:
                self.logger.warning("Agent info sheet is empty")
                return pd.DataFrame()
            
            # Standardize column names (handle variations)
            df.columns = df.columns.str.strip()
            
            # Map columns according to AGENT_INFO_COLUMNS config
            # Handle variations in column names
            column_mapping = {}
            for expected_col, config_name in AGENT_INFO_COLUMNS.items():
                # Try exact match first
                if config_name in df.columns:
                    column_mapping[config_name] = expected_col
                else:
                    # Try case-insensitive match
                    for actual_col in df.columns:
                        if actual_col.lower() == config_name.lower():
                            column_mapping[actual_col] = expected_col
                            break
            
            # Rename columns if mapping found
            if column_mapping:
                df = df.rename(columns=column_mapping)
                self.logger.info(f"Renamed columns: {column_mapping}")
            
            # Ensure we have the basic required columns
            if 'name' not in df.columns:
                self.logger.error("Agent info sheet missing 'name' column")
                return pd.DataFrame()
            
            # Clean agent names (remove extra whitespace)
            df['name'] = df['name'].astype(str).str.strip()
            
            # Filter out empty agent names
            df = df[df['name'].notna() & (df['name'] != '')]
            
            self.logger.info(f"Loaded agent info for {len(df)} agents")
            self.logger.debug(f"Columns: {list(df.columns)}")
            
            # Cache the data
            self.agent_info_cache = df
            self.last_load_time = datetime.now()
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading agent info: {e}")
            return pd.DataFrame()
    
    def get_agent_info(self, agent_name: str) -> Optional[Dict]:
        """
        Get info for a specific agent
        
        Args:
            agent_name: Agent name to lookup
            
        Returns:
            Dictionary with agent info or None if not found
        """
        agent_info = self.load_agent_info()
        
        if agent_info.empty:
            return None
        
        # Try to find agent (case-insensitive, handle variations)
        agent_name_clean = agent_name.strip()
        
        # Try exact match first
        agent_row = agent_info[agent_info['name'].str.strip() == agent_name_clean]
        
        # Try case-insensitive match
        if agent_row.empty:
            agent_row = agent_info[agent_info['name'].str.strip().str.lower() == agent_name_clean.lower()]
        
        if agent_row.empty:
            self.logger.debug(f"Agent '{agent_name}' not found in agent info")
            return None
        
        # Convert to dictionary
        info_dict = agent_row.iloc[0].to_dict()
        
        return info_dict
    
    def get_agent_id(self, agent_name: str) -> Optional[str]:
        """
        Get agent ID for a given agent name
        
        Args:
            agent_name: Agent name
            
        Returns:
            Agent ID or None if not found
        """
        info = self.get_agent_info(agent_name)
        return info.get('_id') if info else None
    
    def get_team_color(self, agent_name: str) -> Optional[str]:
        """
        Get team color for a given agent name
        
        Args:
            agent_name: Agent name
            
        Returns:
            Team color or None if not found
        """
        info = self.get_agent_info(agent_name)
        return info.get('team_color') if info else None
    
    def get_fte_status(self, agent_name: str) -> Optional[str]:
        """
        Get FTE status for a given agent name
        
        Args:
            agent_name: Agent name
            
        Returns:
            FTE status or None if not found
        """
        info = self.get_agent_info(agent_name)
        return info.get('emp_fte_status') if info else None
    
    def add_agent_info_to_dataframe(self, df: pd.DataFrame, agent_name_column: str = 'agent_name') -> pd.DataFrame:
        """
        Add agent info columns to an existing dataframe
        
        Args:
            df: DataFrame to add agent info to
            agent_name_column: Name of the column containing agent names in df
            
        Returns:
            DataFrame with agent info columns added
        """
        if df.empty:
            return df
        
        # Load agent info
        agent_info = self.load_agent_info()
        
        if agent_info.empty:
            self.logger.warning("No agent info available to merge")
            return df
        
        # Merge agent info
        # Handle name variations - try exact match, then case-insensitive
        df_merged = df.copy()
        
        for idx, row in df.iterrows():
            agent_name = row[agent_name_column]
            agent_meta = self.get_agent_info(agent_name)
            
            if agent_meta:
                # Add all agent meta columns to dataframe
                for key, value in agent_meta.items():
                    if key not in df_merged.columns:
                        df_merged.at[idx, key] = value
        
        self.logger.info(f"Added agent info to {len(df)} rows")
        
        return df_merged
    
    def list_all_agents(self) -> List[str]:
        """
        Get list of all agent names
        
        Returns:
            List of agent names
        """
        agent_info = self.load_agent_info()
        
        if agent_info.empty:
            return []
        
        return agent_info['name'].tolist()
    
    def get_agents_by_team(self, team_color: str) -> List[str]:
        """
        Get list of agents for a specific team
        
        Args:
            team_color: Team color to filter by
            
        Returns:
            List of agent names
        """
        agent_info = self.load_agent_info()
        
        if agent_info.empty:
            return []
        
        team_agents = agent_info[agent_info['team_color'].str.lower() == team_color.lower()]
        return team_agents['name'].tolist()
    
    def refresh_cache(self):
        """Force reload of agent info cache"""
        self.agent_info_cache = None
        self.last_load_time = None
        self.logger.info("Agent info cache cleared")


# Standalone usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("="*70)
    print("Agent Info Manager - Testing")
    print("="*70)
    print()
    
    # Initialize manager
    manager = AgentInfoManager()
    
    # Load agent info
    print("📊 Loading agent info from Google Sheets...")
    agent_info = manager.load_agent_info()
    
    if not agent_info.empty:
        print(f"✅ Loaded info for {len(agent_info)} agents")
        print(f"\nColumns: {list(agent_info.columns)}")
        print("\nSample agents:")
        print(agent_info.head())
        
        # Test lookup
        if len(agent_info) > 0:
            sample_agent = agent_info.iloc[0]['name']
            print(f"\n🔍 Testing lookup for: {sample_agent}")
            
            info = manager.get_agent_info(sample_agent)
            if info:
                print(f"  Team: {info.get('team_color', 'N/A')}")
                print(f"  FTE Status: {info.get('emp_fte_status', 'N/A')}")
                print(f"  Start Date: {info.get('emp_start_date', 'N/A')}")
                print(f"  ID: {info.get('_id', 'N/A')}")
            
            # Test team filtering
            if 'team_color' in agent_info.columns:
                teams = agent_info['team_color'].unique()
                print(f"\n📊 Teams found: {teams}")
                for team in teams[:3]:  # Show first 3 teams
                    team_agents = manager.get_agents_by_team(team)
                    print(f"  • {team}: {len(team_agents)} agents")
    else:
        print("❌ Failed to load agent info")
    
    print("\n" + "="*70)
