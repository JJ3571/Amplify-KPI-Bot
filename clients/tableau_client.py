"""
Tableau REST API Client for Amplify KPI Bot
Provides data access from Tableau Server/Cloud as alternative to CSV exports
"""

import json
import requests
import pandas as pd
from pathlib import Path
import logging
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET
from io import StringIO
import re
from config import TABLEAU_CONFIG

class TableauClient:
    """Client for Tableau REST API data access"""
    
    def __init__(self, credentials_file="credentials.json", server_url=None, site_name=None):
        """
        Initialize Tableau client
        
        Args:
            credentials_file (str): Path to credentials JSON file
            server_url (str): Tableau server URL (optional, can be set later)
            site_name (str): Tableau site name (optional, empty for default)
        """
        self.credentials_file = Path(credentials_file)
        self.server_url = server_url
        self.site_name = site_name or ""
        self.auth_token = None
        self.site_id = None
        self.token_name = None
        self.token_secret = None
        
        self._load_credentials()
    
    def _load_credentials(self):
        """Load Tableau API credentials from JSON file"""
        try:
            with open(self.credentials_file) as f:
                creds = json.load(f)
            
            api_key = creds.get('tableau_api_key')
            if not api_key:
                raise ValueError("tableau_api_key not found in credentials.json")
            
            # Get token name (defaults to tableau_token_name if not in API key)
            token_name = creds.get('tableau_token_name', 'AmplifyKPIBot')
            
            # The API key is just the secret (could be in format secret1:secret2)
            self.token_name = token_name
            self.token_secret = api_key
            logging.info(f"Loaded Tableau API credentials for token: {self.token_name}")
                
        except FileNotFoundError:
            raise FileNotFoundError(f"Credentials file not found: {self.credentials_file}")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in credentials file")
    
    def connect(self, server_url: str, site_name: str = ""):
        """
        Authenticate with Tableau Server
        
        Args:
            server_url (str): Tableau server URL (e.g., "https://10az.online.tableau.com")
            site_name (str): Site name (empty string for default site)
        
        Returns:
            bool: True if authentication successful
        """
        # Parse and clean server URL
        server_url = self._parse_server_url(server_url)
        
        # Extract site from URL if present
        site_match = re.search(r'[/#]+site/([^/]+)', server_url)
        if site_match and not site_name:
            site_name = site_match.group(1)
            logging.info(f"Detected site from URL: {site_name}")
        
        # Clean server URL to base domain
        server_match = re.match(r'(https?://[^/#?]+)', server_url)
        if server_match:
            server_url = server_match.group(1)
        
        self.server_url = server_url
        self.site_name = site_name
        
        logging.info(f"Connecting to Tableau: {self.server_url}, Site: {self.site_name or '(default)'}")
        
        # Authentication endpoint
        api_version = TABLEAU_CONFIG.get('api_version', '3.19')
        auth_url = f"{self.server_url}/api/{api_version}/auth/signin"
        
        # Build authentication XML payload
        auth_payload = f"""
        <tsRequest>
            <credentials personalAccessTokenName="{self.token_name}" 
                        personalAccessTokenSecret="{self.token_secret}">
                <site contentUrl="{self.site_name}" />
            </credentials>
        </tsRequest>
        """
        
        headers = {
            'Content-Type': 'application/xml',
            'Accept': 'application/xml'
        }
        
        try:
            response = requests.post(auth_url, data=auth_payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                
                # Handle XML namespace
                ns = {'t': 'http://tableau.com/api'}
                credentials = root.find('.//t:credentials', ns)
                
                if credentials is not None:
                    self.auth_token = credentials.get('token')
                    site = credentials.find('t:site', ns)
                    if site is not None:
                        self.site_id = site.get('id')
                    
                    logging.info("Successfully authenticated with Tableau")
                    return True
                else:
                    logging.error("Authentication failed: Invalid response format")
                    logging.debug(f"Response: {response.text[:500]}")
                    return False
            else:
                logging.error(f"Authentication failed: HTTP {response.status_code}")
                logging.error(f"Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Connection error: {e}")
            return False
        except Exception as e:
            logging.error(f"Authentication error: {e}")
            return False
    
    def _parse_server_url(self, url: str) -> str:
        """Parse and clean server URL"""
        url = url.strip()
        if not url.startswith('http'):
            url = f"https://{url}"
        return url
    
    def get_workbooks(self) -> Optional[List[Dict]]:
        """
        Get list of accessible workbooks (handles pagination)
        
        Returns:
            List of workbook dictionaries or None if failed
        """
        if not self.auth_token:
            logging.error("Not authenticated. Call connect() first.")
            return None
        
        all_workbooks = []
        page_number = 1
        page_size = TABLEAU_CONFIG.get('page_size', 100)
        api_version = TABLEAU_CONFIG.get('api_version', '3.19')
        ns = {'t': 'http://tableau.com/api'}
        
        try:
            while True:
                url = f"{self.server_url}/api/{api_version}/sites/{self.site_id}/workbooks"
                params = {'pageSize': page_size, 'pageNumber': page_number}
                headers = {'X-Tableau-Auth': self.auth_token, 'Accept': 'application/xml'}
                
                response = requests.get(url, headers=headers, params=params, timeout=30)
                
                if response.status_code != 200:
                    logging.error(f"Failed to get workbooks: HTTP {response.status_code}")
                    return None if not all_workbooks else all_workbooks
                
                root = ET.fromstring(response.content)
                
                # Get pagination info
                pagination = root.find('.//t:pagination', ns)
                if pagination is not None:
                    total_available = int(pagination.get('totalAvailable', 0))
                else:
                    total_available = 0
                
                # Parse workbooks on this page
                workbooks_on_page = 0
                for workbook in root.findall('.//t:workbook', ns):
                    wb_info = {
                        'id': workbook.get('id'),
                        'name': workbook.get('name'),
                        'contentUrl': workbook.get('contentUrl'),
                        'createdAt': workbook.get('createdAt'),
                        'updatedAt': workbook.get('updatedAt')
                    }
                    
                    project = workbook.find('t:project', ns)
                    if project is not None:
                        wb_info['project_name'] = project.get('name')
                    
                    all_workbooks.append(wb_info)
                    workbooks_on_page += 1
                
                # Check if we need to fetch more pages
                if len(all_workbooks) >= total_available or workbooks_on_page == 0:
                    break
                
                page_number += 1
            
            logging.info(f"Retrieved {len(all_workbooks)} workbooks")
            return all_workbooks
                
        except Exception as e:
            logging.error(f"Error getting workbooks: {e}")
            return None if not all_workbooks else all_workbooks
    
    def get_views(self, workbook_id: str = None) -> Optional[List[Dict]]:
        """
        Get list of accessible views (handles pagination)
        
        Args:
            workbook_id (str): Optional workbook ID to filter views
        
        Returns:
            List of view dictionaries or None if failed
        """
        if not self.auth_token:
            logging.error("Not authenticated. Call connect() first.")
            return None
        
        all_views = []
        page_number = 1
        page_size = TABLEAU_CONFIG.get('page_size', 100)
        api_version = TABLEAU_CONFIG.get('api_version', '3.19')
        ns = {'t': 'http://tableau.com/api'}
        
        try:
            while True:
                url = f"{self.server_url}/api/{api_version}/sites/{self.site_id}/views"
                params = {'pageSize': page_size, 'pageNumber': page_number}
                headers = {'X-Tableau-Auth': self.auth_token, 'Accept': 'application/xml'}
                
                response = requests.get(url, headers=headers, params=params, timeout=30)
                
                if response.status_code != 200:
                    logging.error(f"Failed to get views: HTTP {response.status_code}")
                    return None if not all_views else all_views
                
                root = ET.fromstring(response.content)
                
                # Get pagination info
                pagination = root.find('.//t:pagination', ns)
                if pagination is not None:
                    total_available = int(pagination.get('totalAvailable', 0))
                else:
                    total_available = 0
                
                # Parse views on this page
                views_on_page = 0
                for view in root.findall('.//t:view', ns):
                    workbook = view.find('t:workbook', ns)
                    wb_id = workbook.get('id') if workbook is not None else None
                    
                    # Filter by workbook if specified
                    if workbook_id and wb_id != workbook_id:
                        continue
                    
                    view_info = {
                        'id': view.get('id'),
                        'name': view.get('name'),
                        'contentUrl': view.get('contentUrl'),
                        'workbook_id': wb_id,
                        'workbook_name': workbook.get('name') if workbook is not None else None
                    }
                    
                    all_views.append(view_info)
                    views_on_page += 1
                
                # Check if we need to fetch more pages
                if len(all_views) >= total_available or views_on_page == 0:
                    break
                
                page_number += 1
            
            logging.info(f"Retrieved {len(all_views)} views")
            return all_views
                
        except Exception as e:
            logging.error(f"Error getting views: {e}")
            return None if not all_views else all_views
    
    def query_view(self, view_id: str, max_age: int = -1) -> Optional[pd.DataFrame]:
        """
        Query data from a specific view
        
        Args:
            view_id (str): View ID to query
            max_age (int): Maximum age of cached data in minutes (-1 for live)
        
        Returns:
            DataFrame with view data or None if failed
        """
        if not self.auth_token:
            logging.error("Not authenticated. Call connect() first.")
            return None
        
        api_version = TABLEAU_CONFIG.get('api_version', '3.19')
        url = f"{self.server_url}/api/{api_version}/sites/{self.site_id}/views/{view_id}/data"
        headers = {'X-Tableau-Auth': self.auth_token}
        params = {'maxAge': max_age}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=60)
            
            if response.status_code == 200:
                # Try to parse as CSV
                try:
                    df = pd.read_csv(StringIO(response.text))
                    logging.info(f"Retrieved view data: {len(df)} rows, {len(df.columns)} columns")
                    return df
                except Exception as e:
                    logging.error(f"Could not parse view data as CSV: {e}")
                    return None
            else:
                logging.error(f"Failed to query view: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logging.error(f"Error querying view: {e}")
            return None
    
    def find_view_by_name(self, view_name: str, workbook_name: str = None) -> Optional[str]:
        """
        Find view ID by name
        
        Args:
            view_name (str): Name of the view to find
            workbook_name (str): Optional workbook name to narrow search
        
        Returns:
            View ID or None if not found
        """
        views = self.get_views()
        if not views:
            return None
        
        for view in views:
            name_match = view['name'].lower() == view_name.lower()
            wb_match = (not workbook_name or 
                       (view.get('workbook_name', '').lower() == workbook_name.lower()))
            
            if name_match and wb_match:
                logging.info(f"Found view '{view_name}': ID={view['id']}")
                return view['id']
        
        logging.warning(f"View '{view_name}' not found")
        return None
    
    def disconnect(self):
        """Sign out and invalidate the authentication token"""
        if not self.auth_token:
            return
        
        api_version = TABLEAU_CONFIG.get('api_version', '3.19')
        url = f"{self.server_url}/api/{api_version}/auth/signout"
        headers = {'X-Tableau-Auth': self.auth_token}
        
        try:
            response = requests.post(url, headers=headers, timeout=10)
            if response.status_code == 204:
                logging.info("Signed out from Tableau")
            self.auth_token = None
            self.site_id = None
        except Exception as e:
            logging.warning(f"Error during signout: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatically disconnect"""
        self.disconnect()
