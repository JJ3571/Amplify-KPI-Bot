#!/usr/bin/env python3
"""
Setup helper for KPI Calculator Bot
Helps configure Google Sheets integration and validate setup
"""

import json
import os
from pathlib import Path

def check_credentials():
    """Check if Google credentials file exists and is valid"""
    credentials_file = Path("credentials.json")
    
    if not credentials_file.exists():
        print("❌ credentials.json not found")
        print("   Please download your Google service account credentials")
        print("   and save them as 'credentials.json' in the project root.")
        return False
    
    try:
        with open(credentials_file) as f:
            creds = json.load(f)
        
        required_fields = ["type", "project_id", "private_key", "client_email"]
        missing_fields = [field for field in required_fields if field not in creds]
        
        if missing_fields:
            print(f"❌ Invalid credentials file. Missing fields: {missing_fields}")
            return False
        
        if creds.get("type") != "service_account":
            print("❌ Credentials file must be for a service account")
            return False
        
        print("✅ Google credentials file is valid")
        print(f"   Service Account: {creds.get('client_email')}")
        print(f"   Project ID: {creds.get('project_id')}")
        return True
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON in credentials file")
        return False
    except Exception as e:
        print(f"❌ Error reading credentials: {e}")
        return False

def test_google_sheets_connection():
    """Test connection to Google Sheets (optional - not required for Amplify system)"""
    try:
        # Note: Google Sheets integration is optional
        # The Amplify KPI system works with CSV exports
        import gspread
        from google.oauth2.service_account import Credentials
        
        # Basic credential check only
        cred_file = Path("credentials.json")
        if cred_file.exists():
            print("✅ Google Sheets credentials found (optional feature)")
            return True
        else:
            print("ℹ️  Google Sheets not configured (not required - CSV exports work fine)")
            return False
        
    except ImportError:
        print("ℹ️  Google Sheets packages not installed (optional)")
        return False
    except Exception as e:
        print(f"ℹ️  Google Sheets check skipped: {e}")
        return False

def check_directory_structure():
    """Check and create necessary directories for Amplify KPI system"""
    directories = ["exports", "scorecards", "results"]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✅ Directory exists: {directory}")

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        "pandas", "numpy", "gspread", "google-auth", 
        "google-auth-oauthlib", "google-auth-httplib2", "openpyxl"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {missing_packages}")
        print("   Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages are installed")
        return True

def create_sample_data():
    """Create sample CSV export files for testing the Amplify KPI system"""
    exports_dir = Path("exports")
    exports_dir.mkdir(exist_ok=True)
    
    # Sample time utilization export
    time_util_sample = """Name,Time Utilization Percent,Total Hours Worked
Dajah Gray,0.85,40
Alison Daniel,0.90,42
Amanda Clark,0.78,38"""
    
    # Sample cases closed export
    cases_closed_sample = """Case Owner,Case Number,Product,Date/Time Closed
Dajah Gray,CASE-001,Amplify,2024-10-01 10:30:00
Dajah Gray,CASE-002,Amplify,2024-10-01 14:15:00
Alison Daniel,CASE-003,Amplify,2024-10-01 09:45:00"""
    
    # Sample QA scores export
    qa_scores_sample = """Agent Name,Avg Score,Case Count
Dajah Gray,0.92,5
Alison Daniel,0.95,6
Amanda Clark,0.88,4"""
    
    # Write sample files
    sample_files = {
        "time_util_sample.csv": time_util_sample,
        "cases_closed_sample.csv": cases_closed_sample,
        "qa_scores_sample.csv": qa_scores_sample
    }
    
    for filename, content in sample_files.items():
        file_path = exports_dir / filename
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"✅ Created sample export file: {file_path}")

def print_next_steps():
    """Print instructions for next steps"""
    print("\n" + "="*60)
    print("SETUP COMPLETE - NEXT STEPS")
    print("="*60)
    
    print("\n1. Test with sample data:")
    print("   python scripts/examples_usage_updated.py")
    
    print("\n2. Validate the system:")
    print("   python scripts/final_validation.py")
    
    print("\n3. Process your CSV export files:")
    print("   python main.py --exports-folder exports --output results.xlsx --generate-scorecards")
    
    print("\n4. Generate individual scorecard:")
    print("   python main.py --exports-folder exports --agent \"Agent Name\" --scorecard scorecard.csv")
    
    print("\n5. Customize KPI weights and goals:")
    print("   - Edit config.py to adjust weights and targets")
    print("   - Review named_functions.py for calculation logic")
    
    print("\n6. Required CSV export files (place in exports/ folder):")
    print("   - time_util*.csv, cases_closed*.csv, qa_scores*.csv")
    print("   - See README.md for complete list and column requirements")

def main():
    """Main setup function"""
    print("Amplify KPI Calculator Bot - Setup Helper")
    print("="*50)
    
    print("\n🔍 Checking setup requirements...")
    
    # Check basic requirements
    deps_ok = check_dependencies()
    check_directory_structure()
    
    # Check Google Sheets setup (optional for Amplify system)
    print("\n🔍 Checking Google Sheets integration (optional)...")
    creds_ok = check_credentials()
    
    if creds_ok:
        sheets_ok = test_google_sheets_connection()
    else:
        sheets_ok = False
        print("ℹ️  Google Sheets not configured - CSV export processing will be used")
    
    # Create sample data
    print("\n📁 Creating sample export files...")
    create_sample_data()
    
    # Summary
    print("\n" + "="*50)
    print("SETUP SUMMARY")
    print("="*50)
    
    print(f"Dependencies: {'✅' if deps_ok else '❌'}")
    print(f"Google Credentials: {'✅' if creds_ok else 'ℹ️  Optional'}")
    print(f"Google Sheets Connection: {'✅' if sheets_ok else 'ℹ️  Optional'}")
    print("Directory Structure: ✅")
    print("Sample Export Files: ✅")
    
    if deps_ok:
        print("\n🎉 Setup complete! The Amplify KPI Calculator is ready to use.")
        print("💡 Place your CSV export files in the 'exports' folder to get started.")
    else:
        print("\n⚠️  Please install missing dependencies first.")
        print("   Run: pip install -r requirements.txt")
    
    print_next_steps()

if __name__ == "__main__":
    main()