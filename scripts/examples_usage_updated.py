#!/usr/bin/env python3
"""
Updated example usage for the Amplify KPI Calculator Bot
Demonstrates the new CSV-based system matching your actual Excel implementation
"""

from main import AmplifyKPIBot
import logging
from pathlib import Path

# Configure logging for examples
logging.basicConfig(level=logging.INFO)

def example_1_basic_processing():
    """Example 1: Basic CSV processing with sample data"""
    print("\n=== Example 1: Basic CSV Export Processing ===")
    
    bot = AmplifyKPIBot(exports_folder="exports")
    
    try:
        # Load and process all export data
        print("Loading CSV export files...")
        agent_data = bot.load_and_process_data()
        print(f"✅ Loaded data for {len(agent_data)} agents")
        
        # Calculate KPIs for all agents
        print("Calculating KPIs...")
        results_df, team_stats = bot.calculate_all_kpis()
        
        # Display results
        bot.display_summary(results_df, team_stats)
        
        # Save results
        bot.save_results(results_df, "results/example_1_results.xlsx")
        print("✅ Results saved to results/example_1_results.xlsx")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def example_2_generate_scorecards():
    """Example 2: Generate individual agent scorecards"""
    print("\n=== Example 2: Generate Individual Scorecards ===")
    
    bot = AmplifyKPIBot(exports_folder="exports")
    
    try:
        # Load and process data
        bot.load_and_process_data()
        
        # Generate all scorecards
        scorecard_results, summary_df = bot.generate_scorecards("example_scorecards")
        
        print(f"✅ Generated {scorecard_results['total_agents']} scorecards")
        print(f"📁 Scorecards saved in: {scorecard_results['output_folder']}")
        
        # Show top performers
        print("\n🏆 Top 3 Performers:")
        top_3 = summary_df.head(3)
        for _, agent in top_3.iterrows():
            print(f"   {agent['Agent Name']}: {agent['KPI Score']} ({agent['Performance Rating']})")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def example_3_individual_scorecard():
    """Example 3: Generate scorecard for specific agent"""
    print("\n=== Example 3: Individual Agent Scorecard ===")
    
    bot = AmplifyKPIBot(exports_folder="exports")
    
    try:
        # Load and process data
        bot.load_and_process_data()
        
        # Generate scorecard for Dajah Gray (matching your Excel example)
        agent_name = "Dajah Gray"
        scorecard_data = bot.generate_individual_scorecard(
            agent_name, 
            f"individual_{agent_name.replace(' ', '_')}_scorecard.csv"
        )
        
        print(f"✅ Generated individual scorecard for {agent_name}")
        
        # Display key metrics
        breakdown = scorecard_data['agent_breakdown']
        final_scores = scorecard_data['final_scores']
        
        print(f"\n📊 Key Metrics for {agent_name}:")
        print(f"   Time Utilization: {breakdown['time_utilization']}")
        print(f"   Working Hours: {breakdown['working_hours']}")
        print(f"   Cases Per Hour: {breakdown['cph']}")
        print(f"   QA Score: {breakdown['qa_score']}")
        print(f"   Final KPI Score: {final_scores['final_weighted_score']}")
        print(f"   Performance Rating: {final_scores['performance_rating']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def example_4_custom_folder():
    """Example 4: Using custom export folder"""
    print("\n=== Example 4: Custom Export Folder ===")
    
    # Create a custom exports folder with different data
    custom_folder = "custom_exports"
    Path(custom_folder).mkdir(exist_ok=True)
    
    # You would put your actual CSV export files here
    print(f"📁 Using custom export folder: {custom_folder}")
    print("   (Put your CSV export files in this folder)")
    
    # Initialize bot with custom folder
    bot = AmplifyKPIBot(exports_folder=custom_folder)
    
    print("   To use: bot.load_and_process_data()")
    print("   Then: bot.calculate_all_kpis()")

def example_5_understanding_csv_structure():
    """Example 5: Understanding required CSV file structure"""
    print("\n=== Example 5: CSV File Requirements ===")
    
    print("📋 Required CSV Export Files:")
    print("   1. time_util*.csv - Time Utilization data")
    print("      Columns: Name, Time Utilization Percent, Total Hours Worked")
    print()
    print("   2. cases_closed*.csv - Closed cases from Salesforce")
    print("      Columns: Case Owner, Case Number, Product, Date/Time Closed")
    print()
    print("   3. cases_transferred*.csv - Transferred cases") 
    print("      Columns: Case Owner, Case Number, Product, Transfer Reason")
    print()
    print("   4. chat_response*.csv - Chat response times")
    print("      Columns: Name, AVG Agent Speed to Answer (Seconds), Response Count")
    print()
    print("   5. email_response*.csv - Email response times")
    print("      Columns: Name, AVG Business Minutes Until First Email Reply, Email Count")
    print()
    print("   6. qa_scores*.csv - QA scores")
    print("      Columns: Agent Name, Avg Score, Case Count")
    print()
    print("   7. qa_bcf*.csv - QA BCF percentages")
    print("      Columns: Agent Name, Fail % (BCF percentage), Cases Audited")
    print()
    print("   8. sla_cases*.csv - Cases out of SLA")
    print("      Columns: Case Owner, Case Number, Days Since Last Update, Product")
    print()
    print("📝 Optional files:")
    print("   - csat*.csv - Customer satisfaction data")
    print("   - phone_response*.csv - Phone response times")
    print()
    print("💡 File naming uses glob patterns, so time_util_2024_10_14.csv works!")

def show_kpi_weights_and_goals():
    """Show the KPI weights and goals used in calculations"""
    print("\n=== KPI Weights and Goals ===")
    
    from config import DEFAULT_WEIGHTS, METRIC_GOALS
    
    print("📊 KPI Weights (matching your Excel #Controls sheet):")
    for metric, weight in DEFAULT_WEIGHTS.items():
        print(f"   {metric.replace('_', ' ').title()}: {weight*100:.1f}%")
    
    print("\n🎯 Metric Goals/Targets:")
    for metric, goal in METRIC_GOALS.items():
        if metric == 'max_score':
            continue
        if 'percentage' in metric:
            print(f"   {metric.replace('_', ' ').title()}: {goal*100:.1f}%")
        else:
            print(f"   {metric.replace('_', ' ').title()}: {goal}")

if __name__ == "__main__":
    print("Amplify KPI Calculator Bot - Updated Examples")
    print("=" * 60)
    
    # Show configuration
    show_kpi_weights_and_goals()
    
    # Run examples with sample data
    try:
        example_1_basic_processing()
        example_2_generate_scorecards()  
        example_3_individual_scorecard()
        example_4_custom_folder()
        example_5_understanding_csv_structure()
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        logging.error(f"Error in examples: {e}")
    
    print("\n🎉 All examples completed!")
    print("\n💡 Next Steps:")
    print("   1. Place your actual CSV export files in the 'exports' folder")
    print("   2. Run: python main.py --exports-folder exports --output results.xlsx --generate-scorecards")
    print("   3. Check the 'scorecards' folder for individual agent scorecards")
    print("   4. Review results.xlsx for team-level data")