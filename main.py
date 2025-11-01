#!/usr/bin/env python3
"""Main application for crypto technical analysis."""

import sys
from colorama import Fore, Style, init
from tabulate import tabulate
from typing import List, Dict

from config import Config
from cointracker_client import CoinTrackerClient
from market_data import MarketDataProvider
from technical_analysis import TechnicalAnalyzer
from recommendation_engine import RecommendationEngine, prioritize_recommendations


# Initialize colorama for cross-platform colored output
init(autoreset=True)


def print_header():
    """Print application header."""
    print("\n" + "=" * 80)
    print(f"{Fore.CYAN}{Style.BRIGHT}Crypto Technical Analysis Dashboard{Style.RESET_ALL}".center(80))
    print("=" * 80 + "\n")


def print_section_header(title: str):
    """Print a section header."""
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}{'─' * 80}")
    print(f"{title}")
    print(f"{'─' * 80}{Style.RESET_ALL}\n")


def format_signal_color(signal: str) -> str:
    """Get color formatting for a signal."""
    colors = {
        'strong_buy': Fore.GREEN + Style.BRIGHT,
        'buy': Fore.GREEN,
        'hold': Fore.YELLOW,
        'sell': Fore.RED,
        'strong_sell': Fore.RED + Style.BRIGHT,
    }
    return colors.get(signal, '')


def display_portfolio_summary(holdings: List[Dict], total_value: float):
    """Display portfolio summary."""
    print_section_header("📊 Portfolio Summary")
    
    table_data = []
    for holding in holdings:
        table_data.append([
            holding['symbol'],
            holding['name'],
            f"{holding['amount']:.4f}",
            f"${holding['price_usd']:.2f}",
            f"${holding['value_usd']:.2f}"
        ])
    
    headers = ['Symbol', 'Name', 'Amount', 'Price', 'Value (USD)']
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    print(f"\n{Fore.CYAN}{Style.BRIGHT}Total Portfolio Value: ${total_value:,.2f}{Style.RESET_ALL}\n")


def display_recommendation(rec: Dict):
    """Display a single recommendation."""
    signal = rec['signal']
    color = format_signal_color(signal)
    
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{'═' * 80}")
    print(f"{rec['symbol']} - ${rec['current_price']:.2f} | "
          f"Holdings Value: ${rec['holding_value']:,.2f}")
    print(f"{'═' * 80}{Style.RESET_ALL}\n")
    
    # Signal and summary
    print(f"{color}{rec['summary']}{Style.RESET_ALL}\n")
    
    # Confidence
    conf_color = Fore.GREEN if rec['confidence'] == 'high' else Fore.YELLOW if rec['confidence'] == 'medium' else Fore.WHITE
    print(f"Confidence: {conf_color}{rec['confidence'].upper()}{Style.RESET_ALL}\n")
    
    # Alerts (if any)
    if rec['alerts']:
        print(f"{Fore.YELLOW}{Style.BRIGHT}🔔 ALERTS:{Style.RESET_ALL}")
        for alert in rec['alerts']:
            print(f"  {alert}")
        print()
    
    # Reasons
    if rec['reasons']:
        print(f"{Style.BRIGHT}Analysis:{Style.RESET_ALL}")
        for reason in rec['reasons']:
            print(f"  {reason}")
        print()


def display_all_recommendations(recommendations: List[Dict]):
    """Display all recommendations."""
    print_section_header("📈 Technical Analysis Recommendations")
    
    # Prioritize recommendations
    sorted_recs = prioritize_recommendations(recommendations)
    
    for rec in sorted_recs:
        display_recommendation(rec)


def display_alerts_summary(recommendations: List[Dict]):
    """Display a summary of all alerts."""
    all_alerts = []
    for rec in recommendations:
        all_alerts.extend(rec.get('alerts', []))
    
    if not all_alerts:
        return
    
    print_section_header("🚨 Alert Summary")
    
    for alert in all_alerts:
        # Color code alerts based on content
        if '🚀' in alert or '💡' in alert:
            print(f"{Fore.GREEN}{alert}{Style.RESET_ALL}")
        elif '⚠️' in alert or '📉' in alert:
            print(f"{Fore.RED}{alert}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}{alert}{Style.RESET_ALL}")


def display_action_summary(recommendations: List[Dict]):
    """Display action summary by signal type."""
    print_section_header("📋 Action Summary")
    
    signal_groups = {
        'strong_buy': [],
        'buy': [],
        'hold': [],
        'sell': [],
        'strong_sell': []
    }
    
    for rec in recommendations:
        signal_groups[rec['signal']].append(rec['symbol'])
    
    table_data = []
    for signal, symbols in signal_groups.items():
        if symbols:
            color = format_signal_color(signal)
            signal_display = signal.replace('_', ' ').upper()
            symbols_str = ', '.join(symbols)
            table_data.append([
                f"{color}{signal_display}{Style.RESET_ALL}",
                f"{len(symbols)}",
                symbols_str
            ])
    
    if table_data:
        headers = ['Signal', 'Count', 'Assets']
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
    else:
        print("No recommendations available.")


def main():
    """Main application entry point."""
    try:
        # Validate configuration
        Config.validate()
        
        print_header()
        print(f"{Fore.CYAN}Fetching your portfolio from CoinTracker...{Style.RESET_ALL}")
        
        # Initialize clients
        cointracker = CoinTrackerClient()
        market_data = MarketDataProvider()
        
        # Fetch holdings
        holdings = cointracker.get_holdings()
        
        if not holdings:
            print(f"\n{Fore.YELLOW}No holdings found in your CoinTracker portfolio.{Style.RESET_ALL}")
            print("Please make sure you have assets tracked in CoinTracker.")
            return
        
        total_value = sum(h['value_usd'] for h in holdings)
        
        # Display portfolio summary
        display_portfolio_summary(holdings, total_value)
        
        print(f"\n{Fore.CYAN}Analyzing {len(holdings)} asset(s)...{Style.RESET_ALL}\n")
        
        # Analyze each holding
        recommendations = []
        
        for i, holding in enumerate(holdings, 1):
            symbol = holding['symbol']
            print(f"  [{i}/{len(holdings)}] Analyzing {symbol}...", end='\r')
            
            # Get historical price data
            price_data = market_data.get_historical_prices(symbol)
            
            if price_data is None or len(price_data) < 50:
                print(f"  [{i}/{len(holdings)}] {symbol} - {Fore.YELLOW}⚠️  Insufficient data{Style.RESET_ALL}")
                continue
            
            # Perform technical analysis
            analyzer = TechnicalAnalyzer(price_data)
            
            # Generate recommendation
            engine = RecommendationEngine(
                analyzer=analyzer,
                symbol=symbol,
                holding_value=holding['value_usd']
            )
            
            recommendation = engine.generate_recommendation()
            recommendations.append(recommendation)
            
            print(f"  [{i}/{len(holdings)}] {symbol} - {Fore.GREEN}✓ Complete{Style.RESET_ALL}        ")
        
        if not recommendations:
            print(f"\n{Fore.YELLOW}Could not generate recommendations. "
                  f"Please check your holdings and try again.{Style.RESET_ALL}")
            return
        
        # Display results
        print()  # Clear line
        display_alerts_summary(recommendations)
        display_action_summary(recommendations)
        display_all_recommendations(recommendations)
        
        # Footer
        print(f"\n{Fore.CYAN}{'═' * 80}")
        print(f"Analysis complete! Found {len(recommendations)} recommendations.")
        print(f"{'═' * 80}{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}⚠️  Disclaimer: This is for informational purposes only. "
              f"Not financial advice.{Style.RESET_ALL}\n")
        
    except ValueError as e:
        print(f"\n{Fore.RED}{Style.BRIGHT}Configuration Error:{Style.RESET_ALL} {e}\n")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Analysis interrupted by user.{Style.RESET_ALL}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}{Style.BRIGHT}Error:{Style.RESET_ALL} {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

