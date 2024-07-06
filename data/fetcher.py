# data/fetcher.py

import yfinance as yf
import pandas as pd

def fetch_data(ticker, start=None, end=None, period='1y', interval='1d'):
    """
    Fetch historical data for a given ticker.
    
    Args:
    - ticker (str): The stock ticker symbol
    - start (str, optional): Start date for data fetching (format: 'YYYY-MM-DD')
    - end (str, optional): End date for data fetching (format: 'YYYY-MM-DD')
    - period (str, optional): The period to download (default is '1y')
    - interval (str, optional): The interval between data points (default is '1d')
    
    Returns:
    - pd.DataFrame: DataFrame containing the fetched stock data
    """
    try:
        df = yf.download(ticker, start=start, end=end, period=period, interval=interval)
        df.index = pd.to_datetime(df.index)
        df = df.reset_index()
        
        if "Date" in df.columns:
            df = df.sort_values(by='Date')
            df['Date'] = df['Date'].dt.tz_localize(None)
        elif "Datetime" in df.columns:
            df = df.sort_values(by='Datetime')
            df['Datetime'] = df['Datetime'].dt.tz_localize(None)
        
        return df
    except Exception as e:
        print(f"Error fetching data for {ticker}: {str(e)}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error
