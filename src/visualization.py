"""
Visualization module for Wilder World portfolio analysis.
Creates charts and visualizations using plotly and matplotlib.
"""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set style for matplotlib
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class WilderVisualizer:
    """Creates visualizations for Wilder World portfolio analysis."""
    
    def __init__(self, output_dir: Optional[str] = None):
        """Initialize the visualizer with output directory."""
        if output_dir is None:
            self.output_dir = os.path.join(os.path.dirname(__file__), '..', 'output', 'visualizations')
        else:
            self.output_dir = output_dir
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Define color scheme
        self.wallet_colors = {
            'hot': '#FF6B6B',
            'digital_re': '#4ECDC4',
            'eth_stake': '#45B7D1',
            'warm': '#F9CA24'
        }
        
        self.collection_colors = {
            'airwild_s0': '#E74C3C',
            'airwild_s1': '#E67E22',
            'airwild_s2': '#F39C12',
            'wheels': '#16A085',
            'cribs': '#27AE60',
            'crafts': '#2980B9',
            'land': '#8E44AD',
            'beasts_wolves': '#34495E',
            'beasts_wapes': '#7F8C8D',
            'moto': '#C0392B',
            'pals_gens': '#D35400'
        }
    
    def create_portfolio_composition_chart(self, wild_holdings: Dict, nft_holdings: Dict, 
                                         lp_positions: Dict, prices: Dict) -> go.Figure:
        """Create a portfolio composition pie chart."""
        # Calculate values
        wild_value = sum(w['current_balance'] for w in wild_holdings.values()) * prices.get('WILD', 0)
        lp_value = sum(w['current_balance'] for w in lp_positions.values()) * prices.get('LP_EST', 0)
        
        # Estimate NFT value (placeholder - would need floor prices)
        nft_count = sum(
            sum(collection['current_holdings'] for collection in wallet.values())
            for wallet in nft_holdings.values()
        )
        nft_value_est = nft_count * 0.1 * prices.get('ETH', 0)  # Rough estimate
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=['WILD Tokens', 'LP Tokens', 'NFTs'],
            values=[wild_value, lp_value, nft_value_est],
            hole=.3,
            marker_colors=['#4ECDC4', '#45B7D1', '#F9CA24']
        )])
        
        fig.update_layout(
            title='Portfolio Composition by Value (USD)',
            showlegend=True,
            width=800,
            height=600
        )
        
        return fig
    
    def create_wild_holdings_by_wallet(self, wild_holdings: Dict) -> go.Figure:
        """Create a bar chart of WILD token holdings by wallet."""
        wallets = list(wild_holdings.keys())
        balances = [wild_holdings[w]['current_balance'] for w in wallets]
        
        fig = go.Figure(data=[
            go.Bar(
                x=wallets,
                y=balances,
                marker_color=[self.wallet_colors.get(w, '#95A5A6') for w in wallets],
                text=[f'{b:,.0f}' for b in balances],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title='WILD Token Holdings by Wallet',
            xaxis_title='Wallet',
            yaxis_title='WILD Tokens',
            showlegend=False,
            width=800,
            height=500
        )
        
        return fig
    
    def create_nft_holdings_heatmap(self, nft_holdings: Dict) -> go.Figure:
        """Create a heatmap of NFT holdings across wallets and collections."""
        # Prepare data
        collections = set()
        for wallet_data in nft_holdings.values():
            collections.update(wallet_data.keys())
        
        collections = sorted(list(collections))
        wallets = sorted(list(nft_holdings.keys()))
        
        # Create matrix
        z = []
        for collection in collections:
            row = []
            for wallet in wallets:
                count = nft_holdings[wallet].get(collection, {}).get('current_holdings', 0)
                row.append(count)
            z.append(row)
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=z,
            x=wallets,
            y=collections,
            colorscale='Viridis',
            text=z,
            texttemplate='%{text}',
            textfont={"size": 12}
        ))
        
        fig.update_layout(
            title='NFT Holdings Heatmap',
            xaxis_title='Wallet',
            yaxis_title='Collection',
            width=800,
            height=600
        )
        
        return fig
    
    def create_gas_cost_breakdown(self, gas_costs: Dict) -> go.Figure:
        """Create a stacked bar chart of gas costs by type and wallet."""
        wallets = list(gas_costs.keys())
        
        fig = go.Figure()
        
        # Add bars for each transaction type
        fig.add_trace(go.Bar(
            name='Normal Transactions',
            x=wallets,
            y=[gas_costs[w]['normal_txns'] for w in wallets],
            marker_color='#3498DB'
        ))
        
        fig.add_trace(go.Bar(
            name='Token Transactions',
            x=wallets,
            y=[gas_costs[w]['token_txns'] for w in wallets],
            marker_color='#2ECC71'
        ))
        
        fig.add_trace(go.Bar(
            name='NFT Transactions',
            x=wallets,
            y=[gas_costs[w]['nft_txns'] for w in wallets],
            marker_color='#E74C3C'
        ))
        
        fig.update_layout(
            title='Gas Costs by Transaction Type and Wallet (ETH)',
            xaxis_title='Wallet',
            yaxis_title='Gas Cost (ETH)',
            barmode='stack',
            width=800,
            height=500
        )
        
        return fig
    
    def create_transaction_timeline(self, all_data: Dict) -> go.Figure:
        """Create a timeline visualization of all transactions."""
        fig = make_subplots(
            rows=len(all_data),
            cols=1,
            subplot_titles=[f'{w.title()} Wallet' for w in all_data.keys()],
            shared_xaxes=True,
            vertical_spacing=0.05
        )
        
        row = 1
        for wallet_name, wallet_data in all_data.items():
            # Combine all transactions
            all_txns = []
            
            # Normal transactions
            normal_txns = wallet_data.get('normal_txns', [])
            if normal_txns:
                df = pd.DataFrame(normal_txns)
                df['timestamp'] = pd.to_datetime(df['timeStamp'].astype(int), unit='s')
                df['type'] = 'ETH'
                all_txns.append(df[['timestamp', 'type']])
            
            # Token transactions
            token_txns = wallet_data.get('token_txns', {}).get('all', [])
            if token_txns:
                df = pd.DataFrame(token_txns)
                df['timestamp'] = pd.to_datetime(df['timeStamp'].astype(int), unit='s')
                df['type'] = 'Token'
                all_txns.append(df[['timestamp', 'type']])
            
            # NFT transactions
            nft_txns = wallet_data.get('nft_txns', {}).get('all', [])
            if nft_txns:
                df = pd.DataFrame(nft_txns)
                df['timestamp'] = pd.to_datetime(df['timeStamp'].astype(int), unit='s')
                df['type'] = 'NFT'
                all_txns.append(df[['timestamp', 'type']])
            
            if all_txns:
                combined_df = pd.concat(all_txns, ignore_index=True)
                
                # Group by date and type
                daily_counts = combined_df.groupby([combined_df['timestamp'].dt.date, 'type']).size().reset_index(name='count')
                
                # Add scatter plots for each type
                for tx_type in ['ETH', 'Token', 'NFT']:
                    type_data = daily_counts[daily_counts['type'] == tx_type]
                    if not type_data.empty:
                        fig.add_trace(
                            go.Scatter(
                                x=type_data['timestamp'],
                                y=type_data['count'],
                                mode='markers',
                                name=tx_type,
                                marker=dict(
                                    size=10,
                                    color={'ETH': '#3498DB', 'Token': '#2ECC71', 'NFT': '#E74C3C'}[tx_type]
                                ),
                                showlegend=(row == 1)
                            ),
                            row=row,
                            col=1
                        )
            
            row += 1
        
        fig.update_xaxes(title_text="Date", row=len(all_data), col=1)
        fig.update_yaxes(title_text="Transaction Count")
        
        fig.update_layout(
            title='Transaction Activity Timeline',
            height=200 * len(all_data),
            width=1000
        )
        
        return fig
    
    def create_inter_wallet_flow_diagram(self, inter_wallet_transfers: pd.DataFrame) -> go.Figure:
        """Create a Sankey diagram of inter-wallet transfers."""
        if inter_wallet_transfers.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No inter-wallet transfers found",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # Map wallet addresses to names
        address_to_name = {
            '0x2c9fcff5ee4f43e2a42fa6b79c14664cc69696de': 'Hot Wallet',
            '0x54c1a42aa00a44c311bec1f60cc4540f26c06b71': 'Digital RE Wallet',
            '0xc3455f9b8119ecdf2a56e0e771c39e954a09da97': 'ETH Staking Wallet',
            '0x89eb314457ad6c5ce6e84b72c4581181bb2b765a': 'Warm Wallet'
        }
        
        # Prepare data for Sankey
        transfers = inter_wallet_transfers.copy()
        transfers['from_name'] = transfers['from'].str.lower().map(address_to_name)
        transfers['to_name'] = transfers['to'].str.lower().map(address_to_name)
        
        # Group by transfer type and aggregate
        grouped = transfers.groupby(['from_name', 'to_name', 'transfer_type'])['value'].sum().reset_index()
        
        # Create node labels
        nodes = list(set(grouped['from_name'].unique()) | set(grouped['to_name'].unique()))
        node_dict = {node: i for i, node in enumerate(nodes)}
        
        # Create links
        links = {
            'source': [node_dict[x] for x in grouped['from_name']],
            'target': [node_dict[x] for x in grouped['to_name']],
            'value': grouped['value'].tolist(),
            'label': grouped['transfer_type'].tolist()
        }
        
        # Create Sankey diagram
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=nodes,
                color=[self.wallet_colors.get(n.split()[0].lower(), '#95A5A6') for n in nodes]
            ),
            link=dict(
                source=links['source'],
                target=links['target'],
                value=links['value'],
                label=links['label']
            )
        )])
        
        fig.update_layout(
            title='Inter-Wallet Transfer Flow',
            width=800,
            height=600
        )
        
        return fig
    
    def save_all_visualizations(self, wild_holdings: Dict, nft_holdings: Dict,
                               lp_positions: Dict, gas_costs: Dict,
                               inter_wallet_transfers: pd.DataFrame,
                               all_data: Dict, prices: Dict):
        """Generate and save all visualizations."""
        logger.info("Creating visualizations...")
        
        # 1. Portfolio composition
        fig = self.create_portfolio_composition_chart(wild_holdings, nft_holdings, lp_positions, prices)
        fig.write_html(os.path.join(self.output_dir, 'portfolio_composition.html'))
        logger.info("Saved portfolio composition chart")
        
        # 2. WILD holdings by wallet
        fig = self.create_wild_holdings_by_wallet(wild_holdings)
        fig.write_html(os.path.join(self.output_dir, 'wild_holdings_by_wallet.html'))
        logger.info("Saved WILD holdings chart")
        
        # 3. NFT holdings heatmap
        fig = self.create_nft_holdings_heatmap(nft_holdings)
        fig.write_html(os.path.join(self.output_dir, 'nft_holdings_heatmap.html'))
        logger.info("Saved NFT holdings heatmap")
        
        # 4. Gas cost breakdown
        fig = self.create_gas_cost_breakdown(gas_costs)
        fig.write_html(os.path.join(self.output_dir, 'gas_cost_breakdown.html'))
        logger.info("Saved gas cost breakdown")
        
        # 5. Transaction timeline
        fig = self.create_transaction_timeline(all_data)
        fig.write_html(os.path.join(self.output_dir, 'transaction_timeline.html'))
        logger.info("Saved transaction timeline")
        
        # 6. Inter-wallet transfers
        fig = self.create_inter_wallet_flow_diagram(inter_wallet_transfers)
        fig.write_html(os.path.join(self.output_dir, 'inter_wallet_transfers.html'))
        logger.info("Saved inter-wallet transfer diagram")
        
        logger.info("All visualizations saved successfully!")
    
    def create_summary_dashboard(self, summary_data: Dict) -> go.Figure:
        """Create a summary dashboard with key metrics."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('WILD Token Distribution', 'NFT Holdings by Collection',
                          'Gas Costs by Type', 'Wallet Overview'),
            specs=[[{'type': 'pie'}, {'type': 'bar'}],
                   [{'type': 'pie'}, {'type': 'table'}]]
        )
        
        # 1. WILD token distribution
        wild_data = summary_data['wild_token']['by_wallet']
        fig.add_trace(
            go.Pie(
                labels=list(wild_data.keys()),
                values=list(wild_data.values()),
                marker_colors=[self.wallet_colors.get(w, '#95A5A6') for w in wild_data.keys()]
            ),
            row=1, col=1
        )
        
        # 2. NFT holdings by collection
        nft_data = [(k, v['total']) for k, v in summary_data['nft_holdings'].items()]
        nft_data.sort(key=lambda x: x[1], reverse=True)
        if nft_data:
            fig.add_trace(
                go.Bar(
                    x=[x[0] for x in nft_data[:10]],  # Top 10 collections
                    y=[x[1] for x in nft_data[:10]],
                    marker_color=[self.collection_colors.get(x[0], '#95A5A6') for x in nft_data[:10]]
                ),
                row=1, col=2
            )
        
        # 3. Gas costs by type
        gas_by_type = summary_data['gas_costs']['by_type']
        fig.add_trace(
            go.Pie(
                labels=list(gas_by_type.keys()),
                values=list(gas_by_type.values()),
                marker_colors=['#3498DB', '#2ECC71', '#E74C3C']
            ),
            row=2, col=1
        )
        
        # 4. Wallet overview table
        wallet_data = []
        for wallet in wild_data.keys():
            wallet_data.append([
                wallet.title(),
                f"{wild_data.get(wallet, 0):,.0f}",
                f"{summary_data['lp_tokens']['by_wallet'].get(wallet, 0):,.2f}",
                f"{summary_data['gas_costs']['by_wallet'].get(wallet, 0):.4f}"
            ])
        
        fig.add_trace(
            go.Table(
                header=dict(values=['Wallet', 'WILD Tokens', 'LP Tokens', 'Gas (ETH)']),
                cells=dict(values=list(zip(*wallet_data)))
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title='Wilder World Portfolio Summary Dashboard',
            showlegend=False,
            height=800,
            width=1200
        )
        
        return fig