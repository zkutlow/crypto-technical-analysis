#!/bin/bash

# Setup script for Crypto Technical Analysis Dashboard

echo "🚀 Setting up Crypto Technical Analysis Dashboard..."
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Found Python $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✓ Virtual environment created"
echo ""
echo "🔧 Activating virtual environment..."

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo "✓ Virtual environment activated"
echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✓ Dependencies installed successfully"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env configuration file..."
    cat > .env << 'EOF'
# Coinbase CDP API Configuration
# Path to your Coinbase CDP API key JSON file (downloaded from Coinbase)
COINBASE_API_KEY_FILE=/path/to/your/cdp_api_key.json

# Analysis Preferences
RSI_OVERSOLD=30
RSI_OVERBOUGHT=70
MIN_PORTFOLIO_VALUE=100
EOF
    echo "✓ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT Setup Steps:"
    echo "   1. Get your Coinbase CDP API key from: https://portal.cdp.coinbase.com/"
    echo "   2. Download the JSON file and move it to this folder"
    echo "   3. Edit .env and set COINBASE_API_KEY_FILE to the full path of your JSON file"
    echo "   4. Only enable VIEW permissions when creating the API key"
else
    echo ""
    echo "✓ .env file already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Get your Coinbase CDP API key (JSON file) from:"
echo "   https://portal.cdp.coinbase.com/"
echo "2. Move the JSON file to this project folder"
echo "3. Edit .env and set COINBASE_API_KEY_FILE to the full path"
echo "4. Activate the virtual environment:"
echo "   source venv/bin/activate  (Linux/Mac)"
echo "   venv\\Scripts\\activate     (Windows)"
echo "5. Run the application:"
echo "   python main.py"
echo ""

