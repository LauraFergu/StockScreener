#!/usr/bin/env python3
"""
Stock Screener - Filter stocks based on financial metrics
"""

import argparse
import requests
import pandas as pd
import time
import logging
from typing import List, Dict, Optional
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StockScreener:
    def __init__(self):
        self.stocks_data = []
    
    def fetch_stock_data(self, symbols: List[str]) -> bool:
        """Fetch stock data from Alpha Vantage API with retry logic"""
        logger.info(f"Fetching data for {len(symbols)} symbols")
        
        for symbol in symbols:
            success = False
            for attempt in range(Config.RETRY_ATTEMPTS):
                try:
                    params = {
                        'function': 'OVERVIEW',
                        'symbol': symbol,
                        'apikey': Config.get_api_key()
                    }
                    
                    response = requests.get(
                        Config.API_BASE_URL, 
                        params=params,
                        timeout=Config.REQUEST_TIMEOUT
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if 'Symbol' in data:
                            stock_info = {
                                'symbol': data.get('Symbol', ''),
                                'pe_ratio': self._safe_float(data.get('PERatio')),
                                'market_cap': self._safe_float(data.get('MarketCapitalization')),
                                'name': data.get('Name', ''),
                                'sector': data.get('Sector', ''),
                                'dividend_yield': self._safe_float(data.get('DividendYield'))
                            }
                            self.stocks_data.append(stock_info)
                            logger.info(f"Successfully fetched data for {symbol}")
                            success = True
                            break
                        else:
                            logger.warning(f"No data found for symbol {symbol}")
                    else:
                        logger.warning(f"HTTP {response.status_code} for {symbol}")
                        
                except requests.exceptions.Timeout:
                    logger.warning(f"Timeout for {symbol} (attempt {attempt + 1})")
                except Exception as e:
                    logger.error(f"Error fetching {symbol} (attempt {attempt + 1}): {str(e)}")
                
                if attempt < Config.RETRY_ATTEMPTS - 1:
                    time.sleep(Config.RETRY_DELAY)
            
            if not success:
                logger.error(f"Failed to fetch data for {symbol} after {Config.RETRY_ATTEMPTS} attempts")
                
        return len(self.stocks_data) > 0
    
    def _safe_float(self, value) -> float:
        """Safely convert value to float"""
        if value is None or value == 'None' or value == '':
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
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
    
    def filter_by_dividend_yield(self, stocks: List[Dict], min_yield: Optional[float] = None) -> List[Dict]:
        """Filter stocks by dividend yield"""
        if min_yield is None:
            return stocks
            
        filtered_stocks = []
        
        for stock in stocks:
            dividend_yield = stock.get('dividend_yield', 0)
            
            # Apply minimum dividend yield filter
            if dividend_yield >= min_yield:
                filtered_stocks.append(stock)
                
        return filtered_stocks
    
    def export_to_csv(self, stocks: List[Dict], filename: str) -> bool:
        """Export filtered stocks to CSV file"""
        try:
            df = pd.DataFrame(stocks)
            df.to_csv(filename, index=False)
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {str(e)}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Stock Screener Tool')
    parser.add_argument('--min-pe', type=float, help='Minimum P/E ratio')
    parser.add_argument('--max-pe', type=float, help='Maximum P/E ratio')
    parser.add_argument('--min-market-cap', type=float, help='Minimum market cap')
    parser.add_argument('--min-dividend-yield', type=float, help='Minimum dividend yield percentage')
    parser.add_argument('--symbols', nargs='+', default=Config.DEFAULT_SYMBOLS, 
                        help=f'Stock symbols to screen (default: {" ".join(Config.DEFAULT_SYMBOLS)})')
    parser.add_argument('--export', type=str, help='Export results to CSV file')
    
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
            
        if args.min_dividend_yield:
            filtered_stocks = screener.filter_by_dividend_yield(filtered_stocks, args.min_dividend_yield)
            print(f"After dividend yield filtering: {len(filtered_stocks)} stocks remain")
        
        print("\nFiltered Results:")
        print("-" * 90)
        print(f"{'Symbol':<8} {'Name':<20} {'P/E':<8} {'Market Cap':<12} {'Div Yield':<10} {'Sector'}")
        print("-" * 90)
        for stock in filtered_stocks:
            market_cap_str = f"${stock['market_cap']/1e9:.1f}B" if stock['market_cap'] > 0 else "N/A"
            div_yield_str = f"{stock['dividend_yield']:.2f}%" if stock['dividend_yield'] > 0 else "N/A"
            print(f"{stock['symbol']:<8} {stock['name'][:19]:<20} {stock['pe_ratio']:<8.1f} {market_cap_str:<12} {div_yield_str:<10} {stock['sector']}")
        
        # Export to CSV if requested
        if args.export and filtered_stocks:
            if screener.export_to_csv(filtered_stocks, args.export):
                print(f"\nResults exported to {args.export}")
            else:
                print("\nFailed to export results")
            
    else:
        print("No stock data retrieved")

if __name__ == '__main__':
    main()