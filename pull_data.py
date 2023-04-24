import concurrent.futures
import logging
import sys
import time
from datetime import datetime
from typing import Optional, List

import numpy as np
import pandas as pd
import yfinance as yf

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def download_data(ticker: str, period: str, interval: str) -> Optional[pd.DataFrame]:
    try:
        data = yf.download(tickers=ticker, period=period, interval=interval)
        data['Ticker'] = ticker
        return data
    except Exception as e:
        logging.error(f"Error downloading data for {ticker}: {e}")
        return None


def is_market_open() -> bool:
    now = datetime.now()
    current_time = now.time()
    day_of_week = now.weekday()

    # Check if it's Monday to Friday (0: Monday, 1: Tuesday, ..., 4: Friday)
    if 0 <= day_of_week <= 4:
        # Check if the time is between 9:00 AM and 4:00 PM
        if datetime.strptime("09:00:00", "%H:%M:%S").time() <= current_time <= datetime.strptime("16:00:00", "%H:%M:%S").time():
            return True

    return False


def main():
    tickers = ['BTC-USD', 'ETH-USD', 'USDT-USD', 'BNB-USD', 'USDC-USD', 'XRP-USD', 'ADA-USD', 'DOGE-USD', 'MATIC-USD', 'SOL-USD', 'DOT-USD', 'BUSD-USD', 'LTC-USD', 'SHIB-USD', 'TRX-USD', 'AVAX-USD', 'WBTC-USD', 'LINK-USD', 'FIL-USD', 'TUSD-USD', 'APT21794-USD', 'ARB11841-USD', 'STX4847-USD', 'WBNB-USD', 'CFX-USD', 'GALA-USD', 'ID21846-USD', 'IDEX-USD', 'SRM-USD', 'WETH-USD']
    period = '60d'
    interval = '5m'

    while True:
        if is_market_open():
            for ticker in tickers:
                data = download_data(ticker, period, interval)

                if data is not None:
                    filename = f"{data['Ticker'][0]}.csv"
                    data.to_csv(filename, index=False)
                else:
                    logging.error(f"Failed to download data for {ticker}")

            logging.info("All data downloaded and saved to disk.")
        else:
            logging.info("Market is closed. Waiting for the market to open.")

        time.sleep(5 * 60)  # Sleep for 5 minutes


if __name__ == "__main__":
    main()