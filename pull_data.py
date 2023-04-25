
import logging
import multiprocessing as mp
import sys
import time
from datetime import datetime
from typing import Optional, List

import numpy as np
import pandas as pd
import yfinance as yf
import pushbullet

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def download_data(ticker: str, period: str, interval: Optional[str] = None) -> Optional[pd.DataFrame]:
    try:
        if interval is not None:
            data = yf.download(tickers=ticker, period=period, interval=interval)
        else:
            # This is for downloading data from start to current date at day level
            data = yf.download(tickers=ticker, period=period)
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
        #if datetime.strptime("09:00:00", "%H:%M:%S").time() <= current_time <= datetime.strptime("16:00:00", "%H:%M:%S").time():
        return True

    return False


def download_ticker_data(ticker: str, period: str, interval: Optional[str] = None) -> None:
    data = download_data(ticker, period, interval)
    output_folder = "daily_data" if interval is None else "data"
    if data is not None:
        filename = f"{output_folder}/{data['Ticker'][0]}.csv"
        data.reset_index(inplace=True)
        data.to_csv(filename, index=False)
        logging.info(f"Downloaded data for {ticker}")
    else:
        logging.error(f"Failed to download data for {ticker}")


def download_all_data(tickers: List[str], period: str, interval: Optional[str] = None) -> None:
    with mp.Pool() as pool:
        results = [pool.apply_async(download_ticker_data, args=(ticker, period, interval)) for ticker in tickers]
        for result in results:
            result.get()


def main():
    tickers = ['BTC-USD', 'ETH-USD', 'USDT-USD', 'BNB-USD', 'USDC-USD', 'XRP-USD', 'ADA-USD', 'DOGE-USD', 'MATIC-USD', 'SOL-USD', 'DOT-USD', 'BUSD-USD', 'LTC-USD', 'SHIB-USD', 'TRX-USD', 'AVAX-USD', 'WBTC-USD', 'LINK-USD', 'FIL-USD', 'TUSD-USD', 'APT21794-USD', 'ARB11841-USD', 'STX4847-USD', 'WBNB-USD', 'CFX-USD', 'GALA-USD', 'ID21846-USD', 'IDEX-USD', 'SRM-USD', 'WETH-USD']
    daily_period = 'max'
    intraday_period = '60d'
    intraday_interval = '5m'

    pb = pushbullet.Pushbullet("o.cjRUVwPfdrNq1XTK7DJ2lxBh0XgDPU86")
    pb.push_note("Pull Data", "We starting python script again")
    # Download daily data
    download_all_data(tickers, daily_period)
    logging.info("All daily data downloaded and saved to disk.")

    while True:
        if is_market_open():
            # Download intraday data
            download_all_data(tickers, intraday_period, intraday_interval)
            logging.info("All intraday data downloaded and saved to disk.")
        else:
            logging.info("Market is closed. Waiting for the market to open.")

        time.sleep(5 * 60)  # Sleep for 5 minutes


if __name__ == "__main__":
    main()
