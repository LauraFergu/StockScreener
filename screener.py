#!/usr/bin/env python3
"""
Stock Screener - Filter stocks based on financial metrics
"""

import argparse
import requests
import pandas as pd
from typing import List, Dict, Optional

class StockScreener:
    def __init__(self):
        self.stocks_data = []
    
    def fetch_stock_data(self, symbols: List[str]) -> bool:
        """Fetch stock data from Alpha Vantage API"""
        base_url = "https://www.alphavantage.co/query"
        api_key = "demo"  # Use demo key for testing
        
        for symbol in symbols:
            try:
                params = {
                    'function': 'OVERVIEW',
                    'symbol': symbol,
                    'apikey': api_key
                }
                response = requests.get(base_url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'Symbol' in data:
                        stock_info = {
                            'symbol': data.get('Symbol', ''),
                            'pe_ratio': float(data.get('PERatio', 0)) if data.get('PERatio') != 'None' else 0,
                            'market_cap': float(data.get('MarketCapitalization', 0)) if data.get('MarketCapitalization') else 0,
                            'name': data.get('Name', ''),
                            'sector': data.get('Sector', ''),
                            'dividend_yield': float(data.get('DividendYield', 0)) if data.get('DividendYield') != 'None' else 0
                        }
                        self.stocks_data.append(stock_info)
                        
            except Exception as e:
                print(f"Error fetching data for {symbol}: {str(e)}")
                continue
                
        return len(self.stocks_data) > 0
    
    def filter_by_pe_ratio(self, min_pe: float, max_pe: float) -> List[Dict]:
        """Filter stocks by P/E ratio"""
        # TODO: Implement P/E filtering
        return self.stocks_data
    
    def filter_by_market_cap(self, min_cap: float) -> List[Dict]:
        """Filter stocks by market cap"""
        # TODO: Implement market cap filtering
        return self.stocks_data

def main():
    parser = argparse.ArgumentParser(description='Stock Screener Tool')
    parser.add_argument('--min-pe', type=float, help='Minimum P/E ratio')
    parser.add_argument('--max-pe', type=float, help='Maximum P/E ratio')
    parser.add_argument('--min-market-cap', type=float, help='Minimum market cap')
    parser.add_argument('--symbols', nargs='+', default=['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA'], 
                        help='Stock symbols to screen (default: AAPL GOOGL MSFT TSLA NVDA)')
    
    args = parser.parse_args()
    
    screener = StockScreener()
    print("Stock Screener initialized...")
    print(f"Fetching data for symbols: {args.symbols}")
    
    if screener.fetch_stock_data(args.symbols):
        print(f"Successfully fetched data for {len(screener.stocks_data)} stocks")
        for stock in screener.stocks_data:
            print(f"{stock['symbol']}: {stock['name']} (PE: {stock['pe_ratio']})")
    else:
        print("No stock data retrieved")

if __name__ == '__main__':
    main()