"""
Salesforce Client
Handles authentication and data retrieval from Salesforce
Supports OAuth 2.0 with refresh tokens for SSO environments
"""

import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import pandas as pd
import requests
from pathlib import Path

try:
    from simple_salesforce import Salesforce, SalesforceLogin
    SALESFORCE_AVAILABLE = True
except ImportError:
    SALESFORCE_AVAILABLE = False
    logging.warning("simple-salesforce not installed. Install with: pip install simple-salesforce")

from config import CREDENTIALS_FILE


class SalesforceClient:
    """Client for accessing Salesforce data with OAuth support"""
    
    def __init__(self, credentials_file: str = CREDENTIALS_FILE):
        """
        Initialize Salesforce client
        
        Args:
            credentials_file: Path to credentials JSON file
        """
        self.credentials_file = credentials_file
        self.sf = None
        self.session_id = None
        self.instance_url = None
        self.access_token = None
        self.refresh_token = None
        self.logger = logging.getLogger(__name__)
    
    def _load_credentials(self) -> Dict[str, str]:
        """Load Salesforce credentials from file"""
        try:
            with open(self.credentials_file, 'r') as f:
                creds = json.load(f)
            
            # OAuth with refresh token (recommended for SSO)
            if 'salesforce_refresh_token' in creds:
                required = ['salesforce_client_id', 'salesforce_client_secret', 
                           'salesforce_refresh_token', 'salesforce_instance_url']
                if all(key in creds for key in required):
                    return {
                        'auth_type': 'oauth_refresh',
                        'client_id': creds['salesforce_client_id'],
                        'client_secret': creds['salesforce_client_secret'],
                        'refresh_token': creds['salesforce_refresh_token'],
                        'instance_url': creds['salesforce_instance_url']
                    }
            
            # Session token auth (temporary, for testing)
            if 'salesforce_session_id' in creds and 'salesforce_instance_url' in creds:
                return {
                    'auth_type': 'session',
                    'session_id': creds['salesforce_session_id'],
                    'instance_url': creds['salesforce_instance_url']
                }
            
            # Username/password auth (won't work with SSO)
            required = ['salesforce_username', 'salesforce_password', 'salesforce_security_token']
            if all(key in creds for key in required):
                return {
                    'auth_type': 'password',
                    'username': creds['salesforce_username'],
                    'password': creds['salesforce_password'],
                    'security_token': creds['salesforce_security_token'],
                    'domain': creds.get('salesforce_domain', 'login')
                }
            
            raise ValueError(
                "Missing Salesforce credentials. Need one of:\n"
                "  1. OAuth (recommended): salesforce_client_id, salesforce_client_secret, "
                "salesforce_refresh_token, salesforce_instance_url\n"
                "  2. Session (temporary): salesforce_session_id, salesforce_instance_url\n"
                "  3. Username/Password (won't work with SSO): salesforce_username, "
                "salesforce_password, salesforce_security_token"
            )
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Credentials file not found: {self.credentials_file}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in credentials file: {self.credentials_file}")
    
    def _refresh_access_token(self, client_id: str, client_secret: str, 
                              refresh_token: str, instance_url: str) -> Dict[str, str]:
        """
        Use refresh token to get a new access token
        
        Args:
            client_id: OAuth client ID from Connected App
            client_secret: OAuth client secret from Connected App
            refresh_token: OAuth refresh token
            instance_url: Salesforce instance URL
            
        Returns:
            Dictionary with access_token and instance_url
        """
        token_url = f"{instance_url}/services/oauth2/token"
        
        data = {
            'grant_type': 'refresh_token',
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token
        }
        
        try:
            response = requests.post(token_url, data=data, timeout=30)
            response.raise_for_status()
            
            token_data = response.json()
            
            self.logger.info("✅ Successfully refreshed access token")
            
            return {
                'access_token': token_data['access_token'],
                'instance_url': token_data['instance_url']
            }
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to refresh access token: {e}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response: {e.response.text}")
            raise RuntimeError(f"Token refresh failed: {e}")
    
    def connect(self) -> bool:
        """
        Authenticate and connect to Salesforce
        
        Returns:
            bool: True if connection successful
        """
        try:
            creds = self._load_credentials()
            
            if creds['auth_type'] == 'oauth_refresh':
                # Use OAuth refresh token to get access token
                token_data = self._refresh_access_token(
                    creds['client_id'],
                    creds['client_secret'],
                    creds['refresh_token'],
                    creds['instance_url']
                )
                
                self.access_token = token_data['access_token']
                self.instance_url = token_data['instance_url']
                
                if SALESFORCE_AVAILABLE:
                    self.sf = Salesforce(
                        instance_url=self.instance_url,
                        session_id=self.access_token
                    )
                else:
                    self.session_id = self.access_token
                
                self.logger.info(f"✅ Connected to Salesforce using OAuth")
                self.logger.info(f"   Instance: {self.instance_url}")
                
            elif creds['auth_type'] == 'session':
                # Convert lightning.force.com to proper instance URL
                instance_url = creds['instance_url']
                if 'lightning.force.com' in instance_url:
                    domain_parts = instance_url.replace('https://', '').split('.')[0]
                    instance_url = f"https://{domain_parts}.my.salesforce.com"
                    self.logger.info(f"Converted Lightning URL to API URL: {instance_url}")
                
                if not SALESFORCE_AVAILABLE:
                    self.logger.warning("simple-salesforce not available, using direct API calls")
                    self.session_id = creds['session_id']
                    self.instance_url = instance_url
                else:
                    self.sf = Salesforce(
                        instance_url=instance_url,
                        session_id=creds['session_id']
                    )
                    self.session_id = creds['session_id']
                    self.instance_url = instance_url
                
                self.logger.info(f"✅ Connected to Salesforce using session token")
                self.logger.info(f"   Instance: {self.instance_url}")
                
            elif creds['auth_type'] == 'password':
                if not SALESFORCE_AVAILABLE:
                    raise ImportError("simple-salesforce required for password auth")
                
                self.sf = Salesforce(
                    username=creds['username'],
                    password=creds['password'],
                    security_token=creds['security_token'],
                    domain=creds['domain']
                )
                self.session_id = self.sf.session_id
                self.instance_url = self.sf.sf_instance
                
                self.logger.info(f"✅ Connected to Salesforce as {creds['username']}")
                self.logger.info(f"   Instance: {self.instance_url}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Salesforce: {e}")
            return False
    
    def test_api_access(self) -> Dict[str, Any]:
        """
        Test if Salesforce API is enabled and accessible
        
        Returns:
            Dictionary with API test results
        """
        if not self.session_id or not self.instance_url:
            if not self.connect():
                return {'success': False, 'error': 'Failed to connect'}
        
        results = {
            'success': False,
            'instance_url': self.instance_url,
            'api_enabled': False,
            'tests': {}
        }
        
        headers = {
            'Authorization': f'Bearer {self.session_id}',
            'Content-Type': 'application/json'
        }
        
        # Test 1: Get API versions
        try:
            url = f"{self.instance_url}/services/data/"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                versions = response.json()
                results['api_enabled'] = True
                results['latest_version'] = versions[-1]['version'] if versions else None
                results['tests']['versions'] = 'OK'
            elif 'API_DISABLED_FOR_ORG' in response.text:
                results['tests']['versions'] = 'API_DISABLED_FOR_ORG'
                return results
            else:
                results['tests']['versions'] = f'HTTP {response.status_code}'
                
        except Exception as e:
            results['tests']['versions'] = f'Error: {str(e)}'
            return results
        
        # Test 2: Query a simple object
        try:
            version = results.get('latest_version', 'v58.0')
            url = f"{self.instance_url}/services/data/{version}/query/"
            params = {'q': 'SELECT Id FROM User LIMIT 1'}
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                results['tests']['query'] = 'OK'
                results['success'] = True
            else:
                results['tests']['query'] = f'HTTP {response.status_code}'
                
        except Exception as e:
            results['tests']['query'] = f'Error: {str(e)}'
        
        # Test 3: List objects
        try:
            version = results.get('latest_version', 'v58.0')
            url = f"{self.instance_url}/services/data/{version}/sobjects/"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                sobjects = response.json()
                results['tests']['sobjects'] = 'OK'
                results['object_count'] = len(sobjects.get('sobjects', []))
            else:
                results['tests']['sobjects'] = f'HTTP {response.status_code}'
                
        except Exception as e:
            results['tests']['sobjects'] = f'Error: {str(e)}'
        
        return results
    
    def query(self, soql: str) -> pd.DataFrame:
        """
        Execute a SOQL query and return results as DataFrame
        
        Args:
            soql: SOQL query string
            
        Returns:
            DataFrame with query results
        """
        if not self.sf:
            if not self.connect():
                raise RuntimeError("Failed to connect to Salesforce")
        
        try:
            results = self.sf.query_all(soql)
            records = results['records']
            
            # Remove 'attributes' metadata from each record
            clean_records = []
            for record in records:
                clean_record = {k: v for k, v in record.items() if k != 'attributes'}
                clean_records.append(clean_record)
            
            df = pd.DataFrame(clean_records)
            self.logger.info(f"Query returned {len(df)} records")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Query failed: {e}")
            raise
    
    def describe_object(self, object_name: str) -> Dict[str, Any]:
        """
        Get metadata about a Salesforce object
        
        Args:
            object_name: Name of the object (e.g., 'Case', 'Account')
            
        Returns:
            Dictionary with object metadata
        """
        if not self.sf:
            if not self.connect():
                raise RuntimeError("Failed to connect to Salesforce")
        
        try:
            obj = getattr(self.sf, object_name)
            return obj.describe()
        except Exception as e:
            self.logger.error(f"Failed to describe {object_name}: {e}")
            raise
    
    def get_reports(self) -> pd.DataFrame:
        """
        Get list of available reports
        
        Returns:
            DataFrame with report information
        """
        if not self.sf:
            if not self.connect():
                raise RuntimeError("Failed to connect to Salesforce")
        
        try:
            # Query reports the user has access to
            soql = """
                SELECT Id, Name, DeveloperName, FolderName, LastRunDate, Description
                FROM Report
                ORDER BY LastRunDate DESC NULLS LAST
                LIMIT 200
            """
            
            df = self.query(soql)
            self.logger.info(f"Found {len(df)} accessible reports")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Failed to get reports: {e}")
            raise
    
    def run_report(self, report_id: str) -> pd.DataFrame:
        """
        Run a Salesforce report and get results
        
        Args:
            report_id: Salesforce report ID (15 or 18 characters)
            
        Returns:
            DataFrame with report results
        """
        if not self.sf:
            if not self.connect():
                raise RuntimeError("Failed to connect to Salesforce")
        
        try:
            # Use Salesforce Analytics API
            url = f"{self.sf.base_url}analytics/reports/{report_id}"
            
            response = self.sf._call_salesforce(
                method='GET',
                url=url,
                name='run_report'
            )
            
            # Parse report results
            if 'factMap' in response:
                # Matrix or Summary report
                rows = []
                for key, data in response['factMap'].items():
                    if 'rows' in data:
                        for row in data['rows']:
                            row_data = {}
                            for i, cell in enumerate(row['dataCells']):
                                col_name = f"Column_{i}"
                                row_data[col_name] = cell.get('label', cell.get('value'))
                            rows.append(row_data)
                
                df = pd.DataFrame(rows)
            else:
                self.logger.warning("Report format not fully supported, returning raw data")
                df = pd.DataFrame([response])
            
            self.logger.info(f"Report returned {len(df)} records")
            return df
            
        except Exception as e:
            self.logger.error(f"Failed to run report {report_id}: {e}")
            raise
    
    def test_access(self) -> Dict[str, Any]:
        """
        Test Salesforce access and return information about what's available
        
        Returns:
            Dictionary with access information
        """
        if not self.sf:
            if not self.connect():
                return {'success': False, 'error': 'Failed to connect'}
        
        info = {
            'success': True,
            'instance': self.sf.sf_instance,
            'api_version': self.sf.sf_version,
            'username': self._load_credentials()['username']
        }
        
        # Test object access
        try:
            case_desc = self.describe_object('Case')
            info['case_access'] = True
            info['case_fields'] = [f['name'] for f in case_desc['fields'][:10]]  # First 10 fields
        except:
            info['case_access'] = False
        
        # Test query access
        try:
            test_query = "SELECT Id, CaseNumber FROM Case LIMIT 1"
            result = self.query(test_query)
            info['query_access'] = True
            info['sample_case_count'] = len(result)
        except:
            info['query_access'] = False
        
        # Test report access
        try:
            reports = self.get_reports()
            info['report_access'] = True
            info['report_count'] = len(reports)
        except:
            info['report_access'] = False
        
        return info
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.sf = None


if __name__ == "__main__":
    """Test Salesforce connection and access"""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Salesforce API Access Test")
    print("=" * 60)
    print("\nThis will test if Salesforce API is enabled for your org.")
    print("\nFor SSO users, you'll need to add to credentials.json:")
    print("  salesforce_session_id: Your session token")
    print("  salesforce_instance_url: Your instance URL")
    print("\nHow to get these:")
    print("  1. Log into Salesforce in your browser")
    print("  2. Open browser DevTools (F12)")
    print("  3. Go to Application/Storage > Cookies")
    print("  4. Find 'sid' cookie - this is your session_id")
    print("  5. Instance URL is like: https://amplify.my.salesforce.com")
    print("=" * 60)
    
    try:
        client = SalesforceClient()
        
        print("\n📊 Testing API access...")
        results = client.test_api_access()
        
        print(f"\nInstance URL: {results.get('instance_url', 'Unknown')}")
        
        if results.get('api_enabled'):
            print("\n✅ API IS ENABLED!")
            print(f"   Latest API Version: v{results.get('latest_version')}")
            
            print(f"\n🔍 Test Results:")
            for test, status in results.get('tests', {}).items():
                icon = '✅' if status == 'OK' else '❌'
                print(f"  {icon} {test}: {status}")
            
            if results.get('object_count'):
                print(f"\n📦 Accessible Objects: {results['object_count']}")
            
            if results.get('success'):
                print("\n🎉 You can use the Salesforce API!")
                print("   You can now query data, run reports, etc.")
        else:
            print("\n❌ API Access Issue")
            
            if any('API_DISABLED_FOR_ORG' in str(v) for v in results.get('tests', {}).values()):
                print("\n⚠️  API_DISABLED_FOR_ORG detected")
                print("   The Salesforce API is not enabled for your organization.")
                print("   You'll need to use manual CSV exports instead.")
            else:
                print("\n� Test Results:")
                for test, status in results.get('tests', {}).items():
                    print(f"  - {test}: {status}")
                
                print("\n💡 Possible issues:")
                print("   - Invalid session token (expired?)")
                print("   - Wrong instance URL")
                print("   - API not enabled for your org")
            
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\n💡 Add to credentials.json:")
        print('  "salesforce_session_id": "your_session_token",')
        print('  "salesforce_instance_url": "https://amplify.my.salesforce.com"')
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logging.exception("Test failed")
