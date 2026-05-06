#!/usr/bin/env python3
"""
Test script for KPI Calculator Bot
Quick verification that all components work correctly
"""

import sys
import pandas as pd
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that all modules import correctly"""
    print("Testing imports...")
    try:
        from main import KPIBot
        from core import KPICalculator
        from core import FileHandler
        from config import DEFAULT_WEIGHTS, SCORING_THRESHOLDS
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_kpi_calculator():
    """Test KPI calculator with sample data"""
    print("\nTesting KPI Calculator...")
    try:
        from core import KPICalculator
        
        calculator = KPICalculator()
        
        # Sample agent data
        sample_agent = {
            'customer_satisfaction': 4.2,
            'response_time': 8,
            'resolution_time': 3,
            'first_contact_resolution': 0.78,
            'quality_score': 0.88
        }
        
        scores = calculator.calculate_agent_kpi(sample_agent)
        
        assert 'overall_kpi' in scores
        assert 'performance_rating' in scores
        assert isinstance(scores['overall_kpi'], (int, float))
        
        print(f"✅ KPI Calculator working - Sample KPI: {scores['overall_kpi']}")
        print(f"   Performance Rating: {scores['performance_rating']}")
        return True
        
    except Exception as e:
        print(f"❌ KPI Calculator error: {e}")
        return False

def test_file_handler():
    """Test file handler with sample data"""
    print("\nTesting File Handler...")
    try:
        from file_handler import FileHandler
        
        handler = FileHandler()
        
        # Create sample data
        sample_data = pd.DataFrame({
            'agent_id': ['A001', 'A002'],
            'agent_name': ['Test Agent 1', 'Test Agent 2'],
            'customer_satisfaction': [4.2, 4.5],
            'response_time': [8, 10]
        })
        
        # Test saving and loading CSV
        test_file = "test_data.csv"
        saved_path = handler.save_csv(sample_data, test_file)
        loaded_data = handler.read_csv(saved_path)
        
        assert len(loaded_data) == len(sample_data)
        assert list(loaded_data.columns) == list(sample_data.columns)
        
        # Clean up
        Path(saved_path).unlink(missing_ok=True)
        
        print("✅ File Handler working correctly")
        return True
        
    except Exception as e:
        print(f"❌ File Handler error: {e}")
        return False

def test_bot_initialization():
    """Test bot initialization"""
    print("\nTesting Bot Initialization...")
    try:
        from main import KPIBot
        
        # Test without Google Sheets (to avoid credential issues)
        bot = KPIBot(use_sheets=False)
        
        assert bot.file_handler is not None
        assert bot.kpi_calculator is not None
        
        print("✅ Bot initialization successful (without Google Sheets)")
        
        # Try with Google Sheets (will fail gracefully if no credentials)
        try:
            bot_with_sheets = KPIBot(use_sheets=True)
            if bot_with_sheets.sheets_client:
                print("✅ Google Sheets client initialized successfully")
            else:
                print("ℹ️  Google Sheets client not available (credentials not found)")
        except:
            print("ℹ️  Google Sheets client not available (credentials not found)")
        
        return True
        
    except Exception as e:
        print(f"❌ Bot initialization error: {e}")
        return False

def test_full_workflow():
    """Test complete workflow with sample data"""
    print("\nTesting Full Workflow...")
    try:
        from main import KPIBot
        
        bot = KPIBot(use_sheets=False)
        
        # Create sample KPI data
        sample_kpi_data = pd.DataFrame({
            'agent_id': ['A001', 'A002', 'A003'],
            'agent_name': ['Alice Johnson', 'Bob Smith', 'Carol Brown'],
            'customer_satisfaction': [4.2, 4.7, 3.8],
            'response_time': [8, 5, 15],
            'resolution_time': [3, 2, 5],
            'first_contact_resolution': [0.78, 0.85, 0.65],
            'quality_score': [0.88, 0.92, 0.75]
        })
        
        # Process KPIs
        results = bot.process_kpi_batch(sample_kpi_data)
        
        assert len(results) == 3
        assert 'overall_kpi' in results.columns
        assert 'performance_rating' in results.columns
        
        print("✅ Full workflow test successful")
        print(f"   Processed {len(results)} agents")
        print(f"   Average KPI: {results['overall_kpi'].mean():.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Full workflow error: {e}")
        return False

def main():
    """Run all tests"""
    print("KPI Calculator Bot - Test Suite")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_kpi_calculator,
        test_file_handler,
        test_bot_initialization,
        test_full_workflow
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 40)
    print("TEST SUMMARY")
    print("=" * 40)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The KPI Calculator Bot is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())