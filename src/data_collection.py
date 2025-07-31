"""
Data collection module for Wilder World Ethereum analysis.
Handles fetching transaction data from Etherscan API with rate limiting.
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from etherscan import Etherscan
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(Path(__file__).parent.parent / 'config' / '.env')

class WilderDataCollector:
    """Collects Ethereum blockchain data for Wilder World analysis."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize the data collector with API credentials and cache directory."""
        self.api_key = os.getenv('ETHERSCAN_API_KEY')
        if not self.api_key:
            raise ValueError("ETHERSCAN_API_KEY not found in environment variables")
        
        self.eth = Etherscan(self.api_key)
        self.rate_limit = int(os.getenv('ETHERSCAN_RATE_LIMIT', 5))
        self.last_request_time = 0
        
        # Set up cache directory
        if cache_dir is None:
            cache_dir = Path(__file__).parent.parent / 'data' / 'raw'
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load wallet addresses
        self.wallets = {
            'hot': os.getenv('HOT_WALLET_ADDRESS'),
            'digital_re': os.getenv('DIGITAL_RE_ADDRESS'),
            'eth_stake': os.getenv('ETH_STAKE_ADDRESS'),
            'warm': os.getenv('WARM_WALLET_ADDRESS')
        }
        
        # Load contract addresses
        self.contracts = {
            'wild_token': os.getenv('WILD_TOKEN_CONTRACT'),
            'uniswap_lp': os.getenv('UNISWAP_V2_WILD_ETH_LP'),
            'airwild_s0': os.getenv('AIRWILD_S0_CONTRACT'),
            'airwild_s1': os.getenv('AIRWILD_S1_CONTRACT'),
            'airwild_s2': os.getenv('AIRWILD_S2_CONTRACT'),
            'wheels': os.getenv('WHEELS_CONTRACT'),
            'cribs': os.getenv('CRIBS_CONTRACT'),
            'crafts': os.getenv('CRAFTS_CONTRACT'),
            'land': os.getenv('LAND_CONTRACT'),
            'beasts_wolves': os.getenv('BEASTS_WOLVES_CONTRACT'),
            'beasts_wapes': os.getenv('BEASTS_WAPES_CONTRACT'),
            'moto': os.getenv('MOTO_CONTRACT'),
            'pals_gens': os.getenv('PALS_GENS_CONTRACT')
        }
        
    def _rate_limit_wait(self):
        """Implement rate limiting for API calls."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 1.0 / self.rate_limit
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _cache_response(self, filename: str, data: Any) -> None:
        """Cache API response to file."""
        cache_path = self.cache_dir / filename
        with open(cache_path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Cached response to {cache_path}")
    
    def _load_cache(self, filename: str) -> Optional[Any]:
        """Load cached response if it exists."""
        cache_path = self.cache_dir / filename
        if cache_path.exists():
            with open(cache_path, 'r') as f:
                logger.info(f"Loading cached response from {cache_path}")
                return json.load(f)
        return None
    
    def fetch_normal_transactions(self, wallet_name: str, force_refresh: bool = False) -> List[Dict]:
        """Fetch normal ETH transactions for a wallet."""
        wallet_address = self.wallets[wallet_name]
        cache_filename = f"normal_txns_{wallet_name}.json"
        
        if not force_refresh:
            cached_data = self._load_cache(cache_filename)
            if cached_data:
                return cached_data
        
        logger.info(f"Fetching normal transactions for {wallet_name} wallet: {wallet_address}")
        self._rate_limit_wait()
        
        try:
            transactions = self.eth.get_normal_txs_by_address(
                address=wallet_address,
                startblock=0,
                endblock=99999999,
                sort='asc'
            )
            self._cache_response(cache_filename, transactions)
            return transactions
        except Exception as e:
            logger.error(f"Error fetching normal transactions: {e}")
            return []
    
    def fetch_token_transactions(self, wallet_name: str, contract_address: Optional[str] = None, 
                               force_refresh: bool = False) -> List[Dict]:
        """Fetch ERC20 token transactions for a wallet."""
        wallet_address = self.wallets[wallet_name]
        
        if contract_address:
            cache_filename = f"token_txns_{wallet_name}_{contract_address[:8]}.json"
        else:
            cache_filename = f"token_txns_{wallet_name}_all.json"
        
        if not force_refresh:
            cached_data = self._load_cache(cache_filename)
            if cached_data:
                return cached_data
        
        logger.info(f"Fetching token transactions for {wallet_name} wallet: {wallet_address}")
        self._rate_limit_wait()
        
        try:
            if contract_address:
                transactions = self.eth.get_erc20_token_transfer_events_by_address(
                    address=wallet_address,
                    contractaddress=contract_address,
                    startblock=0,
                    endblock=99999999,
                    sort='asc'
                )
            else:
                transactions = self.eth.get_erc20_token_transfer_events_by_address(
                    address=wallet_address,
                    startblock=0,
                    endblock=99999999,
                    sort='asc'
                )
            
            self._cache_response(cache_filename, transactions)
            return transactions
        except Exception as e:
            logger.error(f"Error fetching token transactions: {e}")
            return []
    
    def fetch_nft_transactions(self, wallet_name: str, contract_address: Optional[str] = None,
                              force_refresh: bool = False) -> List[Dict]:
        """Fetch ERC721 NFT transactions for a wallet."""
        wallet_address = self.wallets[wallet_name]
        
        if contract_address:
            cache_filename = f"nft_txns_{wallet_name}_{contract_address[:8]}.json"
        else:
            cache_filename = f"nft_txns_{wallet_name}_all.json"
        
        if not force_refresh:
            cached_data = self._load_cache(cache_filename)
            if cached_data:
                return cached_data
        
        logger.info(f"Fetching NFT transactions for {wallet_name} wallet: {wallet_address}")
        self._rate_limit_wait()
        
        try:
            if contract_address:
                transactions = self.eth.get_erc721_token_transfer_events_by_address(
                    address=wallet_address,
                    contractaddress=contract_address,
                    startblock=0,
                    endblock=99999999,
                    sort='asc'
                )
            else:
                transactions = self.eth.get_erc721_token_transfer_events_by_address(
                    address=wallet_address,
                    startblock=0,
                    endblock=99999999,
                    sort='asc'
                )
            
            self._cache_response(cache_filename, transactions)
            return transactions
        except Exception as e:
            logger.error(f"Error fetching NFT transactions: {e}")
            return []
    
    def fetch_internal_transactions(self, wallet_name: str, force_refresh: bool = False) -> List[Dict]:
        """Fetch internal transactions for a wallet."""
        wallet_address = self.wallets[wallet_name]
        cache_filename = f"internal_txns_{wallet_name}.json"
        
        if not force_refresh:
            cached_data = self._load_cache(cache_filename)
            if cached_data:
                return cached_data
        
        logger.info(f"Fetching internal transactions for {wallet_name} wallet: {wallet_address}")
        self._rate_limit_wait()
        
        try:
            transactions = self.eth.get_internal_txs_by_address(
                address=wallet_address,
                startblock=0,
                endblock=99999999,
                sort='asc'
            )
            self._cache_response(cache_filename, transactions)
            return transactions
        except Exception as e:
            logger.error(f"Error fetching internal transactions: {e}")
            return []
    
    def collect_all_wallet_data(self, force_refresh: bool = False) -> Dict[str, Dict]:
        """Collect all transaction data for all wallets."""
        all_data = {}
        
        for wallet_name in self.wallets:
            logger.info(f"\n{'='*60}")
            logger.info(f"Collecting data for {wallet_name.upper()} wallet")
            logger.info(f"{'='*60}")
            
            wallet_data = {
                'normal_txns': self.fetch_normal_transactions(wallet_name, force_refresh),
                'token_txns': {},
                'nft_txns': {},
                'internal_txns': self.fetch_internal_transactions(wallet_name, force_refresh)
            }
            
            # Fetch WILD token transactions
            wild_txns = self.fetch_token_transactions(
                wallet_name, 
                self.contracts['wild_token'], 
                force_refresh
            )
            if wild_txns:
                wallet_data['token_txns']['wild'] = wild_txns
            
            # Fetch Uniswap LP token transactions
            lp_txns = self.fetch_token_transactions(
                wallet_name,
                self.contracts['uniswap_lp'],
                force_refresh
            )
            if lp_txns:
                wallet_data['token_txns']['uniswap_lp'] = lp_txns
            
            # Fetch all token transactions (to catch any we might have missed)
            all_token_txns = self.fetch_token_transactions(wallet_name, None, force_refresh)
            wallet_data['token_txns']['all'] = all_token_txns
            
            # Fetch NFT transactions for each collection
            nft_collections = [
                'airwild_s0', 'airwild_s1', 'airwild_s2', 'wheels', 'cribs',
                'crafts', 'land', 'beasts_wolves', 'beasts_wapes', 'moto', 'pals_gens'
            ]
            
            for collection in nft_collections:
                if self.contracts[collection]:
                    nft_txns = self.fetch_nft_transactions(
                        wallet_name,
                        self.contracts[collection],
                        force_refresh
                    )
                    if nft_txns:
                        wallet_data['nft_txns'][collection] = nft_txns
            
            # Also fetch all NFT transactions
            all_nft_txns = self.fetch_nft_transactions(wallet_name, None, force_refresh)
            wallet_data['nft_txns']['all'] = all_nft_txns
            
            all_data[wallet_name] = wallet_data
            
            # Summary statistics
            logger.info(f"\nSummary for {wallet_name} wallet:")
            logger.info(f"  Normal transactions: {len(wallet_data['normal_txns'])}")
            logger.info(f"  WILD token transactions: {len(wallet_data['token_txns'].get('wild', []))}")
            logger.info(f"  All token transactions: {len(wallet_data['token_txns'].get('all', []))}")
            logger.info(f"  NFT collections with activity: {sum(1 for v in wallet_data['nft_txns'].values() if v and len(v) > 0)}")
            logger.info(f"  Internal transactions: {len(wallet_data['internal_txns'])}")
        
        return all_data
    
    def save_consolidated_data(self, data: Dict[str, Dict], filename: str = 'all_wallet_data.json') -> None:
        """Save all collected data to a single JSON file."""
        output_path = self.cache_dir.parent / 'processed' / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved consolidated data to {output_path}")


if __name__ == "__main__":
    # Test the data collector
    collector = WilderDataCollector()
    
    # Collect all data
    all_data = collector.collect_all_wallet_data(force_refresh=False)
    
    # Save consolidated data
    collector.save_consolidated_data(all_data)
    
    logger.info("\nData collection complete!")