"""
Google Drive CSV Importer
Downloads Salesforce CSV export files from Google Drive and caches them locally
"""

import os
import logging
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
import pandas as pd

try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    import io
    DRIVE_AVAILABLE = True
except ImportError:
    DRIVE_AVAILABLE = False
    logging.warning("google-api-python-client not installed. Install with: pip install google-api-python-client")

from config import GOOGLE_DRIVE_CONFIG, CREDENTIALS_FILE, EXPORT_FILE_PATTERNS


class GoogleDriveImporter:
    """Import CSV files from Google Drive shared folder"""
    
    def __init__(self, credentials_file: str = CREDENTIALS_FILE, local_cache_dir: str = 'exports'):
        """
        Initialize Google Drive importer
        
        Args:
            credentials_file: Path to service account credentials JSON file
            local_cache_dir: Directory to cache downloaded files
        """
        if not DRIVE_AVAILABLE:
            raise ImportError(
                "google-api-python-client is required for Google Drive integration. "
                "Install with: pip install google-api-python-client"
            )
        
        self.credentials_file = credentials_file
        self.local_cache_dir = Path(local_cache_dir)
        self.local_cache_dir.mkdir(exist_ok=True)
        
        self.service = None
        self.folder_id = GOOGLE_DRIVE_CONFIG['salesforce_csvs_folder_id']
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> bool:
        """
        Connect to Google Drive API
        
        Returns:
            bool: True if connection successful
        """
        try:
            creds = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            
            self.service = build('drive', 'v3', credentials=creds)
            self.logger.info("✅ Connected to Google Drive")
            return True
            
        except FileNotFoundError:
            self.logger.error(f"Credentials file not found: {self.credentials_file}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to connect to Google Drive: {e}")
            return False
    
    def list_csv_files(self, folder_id: str = None) -> List[Dict]:
        """
        List all CSV files in the specified folder
        
        Args:
            folder_id: Folder ID (defaults to configured folder)
            
        Returns:
            List of file dictionaries with 'name', 'id', 'modifiedTime', etc.
        """
        if not self.service:
            if not self.connect():
                return []
        
        folder_id = folder_id or self.folder_id
        
        try:
            query = f"'{folder_id}' in parents and mimeType='text/csv' and trashed=false"
            results = self.service.files().list(
                q=query,
                fields='files(id, name, modifiedTime, size)',
                orderBy='modifiedTime desc'
            ).execute()
            
            files = results.get('files', [])
            self.logger.info(f"Found {len(files)} CSV files in Drive folder")
            
            return files
            
        except Exception as e:
            self.logger.error(f"Error listing CSV files: {e}")
            return []
    
    def find_latest_csv(self, pattern: str) -> Optional[Dict]:
        """
        Find the most recently modified CSV file matching a pattern
        
        Args:
            pattern: Pattern to match in filename (e.g., 'cases_closed')
            
        Returns:
            File dictionary or None if not found
        """
        files = self.list_csv_files()
        
        # Filter files matching pattern
        matching_files = [
            f for f in files 
            if pattern.lower() in f['name'].lower()
        ]
        
        if not matching_files:
            self.logger.warning(f"No CSV files found matching pattern: {pattern}")
            return None
        
        # Return most recent (already sorted by modifiedTime desc)
        return matching_files[0]
    
    def download_csv(self, file_id: str, filename: str = None) -> Optional[Path]:
        """
        Download a CSV file from Google Drive
        
        Args:
            file_id: Google Drive file ID
            filename: Local filename (defaults to Drive filename)
            
        Returns:
            Path to downloaded file or None if failed
        """
        if not self.service:
            if not self.connect():
                return None
        
        try:
            # Get file metadata if filename not provided
            if not filename:
                file_metadata = self.service.files().get(fileId=file_id).execute()
                filename = file_metadata['name']
            
            # Download file
            request = self.service.files().get_media(fileId=file_id)
            file_path = self.local_cache_dir / filename
            
            with open(file_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
            
            self.logger.info(f"Downloaded: {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"Error downloading file {file_id}: {e}")
            return None
    
    def import_csv_by_pattern(self, pattern: str, use_cache: bool = True) -> Optional[pd.DataFrame]:
        """
        Download and import a CSV file matching a pattern
        
        Args:
            pattern: Pattern to match in filename
            use_cache: If True, use local cache if file is recent (< 1 hour old)
            
        Returns:
            DataFrame or None if failed
        """
        # Check local cache first
        if use_cache:
            cached_files = list(self.local_cache_dir.glob(f"*{pattern}*"))
            if cached_files:
                # Use most recent cached file
                latest_cache = max(cached_files, key=os.path.getmtime)
                
                # Check if cache is recent (< 1 hour old)
                cache_age = datetime.now().timestamp() - os.path.getmtime(latest_cache)
                if cache_age < 3600:  # 1 hour
                    self.logger.info(f"Using cached file: {latest_cache}")
                    try:
                        return pd.read_csv(latest_cache)
                    except Exception as e:
                        self.logger.warning(f"Error reading cached file: {e}")
        
        # Download from Drive
        file_info = self.find_latest_csv(pattern)
        if not file_info:
            return None
        
        # Download file
        file_path = self.download_csv(file_info['id'], file_info['name'])
        if not file_path:
            return None
        
        # Read CSV
        try:
            df = pd.read_csv(file_path)
            self.logger.info(f"Imported CSV: {len(df)} rows, {len(df.columns)} columns")
            return df
        except Exception as e:
            self.logger.error(f"Error reading CSV: {e}")
            return None
    
    def sync_all_exports(self) -> Dict[str, pd.DataFrame]:
        """
        Download all CSV export files and return as DataFrames
        
        Returns:
            Dictionary mapping data types to DataFrames
        """
        self.logger.info("Syncing all CSV exports from Google Drive...")
        
        datasets = {}
        
        for data_type, pattern in EXPORT_FILE_PATTERNS.items():
            # Extract pattern from filename (e.g., 'time_util_export.csv' -> 'time_util')
            pattern_base = pattern.replace('_export.csv', '').replace('.csv', '')
            
            df = self.import_csv_by_pattern(pattern_base)
            if df is not None and len(df) > 0:
                datasets[data_type] = df
                self.logger.info(f"✅ {data_type}: {len(df)} rows")
            else:
                self.logger.warning(f"⚠️ {data_type}: No data found")
        
        self.logger.info(f"Completed sync: {len(datasets)}/{len(EXPORT_FILE_PATTERNS)} datasets")
        
        return datasets
    
    def check_connection(self) -> Dict[str, any]:
        """
        Check Google Drive connection and list files
        
        Returns:
            Dictionary with connection status and file count
        """
        if not self.service:
            if not self.connect():
                return {
                    'available': False,
                    'files_found': 0,
                    'message': 'Failed to connect to Google Drive'
                }
        
        files = self.list_csv_files()
        
        return {
            'available': True,
            'files_found': len(files),
            'files': files[:10],  # First 10 files for debugging
            'message': f'Connected to Google Drive, found {len(files)} CSV files'
        }
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.service = None


# Standalone usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("="*70)
    print("Google Drive CSV Importer - Testing")
    print("="*70)
    print()
    
    # Initialize importer
    importer = GoogleDriveImporter()
    
    # Test connection
    print("📊 Checking Google Drive connection...")
    status = importer.check_connection()
    
    if status['available']:
        print(f"✅ {status['message']}")
        
        if status['files']:
            print("\nSample files:")
            for f in status['files'][:5]:
                print(f"  • {f['name']} (modified: {f.get('modifiedTime', 'unknown')})")
    else:
        print(f"❌ {status['message']}")
    
    # Test syncing all exports
    print("\n📊 Syncing all CSV exports...")
    datasets = importer.sync_all_exports()
    
    if datasets:
        print(f"\n✅ Successfully imported {len(datasets)} datasets:")
        for data_type, df in datasets.items():
            print(f"  • {data_type}: {len(df)} rows, {list(df.columns)}")
    else:
        print("❌ No datasets imported")
    
    print("\n" + "="*70)
