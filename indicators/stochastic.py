# indicators/stochastic.py

import pandas as pd

def calculate_stochastic(df, k=14, d=3):
    """
    Calculate Stochastic Oscillator for a given DataFrame.
    
    Args:
    - df (pd.DataFrame): DataFrame containing 'High', 'Low', 'Close' prices
    - k (int): Window period for %K calculation (default is 14)
    - d (int): Smoothing period for %D calculation (default is 3)
    
    Returns:
    - pd.DataFrame: DataFrame with added columns '%K', '%D'
    """
    df = df.copy()
    
    # Calculate %K
    df['Lowest Low'] = df['Low'].rolling(window=k).min()
    df['Highest High'] = df['High'].rolling(window=k).max()
    df['%K'] = 100 * ((df['Close'] - df['Lowest Low']) / (df['Highest High'] - df['Lowest Low']))
    
    # Calculate %D
    df['%D'] = df['%K'].rolling(window=d).mean()
    
    return df

def check_stochastic_conditions(df, oversold_threshold=20):
    """
    Identify Stochastic conditions in the DataFrame.
    
    Args:
    - df (pd.DataFrame): DataFrame containing '%K' and '%D' columns
    - oversold_threshold (float): Threshold for oversold region (default is 20)
    
    Returns:
    - pd.DataFrame: DataFrame with added Stochastic condition columns
    """
    df = df.copy()
    
    # Identify Positive Crossover (PCO)
    df['Stochastic_PCO'] = (df['%K'] > df['%D']) & (df['%K'].shift(1) <= df['%D'].shift(1))
    
    # Identify Oversold condition
    df['Stochastic_Oversold'] = df['%K'] < oversold_threshold
    
    # Combine conditions: PCO from oversold region
    df['Stochastic_PC_from_Oversold'] = df['Stochastic_PCO'] & df['Stochastic_Oversold']
    
    return df