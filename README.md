# Wilder World Analytics Hub

A comprehensive analytics platform for tracking WILD token holdings, analyzing Operation Titan buyback impacts, and monitoring portfolio performance.

## 🌟 Features

### Operation Titan Analysis
- Real-time tracking of 9 DAO treasury wallets participating in the 911 ETH buyback program
- Price impact modeling and supply dynamics analysis
- Automated monitoring with configurable alerts
- Interactive HTML dashboards with Plotly visualizations

### Portfolio Analytics
- Multi-wallet tracking across hot, warm, digital RE, and ETH stake addresses
- WILD token balance monitoring and transaction history
- LP token analysis and exposure calculations
- Inter-wallet transfer visualization
- Gas cost analysis and optimization insights

### Automated Dashboards
- Self-updating HTML dashboards with interactive charts
- Main navigation hub for all analytics
- Historical data tracking and trend analysis
- Mobile-responsive design

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Conda (recommended) or virtual environment
- Etherscan API key
- Infura API key

### Installation

1. Clone the repository:
```bash
git clone [your-repo-url]
cd wilder-world
```

2. Create and activate conda environment:
```bash
conda create -n crypto_env python=3.11
conda activate crypto_env
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp config/.env.example config/.env
# Edit config/.env with your API keys and wallet addresses
```

### Configuration

Create a `config/.env` file with the following variables:
```env
# API Keys
ETHERSCAN_API_KEY=your_etherscan_api_key
INFURA_PROJECT_ID=your_infura_project_id

# Wallet Addresses
HOT_WALLET_ADDRESS=0x...
WARM_WALLET_ADDRESS=0x...
DIGITAL_RE_ADDRESS=0x...
ETH_STAKE_ADDRESS=0x...

# Token Contracts
WILD_TOKEN_CONTRACT=0x2a3bff78b79a009976eea096a51a948a3dc00e34
```

## 📊 Usage

### Refresh All Dashboards
```bash
python refresh_all_dashboards.py
```

### Run Specific Analysis

#### Operation Titan Analysis
```bash
python run_titan_analysis.py
```

#### Wallet Analysis & Visualizations
```bash
python test_setup.py
```

### View Dashboards
After running the analysis, open the main dashboard:
```bash
open output/index.html
```

### Automated Monitoring
Start continuous monitoring (runs every 30 minutes):
```bash
python src/titan_automation.py
```

## 📁 Project Structure

```
wilder-world/
├── config/              # Configuration files
│   └── .env            # Environment variables (not in git)
├── data/               # Data storage
│   ├── raw/            # Raw API responses
│   ├── processed/      # Processed analytics data
│   └── cache/          # Price and data caches
├── src/                # Source code
│   ├── titan_tracker.py        # Operation Titan tracking
│   ├── analysis_functions.py   # Core analysis logic
│   ├── data_collection.py      # Etherscan data fetcher
│   ├── price_fetcher.py        # Price data management
│   ├── visualization.py        # Chart generation
│   ├── titan_dashboard.py      # Dashboard generator
│   ├── titan_automation.py     # Automated monitoring
│   └── main_dashboard.py       # Navigation hub
├── output/             # Generated dashboards
│   ├── index.html     # Main navigation
│   ├── titan_reports/ # Titan analysis reports
│   └── visualizations/# Portfolio charts
└── requirements.txt    # Python dependencies
```

## 🎯 Operation Titan Details

Operation Titan is a multi-phase buyback program where 9 DAOs allocated 911 ETH to purchase WILD tokens:

- **Phase 1**: 455 ETH deployed (completed)
- **Phase 2**: 228 ETH allocation (greenlit July 2025)
- **Phase 3**: 228 ETH reserved

### Participating DAOs
1. Wheels DAO (414 ETH)
2. CyberKongz DAO (159 ETH)
3. WHALE Community (100 ETH)
4. Kong Land Alpha DAO (80 ETH)
5. Wilder Beasts DAO (60 ETH)
6. Wilder Moto DAO (40 ETH)
7. Wilder Crafts DAO (30 ETH)
8. Wilder Cribs DAO (23 ETH)
9. Meow DAO (5 ETH)

## 📈 Analytics Features

### Price Impact Modeling
- Calculates expected price impact from buyback volume
- Models deflationary effects from 80% burn rate
- Provides conservative, base case, and optimistic price targets

### Trading Signals
- Generates buy/hold/sell signals based on:
  - Buyback progress and momentum
  - Price deviation from targets
  - Supply dynamics and burn rate
  - Market sentiment indicators

### Risk Assessment
- Monitors execution risk of DAO commitments
- Tracks market volatility impact
- Analyzes concentration risk
- Evaluates timing considerations

## 🔧 Development

### Running Tests
```bash
python test_setup.py
```

### Adding New Analysis
1. Create new analysis functions in `src/analysis_functions.py`
2. Add visualization in `src/visualization.py`
3. Update dashboard generation in relevant dashboard file
4. Add to refresh scripts if needed

### Contributing
1. Fork the repository
2. Create a feature branch
3. Commit changes with clear messages
4. Submit a pull request

## 📝 Documentation

- `titananalysis.MD` - Detailed Operation Titan program overview
- `wilderworld.MD` - WILD token and ecosystem information
- `WILDER_ANALYSIS_README.md` - Original analysis documentation

## ⚠️ Important Notes

- Never commit `.env` files or API keys
- Data files in `data/` directory are gitignored
- Output HTML files are regenerated on each run
- Use conda environment for consistency

## 🚀 Deployment

This project is designed to be deployed on Render:

1. Connect your GitHub repository to Render
2. Set environment variables in Render dashboard
3. Deploy as a static site or web service
4. Configure automatic deploys on push

## 📞 Support

For issues or questions:
- Check existing documentation
- Review code comments
- Open an issue on GitHub

## 📄 License

This project is for personal portfolio tracking and analysis. Use at your own risk.

---

Made with 💚 for the Wilder World community