#!/usr/bin/env python3
"""
Test script to verify the Wilder World analysis setup.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from data_collection import WilderDataCollector
        print("✓ data_collection module imported successfully")
        
        from price_fetcher import PriceFetcher
        print("✓ price_fetcher module imported successfully")
        
        from analysis_functions import WilderAnalyzer
        print("✓ analysis_functions module imported successfully")
        
        from visualization import WilderVisualizer
        print("✓ visualization module imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_environment():
    """Test that environment variables are loaded."""
    print("\nTesting environment variables...")
    from dotenv import load_dotenv
    load_dotenv('config/.env')
    
    required_vars = [
        'ETHERSCAN_API_KEY',
        'HOT_WALLET_ADDRESS',
        'DIGITAL_RE_ADDRESS',
        'ETH_STAKE_ADDRESS',
        'WARM_WALLET_ADDRESS',
        'WILD_TOKEN_CONTRACT'
    ]
    
    all_good = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: [CONFIGURED]")
        else:
            print(f"✗ {var}: Not found")
            all_good = False
    
    return all_good

def test_directories():
    """Test that all required directories exist."""
    print("\nTesting directory structure...")
    
    dirs = [
        'config',
        'data/raw',
        'data/processed',
        'data/cache',
        'src',
        'output/reports',
        'output/visualizations'
    ]
    
    all_good = True
    for dir_path in dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✓ {dir_path} exists")
        else:
            print(f"✗ {dir_path} missing")
            all_good = False
    
    return all_good

def test_basic_functionality():
    """Test basic functionality of the modules."""
    print("\nTesting basic functionality...")
    
    try:
        from price_fetcher import PriceFetcher
        fetcher = PriceFetcher()
        print("✓ PriceFetcher initialized successfully")
        
        # Test getting current prices
        prices = fetcher.get_current_prices()
        if prices and 'ETH' in prices:
            print(f"✓ Current ETH price: ${prices['ETH']:,.2f}")
        else:
            print("✗ Failed to fetch current prices")
        
        return True
    except Exception as e:
        print(f"✗ Functionality test error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Wilder World Analysis Setup Test")
    print("=" * 60)
    
    tests = [
        test_imports(),
        test_environment(),
        test_directories(),
        test_basic_functionality()
    ]
    
    if all(tests):
        print("\n✅ All tests passed! The setup is ready.")
        print("\nYou can now:")
        print("1. Run the Jupyter notebook: jupyter notebook wilder_world_analysis.ipynb")
        print("2. Or run data collection: python src/data_collection.py")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()