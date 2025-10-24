#!/usr/bin/env python3
"""
Quick start script for your specific Google Sheets setup
Modify the sheet names to match your actual sheets
"""

from main import KPIBot
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def process_your_sheets():
    """
    Example of processing your actual Google Sheets
    Modify the sheet names and worksheet names to match your setup
    """
    print("KPI Calculator Bot - Processing Your Google Sheets")
    print("="*60)
    
    # Initialize bot with Google Sheets support
    bot = KPIBot(use_sheets=True)
    
    try:
        # Load agent database from your "Agent Info" sheet
        print("Loading agent database from 'Agent Info & Team Distribution'...")
        agent_db = bot.load_agent_database(
            source_type="sheets", 
            sheet_name="Agent Info & Team Distribution"
        )
        print(f"✅ Loaded {len(agent_db)} agents from database")
        
        # Load KPI data from your KPI calculator sheet
        print("Loading KPI data from '[v2.4] KPI Calculator'...")
        
        # You might need to adjust the worksheet_name based on your sheet structure
        # Common worksheet names: "Data", "Raw Data", "KPI Data", "Sheet1"
        kpi_data = bot.load_kpi_data(
            source_type="sheets", 
            sheet_name="[v2.4] KPI Calculator",
            worksheet_name="Sheet1"  # Adjust this to match your actual worksheet name
        )
        print(f"✅ Loaded KPI data for {len(kpi_data)} records")
        
        # Display column names to help you understand the data structure
        print(f"\nKPI Data Columns: {list(kpi_data.columns)}")
        if agent_db is not None and len(agent_db) > 0:
            print(f"Agent DB Columns: {list(agent_db.columns)}")
        
        # Process KPIs and save results
        print("\nProcessing KPIs...")
        results = bot.process_kpi_batch(
            kpi_data, 
            agent_db, 
            output_file="data/results/your_kpi_results.xlsx"
        )
        
        print(f"\n🎉 Processing complete!")
        print(f"Results saved to: data/results/your_kpi_results.xlsx")
        print(f"Total agents processed: {len(results)}")
        
        # Show top performers
        if 'overall_kpi' in results.columns:
            top_performers = results.nlargest(5, 'overall_kpi')[['agent_name', 'overall_kpi', 'performance_rating']]
            print(f"\nTop 5 Performers:")
            print(top_performers.to_string(index=False))
        
    except Exception as e:
        print(f"❌ Error processing sheets: {e}")
        print(f"\nTroubleshooting tips:")
        print(f"1. Make sure sheet names are exactly: 'Agent Info & Team Distribution' and '[v2.4] KPI Calculator'")
        print(f"2. Check that your service account has access to these sheets")
        print(f"3. Verify the worksheet names within each sheet")
        print(f"4. Ensure the data contains the required KPI columns")

def inspect_sheet_structure():
    """
    Helper function to inspect your sheet structure
    Use this to understand what worksheets and columns are available
    """
    print("\nInspecting Sheet Structure...")
    print("-" * 40)
    
    bot = KPIBot(use_sheets=True)
    
    # Try to load and inspect the sheets
    sheet_names = [
        "Agent Info & Team Distribution", 
        "[v2.4] KPI Calculator"
    ]
    
    for sheet_name in sheet_names:
        try:
            print(f"\n📊 Sheet: {sheet_name}")
            
            # Try common worksheet names
            worksheet_names = ["Sheet1", "Data", "Agent_DB", "KPI_Data", "Raw Data"]
            
            for ws_name in worksheet_names:
                try:
                    data = bot.sheets_client.read_sheet_data(sheet_name, ws_name)
                    print(f"  ✅ Worksheet '{ws_name}': {len(data)} rows, {len(data.columns)} columns")
                    print(f"     Columns: {list(data.columns)}")
                    if len(data) > 0:
                        print(f"     Sample data: {data.iloc[0].to_dict()}")
                    break
                except:
                    continue
            else:
                print(f"  ❌ No accessible worksheets found")
                
        except Exception as e:
            print(f"  ❌ Cannot access sheet: {e}")

if __name__ == "__main__":
    # First, inspect the structure to understand your data
    inspect_sheet_structure()
    
    # Then process the data
    process_your_sheets()