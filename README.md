# Stock Screener

A Python tool for screening stocks based on various financial metrics.

## Features
- Filter stocks by P/E ratio
- Market cap filtering
- Dividend yield screening
- Technical indicator analysis

## Installation
```bash
pip install -r requirements.txt
```

## Usage

Basic screening:
```bash
python screener.py --min-pe 10 --max-pe 20 --min-market-cap 1000000000
```

Screen specific symbols:
```bash
python screener.py --symbols AAPL MSFT GOOGL --min-pe 15 --max-pe 25
```

Export results to CSV:
```bash
python screener.py --min-pe 10 --max-pe 30 --export results.csv
```

## Examples

Filter stocks with P/E ratio between 10-25 and minimum market cap of $1B:
```bash
python screener.py --min-pe 10 --max-pe 25 --min-market-cap 1000000000
```