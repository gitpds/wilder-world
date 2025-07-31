"""
Operation Titan Dashboard Generator
Creates comprehensive HTML reports with interactive visualizations
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from jinja2 import Template

class TitanDashboard:
    """Generates HTML dashboard for Operation Titan analysis"""
    
    def __init__(self, output_dir: Optional[str] = None):
        """Initialize dashboard generator"""
        if output_dir is None:
            self.output_dir = os.path.join(os.path.dirname(__file__), '..', 'output', 'titan_reports')
        else:
            self.output_dir = output_dir
            
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Color scheme for visualizations
        self.colors = {
            'primary': '#2a3bff',  # WILD blue
            'success': '#00d4ff',
            'warning': '#ffb700',
            'danger': '#ff3b3b',
            'dark': '#1a1a1a',
            'light': '#f5f5f5'
        }
        
        self.dao_colors = {
            'Wheels DAO': '#FF6B6B',
            'Beasts DAO': '#4ECDC4',
            'Kicks DAO': '#45B7D1',
            'Cribs DAO': '#F9CA24',
            'Crafts DAO': '#6C5CE7',
            'Moto DAO': '#A29BFE',
            'Land DAO': '#FD79A8',
            'PALs DAO': '#FDCB6E',
            'Wilder World DAO': '#00B894'
        }
        
    def generate_dashboard(self, titan_data: Dict[str, Any], analyzer_data: Dict[str, Any]) -> str:
        """Generate complete HTML dashboard"""
        # Create all visualizations
        charts = {
            'dao_progress': self.create_dao_progress_chart(titan_data),
            'supply_dynamics': self.create_supply_dynamics_chart(titan_data),
            'price_impact': self.create_price_impact_chart(titan_data, analyzer_data),
            'risk_matrix': self.create_risk_matrix(analyzer_data),
            'timeline': self.create_buyback_timeline(titan_data),
            'wallet_exposure': self.create_wallet_exposure_chart(analyzer_data),
            'technical_analysis': self.create_technical_analysis_chart(analyzer_data)
        }
        
        # Generate HTML report
        html_content = self.render_html_template(titan_data, analyzer_data, charts)
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'titan_analysis_{timestamp}.html'
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(html_content)
            
        # Also save latest version
        latest_path = os.path.join(self.output_dir, 'titan_analysis_latest.html')
        with open(latest_path, 'w') as f:
            f.write(html_content)
            
        return filepath
    
    def create_dao_progress_chart(self, titan_data: Dict[str, Any]) -> str:
        """Create DAO buyback progress visualization"""
        dao_balances = titan_data.get('dao_balances', {})
        
        dao_names = []
        eth_remaining = []
        wild_acquired = []
        progress_pct = []
        
        for dao_name, info in dao_balances.items():
            if 'error' not in info:
                dao_names.append(dao_name)
                eth_remaining.append(info.get('eth_remaining', 0))
                wild_acquired.append(info.get('wild_balance', 0))
                progress_pct.append(info.get('buyback_progress', 0))
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('ETH Remaining by DAO', 'WILD Acquired by DAO', 
                          'Buyback Progress (%)', 'ETH Allocation vs Spent'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}],
                   [{'type': 'bar'}, {'type': 'scatter'}]]
        )
        
        # ETH Remaining
        fig.add_trace(
            go.Bar(x=dao_names, y=eth_remaining, name='ETH Remaining',
                   marker_color=[self.dao_colors.get(name, '#333') for name in dao_names]),
            row=1, col=1
        )
        
        # WILD Acquired
        fig.add_trace(
            go.Bar(x=dao_names, y=wild_acquired, name='WILD Acquired',
                   marker_color=[self.dao_colors.get(name, '#333') for name in dao_names]),
            row=1, col=2
        )
        
        # Progress Percentage
        fig.add_trace(
            go.Bar(x=dao_names, y=progress_pct, name='Progress %',
                   marker_color=[self.colors['success'] if p > 50 else self.colors['warning'] 
                               for p in progress_pct]),
            row=2, col=1
        )
        
        # Allocation vs Spent scatter
        allocations = [dao_balances[name].get('eth_allocation', 0) for name in dao_names]
        spent = [dao_balances[name].get('eth_allocation', 0) - 
                dao_balances[name].get('eth_remaining', 0) for name in dao_names]
        
        fig.add_trace(
            go.Scatter(x=allocations, y=spent, mode='markers+text',
                      text=dao_names, textposition='top center',
                      marker=dict(size=15, color=[self.dao_colors.get(name, '#333') 
                                                 for name in dao_names])),
            row=2, col=2
        )
        
        # Add diagonal line for reference
        max_alloc = max(allocations) if allocations else 100
        fig.add_trace(
            go.Scatter(x=[0, max_alloc], y=[0, max_alloc], 
                      mode='lines', line=dict(dash='dash', color='gray'),
                      name='Full Spend Line', showlegend=False),
            row=2, col=2
        )
        
        fig.update_layout(
            title='DAO Buyback Progress Overview',
            height=800,
            showlegend=False,
            template='plotly_dark'
        )
        
        fig.update_xaxes(title_text='ETH Allocated', row=2, col=2)
        fig.update_yaxes(title_text='ETH Spent', row=2, col=2)
        
        return fig.to_html(include_plotlyjs='cdn', div_id='dao_progress')
    
    def create_supply_dynamics_chart(self, titan_data: Dict[str, Any]) -> str:
        """Create supply dynamics visualization"""
        supply = titan_data.get('supply_dynamics', {})
        
        # Create pie chart for supply distribution
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('WILD Supply Distribution', 'Deflationary Impact'),
            specs=[[{'type': 'pie'}, {'type': 'bar'}]]
        )
        
        # Supply distribution
        labels = ['Circulating', 'OTC Locked', 'DAO Buyback Target', 'Burned (Est)']
        values = [
            supply.get('effective_circulating', 0),
            supply.get('otc_locked', 0),
            supply.get('dao_buyback_target', 0),
            supply.get('estimated_burns', 0)
        ]
        
        fig.add_trace(
            go.Pie(labels=labels, values=values,
                   marker=dict(colors=[self.colors['primary'], self.colors['warning'],
                                     self.colors['success'], self.colors['danger']])),
            row=1, col=1
        )
        
        # Deflationary impact over time
        months = list(range(1, 13))
        monthly_deflation = supply.get('supply_reduction_pct', 4) / 12
        cumulative_reduction = [monthly_deflation * m for m in months]
        
        fig.add_trace(
            go.Bar(x=months, y=cumulative_reduction,
                   name='Cumulative Supply Reduction %',
                   marker_color=self.colors['success']),
            row=1, col=2
        )
        
        fig.update_layout(
            title='WILD Token Supply Dynamics',
            height=400,
            template='plotly_dark'
        )
        
        fig.update_xaxes(title_text='Months', row=1, col=2)
        fig.update_yaxes(title_text='Supply Reduction %', row=1, col=2)
        
        return fig.to_html(include_plotlyjs='cdn', div_id='supply_dynamics')
    
    def create_price_impact_chart(self, titan_data: Dict[str, Any], analyzer_data: Dict[str, Any]) -> str:
        """Create price impact and targets visualization"""
        price_impact = titan_data.get('price_impact', {})
        price_targets = analyzer_data.get('price_targets', {})
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Price Impact Components', 'Price Targets', 
                          'Volume Analysis', 'Trading Signals'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}],
                   [{'type': 'pie'}, {'type': 'indicator'}]]
        )
        
        # Price impact components
        components = ['Direct Buyback', 'Supply Reduction', 'Burn Mechanism', 'Total']
        values = [
            price_impact.get('estimated_price_impact_pct', 0),
            price_impact.get('supply_reduction_impact', 0) * 0.3,
            2.0,  # Estimated burn impact
            price_impact.get('combined_impact_estimate', 0)
        ]
        
        fig.add_trace(
            go.Bar(x=components, y=values, 
                   marker_color=[self.colors['primary'], self.colors['success'],
                               self.colors['danger'], self.colors['warning']]),
            row=1, col=1
        )
        
        # Price targets
        target_names = ['Current', 'Conservative', 'Base Case', 'Optimistic', '1 Year']
        target_values = [
            price_targets.get('current_price', 0.38),
            price_targets.get('conservative', 0),
            price_targets.get('base_case', 0),
            price_targets.get('optimistic', 0),
            price_targets.get('1_year_target', 0)
        ]
        
        fig.add_trace(
            go.Bar(x=target_names, y=target_values,
                   marker_color=['gray', self.colors['success'], self.colors['primary'],
                               self.colors['warning'], self.colors['danger']]),
            row=1, col=2
        )
        
        # Volume analysis pie
        fig.add_trace(
            go.Pie(labels=['Buyback Volume', 'Other Volume'],
                   values=[price_impact.get('total_buyback_usd', 0),
                          price_impact.get('estimated_daily_volume', 0) - 
                          price_impact.get('total_buyback_usd', 0)],
                   marker=dict(colors=[self.colors['primary'], 'gray'])),
            row=2, col=1
        )
        
        # Trading signal indicator
        signals = analyzer_data.get('trading_signals', {})
        signal_value = {'bullish': 1, 'neutral': 0, 'bearish': -1}.get(
            signals.get('overall_sentiment', 'neutral'), 0
        )
        
        fig.add_trace(
            go.Indicator(
                mode='gauge+number+delta',
                value=signal_value,
                title={'text': f"Signal: {signals.get('action', 'HOLD').upper()}"},
                delta={'reference': 0},
                gauge={
                    'axis': {'range': [-1, 1]},
                    'bar': {'color': self.colors['primary']},
                    'steps': [
                        {'range': [-1, -0.5], 'color': self.colors['danger']},
                        {'range': [-0.5, 0.5], 'color': 'gray'},
                        {'range': [0.5, 1], 'color': self.colors['success']}
                    ],
                    'threshold': {
                        'line': {'color': 'white', 'width': 4},
                        'thickness': 0.75,
                        'value': signal_value
                    }
                }
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title='Price Impact Analysis & Targets',
            height=800,
            template='plotly_dark',
            showlegend=False
        )
        
        fig.update_yaxes(title_text='Impact %', row=1, col=1)
        fig.update_yaxes(title_text='Price (USD)', row=1, col=2)
        
        return fig.to_html(include_plotlyjs='cdn', div_id='price_impact')
    
    def create_risk_matrix(self, analyzer_data: Dict[str, Any]) -> str:
        """Create risk assessment matrix"""
        risks = analyzer_data.get('risk_assessment', {})
        
        # Create risk heatmap
        risk_categories = ['Execution', 'Timing', 'Liquidity', 'Front-running']
        risk_levels = ['low', 'medium', 'high']
        
        # Create matrix data
        matrix_data = []
        for category in risk_categories:
            row = []
            current_level = risks.get(f'{category.lower()}_risk', 'medium')
            for level in risk_levels:
                row.append(1 if current_level == level else 0)
            matrix_data.append(row)
        
        fig = go.Figure(data=go.Heatmap(
            z=matrix_data,
            x=risk_levels,
            y=risk_categories,
            colorscale=[[0, 'rgba(0,0,0,0)'], 
                       [1, self.colors['danger']]],
            showscale=False,
            text=[['', '', ''] for _ in risk_categories],
            texttemplate='%{text}',
            textfont={'size': 20}
        ))
        
        # Add checkmarks for current risk levels
        for i, category in enumerate(risk_categories):
            current_level = risks.get(f'{category.lower()}_risk', 'medium')
            j = risk_levels.index(current_level)
            fig.add_annotation(
                x=j, y=i,
                text='✓',
                showarrow=False,
                font=dict(size=24, color='white')
            )
        
        # Add specific concerns as annotations
        concerns = risks.get('specific_concerns', [])
        concern_text = '<br>'.join(concerns[:3]) if concerns else 'No specific concerns identified'
        
        fig.add_annotation(
            text=f'<b>Key Concerns:</b><br>{concern_text}',
            xref='paper', yref='paper',
            x=0.5, y=-0.2,
            showarrow=False,
            font=dict(size=12, color='white'),
            align='center'
        )
        
        fig.update_layout(
            title='Risk Assessment Matrix',
            height=400,
            template='plotly_dark',
            xaxis_title='Risk Level',
            yaxis_title='Risk Category'
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id='risk_matrix')
    
    def create_buyback_timeline(self, titan_data: Dict[str, Any]) -> str:
        """Create timeline visualization of buyback phases"""
        phase_status = titan_data.get('phase_status', {})
        
        # Timeline data
        phases = [
            {'name': 'OTC Phase', 'start': '2024-01-01', 'end': '2024-07-23', 
             'color': self.colors['success'], 'y': 1},
            {'name': 'Phase 1', 'start': '2024-07-23', 'end': '2024-07-28', 
             'color': self.colors['warning'], 'y': 2},
            {'name': 'Phase 2', 'start': '2024-07-28', 'end': '2024-08-04', 
             'color': self.colors['primary'], 'y': 3},
            {'name': 'Packs Buyback', 'start': '2024-08-01', 'end': '2024-12-31', 
             'color': self.colors['danger'], 'y': 4}
        ]
        
        fig = go.Figure()
        
        # Add phase bars
        for phase in phases:
            fig.add_trace(go.Scatter(
                x=[phase['start'], phase['end']],
                y=[phase['y'], phase['y']],
                mode='lines',
                line=dict(color=phase['color'], width=20),
                name=phase['name'],
                hovertemplate=f"{phase['name']}<br>%{{x}}<extra></extra>"
            ))
        
        # Add current date marker as an annotation instead of vline
        current_date = datetime.now()
        fig.add_annotation(
            x=current_date.strftime('%Y-%m-%d'),
            y=2.5,
            text='Today',
            showarrow=True,
            arrowhead=2,
            arrowcolor='white',
            ax=0,
            ay=-40
        )
        
        fig.update_layout(
            title='Operation Titan Timeline',
            xaxis_title='Date',
            yaxis_title='Phase',
            height=300,
            template='plotly_dark',
            yaxis=dict(
                ticktext=['', 'OTC', 'Phase 1', 'Phase 2', 'Packs'],
                tickvals=[0, 1, 2, 3, 4],
                range=[0, 5]
            ),
            showlegend=False
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id='timeline')
    
    def create_wallet_exposure_chart(self, analyzer_data: Dict[str, Any]) -> str:
        """Create wallet exposure visualization"""
        exposure = analyzer_data.get('portfolio_exposure', {})
        
        # Create treemap of WILD exposure
        labels = []
        parents = []
        values = []
        colors = []
        
        # Add total
        labels.append('Total WILD Exposure')
        parents.append('')
        values.append(exposure.get('total_exposure_wild', 0))
        colors.append(self.colors['primary'])
        
        # Add wallet holdings
        for wallet, amount in exposure.get('wild_by_wallet', {}).items():
            if amount > 0:
                labels.append(f'{wallet} WILD')
                parents.append('Total WILD Exposure')
                values.append(amount)
                colors.append(self.colors['success'])
        
        # Add LP exposure
        if exposure.get('lp_exposure', 0) > 0:
            labels.append('LP Token WILD')
            parents.append('Total WILD Exposure')
            values.append(exposure['lp_exposure'])
            colors.append(self.colors['warning'])
        
        fig = go.Figure(go.Treemap(
            labels=labels,
            parents=parents,
            values=values,
            marker=dict(colors=colors),
            textinfo='label+value+percent parent'
        ))
        
        fig.update_layout(
            title='Portfolio WILD Token Exposure',
            height=400,
            template='plotly_dark'
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id='wallet_exposure')
    
    def create_technical_analysis_chart(self, analyzer_data: Dict[str, Any]) -> str:
        """Create technical analysis visualization"""
        # This would integrate with actual price data
        # For now, creating a placeholder structure
        
        fig = make_subplots(
            rows=2, cols=1,
            row_heights=[0.7, 0.3],
            shared_xaxes=True,
            subplot_titles=('WILD/USD Price Action', 'Volume')
        )
        
        # Generate sample data (would be real price data)
        import numpy as np
        dates = pd.date_range(start='2025-07-01', end='2025-07-31', freq='D')
        prices = 0.38 + np.random.randn(len(dates)) * 0.02
        volumes = np.random.randint(1000000, 5000000, len(dates))
        
        # Price candlestick
        fig.add_trace(
            go.Scatter(x=dates, y=prices, mode='lines',
                      line=dict(color=self.colors['primary'], width=2),
                      name='WILD/USD'),
            row=1, col=1
        )
        
        # Add price targets as horizontal lines
        price_targets = analyzer_data.get('price_targets', {})
        target_levels = [
            ('Conservative', price_targets.get('conservative', 0.40), self.colors['success']),
            ('Base Case', price_targets.get('base_case', 0.42), self.colors['primary']),
            ('Optimistic', price_targets.get('optimistic', 0.45), self.colors['warning'])
        ]
        
        for name, level, color in target_levels:
            if level > 0:
                fig.add_hline(y=level, line_dash='dash', line_color=color,
                            annotation_text=f'{name}: ${level:.3f}',
                            annotation_position='right', row=1, col=1)
        
        # Volume bars
        fig.add_trace(
            go.Bar(x=dates, y=volumes, name='Volume',
                   marker_color=self.colors['primary'], opacity=0.5),
            row=2, col=1
        )
        
        fig.update_layout(
            title='WILD Token Technical Analysis',
            height=600,
            template='plotly_dark',
            xaxis2_title='Date',
            yaxis_title='Price (USD)',
            yaxis2_title='Volume',
            showlegend=False
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id='technical_analysis')
    
    def render_html_template(self, titan_data: Dict[str, Any], 
                           analyzer_data: Dict[str, Any], 
                           charts: Dict[str, str]) -> str:
        """Render the complete HTML template"""
        
        template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Operation Titan Analysis - {{ timestamp }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #0a0a0a;
            color: #ffffff;
            margin: 0;
            padding: 0;
            line-height: 1.6;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: linear-gradient(135deg, #2a3bff 0%, #00d4ff 100%);
            padding: 40px;
            border-radius: 16px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(42, 59, 255, 0.3);
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 700;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }
        .section {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        }
        .section h2 {
            color: #00d4ff;
            margin-top: 0;
            font-size: 1.8em;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .metric-card {
            background: #252525;
            border: 1px solid #444;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }
        .metric-label {
            color: #888;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .metric-value {
            font-size: 2em;
            font-weight: 700;
            margin: 10px 0;
            color: #00d4ff;
        }
        .metric-change {
            font-size: 0.9em;
            color: #00ff88;
        }
        .metric-change.negative {
            color: #ff3b3b;
        }
        .chart-container {
            margin: 20px 0;
            border-radius: 8px;
            overflow: hidden;
        }
        .alert {
            padding: 15px 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid;
        }
        .alert-warning {
            background: rgba(255, 183, 0, 0.1);
            border-color: #ffb700;
            color: #ffb700;
        }
        .alert-danger {
            background: rgba(255, 59, 59, 0.1);
            border-color: #ff3b3b;
            color: #ff3b3b;
        }
        .alert-success {
            background: rgba(0, 255, 136, 0.1);
            border-color: #00ff88;
            color: #00ff88;
        }
        .signal-box {
            background: #252525;
            border: 2px solid;
            border-radius: 12px;
            padding: 30px;
            text-align: center;
            margin: 30px 0;
        }
        .signal-bullish {
            border-color: #00ff88;
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
        }
        .signal-bearish {
            border-color: #ff3b3b;
            box-shadow: 0 0 20px rgba(255, 59, 59, 0.3);
        }
        .signal-neutral {
            border-color: #888;
        }
        .footer {
            text-align: center;
            padding: 40px;
            color: #666;
            font-size: 0.9em;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #333;
        }
        th {
            background: #252525;
            color: #00d4ff;
            font-weight: 600;
        }
        tr:hover {
            background: rgba(42, 59, 255, 0.1);
        }
        .tag {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 0.85em;
            font-weight: 600;
            margin: 2px;
        }
        .tag-success {
            background: rgba(0, 255, 136, 0.2);
            color: #00ff88;
        }
        .tag-warning {
            background: rgba(255, 183, 0, 0.2);
            color: #ffb700;
        }
        .tag-danger {
            background: rgba(255, 59, 59, 0.2);
            color: #ff3b3b;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Operation Titan Analysis Dashboard</h1>
            <p>Comprehensive WILD Token Buyback & Market Impact Analysis</p>
            <p style="font-size: 0.9em; opacity: 0.7;">Generated: {{ timestamp }}</p>
        </div>

        <!-- Executive Summary -->
        <div class="section">
            <h2>📊 Executive Summary</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Current Phase</div>
                    <div class="metric-value">{{ phase_status.current_phase }}</div>
                    <div class="metric-change">{{ phase_status.days_since_phase2_greenlit }} days since Phase 2</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Total ETH Allocated</div>
                    <div class="metric-value">{{ total_eth_allocation }} ETH</div>
                    <div class="metric-change">${{ total_usd_value }}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Expected WILD Buyback</div>
                    <div class="metric-value">{{ total_expected_wild }}M</div>
                    <div class="metric-change">{{ supply_reduction_pct }}% supply reduction</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Overall Progress</div>
                    <div class="metric-value">{{ overall_progress }}%</div>
                    <div class="metric-change">{{ execution_status }}</div>
                </div>
            </div>

            <!-- Trading Signal -->
            <div class="signal-box signal-{{ signal_sentiment }}">
                <h3 style="margin-top: 0; font-size: 1.5em;">Trading Signal: {{ signal_action }}</h3>
                <p style="margin: 10px 0; opacity: 0.8;">Confidence: {{ signal_confidence }}</p>
                <div style="text-align: left; background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px;">
                    <strong>Rationale:</strong>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        {% for reason in signal_rationale %}
                        <li>{{ reason }}</li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
        </div>

        <!-- DAO Progress -->
        <div class="section">
            <h2>🏛️ DAO Buyback Progress</h2>
            <div class="chart-container">
                {{ dao_progress_chart }}
            </div>
            
            <!-- DAO Details Table -->
            <table>
                <thead>
                    <tr>
                        <th>DAO Name</th>
                        <th>ETH Allocated</th>
                        <th>ETH Remaining</th>
                        <th>WILD Balance</th>
                        <th>Progress</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {% for dao_name, dao_info in dao_details %}
                    <tr>
                        <td>{{ dao_name }}</td>
                        <td>{{ dao_info.eth_allocation }} ETH</td>
                        <td>{{ dao_info.eth_remaining }} ETH</td>
                        <td>{{ dao_info.wild_balance }}</td>
                        <td>{{ dao_info.progress_str }}%</td>
                        <td>
                            {% if dao_info.progress > 50 %}
                            <span class="tag tag-success">Active</span>
                            {% elif dao_info.progress > 0 %}
                            <span class="tag tag-warning">Started</span>
                            {% else %}
                            <span class="tag tag-danger">Pending</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- Supply Dynamics -->
        <div class="section">
            <h2>🔥 Supply Dynamics & Deflationary Mechanics</h2>
            <div class="chart-container">
                {{ supply_dynamics_chart }}
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Circulating Supply</div>
                    <div class="metric-value">{{ circulating_supply }}M</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">OTC Locked</div>
                    <div class="metric-value">{{ otc_locked }}M</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Annual Deflation Rate</div>
                    <div class="metric-value">{{ annual_deflation }}%</div>
                </div>
            </div>
        </div>

        <!-- Price Analysis -->
        <div class="section">
            <h2>💰 Price Impact & Targets</h2>
            <div class="chart-container">
                {{ price_impact_chart }}
            </div>
            
            <div class="alert alert-success">
                <strong>Price Targets Summary:</strong><br>
                Conservative: ${{ price_targets.conservative }} | 
                Base Case: ${{ price_targets.base_case }} | 
                Optimistic: ${{ price_targets.optimistic }} | 
                1 Year: ${{ price_targets.one_year }}
            </div>
        </div>

        <!-- Risk Assessment -->
        <div class="section">
            <h2>⚠️ Risk Assessment</h2>
            <div class="chart-container">
                {{ risk_matrix_chart }}
            </div>
            
            {% if risk_concerns %}
            <div class="alert alert-warning">
                <strong>Key Risk Factors:</strong>
                <ul style="margin: 10px 0; padding-left: 20px;">
                    {% for concern in risk_concerns %}
                    <li>{{ concern }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% endif %}
        </div>

        <!-- Timeline -->
        <div class="section">
            <h2>📅 Operation Titan Timeline</h2>
            <div class="chart-container">
                {{ timeline_chart }}
            </div>
        </div>

        <!-- Portfolio Exposure -->
        <div class="section">
            <h2>💼 Your Portfolio Exposure</h2>
            <div class="chart-container">
                {{ wallet_exposure_chart }}
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Total WILD Holdings</div>
                    <div class="metric-value">{{ total_wild_holdings }}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">LP Token Exposure</div>
                    <div class="metric-value">{{ lp_exposure }}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Potential Gain (Base Case)</div>
                    <div class="metric-value">${{ potential_gain }}</div>
                </div>
            </div>
        </div>

        <!-- Technical Analysis -->
        <div class="section">
            <h2>📈 Technical Analysis</h2>
            <div class="chart-container">
                {{ technical_analysis_chart }}
            </div>
        </div>

        <!-- Recommendations -->
        <div class="section">
            <h2>🎯 Recommendations & Next Steps</h2>
            
            <h3>Monitoring Checklist:</h3>
            <ul>
                <li>✅ Daily: Check DAO wallet balances for ETH outflows</li>
                <li>✅ Daily: Monitor Uniswap V3 pool for large WILD/ETH swaps</li>
                <li>✅ Weekly: Review burn rate from in-game activities</li>
                <li>✅ Weekly: Update price targets based on buyback progress</li>
            </ul>
            
            <h3>Action Items:</h3>
            <ol>
                <li>Set alerts for DAO wallet transactions > 10 ETH</li>
                <li>Monitor WILD price for entry points below conservative target</li>
                <li>Track Wiami.Fun activity for burn rate acceleration</li>
                <li>Review weekly for Phase 2 execution confirmation</li>
            </ol>
        </div>

        <div class="footer">
            <p>Operation Titan Analysis Dashboard v1.0 | Auto-generated report</p>
            <p>Data sources: Etherscan API, CoinGecko, On-chain Analysis</p>
            <p style="opacity: 0.6;">Disclaimer: This analysis is for informational purposes only. Not financial advice.</p>
        </div>
    </div>
</body>
</html>
        """
        
        template = Template(template_str)
        
        # Prepare template variables
        supply = titan_data.get('supply_dynamics', {})
        price_impact = titan_data.get('price_impact', {})
        phase_status = titan_data.get('phase_status', {})
        signals = analyzer_data.get('trading_signals', {})
        price_targets = analyzer_data.get('price_targets', {})
        risks = analyzer_data.get('risk_assessment', {})
        exposure = analyzer_data.get('portfolio_exposure', {})
        
        # Calculate summary metrics
        dao_balances = titan_data.get('dao_balances', {})
        overall_progress = sum(d.get('buyback_progress', 0) for d in dao_balances.values() 
                              if 'error' not in d) / len(dao_balances) if dao_balances else 0
        
        # Prepare DAO details for table
        dao_details = []
        for name, info in dao_balances.items():
            if 'error' not in info:
                dao_details.append((name, {
                    'eth_allocation': info.get('eth_allocation', 0),
                    'eth_remaining': f"{info.get('eth_remaining', 0):.2f}",
                    'wild_balance': f"{info.get('wild_balance', 0):,.0f}",
                    'progress': info.get('buyback_progress', 0),  # Keep as numeric
                    'progress_str': f"{info.get('buyback_progress', 0):.1f}"  # String version for display
                }))
        
        context = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'phase_status': phase_status,
            'total_eth_allocation': 911,
            'total_usd_value': f"{911 * 3300:,.0f}",
            'total_expected_wild': f"{8.01:.2f}",
            'supply_reduction_pct': f"{supply.get('supply_reduction_pct', 0):.1f}",
            'overall_progress': f"{overall_progress:.1f}",
            'execution_status': titan_data.get('buyback_patterns', {}).get('execution_status', 'pending').upper(),
            
            # Trading signals
            'signal_sentiment': signals.get('overall_sentiment', 'neutral'),
            'signal_action': signals.get('action', 'HOLD').upper(),
            'signal_confidence': signals.get('confidence', 'medium').upper(),
            'signal_rationale': signals.get('rationale', ['Awaiting more data']),
            
            # DAO details
            'dao_details': dao_details,
            
            # Supply dynamics
            'circulating_supply': f"{supply.get('circulating_supply', 0) / 1e6:.0f}",
            'otc_locked': f"{supply.get('otc_locked', 0) / 1e6:.0f}",
            'annual_deflation': f"{analyzer_data.get('buyback_impact', {}).get('deflationary_rate', 0):.1f}",
            
            # Price targets
            'price_targets': {
                'conservative': f"{price_targets.get('conservative', 0):.3f}",
                'base_case': f"{price_targets.get('base_case', 0):.3f}",
                'optimistic': f"{price_targets.get('optimistic', 0):.3f}",
                'one_year': f"{price_targets.get('1_year_target', 0):.3f}"
            },
            
            # Risk concerns
            'risk_concerns': risks.get('specific_concerns', []),
            
            # Portfolio exposure
            'total_wild_holdings': f"{exposure.get('total_wild_holdings', 0):,.0f}",
            'lp_exposure': f"{exposure.get('lp_exposure', 0):,.0f}",
            'potential_gain': f"{exposure.get('total_exposure_wild', 0) * (price_targets.get('base_case', 0.42) - price_targets.get('current_price', 0.38)):,.0f}",
            
            # Charts
            'dao_progress_chart': charts['dao_progress'],
            'supply_dynamics_chart': charts['supply_dynamics'],
            'price_impact_chart': charts['price_impact'],
            'risk_matrix_chart': charts['risk_matrix'],
            'timeline_chart': charts['timeline'],
            'wallet_exposure_chart': charts['wallet_exposure'],
            'technical_analysis_chart': charts['technical_analysis']
        }
        
        return template.render(**context)