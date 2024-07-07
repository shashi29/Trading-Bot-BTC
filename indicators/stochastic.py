# indicators/stochastic.py

import pandas as pd
import numpy as np
np.NaN = np.nan  # Patch np.NaN

from pandas_ta.momentum import stoch
from typing import Dict, Any

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
    stoch_df = stoch(df['High'], df['Low'], df['Close'])
    df = pd.concat([df, stoch_df], axis=1)
    df = df.rename(columns={'STOCHk_14_3_3': '%K', 'STOCHd_14_3_3': '%D'})
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
    df['Stochastic_PCO'] = (df['%K'] > df['%D']) & (df['%K'].shift(1) <= df['%D'].shift(1)) & (df['Ripple_Status'] == True)
    
    # Identify Oversold condition
    df['Stochastic_Oversold'] = (df['%K'] < oversold_threshold) & (df['Ripple_Status'] == True)
    
    # Combine conditions: PCO from oversold region
    df['Stochastic_PC_from_Oversold'] = df['Stochastic_PCO'] & df['Stochastic_Oversold'] & df['Ripple_Status']
    
    return df