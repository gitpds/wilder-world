"""
Analysis functions for Wilder World Ethereum data.
Processes transaction data to extract insights and calculate metrics.
"""

import os
import logging
from typing import Dict, List, Optional, Tuple, Set, Any
from datetime import datetime
from collections import defaultdict
import pandas as pd
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

class WilderAnalyzer:
    """Analyzes Wilder World transaction data."""
    
    def __init__(self):
        """Initialize the analyzer with wallet and contract addresses."""
        # Load wallet addresses
        self.wallets = {
            'hot': os.getenv('HOT_WALLET_ADDRESS').lower(),
            'digital_re': os.getenv('DIGITAL_RE_ADDRESS').lower(),
            'eth_stake': os.getenv('ETH_STAKE_ADDRESS').lower(),
            'warm': os.getenv('WARM_WALLET_ADDRESS').lower()
        }
        
        # Reverse mapping for wallet identification
        self.address_to_wallet = {v: k for k, v in self.wallets.items()}
        
        # Load contract addresses
        self.contracts = {
            'wild_token': os.getenv('WILD_TOKEN_CONTRACT').lower(),
            'uniswap_lp': os.getenv('UNISWAP_V2_WILD_ETH_LP').lower(),
            'airwild_s0': os.getenv('AIRWILD_S0_CONTRACT').lower(),
            'airwild_s1': os.getenv('AIRWILD_S1_CONTRACT').lower(),
            'airwild_s2': os.getenv('AIRWILD_S2_CONTRACT').lower(),
            'wheels': os.getenv('WHEELS_CONTRACT').lower(),
            'cribs': os.getenv('CRIBS_CONTRACT').lower(),
            'crafts': os.getenv('CRAFTS_CONTRACT').lower(),
            'land': os.getenv('LAND_CONTRACT').lower(),
            'beasts_wolves': os.getenv('BEASTS_WOLVES_CONTRACT').lower(),
            'beasts_wapes': os.getenv('BEASTS_WAPES_CONTRACT').lower(),
            'moto': os.getenv('MOTO_CONTRACT').lower(),
            'pals_gens': os.getenv('PALS_GENS_CONTRACT').lower()
        }
        
        # Reverse mapping for contract identification
        self.address_to_contract = {v: k for k, v in self.contracts.items()}
    
    def is_inter_wallet_transfer(self, from_addr: str, to_addr: str) -> bool:
        """Check if a transfer is between owned wallets."""
        from_lower = from_addr.lower()
        to_lower = to_addr.lower()
        return from_lower in self.wallets.values() and to_lower in self.wallets.values()
    
    def process_normal_transactions(self, transactions: List[Dict]) -> pd.DataFrame:
        """Process normal ETH transactions into a DataFrame."""
        if not transactions:
            return pd.DataFrame()
        
        df = pd.DataFrame(transactions)
        
        # Convert numeric fields
        numeric_fields = ['value', 'gas', 'gasPrice', 'gasUsed', 'blockNumber', 'timeStamp']
        for field in numeric_fields:
            if field in df.columns:
                df[field] = pd.to_numeric(df[field], errors='coerce')
        
        # Convert value from Wei to ETH
        df['value_eth'] = df['value'] / 1e18
        
        # Calculate gas cost in ETH
        df['gas_cost_eth'] = (df['gasUsed'] * df['gasPrice']) / 1e18
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timeStamp'], unit='s')
        df['date'] = df['timestamp'].dt.date
        
        # Add transaction direction
        df['from_lower'] = df['from'].str.lower()
        df['to_lower'] = df['to'].str.lower()
        
        # Identify inter-wallet transfers
        df['is_inter_wallet'] = df.apply(
            lambda x: self.is_inter_wallet_transfer(x['from'], x['to']), axis=1
        )
        
        return df
    
    def process_token_transactions(self, transactions: List[Dict], token_type: str = 'ERC20') -> pd.DataFrame:
        """Process token transactions into a DataFrame."""
        if not transactions:
            return pd.DataFrame()
        
        df = pd.DataFrame(transactions)
        
        # Convert numeric fields
        numeric_fields = ['value', 'gas', 'gasPrice', 'gasUsed', 'blockNumber', 'timeStamp']
        for field in numeric_fields:
            if field in df.columns:
                df[field] = pd.to_numeric(df[field], errors='coerce')
        
        # Handle token decimals
        if 'tokenDecimal' in df.columns:
            df['tokenDecimal'] = pd.to_numeric(df['tokenDecimal'], errors='coerce').fillna(18)
        else:
            df['tokenDecimal'] = 18
        
        # Convert value based on token decimals
        if 'value' in df.columns:
            df['value_token'] = df.apply(
                lambda x: x['value'] / (10 ** x['tokenDecimal']) if pd.notna(x['value']) else 0, axis=1
            )
        else:
            # For NFT transactions, set value_token to 1 (since it's 1 NFT)
            df['value_token'] = 1
        
        # Calculate gas cost in ETH
        if 'gasUsed' in df.columns and 'gasPrice' in df.columns:
            df['gas_cost_eth'] = (df['gasUsed'] * df['gasPrice']) / 1e18
        else:
            df['gas_cost_eth'] = 0
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timeStamp'], unit='s')
        df['date'] = df['timestamp'].dt.date
        
        # Add transaction direction
        df['from_lower'] = df['from'].str.lower()
        df['to_lower'] = df['to'].str.lower()
        
        # Identify contract type
        df['contract_lower'] = df['contractAddress'].str.lower()
        df['contract_type'] = df['contract_lower'].map(self.address_to_contract)
        
        # Identify inter-wallet transfers
        df['is_inter_wallet'] = df.apply(
            lambda x: self.is_inter_wallet_transfer(x['from'], x['to']), axis=1
        )
        
        return df
    
    def analyze_wild_token_holdings(self, all_data: Dict) -> Dict[str, Dict]:
        """Analyze WILD token holdings and transactions for all wallets."""
        results = {}
        
        for wallet_name, wallet_data in all_data.items():
            wallet_address = self.wallets[wallet_name]
            
            # Get WILD token transactions
            wild_txns = wallet_data.get('token_txns', {}).get('wild', [])
            if not wild_txns:
                # Try to find WILD transactions in all token transactions
                all_token_txns = wallet_data.get('token_txns', {}).get('all', [])
                wild_txns = [tx for tx in all_token_txns 
                           if tx.get('contractAddress', '').lower() == self.contracts['wild_token']]
            
            if not wild_txns:
                results[wallet_name] = {
                    'current_balance': 0,
                    'total_received': 0,
                    'total_sent': 0,
                    'net_flow': 0,
                    'transaction_count': 0,
                    'avg_purchase_price': 0,
                    'transactions': pd.DataFrame()
                }
                continue
            
            # Process transactions
            df = self.process_token_transactions(wild_txns)
            
            # Calculate flows
            received = df[df['to_lower'] == wallet_address]['value_token'].sum()
            sent = df[df['from_lower'] == wallet_address]['value_token'].sum()
            
            # Exclude inter-wallet transfers from net calculations
            external_received = df[(df['to_lower'] == wallet_address) & (~df['is_inter_wallet'])]['value_token'].sum()
            external_sent = df[(df['from_lower'] == wallet_address) & (~df['is_inter_wallet'])]['value_token'].sum()
            
            results[wallet_name] = {
                'current_balance': received - sent,
                'total_received': received,
                'total_sent': sent,
                'external_received': external_received,
                'external_sent': external_sent,
                'net_flow': external_received - external_sent,
                'transaction_count': len(df),
                'inter_wallet_transfers': df['is_inter_wallet'].sum(),
                'transactions': df
            }
        
        return results
    
    def analyze_nft_holdings(self, all_data: Dict) -> Dict[str, Dict]:
        """Analyze NFT holdings and transactions for all wallets."""
        results = {}
        
        for wallet_name, wallet_data in all_data.items():
            wallet_address = self.wallets[wallet_name]
            wallet_results = {}
            
            # Process each NFT collection
            nft_data = wallet_data.get('nft_txns', {})
            
            for collection_name, collection_address in self.contracts.items():
                if not collection_name.endswith('_token') and not collection_name == 'uniswap_lp':
                    # Get transactions for this collection
                    collection_txns = nft_data.get(collection_name, [])
                    
                    if not collection_txns:
                        # Try to find in all NFT transactions
                        all_nft_txns = nft_data.get('all', [])
                        collection_txns = [tx for tx in all_nft_txns 
                                         if tx.get('contractAddress', '').lower() == collection_address]
                    
                    if not collection_txns:
                        continue
                    
                    # Process transactions
                    df = self.process_token_transactions(collection_txns, 'ERC721')
                    
                    # Track token IDs
                    received_tokens = set(df[df['to_lower'] == wallet_address]['tokenID'].unique())
                    sent_tokens = set(df[df['from_lower'] == wallet_address]['tokenID'].unique())
                    current_tokens = received_tokens - sent_tokens
                    
                    # Calculate gas costs
                    gas_costs = df[df['to_lower'] == wallet_address]['gas_cost_eth'].sum()
                    
                    wallet_results[collection_name] = {
                        'current_holdings': len(current_tokens),
                        'token_ids': sorted(list(current_tokens)),
                        'total_received': len(received_tokens),
                        'total_sent': len(sent_tokens),
                        'gas_cost_eth': gas_costs,
                        'transaction_count': len(df),
                        'transactions': df
                    }
            
            results[wallet_name] = wallet_results
        
        return results
    
    def analyze_lp_positions(self, all_data: Dict) -> Dict[str, Dict]:
        """Analyze Uniswap LP token positions for all wallets."""
        results = {}
        
        for wallet_name, wallet_data in all_data.items():
            wallet_address = self.wallets[wallet_name]
            
            # Get LP token transactions
            lp_txns = wallet_data.get('token_txns', {}).get('uniswap_lp', [])
            if not lp_txns:
                # Try to find LP transactions in all token transactions
                all_token_txns = wallet_data.get('token_txns', {}).get('all', [])
                lp_txns = [tx for tx in all_token_txns 
                         if tx.get('contractAddress', '').lower() == self.contracts['uniswap_lp']]
            
            if not lp_txns:
                results[wallet_name] = {
                    'current_balance': 0,
                    'total_minted': 0,
                    'total_burned': 0,
                    'net_position': 0,
                    'transaction_count': 0,
                    'transactions': pd.DataFrame()
                }
                continue
            
            # Process transactions
            df = self.process_token_transactions(lp_txns)
            
            # Calculate flows
            minted = df[df['to_lower'] == wallet_address]['value_token'].sum()
            burned = df[df['from_lower'] == wallet_address]['value_token'].sum()
            
            results[wallet_name] = {
                'current_balance': minted - burned,
                'total_minted': minted,
                'total_burned': burned,
                'net_position': minted - burned,
                'transaction_count': len(df),
                'transactions': df
            }
        
        return results
    
    def calculate_gas_costs(self, all_data: Dict) -> Dict[str, Dict]:
        """Calculate total gas costs by wallet and transaction type."""
        results = {}
        
        for wallet_name, wallet_data in all_data.items():
            gas_costs = {
                'normal_txns': 0,
                'token_txns': 0,
                'nft_txns': 0,
                'total': 0
            }
            
            # Normal transactions
            normal_txns = wallet_data.get('normal_txns', [])
            if normal_txns:
                df = self.process_normal_transactions(normal_txns)
                # Only count gas for transactions from this wallet
                gas_costs['normal_txns'] = df[df['from_lower'] == self.wallets[wallet_name]]['gas_cost_eth'].sum()
            
            # Token transactions
            all_token_txns = wallet_data.get('token_txns', {}).get('all', [])
            if all_token_txns:
                df = self.process_token_transactions(all_token_txns)
                gas_costs['token_txns'] = df[df['from_lower'] == self.wallets[wallet_name]]['gas_cost_eth'].sum()
            
            # NFT transactions
            all_nft_txns = wallet_data.get('nft_txns', {}).get('all', [])
            if all_nft_txns:
                df = self.process_token_transactions(all_nft_txns, 'ERC721')
                gas_costs['nft_txns'] = df[df['from_lower'] == self.wallets[wallet_name]]['gas_cost_eth'].sum()
            
            gas_costs['total'] = sum([gas_costs['normal_txns'], gas_costs['token_txns'], gas_costs['nft_txns']])
            
            results[wallet_name] = gas_costs
        
        return results
    
    def identify_inter_wallet_transfers(self, all_data: Dict) -> pd.DataFrame:
        """Identify all transfers between owned wallets."""
        inter_wallet_txns = []
        
        for wallet_name, wallet_data in all_data.items():
            # Check normal transactions
            normal_txns = wallet_data.get('normal_txns', [])
            if normal_txns:
                df = self.process_normal_transactions(normal_txns)
                inter_wallet = df[df['is_inter_wallet']].copy()
                inter_wallet['transfer_type'] = 'ETH'
                inter_wallet['value'] = inter_wallet['value_eth']
                inter_wallet_txns.append(inter_wallet[['hash', 'from', 'to', 'value', 'transfer_type', 'timestamp']])
            
            # Check token transactions
            all_token_txns = wallet_data.get('token_txns', {}).get('all', [])
            if all_token_txns:
                df = self.process_token_transactions(all_token_txns)
                inter_wallet = df[df['is_inter_wallet']].copy()
                inter_wallet['transfer_type'] = df['tokenSymbol'].fillna('Unknown Token')
                inter_wallet['value'] = inter_wallet['value_token']
                inter_wallet_txns.append(inter_wallet[['hash', 'from', 'to', 'value', 'transfer_type', 'timestamp']])
            
            # Check NFT transactions
            all_nft_txns = wallet_data.get('nft_txns', {}).get('all', [])
            if all_nft_txns:
                df = self.process_token_transactions(all_nft_txns, 'ERC721')
                inter_wallet = df[df['is_inter_wallet']].copy()
                inter_wallet['transfer_type'] = 'NFT: ' + df['tokenName'].fillna('Unknown')
                inter_wallet['value'] = inter_wallet['tokenID']
                inter_wallet_txns.append(inter_wallet[['hash', 'from', 'to', 'value', 'transfer_type', 'timestamp']])
        
        if inter_wallet_txns:
            result = pd.concat(inter_wallet_txns, ignore_index=True)
            # Remove duplicates (same transaction appears in multiple wallet data)
            result = result.drop_duplicates(subset=['hash'])
            return result.sort_values('timestamp')
        
        return pd.DataFrame()
    
    def create_summary_report(self, all_data: Dict, wild_holdings: Dict, 
                            nft_holdings: Dict, lp_positions: Dict, 
                            gas_costs: Dict) -> Dict:
        """Create a comprehensive summary report of all analyses."""
        summary = {
            'overview': {
                'total_wallets': len(self.wallets),
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'wild_token': {
                'total_balance': sum(w['current_balance'] for w in wild_holdings.values()),
                'by_wallet': {k: v['current_balance'] for k, v in wild_holdings.items()}
            },
            'lp_tokens': {
                'total_balance': sum(w['current_balance'] for w in lp_positions.values()),
                'by_wallet': {k: v['current_balance'] for k, v in lp_positions.items()}
            },
            'nft_holdings': {},
            'gas_costs': {
                'total_eth': sum(w['total'] for w in gas_costs.values()),
                'by_wallet': {k: v['total'] for k, v in gas_costs.items()},
                'by_type': {
                    'normal': sum(w['normal_txns'] for w in gas_costs.values()),
                    'token': sum(w['token_txns'] for w in gas_costs.values()),
                    'nft': sum(w['nft_txns'] for w in gas_costs.values())
                }
            }
        }
        
        # Aggregate NFT holdings
        nft_summary = defaultdict(lambda: {'total': 0, 'by_wallet': {}})
        for wallet_name, collections in nft_holdings.items():
            for collection_name, data in collections.items():
                if data['current_holdings'] > 0:
                    nft_summary[collection_name]['total'] += data['current_holdings']
                    nft_summary[collection_name]['by_wallet'][wallet_name] = data['current_holdings']
        
        summary['nft_holdings'] = dict(nft_summary)
        
        return summary
    
    def analyze_titan_impact(self, titan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Operation Titan's impact on WILD token and portfolio"""
        analysis = {
            'portfolio_exposure': self.calculate_portfolio_exposure(),
            'buyback_impact': self.assess_buyback_impact(titan_data),
            'price_targets': self.calculate_price_targets(titan_data),
            'risk_assessment': self.assess_titan_risks(titan_data)
        }
        
        return analysis
    
    def calculate_portfolio_exposure(self) -> Dict[str, Any]:
        """Calculate portfolio's exposure to WILD token across all wallets"""
        exposure = {
            'total_wild_holdings': 0,
            'wild_by_wallet': {},
            'lp_exposure': 0,
            'total_exposure_wild': 0
        }
        
        # Get current WILD holdings from previous analysis
        for wallet_name, wallet_addr in self.wallets.items():
            # This would use cached data from analyze_wild_token_transactions
            wild_balance = 0  # Placeholder - would get from actual data
            exposure['wild_by_wallet'][wallet_name] = wild_balance
            exposure['total_wild_holdings'] += wild_balance
        
        # Add LP token exposure (50% of LP value is WILD)
        # This would calculate from LP positions
        exposure['lp_exposure'] = 0  # Placeholder
        exposure['total_exposure_wild'] = exposure['total_wild_holdings'] + exposure['lp_exposure']
        
        return exposure
    
    def assess_buyback_impact(self, titan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the impact of Operation Titan buybacks on portfolio value"""
        supply_dynamics = titan_data.get('supply_dynamics', {})
        price_impact = titan_data.get('price_impact', {})
        
        impact = {
            'supply_reduction_benefit': supply_dynamics.get('supply_reduction_pct', 0),
            'estimated_price_appreciation': price_impact.get('combined_impact_estimate', 0),
            'deflationary_rate': self.calculate_deflationary_rate(supply_dynamics),
            'buyback_completion': self.calculate_buyback_completion(titan_data)
        }
        
        return impact
    
    def calculate_deflationary_rate(self, supply_dynamics: Dict[str, Any]) -> float:
        """Calculate annual deflationary rate from burns and locks"""
        # 80% burn rate on in-game spending + buyback locks
        # This is simplified - would need actual burn data
        monthly_burn_estimate = 0.005  # 0.5% monthly burn estimate
        annual_burn = monthly_burn_estimate * 12
        
        # Add one-time supply reduction from buybacks
        buyback_reduction = supply_dynamics.get('supply_reduction_pct', 0) / 100
        
        # Annualized deflationary rate
        return (annual_burn + buyback_reduction) * 100
    
    def calculate_buyback_completion(self, titan_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate buyback completion percentage by DAO"""
        dao_balances = titan_data.get('dao_balances', {})
        completion = {}
        
        for dao_name, balance_info in dao_balances.items():
            if 'error' not in balance_info:
                completion[dao_name] = balance_info.get('buyback_progress', 0)
        
        # Calculate overall completion
        total_progress = sum(completion.values()) / len(completion) if completion else 0
        completion['overall'] = total_progress
        
        return completion
    
    def calculate_price_targets(self, titan_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate potential price targets based on Operation Titan mechanics"""
        current_price = 0.38  # Would get from price data
        
        # Conservative, base, and optimistic scenarios
        price_impact_pct = titan_data.get('price_impact', {}).get('combined_impact_estimate', 0)
        
        targets = {
            'current_price': current_price,
            'conservative': current_price * (1 + price_impact_pct / 100 * 0.5),
            'base_case': current_price * (1 + price_impact_pct / 100),
            'optimistic': current_price * (1 + price_impact_pct / 100 * 1.5),
            'methodology': 'Based on supply reduction and estimated market impact'
        }
        
        # Add longer-term targets based on deflationary mechanics
        annual_deflation = self.calculate_deflationary_rate(titan_data.get('supply_dynamics', {}))
        targets['1_year_target'] = current_price * (1 + annual_deflation / 100)
        
        return targets
    
    def assess_titan_risks(self, titan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks related to Operation Titan execution"""
        patterns = titan_data.get('buyback_patterns', {})
        phase_status = titan_data.get('phase_status', {})
        
        risks = {
            'execution_risk': 'low',
            'timing_risk': 'medium',
            'liquidity_risk': 'medium',
            'front_running_risk': 'high',
            'specific_concerns': []
        }
        
        # Check execution status
        if patterns.get('execution_status') == 'pending' and phase_status.get('phase2_deadline_status') == 'passed':
            risks['execution_risk'] = 'high'
            risks['specific_concerns'].append('Phase 2 deadline passed without detected execution')
        
        # Check for anomalies
        if patterns.get('anomalies'):
            risks['specific_concerns'].extend(patterns['anomalies'])
        
        # Assess liquidity risk based on buyback size
        price_impact = titan_data.get('price_impact', {})
        if price_impact.get('buyback_volume_percentage', 0) > 20:
            risks['liquidity_risk'] = 'high'
            risks['specific_concerns'].append('Buyback volume exceeds 20% of daily volume')
        
        return risks
    
    def generate_titan_trading_signals(self, titan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading signals based on Operation Titan analysis"""
        price_targets = self.calculate_price_targets(titan_data)
        buyback_completion = self.calculate_buyback_completion(titan_data)
        risks = self.assess_titan_risks(titan_data)
        
        signals = {
            'overall_sentiment': 'neutral',
            'action': 'hold',
            'confidence': 'medium',
            'rationale': []
        }
        
        # Bullish signals
        if buyback_completion.get('overall', 0) < 50 and risks['execution_risk'] == 'low':
            signals['overall_sentiment'] = 'bullish'
            signals['action'] = 'accumulate'
            signals['rationale'].append('Buybacks less than 50% complete with low execution risk')
        
        # Check price vs targets
        current = price_targets['current_price']
        if current < price_targets['conservative']:
            signals['rationale'].append('Price below conservative target')
            if signals['overall_sentiment'] != 'bearish':
                signals['overall_sentiment'] = 'bullish'
        
        # Risk adjustments
        if risks['execution_risk'] == 'high':
            signals['confidence'] = 'low'
            signals['rationale'].append('High execution risk detected')
        
        return signals