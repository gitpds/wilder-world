# Wilder World Ethereum Data Analysis

## Project Overview

This project provides a comprehensive analysis of all Ethereum blockchain interactions between personal wallets and the Wilder World ecosystem, including:
- WILD token transactions and holdings
- NFT collection transfers and ownership
- Uniswap LP token provisions and staking activities
- Complete cost basis analysis in ETH and USD
- Inter-wallet transfer tracking
- Gas fee aggregation and analysis

## Data Sources

### APIs (Free Tier)
1. **Etherscan API**
   - API Key: `SW6MCW34PNJJZ48JPZJSSYWIC3SE3VTZZU` (from readme.MD)
   - Endpoints: Account transactions, token transfers, NFT transfers
   - Rate Limit: 5 calls/second

2. **CoinGecko API**
   - No API key required for basic usage
   - Historical ETH/USD price data
   - WILD token price tracking

### Wallet Addresses
From `readme.MD`:
- **Hot Wallet**: `0x2C9fcff5ee4F43E2A42FA6b79c14664CC69696DE`
- **Digital Real Estate Wallet**: `0x54c1a42aa00A44c311BEc1F60cc4540F26c06b71`
- **ETH Staking Node**: `0xc3455f9B8119ECDF2a56E0E771c39E954a09dA97`
- **Warm Wallet**: `0x89eb314457aD6C5Ce6e84B72c4581181bB2b765A`

### Wilder World Contract Addresses
From `wilderworld.MD`:

#### Token Contracts
- **WILD Token**: `0x2a3bff78b79a009976eea096a51a948a3dc00e34`
- **Uniswap V2 WILD/ETH LP**: `0xcaa004418eb42cdf00cb057b7c9e28f0ffd840a5`

#### NFT Collections
- **AirWild Season 0**: `0x1c42576aca321a590a809cd8b18492aafc1f3909`
- **AirWild Season 1**: `0x4d8165cb6861253e9edfbac2f41a386ba1a0a175`
- **AirWild Season 2**: `0x35d2f3cdaf5e2dea9e6ae3553a4caacba860a395`
- **Wheels**: `0xc2e9678A71e50E5AEd036e00e9c5caeb1aC5987D`
- **Cribs**: `0xc3b5284B2C0cfa1871a6ac63B6d6ee43c08BDC79`
- **Crafts**: `0x8b9c0c24307344B6D7941ab654b2aeee25347473`
- **Land**: `0x2a46f2ffd99e19a89476e2f62270e0a35bbf0756`
- **Beasts Wolves**: `0x1a178cfd768f74b3308cbca9998c767f4e5b2cf8`
- **Beasts Wapes**: `0x05F81F870cBca79E9171f22886b58b5597A603AA`
- **Moto**: `0x51bd5948cf84a1041d2720f56ded5e173396fc95`
- **PALs GENs**: `0x90a1f4B78Fa4198BB620b7686f510FD476Ec7A0B`

## Environment Setup

### Project Structure
```
crypto/
├── Wilder EDA.md (this file)
├── wilder_world_analysis.ipynb (main notebook)
├── config/
│   └── .env (API keys and settings)
├── data/
│   ├── raw/ (API responses)
│   ├── processed/ (cleaned data)
│   └── cache/ (price data cache)
├── src/
│   ├── data_collection.py
│   ├── price_fetcher.py
│   ├── analysis_functions.py
│   └── visualization.py
└── output/
    ├── reports/
    └── visualizations/
```

## Analysis Components

### 1. WILD Token Analysis
- **Token Purchases**: Track all WILD token acquisitions
- **Token Sales**: Monitor any WILD token disposals
- **Current Holdings**: Calculate current balance across all wallets
- **Average Cost Basis**: Determine average purchase price
- **Staking Deposits**: Track tokens locked in staking contracts

### 2. Uniswap LP Analysis
- **Liquidity Provisions**: When and how much liquidity was added
- **LP Token Minting**: Track LP tokens received
- **LP Token Burning**: Monitor liquidity removals
- **Impermanent Loss**: Calculate IL based on price movements
- **Fee Earnings**: Estimate trading fee accumulation

### 3. NFT Collection Analysis
- **Acquisition History**: When each NFT was acquired
- **Transfer Patterns**: Track movements between wallets
- **Current Holdings**: Inventory by collection and wallet
- **Gas Costs**: ETH spent on minting/transfers
- **Collection Statistics**: Rarity, floor prices (if available)

### 4. Staking Analysis
- **Staking Timeline**: When stakes were initiated
- **Staked Amounts**: WILD tokens and LP tokens staked
- **Lock Periods**: 12-month lock tracking
- **Reward Projections**: Estimated rewards (if available)
- **Unlock Schedule**: When tokens become available

### 5. Gas Cost Analysis
- **Transaction Types**: Categorize by operation type
- **Historical ETH Costs**: Total ETH spent on gas
- **USD Value at Time**: Convert using historical prices
- **Optimization Opportunities**: Identify high-cost patterns

### 6. Inter-Wallet Analysis
- **Transfer Matrix**: Visualize transfers between owned wallets
- **Asset Movement**: Track NFT and token movements
- **Consolidation Patterns**: Identify wallet usage patterns

### 7. Investment Summary
- **Total Invested**: 
  - ETH spent on purchases
  - ETH spent on gas
  - USD value at time of investment
- **Current Value**:
  - WILD token holdings
  - LP token value
  - NFT collection value
- **Realized Gains/Losses**: From any sales
- **Unrealized Gains/Losses**: Current vs cost basis
- **ROI Calculation**: Overall and by asset type

## Implementation Plan

### Phase 1: Data Collection (Week 1)
1. Set up Etherscan API integration
2. Implement transaction fetching for all wallets
3. Create data caching system
4. Build price data fetcher

### Phase 2: Data Processing (Week 1-2)
1. Parse and categorize transactions
2. Build inter-wallet transfer detection
3. Calculate LP token positions
4. Process staking events

### Phase 3: Analysis & Visualization (Week 2)
1. Create Jupyter notebook structure
2. Implement analysis functions
3. Build interactive visualizations
4. Generate summary reports

### Phase 4: Reporting (Week 2)
1. Create exportable reports
2. Build dashboard visualizations
3. Document findings
4. Prepare presentation materials

## Key Metrics to Track

### Financial Metrics
- Total ETH invested
- Total USD invested (at time)
- Current portfolio value
- Realized P&L
- Unrealized P&L
- Gas efficiency ratio

### Activity Metrics
- Transaction count by type
- Active trading periods
- Wallet utilization
- Collection diversity
- Staking participation rate

### Risk Metrics
- Concentration risk (by asset)
- Liquidity risk (locked tokens)
- Impermanent loss exposure
- Gas cost percentage

## Deliverables

1. **Jupyter Notebook**: Interactive analysis with all code and visualizations
2. **Executive Summary**: High-level findings and insights
3. **Detailed Reports**: 
   - Transaction history CSV
   - Holdings snapshot
   - P&L statement
4. **Visualizations**:
   - Portfolio composition charts
   - Timeline visualizations
   - Transfer flow diagrams
   - Performance dashboards

## Success Criteria

- Complete transaction history for all wallets
- Accurate cost basis calculations
- Clear visualization of asset flows
- Actionable insights for portfolio optimization
- Exportable data for tax/accounting purposes

## Notes

- All API calls use free tiers only
- Historical price data cached to minimize API calls
- Analysis covers from wallet creation to present
- Inter-wallet transfers excluded from P&L calculations
- Staking rewards subject to 12-month lock period