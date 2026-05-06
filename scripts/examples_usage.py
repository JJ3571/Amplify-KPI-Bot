#!/usr/bin/env python3
"""
Example usage of the KPI Calculator Bot
Demonstrates various ways to use the bot for KPI processing
"""

from main import KPIBot
import logging

# Configure logging for examples
logging.basicConfig(level=logging.INFO)

def example_1_sheets_processing():
    """Example 1: Process KPIs from Google Sheets"""
    print("\n=== Example 1: Google Sheets Processing ===")
    
    bot = KPIBot(use_sheets=True)
    
    try:
        # Load agent database from Google Sheets
        agent_db = bot.load_agent_database(
            source_type="sheets", 
            sheet_name="Agent Info"
        )
        print(f"Loaded {len(agent_db)} agents from database")
        
        # Load KPI data from Google Sheets
        # Replace with your actual sheet name
        kpi_data = bot.load_kpi_data(
            source_type="sheets", 
            sheet_name="[v2.4] KPI Calculator",  # Example from your files
            worksheet_name="Data"  # Adjust based on your sheet structure
        )
        print(f"Loaded KPI data for {len(kpi_data)} records")
        
        # Process KPIs
        results = bot.process_kpi_batch(
            kpi_data, 
            agent_db, 
            output_file="results/kpi_results.xlsx"
        )
        
        print(f"Processing complete! Results saved with {len(results)} records")
        
    except Exception as e:
        print(f"Error in sheets processing: {e}")

def example_2_csv_processing():
    """Example 2: Process KPIs from CSV files"""
    print("\n=== Example 2: CSV File Processing ===")
    
    bot = KPIBot(use_sheets=False)
    
    try:
        # Load from CSV files (you'll need to create these)
        # agent_db = bot.load_agent_database(
        #     source_type="file",
        #     file_path="data/agents.csv"
        # )
        
        # kpi_data = bot.load_kpi_data(
        #     source_type="file",
        #     file_path="data/kpi_data.csv"
        # )
        
        # For demonstration, create sample data
        import pandas as pd
        
        # Sample KPI data
        sample_kpi_data = pd.DataFrame({
            'agent_id': ['A001', 'A002', 'A003', 'A004', 'A005'],
            'agent_name': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown', 'Charlie Davis'],
            'customer_satisfaction': [4.2, 4.7, 3.8, 4.5, 3.9],
            'response_time': [8, 12, 25, 6, 18],  # minutes
            'resolution_time': [3, 4, 8, 2, 6],  # hours
            'first_contact_resolution': [0.78, 0.85, 0.65, 0.82, 0.71],  # percentage
            'quality_score': [0.88, 0.92, 0.75, 0.90, 0.82]  # percentage
        })
        
        print("Using sample KPI data for demonstration")
        
        # Process KPIs
        results = bot.process_kpi_batch(
            sample_kpi_data, 
            output_file="sample_results.csv"
        )
        
        print("Sample processing complete!")
        
    except Exception as e:
        print(f"Error in CSV processing: {e}")

def example_3_individual_scorecard():
    """Example 3: Generate individual agent scorecard"""
    print("\n=== Example 3: Individual Agent Scorecard ===")
    
    bot = KPIBot(use_sheets=False)
    
    # Sample data for individual agent
    import pandas as pd
    
    sample_data = pd.DataFrame({
        'agent_id': ['A001'],
        'agent_name': ['John Doe'],
        'customer_satisfaction': [4.2],
        'response_time': [8],
        'resolution_time': [3],
        'first_contact_resolution': [0.78],
        'quality_score': [0.88]
    })
    
    try:
        scorecard = bot.generate_individual_scorecard('A001', sample_data)
        
        print("Individual Scorecard Generated:")
        print(f"Agent: {scorecard['raw_metrics'].get('agent_name', 'Unknown')}")
        print(f"Overall KPI: {scorecard['calculated_scores']['overall_kpi']}")
        print(f"Performance Rating: {scorecard['calculated_scores']['performance_rating']}")
        print("\nRecommendations:")
        for rec in scorecard['recommendations']:
            print(f"- {rec}")
            
    except Exception as e:
        print(f"Error generating individual scorecard: {e}")

def example_4_custom_weights():
    """Example 4: Using custom KPI weights"""
    print("\n=== Example 4: Custom KPI Weights ===")
    
    from kpi_calculator import KPICalculator
    
    # Custom weights - emphasize customer satisfaction and quality
    custom_weights = {
        'customer_satisfaction': 0.4,  # Increased from 0.3
        'response_time': 0.15,         # Decreased from 0.2
        'resolution_time': 0.15,       # Decreased from 0.2
        'first_contact_resolution': 0.15,  # Same
        'quality_score': 0.15          # Same
    }
    
    # Create calculator with custom weights
    calculator = KPICalculator(weights=custom_weights)
    
    # Sample agent data
    agent_data = {
        'customer_satisfaction': 4.2,
        'response_time': 8,
        'resolution_time': 3,
        'first_contact_resolution': 0.78,
        'quality_score': 0.88
    }
    
    scores = calculator.calculate_agent_kpi(agent_data)
    
    print("KPI Calculation with Custom Weights:")
    print(f"Customer Satisfaction Score: {scores.get('customer_satisfaction_score', 'N/A')}")
    print(f"Response Time Score: {scores.get('response_time_score', 'N/A')}")
    print(f"Resolution Time Score: {scores.get('resolution_time_score', 'N/A')}")
    print(f"First Contact Resolution Score: {scores.get('first_contact_resolution_score', 'N/A')}")
    print(f"Quality Score: {scores.get('quality_score_score', 'N/A')}")
    print(f"Overall KPI: {scores['overall_kpi']}")
    print(f"Performance Rating: {scores['performance_rating']}")

if __name__ == "__main__":
    print("KPI Calculator Bot - Example Usage")
    print("=" * 50)
    
    # Run examples
    try:
        # Note: Example 1 requires actual Google Sheets setup
        # Uncomment when you have your sheets configured
        # example_1_sheets_processing()
        
        example_2_csv_processing()
        example_3_individual_scorecard()
        example_4_custom_weights()
        
    except Exception as e:
        print(f"Error running examples: {e}")
        logging.error(f"Error in examples: {e}")
    
    print("\nAll examples completed!")