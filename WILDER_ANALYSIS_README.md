# Wilder World Ethereum Data Analysis

A comprehensive analysis tool for tracking and analyzing Ethereum blockchain interactions with the Wilder World ecosystem across multiple wallets.

## Overview

This project provides automated analysis of:
- WILD token transactions and holdings
- NFT collection transfers and ownership (11 collections)
- Uniswap LP token provisions and positions
- Complete cost basis analysis in ETH and USD
- Inter-wallet transfer tracking
- Gas fee aggregation and analysis

## Quick Start

### 1. Activate the Conda Environment

```bash
eval "$(conda shell.bash hook)" && conda activate crypto_env
```

### 2. Run the Test Script

Verify everything is set up correctly:

```bash
python test_setup.py
```

### 3. Run the Analysis

#### Option A: Use Jupyter Notebook (Recommended)

```bash
jupyter notebook wilder_world_analysis.ipynb
```

Then run all cells in the notebook to perform the complete analysis.

#### Option B: Run Data Collection Directly

```bash
python src/data_collection.py
```

## Project Structure

```
crypto/
├── config/
│   └── .env                    # API keys and configuration
├── data/
│   ├── raw/                    # Raw API responses (cached)
│   ├── processed/              # Processed data files
│   └── cache/                  # Price data cache
├── src/
│   ├── data_collection.py      # Etherscan API data fetcher
│   ├── price_fetcher.py        # CoinGecko price data
│   ├── analysis_functions.py   # Data analysis logic
│   └── visualization.py        # Chart generation
├── output/
│   ├── reports/                # Excel and JSON reports
│   └── visualizations/         # Interactive HTML charts
├── wilder_world_analysis.ipynb # Main analysis notebook
└── test_setup.py               # Setup verification script
```

## Features

### Data Collection
- Fetches all transaction types (normal, token, NFT, internal)
- Implements rate limiting for API compliance
- Caches responses to minimize API calls
- Handles all 4 wallets in parallel

### Analysis Capabilities
- **WILD Token Analysis**: Balance tracking, purchase/sale history, cost basis
- **NFT Portfolio**: Holdings by collection, transfer history, gas costs
- **LP Position Tracking**: Minting/burning events, current positions
- **Gas Cost Analysis**: Breakdown by transaction type and wallet
- **Inter-wallet Transfers**: Automatic detection and exclusion from P&L

### Visualizations
- Portfolio composition charts
- WILD token distribution by wallet
- NFT holdings heatmap
- Gas cost breakdown
- Transaction timeline
- Inter-wallet transfer flow diagram

### Export Options
- Excel workbook with multiple sheets
- JSON summary data
- Interactive HTML visualizations
- CSV transaction histories

## Configuration

The analysis uses the following wallets (configured in `config/.env`):
- Hot Wallet
- Digital Real Estate Wallet  
- ETH Staking Node
- Warm Wallet

Tracked NFT Collections:
- AirWild (Seasons 0, 1, 2)
- Wheels
- Cribs
- Crafts
- Land
- Beasts (Wolves & Wapes)
- Moto
- PALs GENs

## Output Files

After running the analysis, find your results in:

- `output/reports/wilder_world_analysis.xlsx` - Complete Excel report
- `output/reports/portfolio_summary.json` - Summary data in JSON
- `output/visualizations/*.html` - Interactive charts

## Current Prices

The analysis fetches current prices from CoinGecko for:
- ETH/USD
- WILD/USD

Historical prices are cached to improve performance.

## Notes

- All API calls use free tier endpoints
- Inter-wallet transfers are automatically detected and excluded from P&L calculations
- Gas costs are calculated only for transactions initiated by your wallets
- NFT values are estimates (would require floor price data for accuracy)

## Troubleshooting

If you encounter issues:

1. Run `python test_setup.py` to verify setup
2. Check that the conda environment is activated
3. Ensure API keys are properly set in `config/.env`
4. Check `data/raw/` for cached data files

## Future Enhancements

Potential improvements:
- Integration with NFT marketplace APIs for floor prices
- Real-time Uniswap pool data for accurate LP valuations
- Staking reward tracking when contracts are identified
- Tax report generation
- Automated daily/weekly reports