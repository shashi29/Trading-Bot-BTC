# indicators/rsi.py

import pandas as pd
import numpy as np

def calculate_rsi(df, window=14):
    """
    Calculate Relative Strength Index (RSI) for a given DataFrame.
    
    Args:
    - df (pd.DataFrame): DataFrame containing 'Close' prices
    - window (int): Window period for RSI calculation (default is 14)
    
    Returns:
    - pd.DataFrame: DataFrame with added columns 'RSI', 'RSI_Type'
    """
    df = df.copy()
    
    # Calculate price change
    df['Price Change'] = df['Close'].diff()
    
    # Calculate gain and loss
    df['Gain'] = np.where(df['Price Change'] > 0, df['Price Change'], 0)
    df['Loss'] = np.where(df['Price Change'] < 0, abs(df['Price Change']), 0)
    
    # Calculate average gain and average loss
    df['Avg Gain'] = df['Gain'].rolling(window=window, min_periods=1).mean()
    df['Avg Loss'] = df['Loss'].rolling(window=window, min_periods=1).mean()
    
    # Calculate RS (Relative Strength)
    df['RS'] = df['Avg Gain'] / df['Avg Loss']
    
    # Calculate RSI (Relative Strength Index)
    df['RSI'] = 100 - (100 / (1 + df['RS']))
    
    # Classify RSI
    conditions = [
        (df['RSI'] > 60),
        (df['RSI'] > 40)
    ]
    choices = ['Best', 'Better']
    df['RSI_Type'] = np.select(conditions, choices, default='Not Good')
    
    return df

def check_rsi_conditions(df):
    """
    Check for RSI pattern in the DataFrame.
    
    Args:
    - df (pd.DataFrame): DataFrame containing 'RSI_Type' and 'Ripple_Status' columns
    
    Returns:
    - pd.DataFrame: DataFrame with added 'RSI_Flag' column
    """
    df['RSI_Flag'] = (df['RSI_Type'].isin(['Best', 'Better'])) & (df['Ripple_Status'] == True)
    return df