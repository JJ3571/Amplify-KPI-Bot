#!/usr/bin/env python3
"""
Find Tableau Content - Search workbooks and views
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from clients import TableauClient
from config import TABLEAU_CONFIG


def search_all(search_term):
    """Search all workbooks and views for a term"""
    
    with TableauClient() as client:
        if not client.connect(TABLEAU_CONFIG['server_url'], TABLEAU_CONFIG['site_name']):
            print("❌ Failed to connect")
            return
        
        search_lower = search_term.lower()
        
        print(f"\n🔍 Searching for: '{search_term}'\n")
        print("="*80)
        
        # Search workbooks
        workbooks = client.get_workbooks()
        wb_matches = [wb for wb in workbooks if search_lower in wb['name'].lower()]
        
        if wb_matches:
            print(f"\n📚 Found {len(wb_matches)} matching workbooks:\n")
            for wb in wb_matches:
                print(f"  • {wb['name']}")
                print(f"    ID: {wb['id']}")
                print(f"    URL: {wb.get('contentUrl', 'N/A')}")
                print()
        
        # Search views
        views = client.get_views()
        view_matches = [v for v in views if search_lower in v['name'].lower()]
        
        if view_matches:
            print(f"\n📊 Found {len(view_matches)} matching views:\n")
            for v in view_matches:
                print(f"  • {v['name']}")
                print(f"    ID: {v['id']}")
                print(f"    Workbook: {v.get('workbook_name', 'N/A')}")
                print(f"    Workbook ID: {v.get('workbook_id', 'N/A')}")
                print()
        
        if not wb_matches and not view_matches:
            print("\n❌ No matches found")
            print(f"\n💡 Try a different search term or check permissions")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        search_term = " ".join(sys.argv[1:])
    else:
        search_term = input("Enter search term: ").strip()
    
    if search_term:
        search_all(search_term)
    else:
        print("❌ Please provide a search term")
