#!/usr/bin/env python3
"""Crypto technical analysis with manual portfolio input."""

import sys
from colorama import Fore, Style, init
from tabulate import tabulate
from typing import List, Dict

from config import Config
from market_data import MarketDataProvider
from technical_analysis import TechnicalAnalyzer
from recommendation_engine import RecommendationEngine, prioritize_recommendations
from chart_generator import ChartGenerator


# Initialize colorama
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
            f"{holding.get('amount', 'N/A')}",
            f"${holding['price_usd']:.2f}",
            f"${holding['value_usd']:.2f}" if holding['value_usd'] else "N/A"
        ])
    
    headers = ['Symbol', 'Name', 'Amount', 'Price', 'Value (USD)']
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    if total_value:
        print(f"\n{Fore.CYAN}{Style.BRIGHT}Total Portfolio Value: ${total_value:,.2f}{Style.RESET_ALL}\n")


def display_recommendation(rec: Dict):
    """Display a single recommendation."""
    signal = rec['signal']
    color = format_signal_color(signal)
    
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{'═' * 80}")
    print(f"{rec['symbol']} - ${rec['current_price']:.2f}")
    if rec.get('holding_value'):
        print(f"Holdings Value: ${rec['holding_value']:,.2f}")
    print(f"{'═' * 80}{Style.RESET_ALL}\n")
    
    # Signal and summary
    print(f"{color}{rec['summary']}{Style.RESET_ALL}\n")
    
    # Confidence
    conf_color = Fore.GREEN if rec['confidence'] == 'high' else Fore.YELLOW if rec['confidence'] == 'medium' else Fore.WHITE
    print(f"Confidence: {conf_color}{rec['confidence'].upper()}{Style.RESET_ALL}\n")
    
    # Target Prices
    if rec.get('targets'):
        targets = rec['targets']
        print(f"{Fore.CYAN}{Style.BRIGHT}🎯 TARGET PRICES:{Style.RESET_ALL}")
        
        if signal in ['strong_buy', 'buy']:
            if targets.get('buy_target'):
                print(f"  {Fore.GREEN}Buy Target:  ${targets['buy_target']:,.2f}{Style.RESET_ALL}")
            if targets.get('sell_target'):
                profit_pct = ((targets['sell_target'] - targets.get('buy_target', rec['current_price'])) / 
                             targets.get('buy_target', rec['current_price']) * 100)
                print(f"  {Fore.GREEN}Sell Target: ${targets['sell_target']:,.2f} (+{profit_pct:.1f}%){Style.RESET_ALL}")
            if targets.get('stop_loss'):
                loss_pct = ((targets['stop_loss'] - targets.get('buy_target', rec['current_price'])) / 
                           targets.get('buy_target', rec['current_price']) * 100)
                print(f"  {Fore.RED}Stop Loss:   ${targets['stop_loss']:,.2f} ({loss_pct:.1f}%){Style.RESET_ALL}")
            if targets.get('risk_reward_ratio'):
                rr = targets['risk_reward_ratio']
                rr_color = Fore.GREEN if rr >= 2 else Fore.YELLOW if rr >= 1 else Fore.RED
                print(f"  {rr_color}Risk/Reward:  {rr:.2f}:1{Style.RESET_ALL}")
        
        elif signal in ['strong_sell', 'sell']:
            if targets.get('sell_target'):
                print(f"  {Fore.RED}Sell Target: ${targets['sell_target']:,.2f}{Style.RESET_ALL}")
            if targets.get('buy_target'):
                reentry_pct = ((rec['current_price'] - targets['buy_target']) / rec['current_price'] * 100)
                print(f"  {Fore.GREEN}Re-entry:    ${targets['buy_target']:,.2f} (-{reentry_pct:.1f}%){Style.RESET_ALL}")
            if targets.get('stop_loss'):
                print(f"  {Fore.RED}Stop Loss:   ${targets['stop_loss']:,.2f}{Style.RESET_ALL}")
        
        else:  # hold
            if targets.get('buy_target'):
                print(f"  {Fore.YELLOW}Support:     ${targets['buy_target']:,.2f}{Style.RESET_ALL}")
            if targets.get('sell_target'):
                print(f"  {Fore.YELLOW}Resistance:  ${targets['sell_target']:,.2f}{Style.RESET_ALL}")
        
        print()
    
    # Alerts
    if rec.get('alerts'):
        print(f"{Fore.YELLOW}{Style.BRIGHT}🔔 ALERTS:{Style.RESET_ALL}")
        for alert in rec['alerts']:
            print(f"  {alert}")
        print()
    
    # Reasons
    if rec.get('reasons'):
        print(f"{Style.BRIGHT}Analysis:{Style.RESET_ALL}")
        for reason in rec['reasons']:
            print(f"  {reason}")
        print()
    
    # Chart reference
    if rec.get('chart_path'):
        print(f"{Fore.CYAN}📊 Chart saved: {rec['chart_path']}{Style.RESET_ALL}\n")


def display_all_recommendations(recommendations: List[Dict]):
    """Display all recommendations."""
    print_section_header("📈 Technical Analysis Recommendations")
    
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


def get_portfolio_input() -> List[str]:
    """Get portfolio input from user or command line."""
    # Check if symbols were provided as command line arguments
    if len(sys.argv) > 1:
        symbols = [s.strip().upper() for s in sys.argv[1].split(',')]
        symbols = [s for s in symbols if s]
        return symbols
    
    print(f"{Fore.CYAN}Enter the cryptocurrency symbols you want to analyze.{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Examples: BTC, ETH, SOL, ADA, DOGE{Style.RESET_ALL}\n")
    print(f"Enter symbols separated by commas:")
    
    try:
        user_input = input("> ").strip()
    except EOFError:
        print(f"\n{Fore.RED}No input received. Exiting.{Style.RESET_ALL}\n")
        print(f"{Fore.YELLOW}Tip: You can also run: python manual_portfolio.py 'BTC,ETH,SOL'{Style.RESET_ALL}")
        sys.exit(0)
    
    if not user_input:
        print(f"\n{Fore.RED}No symbols entered. Exiting.{Style.RESET_ALL}\n")
        sys.exit(0)
    
    # Parse input
    symbols = [s.strip().upper() for s in user_input.split(',')]
    symbols = [s for s in symbols if s]  # Remove empty strings
    
    return symbols


def main():
    """Main application entry point."""
    try:
        print_header()
        
        # Get portfolio input
        symbols = get_portfolio_input()
        
        print(f"\n{Fore.GREEN}✓ Analyzing {len(symbols)} asset(s): {', '.join(symbols)}{Style.RESET_ALL}\n")
        
        # Initialize market data provider
        market_data = MarketDataProvider()
        
        # Fetch current prices and create holdings list
        holdings = []
        for symbol in symbols:
            price = market_data.get_current_price(symbol)
            if price:
                holdings.append({
                    'symbol': symbol,
                    'name': symbol,
                    'amount': 'N/A',
                    'price_usd': price,
                    'value_usd': 0  # No value since we don't know amount
                })
        
        if not holdings:
            print(f"\n{Fore.YELLOW}Could not fetch price data for any symbols.{Style.RESET_ALL}")
            print("Please check your symbols and try again.")
            return
        
        # Display portfolio summary
        display_portfolio_summary(holdings, 0)
        
        print(f"\n{Fore.CYAN}Analyzing {len(holdings)} asset(s)...{Style.RESET_ALL}\n")
        
        # Initialize chart generator
        chart_gen = ChartGenerator()
        
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
            
            # Generate recommendation (with 0 value since we don't know amount held)
            engine = RecommendationEngine(
                analyzer=analyzer,
                symbol=symbol,
                holding_value=0
            )
            
            recommendation = engine.generate_recommendation()
            
            # Generate chart
            try:
                chart_path = chart_gen.generate_technical_chart(
                    symbol=symbol,
                    price_data=recommendation['price_data'],
                    indicators=recommendation['indicators'],
                    target_prices=recommendation.get('targets')
                )
                recommendation['chart_path'] = chart_path
            except Exception as e:
                print(f"\n  Warning: Could not generate chart for {symbol}: {e}")
                recommendation['chart_path'] = None
            
            recommendations.append(recommendation)
            
            print(f"  [{i}/{len(holdings)}] {symbol} - {Fore.GREEN}✓ Complete{Style.RESET_ALL}        ")
        
        if not recommendations:
            print(f"\n{Fore.YELLOW}Could not generate recommendations.{Style.RESET_ALL}")
            return
        
        # Display results
        print()
        display_alerts_summary(recommendations)
        display_action_summary(recommendations)
        display_all_recommendations(recommendations)
        
        # Footer
        print(f"\n{Fore.CYAN}{'═' * 80}")
        print(f"Analysis complete! Found {len(recommendations)} recommendations.")
        print(f"Charts saved in: ./charts/")
        print(f"{'═' * 80}{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}⚠️  Disclaimer: This is for informational purposes only. "
              f"Not financial advice.{Style.RESET_ALL}\n")
        
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

