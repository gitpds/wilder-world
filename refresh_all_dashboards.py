#!/usr/bin/env python3
"""
Refresh All Dashboards - Updates all crypto analysis dashboards
"""

import os
import sys
import subprocess
import time
import logging
import shlex
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DashboardRefresher:
    """Handles refreshing all crypto analysis dashboards"""
    
    def __init__(self):
        """Initialize the refresher"""
        self.base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.scripts = {
            'wallet_analysis': {
                'name': 'Wallet Analysis & Visualizations',
                'script': 'test_setup.py',
                'description': 'Updates wallet holdings, transactions, and portfolio visualizations'
            },
            'titan_analysis': {
                'name': 'Operation Titan Analysis',
                'script': 'run_titan_analysis.py',
                'description': 'Updates DAO buyback tracking and price impact analysis'
            },
            'main_dashboard': {
                'name': 'Main Dashboard Index',
                'script': 'src/main_dashboard.py',
                'description': 'Regenerates the main navigation hub'
            }
        }
        
    def run_script(self, script_path: str, name: str) -> bool:
        """Run a Python script and capture output"""
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"🚀 Running {name}...")
            logger.info(f"{'='*60}")
            
            # Activate conda environment and run script securely
            # Validate script path
            script_abs_path = os.path.abspath(os.path.join(self.base_dir, script_path))
            if not script_abs_path.startswith(str(self.base_dir)):
                raise ValueError(f"Script path outside allowed directory: {script_path}")
            
            # Use subprocess with proper escaping
            import shlex
            activate_cmd = 'eval "$(/Users/pdsmbp/miniconda3/bin/conda shell.bash hook)" && conda activate crypto_env'
            full_cmd = f'{activate_cmd} && cd {shlex.quote(str(self.base_dir))} && python {shlex.quote(script_abs_path)}'
            
            # Run the command
            process = subprocess.Popen(
                ['/bin/bash', '-c', full_cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Stream output in real-time
            for line in process.stdout:
                print(f"  {line.rstrip()}")
            
            # Wait for completion
            process.wait()
            
            if process.returncode == 0:
                logger.info(f"✅ {name} completed successfully!")
                return True
            else:
                stderr = process.stderr.read()
                logger.error(f"❌ {name} failed with error:")
                logger.error(stderr)
                return False
                
        except Exception as e:
            logger.error(f"❌ Error running {name}: {e}")
            return False
    
    def refresh_all(self):
        """Refresh all dashboards in sequence"""
        start_time = time.time()
        results = {}
        
        print("\n" + "="*70)
        print("🔄 WILDER WORLD DASHBOARD REFRESH")
        print("="*70)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Run each script
        for script_id, script_info in self.scripts.items():
            print(f"\n📋 {script_info['description']}")
            success = self.run_script(script_info['script'], script_info['name'])
            results[script_id] = success
            
            # Small delay between scripts
            if script_id != list(self.scripts.keys())[-1]:
                time.sleep(2)
        
        # Summary
        elapsed_time = time.time() - start_time
        print("\n" + "="*70)
        print("📊 REFRESH SUMMARY")
        print("="*70)
        
        for script_id, success in results.items():
            status = "✅ Success" if success else "❌ Failed"
            print(f"{self.scripts[script_id]['name']}: {status}")
        
        print(f"\nTotal time: {elapsed_time:.1f} seconds")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Open main dashboard if all successful
        if all(results.values()):
            print("\n✨ All dashboards refreshed successfully!")
            print(f"\n🌐 View your dashboards at:")
            print(f"   file://{self.base_dir}/output/index.html")
            
            # Offer to open in browser
            try:
                response = input("\nOpen dashboard in browser? (y/n): ")
                if response.lower() == 'y':
                    import webbrowser
                    webbrowser.open(f"file://{self.base_dir}/output/index.html")
            except:
                pass
        else:
            print("\n⚠️  Some dashboards failed to refresh. Check the errors above.")
        
        return all(results.values())
    
    def quick_refresh(self, dashboard_type: str = None):
        """Quick refresh for specific dashboard type"""
        if dashboard_type and dashboard_type in self.scripts:
            script_info = self.scripts[dashboard_type]
            print(f"\n🔄 Quick refresh: {script_info['name']}")
            return self.run_script(script_info['script'], script_info['name'])
        else:
            print("Available dashboard types:")
            for key, info in self.scripts.items():
                print(f"  - {key}: {info['description']}")
            return False

def main():
    """Main entry point"""
    refresher = DashboardRefresher()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        dashboard_type = sys.argv[1]
        refresher.quick_refresh(dashboard_type)
    else:
        # Refresh everything
        refresher.refresh_all()

if __name__ == "__main__":
    main()