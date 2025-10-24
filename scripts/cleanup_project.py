#!/usr/bin/env python3
"""
Cleanup script for Amplify KPI Calculator Bot
Removes old/legacy files and folders from previous bot versions
"""

from pathlib import Path
import shutil

def cleanup_old_files():
    """Remove old files and folders from previous bot versions"""
    
    print("🧹 Amplify KPI Bot - Cleanup Script")
    print("=" * 60)
    
    # Items to remove
    items_to_remove = {
        "folders": [
            ("data/", "Old data folder from generic KPI bot - no longer used"),
        ],
        "files": [
            # These are now in scripts/ folder or replaced
        ]
    }
    
    # Process folders
    print("\n📁 Checking folders to remove:")
    for folder_path, description in items_to_remove["folders"]:
        path = Path(folder_path)
        if path.exists():
            print(f"\n   🗑️  {folder_path}")
            print(f"      Reason: {description}")
            
            # Show contents
            try:
                contents = list(path.rglob("*"))
                if contents:
                    print(f"      Contains {len(contents)} items:")
                    for item in contents[:5]:  # Show first 5 items
                        print(f"        - {item.relative_to(path.parent)}")
                    if len(contents) > 5:
                        print(f"        ... and {len(contents) - 5} more items")
            except Exception as e:
                print(f"      Error listing contents: {e}")
            
            response = input(f"\n   Remove {folder_path}? (y/n): ").strip().lower()
            if response == 'y':
                try:
                    shutil.rmtree(path)
                    print(f"   ✅ Removed {folder_path}")
                except Exception as e:
                    print(f"   ❌ Error removing {folder_path}: {e}")
            else:
                print(f"   ⏭️  Skipped {folder_path}")
        else:
            print(f"   ℹ️  {folder_path} - Already removed or doesn't exist")
    
    # Process individual files
    if items_to_remove["files"]:
        print("\n📄 Checking files to remove:")
        for file_path, description in items_to_remove["files"]:
            path = Path(file_path)
            if path.exists():
                print(f"\n   🗑️  {file_path}")
                print(f"      Reason: {description}")
                
                response = input(f"   Remove {file_path}? (y/n): ").strip().lower()
                if response == 'y':
                    try:
                        path.unlink()
                        print(f"   ✅ Removed {file_path}")
                    except Exception as e:
                        print(f"   ❌ Error removing {file_path}: {e}")
                else:
                    print(f"   ⏭️  Skipped {file_path}")
            else:
                print(f"   ℹ️  {file_path} - Already removed or doesn't exist")

def show_current_structure():
    """Show the current project structure"""
    print("\n" + "=" * 60)
    print("📊 Current Project Structure")
    print("=" * 60)
    
    root = Path(".")
    important_items = [
        ("config.py", "📝 KPI configuration (weights, goals, patterns)"),
        ("data_importer.py", "📊 CSV data import and processing"),
        ("named_functions.py", "🧮 Excel formula equivalents"),
        ("kpi_calculator.py", "🎯 KPI scoring engine"),
        ("scorecard_generator.py", "📄 Scorecard generation"),
        ("main.py", "🚀 Main application"),
        ("requirements.txt", "📦 Python dependencies"),
        ("exports/", "📁 CSV export files (your data goes here)"),
        ("scorecards/", "📁 Generated agent scorecards"),
        ("scripts/", "🔧 Helper scripts and utilities"),
        ("examples/", "📚 Reference files (Excel templates, etc.)"),
    ]
    
    print("\nCore Application Files:")
    for item, description in important_items:
        path = Path(item)
        if path.exists():
            if path.is_dir():
                count = len(list(path.glob("*")))
                print(f"   {description}: {item} ({count} items)")
            else:
                print(f"   {description}: {item}")
        else:
            print(f"   ⚠️  Missing: {item}")

def main():
    """Main cleanup function"""
    
    # Show current structure first
    show_current_structure()
    
    # Ask if user wants to proceed with cleanup
    print("\n" + "=" * 60)
    response = input("\nProceed with cleanup? (y/n): ").strip().lower()
    
    if response == 'y':
        cleanup_old_files()
        
        print("\n" + "=" * 60)
        print("✨ Cleanup Complete!")
        print("=" * 60)
        print("\n💡 Your project structure is now organized:")
        print("   • Core application files in root directory")
        print("   • Helper scripts in scripts/ folder")
        print("   • CSV exports go in exports/ folder")
        print("   • Generated scorecards in scorecards/ folder")
        print("   • Reference materials in examples/ folder")
        
    else:
        print("\n⏭️  Cleanup cancelled. No changes made.")

if __name__ == "__main__":
    main()
