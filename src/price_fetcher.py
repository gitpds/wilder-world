"""
Price fetching module for historical cryptocurrency prices.
Uses CoinGecko API to get ETH and WILD token prices.
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

from pycoingecko import CoinGeckoAPI
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(Path(__file__).parent.parent / 'config' / '.env')

class PriceFetcher:
    """Fetches and caches historical cryptocurrency prices."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize the price fetcher with CoinGecko API."""
        self.cg = CoinGeckoAPI()
        
        # Set up cache directory
        if cache_dir is None:
            cache_dir = Path(__file__).parent.parent / 'data' / 'cache'
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing cache
        self.price_cache = self._load_price_cache()
        
        # Coin IDs for CoinGecko
        self.coin_ids = {
            'ETH': 'ethereum',
            'WILD': 'wilder-world'
        }
        
        # Rate limiting (CoinGecko free tier: 10-50 calls/minute)
        self.last_request_time = 0
        self.min_request_interval = 0.5  # 2 requests per second
    
    def _rate_limit_wait(self):
        """Implement rate limiting for API calls."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _load_price_cache(self) -> Dict[str, Dict[str, float]]:
        """Load price cache from file."""
        cache_file = self.cache_dir / 'price_cache.json'
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                logger.info(f"Loading price cache from {cache_file}")
                return json.load(f)
        return defaultdict(dict)
    
    def _save_price_cache(self):
        """Save price cache to file."""
        cache_file = self.cache_dir / 'price_cache.json'
        with open(cache_file, 'w') as f:
            json.dump(dict(self.price_cache), f, indent=2)
        logger.debug(f"Saved price cache to {cache_file}")
    
    def _get_cache_key(self, coin: str, date: str) -> str:
        """Generate cache key for a specific coin and date."""
        return f"{coin}_{date}"
    
    def get_historical_price(self, coin: str, date: str) -> Optional[float]:
        """
        Get historical price for a coin on a specific date.
        
        Args:
            coin: Coin symbol (ETH, WILD)
            date: Date in format YYYY-MM-DD
        
        Returns:
            Price in USD or None if not available
        """
        cache_key = self._get_cache_key(coin, date)
        
        # Check cache first
        if cache_key in self.price_cache:
            logger.debug(f"Using cached price for {coin} on {date}")
            return self.price_cache[cache_key]
        
        # Fetch from API
        if coin not in self.coin_ids:
            logger.error(f"Unknown coin: {coin}")
            return None
        
        coin_id = self.coin_ids[coin]
        
        try:
            # Convert date to DD-MM-YYYY format for CoinGecko
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            cg_date = date_obj.strftime('%d-%m-%Y')
            
            logger.info(f"Fetching {coin} price for {date}")
            self._rate_limit_wait()
            
            # Get historical data
            history = self.cg.get_coin_history_by_id(
                id=coin_id,
                date=cg_date,
                localization='false'
            )
            
            if 'market_data' in history and 'current_price' in history['market_data']:
                price = history['market_data']['current_price'].get('usd')
                if price:
                    self.price_cache[cache_key] = price
                    self._save_price_cache()
                    return price
            
            logger.warning(f"No price data available for {coin} on {date}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching price for {coin} on {date}: {e}")
            return None
    
    def get_price_at_timestamp(self, coin: str, timestamp: int) -> Optional[float]:
        """
        Get historical price for a coin at a specific timestamp.
        
        Args:
            coin: Coin symbol (ETH, WILD)
            timestamp: Unix timestamp
        
        Returns:
            Price in USD or None if not available
        """
        # Convert timestamp to date
        date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
        return self.get_historical_price(coin, date)
    
    def get_price_range(self, coin: str, start_date: str, end_date: str) -> Dict[str, float]:
        """
        Get historical prices for a range of dates.
        
        Args:
            coin: Coin symbol (ETH, WILD)
            start_date: Start date in format YYYY-MM-DD
            end_date: End date in format YYYY-MM-DD
        
        Returns:
            Dictionary mapping dates to prices
        """
        prices = {}
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        current = start
        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            price = self.get_historical_price(coin, date_str)
            if price:
                prices[date_str] = price
            current += timedelta(days=1)
        
        return prices
    
    def get_current_prices(self) -> Dict[str, float]:
        """Get current prices for all tracked coins."""
        prices = {}
        
        try:
            logger.info("Fetching current prices")
            self._rate_limit_wait()
            
            # Get prices for multiple coins in one call
            coin_ids_list = list(self.coin_ids.values())
            price_data = self.cg.get_price(
                ids=coin_ids_list,
                vs_currencies='usd'
            )
            
            # Map back to coin symbols
            for symbol, coin_id in self.coin_ids.items():
                if coin_id in price_data and 'usd' in price_data[coin_id]:
                    prices[symbol] = price_data[coin_id]['usd']
            
            logger.info(f"Current prices: {prices}")
            return prices
            
        except Exception as e:
            logger.error(f"Error fetching current prices: {e}")
            return {}
    
    def estimate_gas_price_in_usd(self, gas_used: int, gas_price_gwei: int, timestamp: int) -> Optional[float]:
        """
        Estimate the USD cost of gas for a transaction.
        
        Args:
            gas_used: Amount of gas used
            gas_price_gwei: Gas price in Gwei
            timestamp: Transaction timestamp
        
        Returns:
            Gas cost in USD or None if price not available
        """
        # Convert gas price from Gwei to ETH
        gas_cost_eth = (gas_used * gas_price_gwei) / 1e9
        
        # Get ETH price at timestamp
        eth_price = self.get_price_at_timestamp('ETH', timestamp)
        
        if eth_price:
            return gas_cost_eth * eth_price
        return None
    
    def fill_missing_prices(self, dates_needed: List[str], coin: str = 'ETH') -> Dict[str, float]:
        """
        Fill in missing prices for a list of dates.
        
        Args:
            dates_needed: List of dates in YYYY-MM-DD format
            coin: Coin symbol
        
        Returns:
            Dictionary mapping dates to prices
        """
        prices = {}
        
        for date in dates_needed:
            price = self.get_historical_price(coin, date)
            if price:
                prices[date] = price
            else:
                # Try to get price from nearby dates
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                for offset in [1, -1, 2, -2, 3, -3]:
                    nearby_date = (date_obj + timedelta(days=offset)).strftime('%Y-%m-%d')
                    price = self.get_historical_price(coin, nearby_date)
                    if price:
                        logger.warning(f"Using price from {nearby_date} for {date}")
                        prices[date] = price
                        break
        
        return prices


def test_price_fetcher():
    """Test the price fetcher functionality."""
    fetcher = PriceFetcher()
    
    # Test current prices
    current_prices = fetcher.get_current_prices()
    print(f"Current prices: {current_prices}")
    
    # Test historical price
    test_date = '2024-01-01'
    eth_price = fetcher.get_historical_price('ETH', test_date)
    wild_price = fetcher.get_historical_price('WILD', test_date)
    print(f"\nPrices on {test_date}:")
    print(f"  ETH: ${eth_price}")
    print(f"  WILD: ${wild_price}")
    
    # Test gas price estimation
    gas_used = 21000  # Basic transfer
    gas_price_gwei = 30
    timestamp = int(datetime.strptime(test_date, '%Y-%m-%d').timestamp())
    gas_cost_usd = fetcher.estimate_gas_price_in_usd(gas_used, gas_price_gwei, timestamp)
    print(f"\nGas cost for basic transfer on {test_date}: ${gas_cost_usd:.2f}")


if __name__ == "__main__":
    test_price_fetcher()