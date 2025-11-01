# Crypto Technical Analysis Dashboard

A Python application that connects to your Coinbase account and provides technical analysis with buy/sell/hold recommendations for your cryptocurrency holdings.

## Features

- 📊 **Portfolio Integration**: Automatically fetches your holdings from Coinbase
- 📈 **Technical Analysis**: Calculates multiple indicators including:
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - Moving Averages (SMA, EMA)
  - Bollinger Bands
  - Stochastic Oscillator
  - ATR (Average True Range)
- 🚨 **Smart Alerts**: Flags important conditions like:
  - Oversold/Overbought conditions
  - Bullish/Bearish crossovers
  - Support/Resistance levels
  - Low volatility breakout potential
- 💡 **Actionable Recommendations**: Provides clear buy/sell/hold signals with confidence levels
- 🎯 **Target Price Calculations**: Automatically calculates:
  - Buy/Sell target prices based on support/resistance
  - Stop-loss levels using ATR
  - Risk/reward ratios for each trade
  - Re-entry points for bearish signals
- 📊 **Visual Charts**: Generates comprehensive charts showing:
  - Price action with moving averages
  - Bollinger Bands overlay
  - RSI indicator with overbought/oversold zones
  - MACD histogram and signal lines
  - Volume bars
  - Target price levels marked on charts
- 🎨 **Beautiful CLI**: Colorized output with organized tables and summaries

## Prerequisites

- Python 3.8 or higher
- Coinbase account with crypto holdings
- Coinbase CDP (Cloud Developer Platform) API key

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd crypto-technical-analysis
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your configuration:
```bash
# Copy the example env file
cp env.template .env

# Edit .env and add your Coinbase API credentials
```

## Getting Your Coinbase CDP API Key

1. Log in to [Coinbase Developer Portal](https://portal.cdp.coinbase.com/)
2. Go to "API Keys" section
3. Click "Create API Key"
4. Give it a name (e.g., "Crypto Analysis")
5. Select permissions - **only enable VIEW permissions**:
   - ✅ **View** (required to read your portfolio)
   - ❌ **DO NOT** enable Trade or Transfer permissions
6. Click "Create & Download"
7. Save the downloaded JSON file (e.g., `cdp_api_key.json`)
8. Move the JSON file to a secure location (e.g., your project folder)

**⚠️ Important Security Notes:**
- The JSON file contains your private key - **never share it**
- Store it securely and never commit it to git
- Only grant VIEW permissions to the API key
- You can always revoke keys in the CDP portal
- The JSON file is only shown once - if you lose it, create a new key

## Usage

### **Recommended: Manual Portfolio Input**

The easiest way to use the app (no API keys needed):

```bash
# Activate virtual environment
source venv/bin/activate

# Run with your crypto symbols
python manual_portfolio.py 'BTC,ETH,SOL,ADA'

# Or run interactively and type them in
python manual_portfolio.py
```

The application will:
1. Accept your cryptocurrency symbols (BTC, ETH, SOL, etc.)
2. Retrieve historical price data for each asset
3. Perform technical analysis  
4. Generate recommendations with alerts
5. Display a comprehensive dashboard with actionable insights

### **Alternative: Coinbase API (Advanced)**

If you have a working Coinbase API setup:

```bash
python main.py
```

**Note**: Coinbase's retail API has restricted programmatic access, so the manual input method is recommended for most users.

## Configuration

Edit the `.env` file and point it to your API key JSON file:

```bash
# Coinbase CDP API Configuration
COINBASE_API_KEY_FILE=/Users/yourusername/crypto-technical-analysis/cdp_api_key.json

# Analysis Preferences
RSI_OVERSOLD=30          # RSI level for oversold condition
RSI_OVERBOUGHT=70        # RSI level for overbought condition
MIN_PORTFOLIO_VALUE=100  # Minimum USD value to analyze
```

**Setup Steps:**
1. Move your downloaded `cdp_api_key.json` (or similar name) to your project folder
2. Create a `.env` file: `cp env.template .env`
3. Edit `.env` and set `COINBASE_API_KEY_FILE` to the full path of your JSON file

## Understanding the Output

### Signal Types

- 🟢 **STRONG BUY**: Multiple bullish indicators, score > 50
- 🟢 **BUY**: Bullish indicators, score 20-50
- 🟡 **HOLD**: Neutral indicators, score -20 to 20
- 🔴 **SELL**: Bearish indicators, score -50 to -20
- 🔴 **STRONG SELL**: Multiple bearish indicators, score < -50

### Confidence Levels

- **HIGH**: 6+ indicators supporting the signal
- **MEDIUM**: 4-5 indicators supporting the signal
- **LOW**: Less than 4 indicators

### Alert Types

- 🚀 Bullish crossover detected
- 📉 Bearish crossover detected
- 💡 Interesting opportunity or condition
- ⚠️  Warning or caution needed
- 🔔 Important notification

## Technical Indicators Explained

### RSI (Relative Strength Index)
- Measures momentum on a scale of 0-100
- < 30: Oversold (potential buy)
- > 70: Overbought (potential sell)

### MACD (Moving Average Convergence Divergence)
- Shows relationship between two moving averages
- Bullish when MACD line crosses above signal line
- Bearish when MACD line crosses below signal line

### Moving Averages
- SMA 20/50: Simple moving averages
- EMA 12/26: Exponential moving averages
- Price above MA: Bullish trend
- Price below MA: Bearish trend

### Bollinger Bands
- Shows price volatility
- Price at upper band: Overbought
- Price at lower band: Oversold
- Narrow bands: Low volatility, potential breakout

## Limitations & Disclaimers

⚠️ **Important**: This tool is for informational and educational purposes only. It is NOT financial advice.

- Technical analysis is not foolproof
- Past performance doesn't guarantee future results
- Always do your own research (DYOR)
- Consider multiple factors before making investment decisions
- Consult with a financial advisor for investment advice

## Troubleshooting

### "No holdings found"
- Verify your `COINBASE_API_KEY_FILE` path is correct in `.env`
- Make sure you have crypto assets in your Coinbase account (not just USD)
- Check that your API key has VIEW permissions enabled
- Make sure the JSON file is valid and contains both `name` and `privateKey` fields
- Try creating a new API key in the CDP portal

### "Insufficient data"
- Some cryptocurrencies may not have enough historical data
- Try again later as more data becomes available

### Rate Limiting
- The app includes built-in rate limiting
- If you hit API limits, wait a few minutes and try again

## API Data Sources

- **Portfolio Data**: Coinbase CDP (Cloud Developer Platform) API v3
- **Market Data**: CoinGecko API (free, no API key required)

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review [Coinbase CDP API documentation](https://docs.cdp.coinbase.com/advanced-trade/docs/welcome)
3. Open an issue on GitHub

---

**Disclaimer**: Cryptocurrency investments carry risk. This tool does not provide financial advice. Always conduct your own research and consult with qualified financial advisors before making investment decisions.

