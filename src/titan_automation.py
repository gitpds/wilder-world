#!/usr/bin/env python3
"""
Operation Titan Automation
Automated monitoring and alerting for DAO buyback activities
"""

import os
import sys
import json
import time
import schedule
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.titan_tracker import TitanTracker
from src.analysis_functions import WilderAnalyzer
from src.titan_dashboard import TitanDashboard
from src.price_fetcher import PriceFetcher

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TitanAutomation:
    """Automated monitoring and reporting for Operation Titan"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize automation with configuration"""
        self.tracker = TitanTracker()
        self.analyzer = WilderAnalyzer()
        self.dashboard = TitanDashboard()
        self.price_fetcher = PriceFetcher()
        
        # Load configuration
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'automation_config.json')
        
        self.config = self.load_config(config_path)
        
        # State tracking
        self.state_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'automation_state.json')
        self.state = self.load_state()
        
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load automation configuration"""
        default_config = {
            'monitoring': {
                'check_interval_minutes': 60,
                'dao_transaction_threshold_eth': 10,
                'price_change_threshold_pct': 5,
                'volume_spike_threshold_pct': 200
            },
            'alerts': {
                'enabled': True,
                'email': {
                    'enabled': False,
                    'smtp_server': 'smtp.gmail.com',
                    'smtp_port': 587,
                    'from_address': '',
                    'to_addresses': [],
                    'password': ''
                },
                'webhook': {
                    'enabled': False,
                    'url': ''
                },
                'file': {
                    'enabled': True,
                    'path': 'output/alerts'
                }
            },
            'reports': {
                'weekly_day': 0,  # Monday
                'weekly_hour': 9,  # 9 AM
                'auto_open_browser': False
            }
        }
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
                # Merge with defaults
                for key in default_config:
                    if key in loaded_config:
                        default_config[key].update(loaded_config[key])
                return default_config
        else:
            # Save default config
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default configuration at: {config_path}")
            return default_config
    
    def load_state(self) -> Dict[str, Any]:
        """Load automation state"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {
            'last_check': None,
            'last_report': None,
            'dao_balances': {},
            'alerts_sent': []
        }
    
    def save_state(self):
        """Save automation state"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2, default=str)
    
    def check_dao_activity(self) -> List[Dict[str, Any]]:
        """Check for significant DAO activity"""
        alerts = []
        current_balances = self.tracker.check_dao_balances()
        previous_balances = self.state.get('dao_balances', {})
        
        threshold_eth = self.config['monitoring']['dao_transaction_threshold_eth']
        
        for dao_name, current in current_balances.items():
            if 'error' in current:
                continue
                
            previous = previous_balances.get(dao_name, {})
            
            # Check for significant ETH outflows
            if previous and 'eth_balance' in previous:
                eth_change = previous['eth_balance'] - current['eth_balance']
                if eth_change >= threshold_eth:
                    alerts.append({
                        'type': 'dao_eth_outflow',
                        'severity': 'high',
                        'dao': dao_name,
                        'amount_eth': eth_change,
                        'message': f"{dao_name} sent {eth_change:.2f} ETH (potential buyback)",
                        'timestamp': datetime.now()
                    })
            
            # Check for WILD inflows
            if previous and 'wild_balance' in previous:
                wild_change = current['wild_balance'] - previous['wild_balance']
                if wild_change > 100000:  # 100k WILD threshold
                    alerts.append({
                        'type': 'dao_wild_inflow',
                        'severity': 'medium',
                        'dao': dao_name,
                        'amount_wild': wild_change,
                        'message': f"{dao_name} received {wild_change:,.0f} WILD tokens",
                        'timestamp': datetime.now()
                    })
        
        # Update state
        self.state['dao_balances'] = current_balances
        
        return alerts
    
    def check_price_movements(self) -> List[Dict[str, Any]]:
        """Check for significant price movements"""
        alerts = []
        
        try:
            current_prices = self.price_fetcher.get_current_prices()
            if not current_prices or 'WILD' not in current_prices:
                return alerts
                
            current_price = current_prices['WILD']
            previous_price = self.state.get('last_wild_price', current_price)
            
            price_change_pct = ((current_price - previous_price) / previous_price) * 100
            threshold = self.config['monitoring']['price_change_threshold_pct']
            
            if abs(price_change_pct) >= threshold:
                alerts.append({
                    'type': 'price_movement',
                    'severity': 'high' if abs(price_change_pct) > 10 else 'medium',
                    'price': current_price,
                    'change_pct': price_change_pct,
                    'message': f"WILD price {'surged' if price_change_pct > 0 else 'dropped'} "
                              f"{abs(price_change_pct):.1f}% to ${current_price:.4f}",
                    'timestamp': datetime.now()
                })
            
            # Update state
            self.state['last_wild_price'] = current_price
            
        except Exception as e:
            logger.error(f"Error checking price movements: {e}")
            
        return alerts
    
    def check_buyback_progress(self) -> List[Dict[str, Any]]:
        """Check buyback completion milestones"""
        alerts = []
        titan_data = self.tracker.generate_summary_report()
        patterns = titan_data.get('buyback_patterns', {})
        
        # Check for execution delays
        phase_status = titan_data.get('phase_status', {})
        if (phase_status.get('phase2_deadline_status') == 'passed' and 
            patterns.get('execution_status') == 'pending'):
            alerts.append({
                'type': 'execution_delay',
                'severity': 'high',
                'message': 'Phase 2 deadline passed without detected buyback execution',
                'timestamp': datetime.now()
            })
        
        # Check for completion milestones
        completion = self.analyzer.calculate_buyback_completion(titan_data)
        overall_completion = completion.get('overall', 0)
        
        # Alert at 25%, 50%, 75%, 100% milestones
        milestones = [25, 50, 75, 100]
        for milestone in milestones:
            if (overall_completion >= milestone and 
                f'completion_{milestone}' not in self.state.get('alerts_sent', [])):
                alerts.append({
                    'type': 'completion_milestone',
                    'severity': 'medium',
                    'milestone': milestone,
                    'message': f"Operation Titan buybacks reached {milestone}% completion",
                    'timestamp': datetime.now()
                })
                self.state.setdefault('alerts_sent', []).append(f'completion_{milestone}')
        
        return alerts
    
    def send_alerts(self, alerts: List[Dict[str, Any]]):
        """Send alerts through configured channels"""
        if not alerts or not self.config['alerts']['enabled']:
            return
            
        # File alerts (always enabled as fallback)
        if self.config['alerts']['file']['enabled']:
            alert_dir = os.path.join(os.path.dirname(__file__), '..', 
                                   self.config['alerts']['file']['path'])
            os.makedirs(alert_dir, exist_ok=True)
            
            alert_file = os.path.join(alert_dir, f'alerts_{datetime.now().strftime("%Y%m%d")}.json')
            existing_alerts = []
            if os.path.exists(alert_file):
                with open(alert_file, 'r') as f:
                    existing_alerts = json.load(f)
            
            existing_alerts.extend([{**alert, 'timestamp': str(alert['timestamp'])} 
                                  for alert in alerts])
            
            with open(alert_file, 'w') as f:
                json.dump(existing_alerts, f, indent=2)
            
            # Also create latest file
            latest_file = os.path.join(alert_dir, 'alerts_latest.json')
            with open(latest_file, 'w') as f:
                json.dump(alerts[-10:], f, indent=2, default=str)  # Last 10 alerts
        
        # Email alerts
        if self.config['alerts']['email']['enabled']:
            self.send_email_alerts(alerts)
        
        # Webhook alerts (for Discord, Slack, etc.)
        if self.config['alerts']['webhook']['enabled']:
            self.send_webhook_alerts(alerts)
    
    def send_email_alerts(self, alerts: List[Dict[str, Any]]):
        """Send email alerts"""
        try:
            email_config = self.config['alerts']['email']
            if not email_config['from_address'] or not email_config['to_addresses']:
                logger.warning("Email alerts enabled but not configured")
                return
                
            # Create email content
            high_severity = [a for a in alerts if a['severity'] == 'high']
            subject = f"🚨 Operation Titan Alert: {len(high_severity)} High Priority"
            
            body = "Operation Titan Monitoring Alerts\n\n"
            for alert in alerts:
                emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(alert['severity'], '⚪')
                body += f"{emoji} [{alert['severity'].upper()}] {alert['message']}\n"
                body += f"   Time: {alert['timestamp']}\n\n"
            
            # Send email
            msg = MIMEMultipart()
            msg['From'] = email_config['from_address']
            msg['To'] = ', '.join(email_config['to_addresses'])
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.starttls()
                server.login(email_config['from_address'], email_config['password'])
                server.send_message(msg)
                
            logger.info(f"Sent email alert to {len(email_config['to_addresses'])} recipients")
            
        except Exception as e:
            logger.error(f"Failed to send email alerts: {e}")
    
    def send_webhook_alerts(self, alerts: List[Dict[str, Any]]):
        """Send webhook alerts (Discord/Slack format)"""
        try:
            import requests
            
            webhook_url = self.config['alerts']['webhook']['url']
            if not webhook_url:
                return
                
            for alert in alerts:
                emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(alert['severity'], '⚪')
                
                # Discord webhook format
                payload = {
                    'content': f"{emoji} **Operation Titan Alert**",
                    'embeds': [{
                        'title': alert['type'].replace('_', ' ').title(),
                        'description': alert['message'],
                        'color': {'high': 0xFF0000, 'medium': 0xFFFF00, 'low': 0x00FF00}.get(
                            alert['severity'], 0x808080
                        ),
                        'timestamp': alert['timestamp'].isoformat(),
                        'fields': []
                    }]
                }
                
                # Add specific fields based on alert type
                if alert['type'] == 'dao_eth_outflow':
                    payload['embeds'][0]['fields'].append({
                        'name': 'DAO',
                        'value': alert.get('dao', 'Unknown'),
                        'inline': True
                    })
                    payload['embeds'][0]['fields'].append({
                        'name': 'ETH Amount',
                        'value': f"{alert.get('amount_eth', 0):.2f} ETH",
                        'inline': True
                    })
                
                response = requests.post(webhook_url, json=payload)
                if response.status_code != 204:
                    logger.warning(f"Webhook returned status {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Failed to send webhook alerts: {e}")
    
    def run_monitoring_cycle(self):
        """Run a single monitoring cycle"""
        logger.info("Running monitoring cycle...")
        
        alerts = []
        
        # Check DAO activity
        alerts.extend(self.check_dao_activity())
        
        # Check price movements
        alerts.extend(self.check_price_movements())
        
        # Check buyback progress
        alerts.extend(self.check_buyback_progress())
        
        # Send alerts if any
        if alerts:
            logger.info(f"Found {len(alerts)} alerts")
            self.send_alerts(alerts)
        
        # Update state
        self.state['last_check'] = datetime.now()
        self.save_state()
        
    def generate_weekly_report(self):
        """Generate weekly analysis report"""
        logger.info("Generating weekly report...")
        
        try:
            # Import and run the main analysis
            from run_titan_analysis import run_titan_analysis
            dashboard_path = run_titan_analysis()
            
            # Update state
            self.state['last_report'] = datetime.now()
            self.save_state()
            
            # Create summary alert
            alert = {
                'type': 'weekly_report',
                'severity': 'low',
                'message': f"Weekly Operation Titan report generated: {dashboard_path}",
                'timestamp': datetime.now(),
                'report_path': dashboard_path
            }
            self.send_alerts([alert])
            
            # Open in browser if configured
            if self.config['reports']['auto_open_browser']:
                import webbrowser
                webbrowser.open(f"file://{os.path.abspath(dashboard_path)}")
                
        except Exception as e:
            logger.error(f"Failed to generate weekly report: {e}")
            alert = {
                'type': 'report_error',
                'severity': 'high',
                'message': f"Failed to generate weekly report: {str(e)}",
                'timestamp': datetime.now()
            }
            self.send_alerts([alert])
    
    def setup_schedule(self):
        """Set up automated scheduling"""
        # Monitoring cycles
        interval = self.config['monitoring']['check_interval_minutes']
        schedule.every(interval).minutes.do(self.run_monitoring_cycle)
        
        # Weekly reports
        report_day = self.config['reports']['weekly_day']
        report_hour = self.config['reports']['weekly_hour']
        
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        if 0 <= report_day < 7:
            getattr(schedule.every(), days[report_day]).at(f"{report_hour:02d}:00").do(
                self.generate_weekly_report
            )
        
        logger.info(f"Scheduled monitoring every {interval} minutes")
        logger.info(f"Scheduled weekly reports on {days[report_day]}s at {report_hour}:00")
    
    def run(self):
        """Run the automation service"""
        logger.info("Starting Operation Titan automation service...")
        
        # Run initial cycle
        self.run_monitoring_cycle()
        
        # Set up schedule
        self.setup_schedule()
        
        # Run scheduled tasks
        logger.info("Automation service running. Press Ctrl+C to stop.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Automation service stopped by user")
        except Exception as e:
            logger.error(f"Automation service error: {e}")
            raise

def main():
    """Main entry point for automation"""
    automation = TitanAutomation()
    automation.run()

if __name__ == "__main__":
    main()