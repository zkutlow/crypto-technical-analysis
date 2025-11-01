# Crypto Technical Analysis Dashboard

A Python application that connects to your CoinTracker portfolio and provides technical analysis with buy/sell/hold recommendations for your cryptocurrency holdings.

## Features

- 📊 **Portfolio Integration**: Automatically fetches your holdings from CoinTracker
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
- 🎨 **Beautiful CLI**: Colorized output with organized tables and summaries

## Prerequisites

- Python 3.8 or higher
- CoinTracker account with API access
- CoinTracker API key

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
cp .env.example .env

# Edit .env and add your CoinTracker API key
# You can get your API key from: https://www.cointracker.io/settings/api
```

## Getting Your CoinTracker API Key

1. Log in to [CoinTracker](https://www.cointracker.io/)
2. Go to Settings → API
3. Generate a new API key
4. Copy the key and add it to your `.env` file

## Usage

Run the application:

```bash
python main.py
```

The application will:
1. Fetch your portfolio from CoinTracker
2. Retrieve historical price data for each asset
3. Perform technical analysis
4. Generate recommendations with alerts
5. Display a comprehensive dashboard with actionable insights

## Configuration

You can customize the analysis in the `.env` file:

```bash
# CoinTracker API Configuration
COINTRACKER_API_KEY=your_api_key_here

# Analysis Preferences
RSI_OVERSOLD=30          # RSI level for oversold condition
RSI_OVERBOUGHT=70        # RSI level for overbought condition
MIN_PORTFOLIO_VALUE=100  # Minimum USD value to analyze
```

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
- Verify your CoinTracker API key is correct
- Make sure you have assets tracked in CoinTracker
- Check that your API key has proper permissions

### "Insufficient data"
- Some cryptocurrencies may not have enough historical data
- Try again later as more data becomes available

### Rate Limiting
- The app includes built-in rate limiting
- If you hit API limits, wait a few minutes and try again

## API Data Sources

- **Portfolio Data**: CoinTracker API
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
2. Review CoinTracker API documentation
3. Open an issue on GitHub

---

**Disclaimer**: Cryptocurrency investments carry risk. This tool does not provide financial advice. Always conduct your own research and consult with qualified financial advisors before making investment decisions.

