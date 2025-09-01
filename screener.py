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
    
    def filter_by_pe_ratio(self, min_pe: Optional[float] = None, max_pe: Optional[float] = None) -> List[Dict]:
        """Filter stocks by P/E ratio"""
        filtered_stocks = []
        
        for stock in self.stocks_data:
            pe_ratio = stock.get('pe_ratio', 0)
            
            # Skip stocks with no P/E data
            if pe_ratio == 0:
                continue
                
            # Apply min P/E filter
            if min_pe is not None and pe_ratio < min_pe:
                continue
                
            # Apply max P/E filter
            if max_pe is not None and pe_ratio > max_pe:
                continue
                
            filtered_stocks.append(stock)
            
        return filtered_stocks
    
    def filter_by_market_cap(self, stocks: List[Dict], min_cap: Optional[float] = None) -> List[Dict]:
        """Filter stocks by market cap"""
        if min_cap is None:
            return stocks
            
        filtered_stocks = []
        
        for stock in stocks:
            market_cap = stock.get('market_cap', 0)
            
            # Skip stocks with no market cap data
            if market_cap == 0:
                continue
                
            # Apply minimum market cap filter
            if market_cap >= min_cap:
                filtered_stocks.append(stock)
                
        return filtered_stocks

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
        
        # Apply filters
        filtered_stocks = screener.stocks_data
        
        if args.min_pe or args.max_pe:
            filtered_stocks = screener.filter_by_pe_ratio(args.min_pe, args.max_pe)
            print(f"After P/E filtering: {len(filtered_stocks)} stocks remain")
            
        if args.min_market_cap:
            filtered_stocks = screener.filter_by_market_cap(filtered_stocks, args.min_market_cap)
            print(f"After market cap filtering: {len(filtered_stocks)} stocks remain")
        
        print("\nFiltered Results:")
        print("-" * 80)
        print(f"{'Symbol':<8} {'Name':<25} {'P/E':<8} {'Market Cap':<15} {'Sector'}")
        print("-" * 80)
        for stock in filtered_stocks:
            market_cap_str = f"${stock['market_cap']/1e9:.1f}B" if stock['market_cap'] > 0 else "N/A"
            print(f"{stock['symbol']:<8} {stock['name'][:24]:<25} {stock['pe_ratio']:<8.1f} {market_cap_str:<15} {stock['sector']}")
            
    else:
        print("No stock data retrieved")

if __name__ == '__main__':
    main()