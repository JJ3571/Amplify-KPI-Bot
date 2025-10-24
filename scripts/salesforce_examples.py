"""
Salesforce Data Retrieval Examples
Shows how to use the OAuth-enabled Salesforce client to query data
"""

from salesforce_client import SalesforceClient
from datetime import datetime, timedelta
import pandas as pd


def example_1_query_cases():
    """Example 1: Query recent cases"""
    print("\n" + "=" * 60)
    print("Example 1: Query Recent Cases")
    print("=" * 60)
    
    with SalesforceClient() as client:
        # Query cases from last 7 days
        soql = """
            SELECT Id, CaseNumber, Subject, Status, Priority, 
                   CreatedDate, ClosedDate, Owner.Name
            FROM Case
            WHERE CreatedDate = LAST_N_DAYS:7
            ORDER BY CreatedDate DESC
            LIMIT 100
        """
        
        df = client.query(soql)
        print(f"\n✅ Found {len(df)} cases from last 7 days")
        
        if not df.empty:
            print("\nSample cases:")
            print(df[['CaseNumber', 'Status', 'Priority', 'Owner.Name']].head(10))
            
            # Save to CSV
            output_file = f"data/exports/Cases_Last7Days_{datetime.now().strftime('%Y%m%d')}.csv"
            df.to_csv(output_file, index=False)
            print(f"\n💾 Saved to: {output_file}")


def example_2_query_with_date_range():
    """Example 2: Query cases for specific date range"""
    print("\n" + "=" * 60)
    print("Example 2: Cases for Specific Date Range")
    print("=" * 60)
    
    # Last week's date range
    end_date = datetime.now() - timedelta(days=1)
    start_date = end_date - timedelta(days=7)
    
    with SalesforceClient() as client:
        soql = f"""
            SELECT Id, CaseNumber, Subject, Status, 
                   CreatedDate, ClosedDate, Owner.Name
            FROM Case
            WHERE CreatedDate >= {start_date.strftime('%Y-%m-%dT00:00:00Z')}
              AND CreatedDate <= {end_date.strftime('%Y-%m-%dT23:59:59Z')}
            ORDER BY CreatedDate DESC
        """
        
        df = client.query(soql)
        print(f"\n✅ Found {len(df)} cases")
        print(f"   Date range: {start_date.date()} to {end_date.date()}")
        
        if not df.empty:
            # Group by status
            status_counts = df['Status'].value_counts()
            print("\nCases by Status:")
            print(status_counts)


def example_3_query_closed_cases_by_agent():
    """Example 3: Cases closed by agent"""
    print("\n" + "=" * 60)
    print("Example 3: Cases Closed by Agent (Last 30 Days)")
    print("=" * 60)
    
    with SalesforceClient() as client:
        soql = """
            SELECT Owner.Name, COUNT(Id) TotalClosed
            FROM Case
            WHERE ClosedDate = LAST_N_DAYS:30
              AND IsClosed = true
            GROUP BY Owner.Name
            ORDER BY COUNT(Id) DESC
        """
        
        df = client.query(soql)
        print(f"\n✅ Found {len(df)} agents with closed cases")
        
        if not df.empty:
            print("\nTop 10 agents by cases closed:")
            print(df.head(10).to_string(index=False))


def example_4_available_reports():
    """Example 4: List available reports"""
    print("\n" + "=" * 60)
    print("Example 4: Available Salesforce Reports")
    print("=" * 60)
    
    with SalesforceClient() as client:
        reports = client.get_reports()
        print(f"\n✅ Found {len(reports)} accessible reports")
        
        if not reports.empty:
            print("\nRecent reports (top 20):")
            print(reports[['Name', 'FolderName', 'LastRunDate']].head(20).to_string(index=False))
            
            # Filter for KPI-related reports
            kpi_reports = reports[reports['Name'].str.contains('KPI|Support|Agent', case=False, na=False)]
            if not kpi_reports.empty:
                print(f"\n📊 Found {len(kpi_reports)} KPI-related reports:")
                print(kpi_reports[['Name', 'FolderName']].to_string(index=False))


def example_5_describe_case_object():
    """Example 5: Get Case object metadata"""
    print("\n" + "=" * 60)
    print("Example 5: Case Object Field Information")
    print("=" * 60)
    
    with SalesforceClient() as client:
        case_info = client.describe_object('Case')
        
        print(f"\n✅ Case Object Info:")
        print(f"   Label: {case_info['label']}")
        print(f"   Total Fields: {len(case_info['fields'])}")
        
        # Show some useful fields
        print("\nSample fields:")
        for field in case_info['fields'][:15]:
            field_type = field['type']
            required = '(required)' if not field['nillable'] else ''
            print(f"   - {field['name']}: {field['label']} ({field_type}) {required}")


if __name__ == "__main__":
    """
    Run examples
    
    Prerequisites:
    1. Run: python scripts/salesforce_oauth_setup.py
    2. Complete OAuth flow to get refresh token
    3. Credentials will be saved to credentials.json
    """
    
    print("\n" + "=" * 60)
    print("Salesforce Data Retrieval Examples")
    print("=" * 60)
    print("\n⚠️  Prerequisites:")
    print("   1. Connected App created in Salesforce")
    print("   2. OAuth setup completed (run scripts/salesforce_oauth_setup.py)")
    print("   3. Refresh token saved in credentials.json")
    print()
    
    try:
        # Run examples
        example_1_query_cases()
        example_2_query_with_date_range()
        example_3_query_closed_cases_by_agent()
        example_4_available_reports()
        example_5_describe_case_object()
        
        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\n💡 Next steps:")
        print("   1. Ensure your Salesforce admin created a Connected App")
        print("   2. Run: python scripts/salesforce_oauth_setup.py")
        print("   3. Complete the OAuth authorization flow")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
