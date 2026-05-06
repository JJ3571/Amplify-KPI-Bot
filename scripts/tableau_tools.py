#!/usr/bin/env python3
"""
Tableau API Tools - Unified Testing and Diagnostics
Consolidates all Tableau testing, diagnostics, and exploration utilities
"""

import sys
import json
import requests
import xml.etree.ElementTree as ET
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from clients import TableauClient
from config import TABLEAU_CONFIG


def quick_connection_test():
    """Quick test of Tableau API connection with manual input"""
    print("🔬 Quick Tableau API Connection Test\n")
    print("="*70)
    
    # Load credentials
    try:
        with open('credentials.json') as f:
            creds = json.load(f)
        
        token_name = creds.get('tableau_token_name', 'Unknown')
        token_secret = creds.get('tableau_api_key')
        
        if not token_secret:
            print("❌ No tableau_api_key found in credentials.json")
            return False
        
        print(f"✅ Credentials loaded: Token '{token_name}'\n")
    
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return False
    
    # Get server info
    print("Enter your Tableau details:\n")
    
    server = input("Server URL (default: https://10az.online.tableau.com): ").strip()
    if not server:
        server = "https://10az.online.tableau.com"
    
    site = input("Site name (default: amplify): ").strip()
    if not site:
        site = "amplify"
    
    print(f"\n   Using Server: {server}")
    print(f"   Using Site: {site}")
    
    # Test connection
    print(f"\n🔌 Testing connection...\n")
    
    auth_url = f"{server.rstrip('/')}/api/3.19/auth/signin"
    
    payload = f"""
    <tsRequest>
        <credentials personalAccessTokenName="{token_name}" 
                    personalAccessTokenSecret="{token_secret}">
            <site contentUrl="{site}" />
        </credentials>
    </tsRequest>
    """
    
    headers = {
        'Content-Type': 'application/xml',
        'Accept': 'application/xml'
    }
    
    try:
        response = requests.post(auth_url, data=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            ns = {'t': 'http://tableau.com/api'}
            credentials = root.find('.//t:credentials', ns)
            
            if credentials:
                token = credentials.get('token')
                site_elem = credentials.find('t:site', ns)
                site_id = site_elem.get('id') if site_elem is not None else 'unknown'
                
                print("✅ SUCCESS! Connection established!")
                print(f"   Auth Token: {token[:20]}...")
                print(f"   Site ID: {site_id}")
                print("\n🎉 Your Tableau API credentials are working!")
                return True
            else:
                print("❌ FAILED: Invalid response from server")
                return False
        
        elif response.status_code == 401:
            print("❌ FAILED: Authentication error (401)")
            print("   Possible issues:")
            print("   - Token name or secret is incorrect")
            print("   - Token doesn't have necessary permissions")
            return False
        
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        return False


def diagnose_credentials():
    """Diagnose and validate Tableau credentials setup"""
    print("🔍 Tableau Credentials Diagnostics\n")
    print("="*70)
    
    # Check credentials file
    creds_file = Path('credentials.json')
    if not creds_file.exists():
        print("❌ credentials.json not found!")
        return False
    
    print("✅ credentials.json exists\n")
    
    # Load and check contents
    try:
        with open(creds_file) as f:
            creds = json.load(f)
        
        print("Checking credential fields:")
        
        # Check tableau_token_name
        if 'tableau_token_name' in creds:
            token_name = creds['tableau_token_name']
            print(f"  ✅ tableau_token_name: '{token_name}'")
        else:
            print("  ⚠️  tableau_token_name: Missing (will use default)")
            token_name = None
        
        # Check tableau_api_key
        if 'tableau_api_key' in creds:
            token_secret = creds['tableau_api_key']
            print(f"  ✅ tableau_api_key: {token_secret[:10]}... ({len(token_secret)} chars)")
        else:
            print("  ❌ tableau_api_key: Missing!")
            return False
        
        print(f"\n{'='*70}")
        print("Testing authentication with these credentials...")
        print(f"{'='*70}\n")
        
        # Test the credentials
        server = TABLEAU_CONFIG['server_url']
        site = TABLEAU_CONFIG['site_name']
        
        if not token_name:
            token_name = input("Enter token name (e.g., 'AmplifyKPIBot'): ").strip()
        
        auth_url = f"{server}/api/3.19/auth/signin"
        
        payload = f"""
        <tsRequest>
            <credentials personalAccessTokenName="{token_name}" 
                        personalAccessTokenSecret="{token_secret}">
                <site contentUrl="{site}" />
            </credentials>
        </tsRequest>
        """
        
        headers = {'Content-Type': 'application/xml', 'Accept': 'application/xml'}
        response = requests.post(auth_url, data=payload, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Authentication successful!\n")
            
            # Offer to update credentials.json if needed
            if 'tableau_token_name' not in creds:
                update = input(f"Would you like to add 'tableau_token_name': '{token_name}' to credentials.json? (y/n): ")
                if update.lower() == 'y':
                    creds['tableau_token_name'] = token_name
                    with open(creds_file, 'w') as f:
                        json.dump(creds, f, indent=2)
                    print("✅ Updated credentials.json")
            
            return True
        else:
            print(f"❌ Authentication failed: HTTP {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def list_workbooks_and_views():
    """List all accessible workbooks and views"""
    print("📚 Tableau Workbooks and Views\n")
    print("="*70)
    
    with TableauClient() as client:
        if not client.connect(TABLEAU_CONFIG['server_url'], TABLEAU_CONFIG['site_name']):
            print("❌ Failed to connect")
            return False
        
        print("✅ Connected successfully\n")
        
        # Get workbooks
        workbooks = client.get_workbooks()
        if workbooks:
            print(f"📚 Found {len(workbooks)} workbooks:\n")
            for i, wb in enumerate(workbooks[:20], 1):  # Show first 20
                print(f"{i:2d}. {wb['name']}")
                print(f"    ID: {wb['id']}")
                if wb.get('project_name'):
                    print(f"    Project: {wb['project_name']}")
                print()
            
            if len(workbooks) > 20:
                print(f"    ... and {len(workbooks) - 20} more\n")
        
        # Get views
        views = client.get_views()
        if views:
            print(f"\n{'='*70}")
            print(f"📈 Found {len(views)} views:\n")
            for i, view in enumerate(views[:20], 1):  # Show first 20
                print(f"{i:2d}. {view['name']}")
                print(f"    ID: {view['id']}")
                if view.get('workbook_name'):
                    print(f"    Workbook: {view['workbook_name']}")
                print()
            
            if len(views) > 20:
                print(f"    ... and {len(views) - 20} more\n")
        
        return True


def explore_workbook(workbook_id=None):
    """Explore views in a specific workbook and test data retrieval"""
    print("🔍 Workbook Explorer\n")
    print("="*70)
    
    if not workbook_id:
        workbook_id = input("\nEnter Workbook ID: ").strip()
    
    if not workbook_id:
        print("❌ Workbook ID required")
        return False
    
    with TableauClient() as client:
        if not client.connect(TABLEAU_CONFIG['server_url'], TABLEAU_CONFIG['site_name']):
            print("❌ Failed to connect")
            return False
        
        print(f"\n🔍 Exploring Workbook: {workbook_id}\n")
        
        # Get all views
        all_views = client.get_views()
        
        if not all_views:
            print("❌ No views found")
            return False
        
        # Filter to this workbook
        workbook_views = [v for v in all_views if v.get('workbook_id') == workbook_id]
        
        if not workbook_views:
            print(f"❌ No views found for workbook ID: {workbook_id}")
            print("\n💡 Tip: Make sure you have the correct workbook ID")
            return False
        
        print(f"📊 Found {len(workbook_views)} views in this workbook:\n")
        
        for i, view in enumerate(workbook_views, 1):
            print(f"{i}. {view['name']}")
            print(f"   ID: {view['id']}")
            print(f"   Content URL: {view.get('contentUrl', 'N/A')}")
            print()
        
        # Ask if user wants to test data retrieval
        print("="*70)
        test = input("\nTest data retrieval from a view? (y/n): ").strip().lower()
        
        if test == 'y':
            view_num = input(f"Enter view number (1-{len(workbook_views)}): ").strip()
            try:
                view_idx = int(view_num) - 1
                if 0 <= view_idx < len(workbook_views):
                    test_view = workbook_views[view_idx]
                    
                    print(f"\n🧪 Testing data retrieval from: {test_view['name']}")
                    print(f"    ID: {test_view['id']}\n")
                    
                    df = client.query_view(test_view['id'])
                    
                    if df is not None:
                        print("✅ Successfully retrieved data!")
                        print(f"   Rows: {len(df)}")
                        print(f"   Columns: {list(df.columns)}\n")
                        print("First few rows:")
                        print(df.head())
                        
                        # Offer to save
                        save = input("\n\nSave data to CSV? (y/n): ").strip().lower()
                        if save == 'y':
                            filename = f"tableau_export_{test_view['name'].replace(' ', '_')}.csv"
                            df.to_csv(filename, index=False)
                            print(f"✅ Saved to {filename}")
                    else:
                        print("❌ Could not retrieve data from this view")
                        print("   Note: Not all views support data export")
                else:
                    print("❌ Invalid view number")
            except ValueError:
                print("❌ Invalid input")
        
        return True


def test_view_filters(view_id=None):
    """Test retrieving data with filters from a specific view"""
    print("🎛️  View Filter Testing\n")
    print("="*70)
    
    if not view_id:
        view_id = input("\nEnter View ID: ").strip()
    
    if not view_id:
        print("❌ View ID required")
        return False
    
    print(f"\n📊 Testing view: {view_id}\n")
    print("Note: Currently testing without filters")
    print("      Tableau REST API v3.19 requires filters to be")
    print("      set through view parameters or URL parameters.\n")
    
    with TableauClient() as client:
        if not client.connect(TABLEAU_CONFIG['server_url'], TABLEAU_CONFIG['site_name']):
            print("❌ Failed to connect")
            return False
        
        print("Retrieving data...\n")
        df = client.query_view(view_id)
        
        if df is not None:
            print("✅ Successfully retrieved data!")
            print(f"   Rows: {len(df)}")
            print(f"   Columns: {list(df.columns)}\n")
            print("Column details:")
            print(df.dtypes)
            print("\nFirst few rows:")
            print(df.head(10))
            
            # Show data summary
            print("\n" + "="*70)
            print("Data Summary:")
            print("="*70)
            print(df.describe())
            
            return True
        else:
            print("❌ Could not retrieve data")
            return False


def main_menu():
    """Main menu for Tableau tools"""
    while True:
        print("\n" + "="*70)
        print("  Tableau API Tools - Main Menu")
        print("="*70)
        print("\n1. Quick Connection Test (manual input)")
        print("2. Diagnose Credentials")
        print("3. List All Workbooks and Views")
        print("4. Explore Specific Workbook")
        print("5. Test View Data Retrieval")
        print("6. Exit")
        print()
        
        choice = input("Select an option (1-6): ").strip()
        
        print("\n" + "="*70 + "\n")
        
        if choice == '1':
            quick_connection_test()
        elif choice == '2':
            diagnose_credentials()
        elif choice == '3':
            list_workbooks_and_views()
        elif choice == '4':
            explore_workbook()
        elif choice == '5':
            test_view_filters()
        elif choice == '6':
            print("👋 Goodbye!\n")
            break
        else:
            print("❌ Invalid option. Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  Tableau API Tools - Unified Testing & Diagnostics")
    print("="*70)
    print("\n  This tool consolidates all Tableau testing utilities:")
    print("  - Connection testing")
    print("  - Credential diagnostics")
    print("  - Workbook/view exploration")
    print("  - Data retrieval testing")
    print("\n" + "="*70 + "\n")
    
    main_menu()
