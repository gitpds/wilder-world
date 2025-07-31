#!/usr/bin/env python3
"""
Run Operation Titan Analysis
Main script to execute the complete WILD token analysis and generate HTML dashboard
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from titan_tracker import TitanTracker
from analysis_functions import WilderAnalyzer
from titan_dashboard import TitanDashboard
from price_fetcher import PriceFetcher

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_existing_data():
    """Load existing analysis data if available"""
    try:
        # Try to load existing WILD token analysis
        data_file = Path(__file__).parent / 'data' / 'processed' / 'all_wallet_data.json'
        if data_file.exists():
            with open(data_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load existing data: {e}")
    return None

def run_titan_analysis():
    """Run the complete Operation Titan analysis"""
    logger.info("Starting Operation Titan Analysis...")
    
    # Initialize components
    tracker = TitanTracker()
    analyzer = WilderAnalyzer()
    dashboard = TitanDashboard()
    price_fetcher = PriceFetcher()
    
    # Step 1: Collect Titan-specific data
    logger.info("Collecting Operation Titan data...")
    titan_data = tracker.generate_summary_report()
    
    # Step 2: Get current prices
    logger.info("Fetching current prices...")
    try:
        current_prices = price_fetcher.get_current_prices()
        if current_prices and 'WILD' in current_prices:
            # Update price in analysis
            titan_data['current_wild_price'] = current_prices['WILD']
            logger.info(f"Current WILD price: ${current_prices['WILD']:.4f}")
    except Exception as e:
        logger.warning(f"Could not fetch current prices: {e}")
        titan_data['current_wild_price'] = 0.38  # Fallback price
    
    # Step 3: Load existing wallet data if available
    existing_data = load_existing_data()
    if existing_data:
        logger.info("Using existing wallet analysis data")
        # Extract WILD balances from existing data
        wild_balances = existing_data.get('wild_analysis', {})
        portfolio_exposure = {
            'total_wild_holdings': wild_balances.get('total_balance', 0),
            'wild_by_wallet': wild_balances.get('balances_by_wallet', {}),
            'lp_exposure': existing_data.get('lp_analysis', {}).get('total_lp_tokens', 0) * 0.5,  # 50% of LP is WILD
            'total_exposure_wild': 0
        }
        portfolio_exposure['total_exposure_wild'] = (
            portfolio_exposure['total_wild_holdings'] + 
            portfolio_exposure['lp_exposure']
        )
    else:
        logger.warning("No existing wallet data found, using placeholder values")
        portfolio_exposure = analyzer.calculate_portfolio_exposure()
    
    # Step 4: Run Titan impact analysis
    logger.info("Analyzing Operation Titan impact...")
    titan_impact = analyzer.analyze_titan_impact(titan_data)
    
    # Update with actual portfolio data if available
    if existing_data:
        titan_impact['portfolio_exposure'] = portfolio_exposure
    
    # Step 5: Generate trading signals
    trading_signals = analyzer.generate_titan_trading_signals(titan_data)
    titan_impact['trading_signals'] = trading_signals
    
    # Step 6: Update price targets with current price
    price_targets = titan_impact.get('price_targets', {})
    price_targets['current_price'] = titan_data.get('current_wild_price', 0.38)
    
    # Recalculate targets based on current price
    current_price = price_targets['current_price']
    price_impact_pct = titan_data.get('price_impact', {}).get('combined_impact_estimate', 0)
    
    price_targets.update({
        'conservative': current_price * (1 + price_impact_pct / 100 * 0.5),
        'base_case': current_price * (1 + price_impact_pct / 100),
        'optimistic': current_price * (1 + price_impact_pct / 100 * 1.5),
        '1_year_target': current_price * (1 + titan_impact.get('buyback_impact', {}).get('deflationary_rate', 0) / 100)
    })
    
    # Step 7: Generate HTML dashboard
    logger.info("Generating HTML dashboard...")
    dashboard_path = dashboard.generate_dashboard(titan_data, titan_impact)
    
    # Step 8: Save analysis data
    output_dir = Path(__file__).parent / 'output' / 'titan_reports'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save raw data
    data_file = output_dir / f'titan_analysis_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(data_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'titan_data': titan_data,
            'titan_impact': titan_impact,
            'current_prices': current_prices if 'current_prices' in locals() else {}
        }, f, indent=2, default=str)
    
    # Also save latest version
    latest_data = output_dir / 'titan_analysis_data_latest.json'
    with open(latest_data, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'titan_data': titan_data,
            'titan_impact': titan_impact,
            'current_prices': current_prices if 'current_prices' in locals() else {}
        }, f, indent=2, default=str)
    
    logger.info(f"Analysis complete! Dashboard saved to: {dashboard_path}")
    
    # Print summary
    print("\n" + "="*60)
    print("OPERATION TITAN ANALYSIS SUMMARY")
    print("="*60)
    print(f"Current Phase: {titan_data['phase_status']['current_phase']}")
    print(f"Days Since Phase 2: {titan_data['phase_status']['days_since_phase2_greenlit']}")
    print(f"Current WILD Price: ${titan_data.get('current_wild_price', 0.38):.4f}")
    print(f"\nPrice Targets:")
    print(f"  Conservative: ${price_targets['conservative']:.4f}")
    print(f"  Base Case: ${price_targets['base_case']:.4f}")
    print(f"  Optimistic: ${price_targets['optimistic']:.4f}")
    print(f"  1 Year: ${price_targets['1_year_target']:.4f}")
    print(f"\nTrading Signal: {trading_signals['action'].upper()} ({trading_signals['overall_sentiment']})")
    print(f"Confidence: {trading_signals['confidence']}")
    print("\nKey Findings:")
    for reason in trading_signals['rationale'][:3]:
        print(f"  • {reason}")
    print("="*60)
    
    return dashboard_path

if __name__ == "__main__":
    try:
        dashboard_path = run_titan_analysis()
        print(f"\nOpen the dashboard in your browser:")
        print(f"file://{os.path.abspath(dashboard_path)}")
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise