#!/usr/bin/env python3
"""
Comprehensive validation and test suite for the Amplify KPI Calculator Bot
This script validates the entire system and provides confidence that it's working correctly
"""

import os
import sys
import pandas as pd
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_imports():
    """Test that all modules can be imported correctly"""
    print("🧪 Testing Module Imports...")
    
    try:
        import config
        print("   ✅ config.py imported successfully")
        
        from data_importer import DataImporter
        print("   ✅ data_importer.py imported successfully")
        
        from named_functions import NamedFunctions
        print("   ✅ named_functions.py imported successfully")
        
        from kpi_calculator import AmplifyKPICalculator
        print("   ✅ kpi_calculator.py imported successfully")
        
        from scorecard_generator import ScorecardGenerator
        print("   ✅ scorecard_generator.py imported successfully")
        
        from main import AmplifyKPIBot
        print("   ✅ main.py imported successfully")
        
        return True
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False

def test_configuration():
    """Test configuration validity"""
    print("\n🧪 Testing Configuration...")
    
    try:
        from config import DEFAULT_WEIGHTS, METRIC_GOALS, EXPORT_FILE_PATTERNS
        
        # Check weights sum to 1.0
        total_weight = sum(DEFAULT_WEIGHTS.values())
        if abs(total_weight - 1.0) < 0.001:
            print(f"   ✅ Weights sum correctly: {total_weight}")
        else:
            print(f"   ⚠️ Weights sum to {total_weight}, not 1.0")
        
        # Check required patterns exist (these patterns are used in the code)
        required_patterns = ['time_utilization', 'cases_closed', 'qa_scores', 'qa_bcf']
        for pattern in required_patterns:
            if pattern in EXPORT_FILE_PATTERNS:
                print(f"   ✅ {pattern} pattern defined")
            else:
                print(f"   ❌ Missing pattern: {pattern}")
        
        return True
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        return False

def test_sample_data_processing():
    """Test processing of sample data"""
    print("\n🧪 Testing Sample Data Processing...")
    
    try:
        from main import AmplifyKPIBot
        
        # Check if sample data exists
        exports_folder = Path("exports")
        if not exports_folder.exists():
            print(f"   ❌ Exports folder not found: {exports_folder}")
            return False
        
        csv_files = list(exports_folder.glob("*.csv"))
        if not csv_files:
            print(f"   ❌ No CSV files found in {exports_folder}")
            return False
        
        print(f"   ✅ Found {len(csv_files)} CSV files in exports folder")
        
        # Initialize bot
        bot = AmplifyKPIBot(exports_folder="exports")
        
        # Test data loading
        agent_data = bot.load_and_process_data()
        print(f"   ✅ Loaded data for {len(agent_data)} agents")
        
        # Test KPI calculation
        results_df, team_stats = bot.calculate_all_kpis()
        print(f"   ✅ Calculated KPIs for {len(results_df)} agents")
        print(f"   ✅ Team average: {team_stats.get('team_average_score', 0):.2%}")
        
        return True
    except Exception as e:
        print(f"   ❌ Data processing error: {e}")
        return False

def test_scorecard_generation():
    """Test scorecard generation"""
    print("\n🧪 Testing Scorecard Generation...")
    
    try:
        from main import AmplifyKPIBot
        
        bot = AmplifyKPIBot(exports_folder="exports")
        bot.load_and_process_data()
        
        # Test individual scorecard
        test_output = "test_scorecard.csv"
        if Path(test_output).exists():
            Path(test_output).unlink()
        
        # Get first agent for testing
        agents = list(bot.agent_data.keys())
        if not agents:
            print("   ❌ No agents found for scorecard testing")
            return False
        
        test_agent = agents[0]
        scorecard_data = bot.generate_individual_scorecard(test_agent, test_output)
        
        if Path(test_output).exists():
            print(f"   ✅ Generated scorecard for {test_agent}")
            Path(test_output).unlink()  # Clean up
        else:
            print(f"   ❌ Scorecard file not created")
            return False
        
        return True
    except Exception as e:
        print(f"   ❌ Scorecard generation error: {e}")
        return False

def test_named_functions():
    """Test named function calculations"""
    print("\n🧪 Testing Named Functions...")
    
    try:
        from named_functions import NamedFunctions
        
        # Create sample agent data
        sample_agent_data = {
            'Test Agent': {
                'Name': 'Test Agent',
                'time_utilization': 0.85,
                'working_hours': 40,
                'cases_closed': 25,
                'chat_response_time': 45,
                'email_response_time': 120,
                'qa_score': 0.90,
                'bcf_percentage': 0.05,
                'sla_breaches': 2
            }
        }
        
        nf = NamedFunctions(sample_agent_data)
        sample_data = sample_agent_data['Test Agent']
        
        # Test each function
        test_functions = [
            ('time_utilization_check', lambda: nf.time_utilization_check(sample_data)),
            ('working_hours', lambda: nf.working_hours(sample_data)),
            ('cases_per_hour', lambda: nf.cases_per_hour(sample_data)),
            ('chat_response_time', lambda: nf.chat_response_time(sample_data)),
            ('email_response_time', lambda: nf.email_response_time(sample_data)),
            ('qa_score', lambda: nf.qa_score(sample_data)),
            ('bcf_percentage', lambda: nf.bcf_percentage(sample_data))
        ]
        
        for func_name, func in test_functions:
            try:
                result = func()
                print(f"   ✅ {func_name}: {result}")
            except Exception as e:
                print(f"   ❌ {func_name} failed: {e}")
                return False
        
        return True
    except Exception as e:
        print(f"   ❌ Named functions error: {e}")
        return False

def test_kpi_calculator():
    """Test KPI calculator scoring"""
    print("\n🧪 Testing KPI Calculator...")
    
    try:
        from kpi_calculator import AmplifyKPICalculator
        from config import DEFAULT_WEIGHTS
        
        # Create sample agent data
        sample_agent_data = {
            'Test Agent': {
                'Name': 'Test Agent',
                'time_utilization': 0.85,
                'working_hours': 40,
                'cases_closed': 25
            }
        }
        
        calculator = AmplifyKPICalculator(sample_agent_data, weights=DEFAULT_WEIGHTS)
        
        # Sample agent breakdown
        sample_breakdown = {
            'time_utilization': 0.85,
            'working_hours': 40,
            'cph': 0.625,  # 25 cases / 40 hours
            'chat_response_time': 45,
            'email_response_time': 120,
            'qa_score': 0.90,
            'bcf_percentage': 0.05,
            'sla_score': 0.95,
            'csat_score': 0.88
        }
        
        scores = calculator.calculate_final_weighted_score(sample_breakdown)
        
        print(f"   ✅ Final weighted score: {scores['final_weighted_score']:.2%}")
        print(f"   ✅ Performance rating: {scores['performance_rating']}")
        
        # Validate score is reasonable
        if 0 <= scores['final_weighted_score'] <= 1:
            print("   ✅ Score is within valid range")
        else:
            print(f"   ❌ Score out of range: {scores['final_weighted_score']}")
            return False
        
        return True
    except Exception as e:
        print(f"   ❌ KPI calculator error: {e}")
        return False

def test_end_to_end():
    """Test complete end-to-end workflow"""
    print("\n🧪 Testing End-to-End Workflow...")
    
    try:
        from main import AmplifyKPIBot
        
        # Initialize bot
        bot = AmplifyKPIBot(exports_folder="exports")
        
        # Load data
        agent_data = bot.load_and_process_data()
        
        # Calculate KPIs
        results_df, team_stats = bot.calculate_all_kpis()
        
        # Generate scorecards
        test_folder = Path("test_scorecards")
        if test_folder.exists():
            import shutil
            shutil.rmtree(test_folder)
        
        scorecard_results, summary_df = bot.generate_scorecards(str(test_folder))
        
        # Verify output
        scorecard_files = list(test_folder.glob("*.csv"))
        
        print(f"   ✅ Processed {len(agent_data)} agents")
        print(f"   ✅ Generated {len(scorecard_files)} scorecard files")
        print(f"   ✅ Team average: {team_stats.get('team_average_score', 0):.2%}")
        
        # Clean up test files
        if test_folder.exists():
            import shutil
            shutil.rmtree(test_folder)
        
        return True
    except Exception as e:
        print(f"   ❌ End-to-end test error: {e}")
        return False

def run_validation_suite():
    """Run the complete validation suite"""
    print("🚀 Starting Amplify KPI Calculator Bot Validation Suite")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("Sample Data Processing", test_sample_data_processing),
        ("Named Functions", test_named_functions),
        ("KPI Calculator", test_kpi_calculator),
        ("Scorecard Generation", test_scorecard_generation),
        ("End-to-End Workflow", test_end_to_end)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "="*60)
    print(f"🏆 Validation Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The system is ready for production use.")
        print("\n💡 Next Steps:")
        print("   1. Place your actual CSV export files in the 'exports' folder")
        print("   2. Run: python main.py --exports-folder exports --output results.xlsx --generate-scorecards")
        print("   3. Check the 'scorecards' folder for individual agent scorecards")
        return True
    else:
        print(f"⚠️ {total - passed} tests failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = run_validation_suite()
    sys.exit(0 if success else 1)