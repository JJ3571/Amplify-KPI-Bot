"""
Amplify KPI Calculator Bot - Main Application
Automatically pulls data from available sources (Tableau, Google Sheets, Salesforce)
and generates KPI Calculator Excel workbook with Export-KPI and Export-QA tabs
"""

import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path

from clients import ConnectionChecker
from core import KPIAggregator
from exporters import ExcelGenerator
from utils import get_last_week_dates

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kpi_bot.log'),
        logging.StreamHandler()
    ]
)


class AmplifyKPIBot:
    """Main KPI Bot application - orchestrates connection checking, data aggregation, and Excel generation"""
    
    def __init__(self, week_start=None, week_end=None, output_dir='data/exports'):
        """
        Initialize Amplify KPI Bot
        
        Args:
            week_start (datetime): Start of week (defaults to last Sunday)
            week_end (datetime): End of week (defaults to last Saturday)
            output_dir (str): Directory for output files
        """
        if week_start is None or week_end is None:
            self.week_start, self.week_end = get_last_week_dates()
        else:
            self.week_start = week_start
            self.week_end = week_end
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Components
        self.connection_checker = ConnectionChecker()
        self.aggregator = KPIAggregator(self.week_start, self.week_end)
        self.excel_generator = ExcelGenerator(output_dir)
        
        # Status
        self.connections = {
            'tableau': False,
            'google_sheets': False,
            'salesforce': False
        }
        self.missing_data = []
    
    def check_connections(self) -> dict:
        """
        Check all data source connections
        
        Returns:
            dict: Connection status for each source
        """
        logging.info("=" * 70)
        logging.info("Checking data source connections...")
        logging.info("=" * 70)
        
        results = self.connection_checker.check_all_connections()
        
        # Update internal status
        self.connections['tableau'] = results['tableau']['available']
        self.connections['google_sheets'] = results['google_sheets']['available']
        self.connections['salesforce'] = results['salesforce']['available']
        
        # Track missing data sources
        self.missing_data = []
        if not self.connections['tableau']:
            self.missing_data.append('Tableau')
        if not self.connections['google_sheets']:
            self.missing_data.append('Google Sheets')
        if not self.connections['salesforce']:
            self.missing_data.append('Salesforce')
        
        return results
    
    def load_data(self) -> bool:
        """
        Load data from all available sources
        
        Returns:
            bool: True if at least some data was loaded successfully
        """
        logging.info("=" * 70)
        logging.info("Loading data from available sources...")
        logging.info("=" * 70)
        
        success_count = 0
        
        # Load Tableau QA data
        if self.connections['tableau']:
            if self.aggregator.load_tableau_qa_data():
                logging.info("✅ Tableau QA data loaded")
                success_count += 1
            else:
                logging.warning("⚠️  Failed to load Tableau QA data")
        
        # Load Tableau KPI data
        if self.connections['tableau']:
            if self.aggregator.load_tableau_kpi_data():
                logging.info("✅ Tableau KPI data loaded")
                success_count += 1
            else:
                logging.warning("⚠️  Failed to load Tableau KPI data")
        
        # Load Google Sheets SLA data
        if self.connections['google_sheets']:
            if self.aggregator.load_google_sheets_sla_data():
                logging.info("✅ Google Sheets SLA data loaded")
                success_count += 1
            else:
                logging.warning("⚠️  Failed to load Google Sheets SLA data")
        
        # Load Salesforce data
        if self.connections['salesforce']:
            if self.aggregator.load_salesforce_data():
                logging.info("✅ Salesforce data loaded")
                success_count += 1
            else:
                logging.warning("⚠️  Failed to load Salesforce data")
        
        if success_count == 0:
            logging.error("❌ No data could be loaded from any source")
            return False
        
        logging.info(f"✅ Data loading complete: {success_count} source(s) loaded")
        return True
    
    def generate_kpi_calculator(self, format='excel') -> tuple:
        """
        Generate KPI Calculator with Export-KPI and Export-QA tabs
        
        Args:
            format (str): Output format - 'excel' (default), 'csv', or 'both'
        
        Returns:
            tuple: (excel_path, csv_paths) - paths to generated files
        """
        logging.info("=" * 70)
        logging.info("Generating KPI Calculator...")
        logging.info("=" * 70)
        
        # Generate Export-QA tab
        export_qa = self.aggregator.generate_export_qa_tab()
        if export_qa is None:
            logging.error("❌ Failed to generate Export-QA tab")
        else:
            logging.info(f"✅ Export-QA generated: {len(export_qa)} agents")
        
        # Generate Export-KPI tab
        export_kpi = self.aggregator.generate_export_kpi_tab()
        if export_kpi is None:
            logging.error("❌ Failed to generate Export-KPI tab")
        else:
            logging.info(f"✅ Export-KPI generated: {len(export_kpi)} agents, {len(export_kpi.columns)} columns")
        
        # Check if we have at least one tab
        if export_qa is None and export_kpi is None:
            logging.error("❌ Cannot generate KPI Calculator - no data available")
            return None, (None, None)
        
        # Generate files
        excel_path = None
        csv_paths = (None, None)
        
        if format in ['excel', 'both']:
            excel_path = self.excel_generator.generate_workbook(
                export_kpi, export_qa, 
                self.week_start, self.week_end,
                self.missing_data
            )
        
        if format in ['csv', 'both']:
            csv_paths = self.excel_generator.generate_csv_exports(
                export_kpi, export_qa,
                self.week_start, self.week_end
            )
        
        return excel_path, csv_paths
    
    def run(self, format='excel', quiet=False) -> bool:
        """
        Main execution flow - check connections, load data, generate output
        
        Args:
            format (str): Output format - 'excel', 'csv', or 'both'
            quiet (bool): Suppress status output
        
        Returns:
            bool: True if successful
        """
        try:
            # Step 1: Check connections
            if not quiet:
                print("\n" + "="*70)
                print("AMPLIFY KPI CALCULATOR BOT")
                print("="*70)
                print(f"\nWeek: {self.week_start.strftime('%m/%d/%Y')} - {self.week_end.strftime('%m/%d/%Y')}")
                print("="*70)
            
            results = self.check_connections()
            
            if not quiet:
                self.connection_checker.print_status_report()
            
            # Check if we have minimum required data (at least Tableau)
            if not self.connections['tableau']:
                print("\n❌ ERROR: Tableau connection is required (provides 80% of data)")
                print("   Please configure Tableau credentials in credentials.json")
                return False
            
            # Step 2: Load data
            if not self.load_data():
                print("\n❌ ERROR: Failed to load data from any source")
                return False
            
            # Step 3: Generate output
            excel_path, csv_paths = self.generate_kpi_calculator(format=format)
            
            # Step 4: Display results
            if not quiet:
                print("\n" + "="*70)
                print("RESULTS")
                print("="*70)
            
            if excel_path:
                print(f"\n✅ Excel workbook created:")
                print(f"   {excel_path}")
            
            if csv_paths[0] or csv_paths[1]:
                print(f"\n✅ CSV files created:")
                if csv_paths[0]:
                    print(f"   Export-KPI: {csv_paths[0]}")
                if csv_paths[1]:
                    print(f"   Export-QA: {csv_paths[1]}")
            
            # Show data completeness
            if self.missing_data:
                print(f"\n⚠️  Missing data sources: {', '.join(self.missing_data)}")
                print("\n📋 Manual data entry required:")
                if 'Google Sheets' in self.missing_data or 'SLA' in ' '.join(self.missing_data):
                    print("   • SLA Cases columns need to be manually populated")
                if 'Salesforce' in self.missing_data:
                    print("   • Cases Closed and Cases Transferred need to be manually populated")
                print("\n   Copy/paste Export-KPI and Export-QA tabs into your live Google Sheet")
            else:
                print("\n✅ All data sources available - KPI Calculator is 100% complete!")
            
            if not quiet:
                print("\n" + "="*70)
                print("✅ KPI Calculator generation complete!")
                print("="*70 + "\n")
            
            return True
            
        except Exception as e:
            logging.error(f"Error in main execution: {e}")
            if not quiet:
                print(f"\n❌ ERROR: {e}")
            return False

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(
        description='Amplify KPI Calculator Bot - Generate KPI Calculator from Tableau, Google Sheets, and Salesforce',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate KPI Calculator for last week (default)
  python main.py
  
  # Generate Excel workbook only
  python main.py --format excel
  
  # Generate CSV files only
  python main.py --format csv
  
  # Generate both Excel and CSV
  python main.py --format both
  
  # Check connection status only
  python main.py --check-connections
  
  # Quiet mode (for cron jobs)
  python main.py --quiet
        """
    )
    
    parser.add_argument('--week', type=str, default='last',
                       help='Week to process: "last" (default), "YYYY-MM-DD" (Sunday date), or "current"')
    parser.add_argument('--format', type=str, default='excel', choices=['excel', 'csv', 'both'],
                       help='Output format: excel (default), csv, or both')
    parser.add_argument('--output-dir', type=str, default='data/exports',
                       help='Directory for output files (default: data/exports)')
    parser.add_argument('--check-connections', action='store_true',
                       help='Check connection status and exit')
    parser.add_argument('--quiet', action='store_true',
                       help='Quiet mode - minimal output (for cron jobs)')
    parser.add_argument('--update-sheets', action='store_true',
                       help='Update Google Sheets with KPI data')
    parser.add_argument('--generate-dataframes', action='store_true',
                       help='Generate comprehensive dataframes with scores and agent info')
    
    args = parser.parse_args()
    
    # Check connections only mode
    if args.check_connections:
        checker = ConnectionChecker()
        results = checker.check_all_connections()
        checker.print_status_report()
        return
    
    # Update sheets mode
    if args.update_sheets or args.generate_dataframes:
        from update_kpi_sheets import update_kpi_calculator_for_last_week
        
        results = update_kpi_calculator_for_last_week(
            update_sheets=args.update_sheets,
            save_dataframe=args.generate_dataframes
        )
        
        if results['success']:
            print("\n✅ Update Complete!")
            print(f"Agents Updated: {results['agents_updated']}")
            print(f"Data Sources: {', '.join(results['data_sources_used'])}")
            if results.get('dataframe_path'):
                print(f"Dataframe: {results['dataframe_path']}")
        else:
            print(f"\n❌ Update Failed: {results['message']}")
        
        exit(0 if results['success'] else 1)
    
    # Parse week argument
    week_start = None
    week_end = None
    
    if args.week == 'last':
        week_start, week_end = get_last_week_dates()
    elif args.week == 'current':
        # Current week (this Sunday to next Saturday)
        today = datetime.now()
        days_since_sunday = (today.weekday() + 1) % 7
        week_start = today - timedelta(days=days_since_sunday)
        week_end = week_start + timedelta(days=6)
    else:
        # Parse as date
        try:
            week_start = datetime.strptime(args.week, '%Y-%m-%d')
            week_end = week_start + timedelta(days=6)
        except ValueError:
            print(f"❌ Invalid week format: {args.week}")
            print("   Use 'last', 'current', or a date in YYYY-MM-DD format (Sunday)")
            return
    
    # Initialize and run bot
    bot = AmplifyKPIBot(week_start=week_start, week_end=week_end, output_dir=args.output_dir)
    success = bot.run(format=args.format, quiet=args.quiet)
    
    # Exit with appropriate code
    exit(0 if success else 1)

if __name__ == "__main__":
    main()