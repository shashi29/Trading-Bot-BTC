# indicators/bollinger_bands.py

import pandas as pd

def calculate_bollinger_bands(df, period=20, std_dev=2):
    """
    Calculate Bollinger Bands for a given DataFrame.
    
    Args:
    - df (pd.DataFrame): DataFrame containing 'Close' prices
    - period (int): Window period for moving average (default is 20)
    - std_dev (int): Number of standard deviations for the bands (default is 2)
    
    Returns:
    - pd.DataFrame: DataFrame with added columns 'SMA', 'Upper_BB', 'Lower_BB'
    """
    df = df.copy()
    
    # Calculate Simple Moving Average (SMA)
    df['SMA'] = df['Close'].rolling(window=period).mean()
    
    # Calculate Standard Deviation
    df['STD'] = df['Close'].rolling(window=period).std()
    
    # Calculate Upper and Lower Bollinger Bands
    df['Upper_BB'] = df['SMA'] + (std_dev * df['STD'])
    df['Lower_BB'] = df['SMA'] - (std_dev * df['STD'])
    
    return df

def check_bollinger_band_condition(df):
    """
    Check for Bollinger Band conditions in the DataFrame.
    
    Args:
    - df (pd.DataFrame): DataFrame containing Bollinger Bands and 'Ripple_Status' columns
    
    Returns:
    - pd.DataFrame: DataFrame with added 'Bollinger_Band_Condition' column
    """
    df['LBB_Uptick'] = df['Lower_BB'].diff() > 0
    df['LBB_Flat'] = df['Lower_BB'].diff().abs() < 1e-5
    df['Bollinger_Band_Condition'] = ((df['LBB_Uptick'] | df['LBB_Flat']) & (df['Ripple_Status'] == True))
    return df