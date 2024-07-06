# indicators/dmi.py

import pandas as pd
import numpy as np

def calculate_dmi(df, window=14):
    """
    Calculate Directional Movement Index (DMI) for a given DataFrame.
    
    Args:
    - df (pd.DataFrame): DataFrame containing 'High', 'Low', 'Close' prices
    - window (int): Window period for DMI calculation (default is 14)
    
    Returns:
    - pd.DataFrame: DataFrame with added DMI columns
    """
    df = df.copy()
    
    # Calculate True Range (TR)
    df['H-L'] = df['High'] - df['Low']
    df['H-PC'] = np.abs(df['High'] - df['Close'].shift(1))
    df['L-PC'] = np.abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    
    # Calculate Directional Movement (+DM and -DM)
    df['+DM'] = np.where((df['High'] - df['High'].shift(1)) > (df['Low'].shift(1) - df['Low']), 
                         np.maximum(df['High'] - df['High'].shift(1), 0), 0)
    df['-DM'] = np.where((df['Low'].shift(1) - df['Low']) > (df['High'] - df['High'].shift(1)), 
                         np.maximum(df['Low'].shift(1) - df['Low'], 0), 0)
    
    # Smoothed versions of TR, +DM, and -DM
    df['TR14'] = df['TR'].rolling(window=window).sum()
    df['+DM14'] = df['+DM'].rolling(window=window).sum()
    df['-DM14'] = df['-DM'].rolling(window=window).sum()
    
    # Calculate +DI and -DI
    df['+DI14'] = 100 * df['+DM14'] / df['TR14']
    df['-DI14'] = 100 * df['-DM14'] / df['TR14']
    
    # Calculate DX
    df['DX'] = 100 * np.abs(df['+DI14'] - df['-DI14']) / (df['+DI14'] + df['-DI14'])
    
    # Calculate ADX
    df['ADX'] = df['DX'].rolling(window=window).mean()
    
    return df

def identify_dmi_conditions(df, adx_threshold=15):
    """
    Identify DMI conditions in the DataFrame.
    
    Args:
    - df (pd.DataFrame): DataFrame containing DMI columns
    - adx_threshold (float): Threshold for ADX value (default is 15)
    
    Returns:
    - pd.DataFrame: DataFrame with added DMI condition columns
    """
    df['ADX_Uptick'] = df['ADX'] > df['ADX'].shift(1)
    
    bins = [-float('inf'), 15, 40, float('inf')]
    labels = ['Less than 15', 'Greater than 15 but less than 40', 'Greater than 40']
    df['ADX_Good'] = pd.cut(df['ADX'], bins=bins, labels=labels, right=False)
    
    return df

def check_ADX_Forming_Ungli(df):
    """
    Check for ADX Forming Ungli condition in the DataFrame.
    
    Args:
    - df (pd.DataFrame): DataFrame containing DMI condition columns and 'Ripple_Status'
    
    Returns:
    - pd.DataFrame: DataFrame with added 'ADX_Forming_Ungli' column
    """
    df['ADX_Forming_Ungli'] = (
        ((df['ADX_Good'] == 'Greater than 15 but less than 40') & (df['ADX_Uptick'] == True) & (df['Ripple_Status'] == True))
        |
        ((df['ADX_Good'] == 'Greater than 40') & (df['Ripple_Status'] == True))
    )
    return df