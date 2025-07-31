#!/usr/bin/env python3
"""
Main Dashboard Generator - Creates an index.html hub for all crypto dashboards
"""

import os
import json
import glob
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MainDashboard:
    """Generates the main index dashboard for Wilder World crypto analysis"""
    
    def __init__(self, output_dir: str = None):
        """Initialize the dashboard generator"""
        self.base_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.output_dir = output_dir or os.path.join(self.base_dir, 'output')
        
        # Define dashboard categories
        self.categories = {
            'titan': {
                'name': 'Operation Titan Analysis',
                'description': 'DAO buyback tracking and price impact analysis',
                'icon': '🎯',
                'dir': 'titan_reports'
            },
            'visualizations': {
                'name': 'Portfolio Visualizations',
                'description': 'Interactive charts for wallet holdings and transactions',
                'icon': '📊',
                'dir': 'visualizations'
            },
            'transactions': {
                'name': 'Transaction Histories',
                'description': 'Detailed transaction logs by wallet',
                'icon': '📜',
                'dir': 'transaction_histories'
            }
        }
        
    def scan_dashboards(self) -> Dict[str, List[Dict]]:
        """Scan output directories for existing dashboards"""
        dashboards = {}
        
        for category_id, category_info in self.categories.items():
            category_path = os.path.join(self.output_dir, category_info['dir'])
            dashboards[category_id] = []
            
            if not os.path.exists(category_path):
                continue
                
            # Find all HTML files
            html_files = glob.glob(os.path.join(category_path, '*.html'))
            
            for html_file in html_files:
                file_info = self.get_file_info(html_file, category_id)
                if file_info:
                    dashboards[category_id].append(file_info)
            
            # Sort by modified time (newest first)
            dashboards[category_id].sort(key=lambda x: x['modified'], reverse=True)
        
        return dashboards
    
    def get_file_info(self, file_path: str, category: str) -> Optional[Dict]:
        """Extract information about a dashboard file"""
        try:
            stat = os.stat(file_path)
            filename = os.path.basename(file_path)
            
            # Parse filename for better display names
            display_name = self.parse_filename(filename, category)
            
            return {
                'filename': filename,
                'display_name': display_name,
                'path': os.path.relpath(file_path, self.output_dir),
                'modified': stat.st_mtime,
                'modified_str': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'size': stat.st_size,
                'size_str': self.format_file_size(stat.st_size)
            }
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return None
    
    def parse_filename(self, filename: str, category: str) -> str:
        """Convert filename to human-readable display name"""
        name = filename.replace('.html', '').replace('_', ' ').title()
        
        # Special handling for specific patterns
        if 'titan_analysis_2' in filename:
            # Extract date from titan_analysis_YYYYMMDD_HHMMSS.html
            try:
                parts = filename.split('_')
                if len(parts) >= 3:
                    date_str = parts[2]
                    time_str = parts[3].replace('.html', '')
                    date = datetime.strptime(date_str + time_str, '%Y%m%d%H%M%S')
                    return f"Titan Analysis - {date.strftime('%B %d, %Y at %I:%M %p')}"
            except:
                pass
        elif filename == 'titan_analysis_latest.html':
            return "Latest Titan Analysis"
        
        return name
    
    def format_file_size(self, size: int) -> str:
        """Format file size in human-readable form"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def get_latest_prices(self) -> Dict[str, float]:
        """Get latest crypto prices from cache"""
        try:
            cache_file = os.path.join(self.base_dir, 'data', 'cache', 'price_cache.json')
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    cache = json.load(f)
                    if cache and isinstance(cache, dict):
                        # Get the most recent entry
                        latest_key = max(cache.keys())
                        prices = cache[latest_key]
                        # Ensure we return a dict
                        if isinstance(prices, dict):
                            return prices
                        else:
                            return {'ETH': 0, 'WILD': 0}
        except Exception as e:
            logger.error(f"Error reading price cache: {e}")
        
        return {'ETH': 0, 'WILD': 0}
    
    def generate_html(self, dashboards: Dict[str, List[Dict]]) -> str:
        """Generate the main index HTML"""
        prices = self.get_latest_prices()
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wilder World Crypto Analytics Hub</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
            color: #ffffff;
            min-height: 100vh;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            padding: 40px 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            margin-bottom: 40px;
            backdrop-filter: blur(10px);
        }}
        
        .header h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #00ff88, #00aaff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .header p {{
            font-size: 1.2em;
            color: #aaaaaa;
        }}
        
        .status-bar {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 20px 0;
            flex-wrap: wrap;
        }}
        
        .status-item {{
            background: rgba(255, 255, 255, 0.1);
            padding: 10px 20px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .status-label {{
            color: #888;
            font-size: 0.9em;
        }}
        
        .status-value {{
            font-size: 1.2em;
            font-weight: bold;
            color: #00ff88;
        }}
        
        .actions {{
            text-align: center;
            margin: 30px 0;
        }}
        
        .btn {{
            display: inline-block;
            padding: 12px 30px;
            background: linear-gradient(45deg, #00ff88, #00aaff);
            color: #000;
            text-decoration: none;
            border-radius: 30px;
            font-weight: bold;
            margin: 0 10px;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
            font-size: 1em;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0, 255, 136, 0.3);
        }}
        
        .btn-secondary {{
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
        }}
        
        .category {{
            margin-bottom: 40px;
        }}
        
        .category-header {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
        }}
        
        .category-icon {{
            font-size: 2em;
        }}
        
        .category-info h2 {{
            font-size: 1.8em;
            margin-bottom: 5px;
        }}
        
        .category-info p {{
            color: #aaa;
            font-size: 0.9em;
        }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }}
        
        .dashboard-card {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .dashboard-card:hover {{
            background: rgba(255, 255, 255, 0.08);
            border-color: rgba(0, 255, 136, 0.5);
            transform: translateY(-2px);
        }}
        
        .dashboard-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #00ff88, #00aaff);
            transform: scaleX(0);
            transition: transform 0.3s ease;
        }}
        
        .dashboard-card:hover::before {{
            transform: scaleX(1);
        }}
        
        .dashboard-title {{
            font-size: 1.3em;
            margin-bottom: 10px;
            color: #fff;
        }}
        
        .dashboard-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            font-size: 0.85em;
            color: #888;
        }}
        
        .dashboard-actions {{
            display: flex;
            gap: 10px;
        }}
        
        .card-btn {{
            flex: 1;
            padding: 8px 16px;
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
            text-decoration: none;
            border-radius: 5px;
            text-align: center;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .card-btn:hover {{
            background: rgba(0, 255, 136, 0.2);
            border-color: rgba(0, 255, 136, 0.5);
        }}
        
        .empty-state {{
            text-align: center;
            padding: 40px;
            color: #666;
        }}
        
        .footer {{
            text-align: center;
            padding: 40px 20px;
            margin-top: 60px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            color: #666;
        }}
        
        .refresh-info {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 20px;
            margin: 30px 0;
        }}
        
        .refresh-info h3 {{
            margin-bottom: 15px;
            color: #00ff88;
        }}
        
        .refresh-commands {{
            background: rgba(0, 0, 0, 0.3);
            padding: 15px;
            border-radius: 5px;
            font-family: monospace;
            margin: 10px 0;
        }}
        
        .command {{
            display: block;
            margin: 5px 0;
            color: #00aaff;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 2em;
            }}
            
            .dashboard-grid {{
                grid-template-columns: 1fr;
            }}
            
            .status-bar {{
                flex-direction: column;
                align-items: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌟 Wilder World Analytics Hub</h1>
            <p>Your comprehensive dashboard for WILD token and portfolio analysis</p>
            
            <div class="status-bar">
                <div class="status-item">
                    <span class="status-label">WILD Price:</span>
                    <span class="status-value">${prices.get('WILD', 0):.4f}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">ETH Price:</span>
                    <span class="status-value">${prices.get('ETH', 0):.2f}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Last Update:</span>
                    <span class="status-value">{datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
                </div>
            </div>
        </div>
        
        <div class="actions">
            <button class="btn" onclick="refreshAll()">🔄 Refresh All Dashboards</button>
            <a href="titan_reports/titan_analysis_latest.html" class="btn btn-secondary">📊 Latest Titan Analysis</a>
        </div>
"""
        
        # Add categories and dashboards
        for category_id, category_info in self.categories.items():
            category_dashboards = dashboards.get(category_id, [])
            
            html += f"""
        <div class="category">
            <div class="category-header">
                <div class="category-icon">{category_info['icon']}</div>
                <div class="category-info">
                    <h2>{category_info['name']}</h2>
                    <p>{category_info['description']}</p>
                </div>
            </div>
            
            <div class="dashboard-grid">
"""
            
            if category_dashboards:
                for dashboard in category_dashboards:
                    html += f"""
                <div class="dashboard-card">
                    <h3 class="dashboard-title">{dashboard['display_name']}</h3>
                    <div class="dashboard-meta">
                        <span>📅 {dashboard['modified_str']}</span>
                        <span>📁 {dashboard['size_str']}</span>
                    </div>
                    <div class="dashboard-actions">
                        <a href="{dashboard['path']}" class="card-btn">View Dashboard</a>
                    </div>
                </div>
"""
            else:
                html += """
                <div class="empty-state">
                    <p>No dashboards found in this category.</p>
                    <p>Run the analysis scripts to generate dashboards.</p>
                </div>
"""
            
            html += """
            </div>
        </div>
"""
        
        # Add refresh instructions
        html += """
        <div class="refresh-info">
            <h3>🔄 How to Refresh Dashboards</h3>
            <p>You can update your dashboards using these commands:</p>
            
            <div class="refresh-commands">
                <span class="command"># Refresh everything (recommended)</span>
                <span class="command">python refresh_all_dashboards.py</span>
            </div>
            
            <div class="refresh-commands">
                <span class="command"># Update Operation Titan analysis only</span>
                <span class="command">python run_titan_analysis.py</span>
            </div>
            
            <div class="refresh-commands">
                <span class="command"># Update wallet analysis and visualizations</span>
                <span class="command">python test_setup.py</span>
            </div>
            
            <div class="refresh-commands">
                <span class="command"># Start automated monitoring (runs continuously)</span>
                <span class="command">python src/titan_automation.py</span>
            </div>
        </div>
        
        <div class="footer">
            <p>Wilder World Analytics Hub | Last generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Made with 💚 for tracking WILD token and Operation Titan</p>
        </div>
    </div>
    
    <script>
        function refreshAll() {{
            if (confirm('This will refresh all dashboards by running the analysis scripts. Continue?')) {{
                alert('To refresh all dashboards, run: python refresh_all_dashboards.py');
            }}
        }}
        
        // Auto-refresh page every 5 minutes
        setTimeout(() => {{
            location.reload();
        }}, 300000);
    </script>
</body>
</html>
"""
        
        return html
    
    def generate_dashboard(self) -> str:
        """Main method to generate the dashboard"""
        logger.info("Generating main dashboard index...")
        
        # Scan for existing dashboards
        dashboards = self.scan_dashboards()
        
        # Generate HTML
        html = self.generate_html(dashboards)
        
        # Save to file
        output_path = os.path.join(self.output_dir, 'index.html')
        with open(output_path, 'w') as f:
            f.write(html)
        
        logger.info(f"Main dashboard saved to: {output_path}")
        return output_path

def main():
    """Generate the main dashboard"""
    dashboard = MainDashboard()
    output_path = dashboard.generate_dashboard()
    print(f"\n✅ Main dashboard generated successfully!")
    print(f"📍 Location: {output_path}")
    print(f"\n🌐 Open in browser: file://{os.path.abspath(output_path)}")

if __name__ == "__main__":
    main()