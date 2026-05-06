"""
Connection Checker - Test availability of data sources
Tests Tableau, Google Sheets, and Salesforce connections
"""

import logging
from pathlib import Path
import json
from typing import Dict, Tuple

# Import clients
from .tableau_client import TableauClient
from sheets import GoogleSheetsClient
from .salesforce_client import SalesforceClient
from config import TABLEAU_CONFIG, GOOGLE_SHEETS_CONFIG


class ConnectionChecker:
    """Check health and availability of all data source connections"""
    
    def __init__(self):
        """Initialize connection checker"""
        self.credentials_file = Path('credentials.json')
        self.results = {
            'tableau': {'available': False, 'message': ''},
            'google_sheets': {'available': False, 'message': ''},
            'salesforce': {'available': False, 'message': ''}
        }
    
    def check_all_connections(self) -> Dict[str, Dict]:
        """
        Check all data source connections
        
        Returns:
            dict: Connection status for each source
                  {source_name: {'available': bool, 'message': str}}
        """
        logging.info("Checking all data source connections...")
        
        # Check each connection
        self.results['tableau'] = self._check_tableau()
        self.results['google_sheets'] = self._check_google_sheets()
        self.results['salesforce'] = self._check_salesforce()
        
        # Log summary
        available = [name for name, status in self.results.items() if status['available']]
        logging.info(f"Available connections: {', '.join(available) if available else 'None'}")
        
        return self.results
    
    def _check_tableau(self) -> Dict[str, any]:
        """
        Check Tableau connection
        
        Returns:
            dict: {'available': bool, 'message': str}
        """
        try:
            # Check credentials file exists
            if not self.credentials_file.exists():
                return {
                    'available': False,
                    'message': 'credentials.json not found'
                }
            
            # Load and check for Tableau credentials
            with open(self.credentials_file) as f:
                creds = json.load(f)
            
            if 'tableau_api_key' not in creds:
                return {
                    'available': False,
                    'message': 'tableau_api_key not in credentials.json'
                }
            
            # Check config
            if not TABLEAU_CONFIG.get('server_url'):
                return {
                    'available': False,
                    'message': 'server_url not configured in config.py'
                }
            
            # Try to connect
            client = TableauClient()
            if not client.connect(TABLEAU_CONFIG['server_url'], TABLEAU_CONFIG.get('site_name', '')):
                return {
                    'available': False,
                    'message': 'Authentication failed - check credentials and server URL'
                }
            
            # Get view count to verify access
            views = client.get_views()
            client.disconnect()
            
            if views is None or len(views) == 0:
                return {
                    'available': False,
                    'message': 'No views accessible - check permissions'
                }
            
            return {
                'available': True,
                'message': f'Connected successfully - {len(views)} views accessible'
            }
            
        except Exception as e:
            return {
                'available': False,
                'message': f'Error: {str(e)}'
            }
    
    def _check_google_sheets(self) -> Dict[str, any]:
        """
        Check Google Sheets connection
        
        Returns:
            dict: {'available': bool, 'message': str}
        """
        try:
            # Check credentials file exists
            if not self.credentials_file.exists():
                return {
                    'available': False,
                    'message': 'credentials.json not found'
                }
            
            # Check for service account credentials
            if not Path('credentials.json').exists():
                return {
                    'available': False,
                    'message': 'Google service account credentials.json not found'
                }
            
            # Try to connect
            client = GoogleSheetsClient()
            if not client.connect():
                return {
                    'available': False,
                    'message': 'Failed to authenticate with Google Sheets API'
                }
            
            # Try to open SLA spreadsheet
            sla_config = GOOGLE_SHEETS_CONFIG.get('sla_cases')
            if not sla_config:
                return {
                    'available': False,
                    'message': 'SLA spreadsheet not configured in config.py'
                }
            
            try:
                spreadsheet = client.get_spreadsheet(sla_config['spreadsheet_id'])
                
                # Check if we can access the sheet
                sheet = spreadsheet.worksheet(sla_config['sheet_name'])
                
                return {
                    'available': True,
                    'message': f'Connected successfully - SLA spreadsheet accessible'
                }
            except Exception as e:
                error_msg = str(e)
                if 'PERMISSION_DENIED' in error_msg:
                    return {
                        'available': False,
                        'message': 'Permission denied - share spreadsheet with service account'
                    }
                else:
                    return {
                        'available': False,
                        'message': f'Cannot access spreadsheet: {error_msg}'
                    }
            
        except Exception as e:
            return {
                'available': False,
                'message': f'Error: {str(e)}'
            }
    
    def _check_salesforce(self) -> Dict[str, any]:
        """
        Check Salesforce connection
        
        Returns:
            dict: {'available': bool, 'message': str}
        """
        try:
            # Check credentials file exists
            if not self.credentials_file.exists():
                return {
                    'available': False,
                    'message': 'credentials.json not found'
                }
            
            # Load and check for Salesforce credentials
            with open(self.credentials_file) as f:
                creds = json.load(f)
            
            salesforce_config = creds.get('salesforce', {})
            
            # Check for OAuth refresh token
            if salesforce_config.get('auth_type') == 'oauth_refresh':
                if not salesforce_config.get('refresh_token'):
                    return {
                        'available': False,
                        'message': 'OAuth not configured - run scripts/salesforce_oauth_setup.py'
                    }
                
                # Try to connect
                try:
                    client = SalesforceClient()
                    if client.connect():
                        # Test with a simple query
                        result = client.sf.query("SELECT Id FROM Case LIMIT 1")
                        return {
                            'available': True,
                            'message': 'Connected successfully via OAuth'
                        }
                    else:
                        return {
                            'available': False,
                            'message': 'OAuth authentication failed'
                        }
                except Exception as e:
                    return {
                        'available': False,
                        'message': f'Connection failed: {str(e)}'
                    }
            else:
                return {
                    'available': False,
                    'message': 'Salesforce not configured (awaiting Connected App approval)'
                }
            
        except Exception as e:
            return {
                'available': False,
                'message': f'Error: {str(e)}'
            }
    
    def get_available_sources(self) -> Tuple[bool, bool, bool]:
        """
        Get simple boolean flags for available data sources
        
        Returns:
            tuple: (tableau_available, sheets_available, salesforce_available)
        """
        return (
            self.results['tableau']['available'],
            self.results['google_sheets']['available'],
            self.results['salesforce']['available']
        )
    
    def print_status_report(self):
        """Print a formatted status report of all connections"""
        print("\n" + "="*70)
        print("DATA SOURCE CONNECTION STATUS")
        print("="*70)
        
        for source_name, status in self.results.items():
            icon = "✅" if status['available'] else "❌"
            name = source_name.replace('_', ' ').title()
            print(f"\n{icon} {name}")
            print(f"   {status['message']}")
        
        # Summary
        available_count = sum(1 for s in self.results.values() if s['available'])
        print("\n" + "="*70)
        print(f"Summary: {available_count}/3 data sources available")
        
        if available_count == 0:
            print("\n⚠️  No data sources available - check credentials and configuration")
        elif available_count < 3:
            unavailable = [name.replace('_', ' ').title() 
                          for name, status in self.results.items() 
                          if not status['available']]
            print(f"\n⚠️  Missing: {', '.join(unavailable)}")
            print("   See setup documentation in data/ folder")
        else:
            print("\n✅ All data sources available!")
        
        print("="*70 + "\n")


# Standalone usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    checker = ConnectionChecker()
    results = checker.check_all_connections()
    checker.print_status_report()
    
    # Show what can be done with current connections
    tableau_ok, sheets_ok, salesforce_ok = checker.get_available_sources()
    
    print("\n📊 Data Availability:")
    print("-" * 70)
    
    if tableau_ok:
        print("✅ Tableau available:")
        print("   - Support Agent Audits (QA scores)")
        print("   - KPI Scorecard data (CSAT, response times, case metrics)")
        print("   - Can populate ~80% of KPI Calculator")
    
    if sheets_ok:
        print("✅ Google Sheets available:")
        print("   - SLA Cases historical data")
        print("   - Can complete KPI Calculator with SLA metrics")
    
    if salesforce_ok:
        print("✅ Salesforce available:")
        print("   - Case data (closed cases, transfers)")
        print("   - Can complete 100% of KPI Calculator")
    
    print("-" * 70)
    
    if tableau_ok and sheets_ok and salesforce_ok:
        print("\n🎉 Full data pipeline available!")
        print("   Run: python main.py --week last")
    elif tableau_ok:
        print("\n✓ Partial data pipeline available (Tableau only)")
        print("   Can generate 80% complete KPI Calculator")
        print("   Run: python main.py --week last --tableau-only")
    else:
        print("\n⚠️  Insufficient data sources to generate KPI Calculator")
        print("   Please configure at least Tableau connection")
