# indicators/dmi.py

import pandas as pd
import numpy as np
from pandas_ta.trend import adx
from typing import Dict, Any

def calculate_dmi(data: Dict[str, Any], window: int = 14) -> pd.DataFrame:
    """
    Calculate DMI indicators and return the DataFrame.
    
    Args:
    data (Dict[str, Any]): Input data dictionary.
    window (int): Window size for ADX calculation.
    
    Returns:
    pd.DataFrame: DataFrame with DMI indicators.
    """
    try:
        df = pd.DataFrame(data)
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        df.set_index('Datetime', inplace=True)
        
        adx_df = adx(df['High'], df['Low'], df['Close'], length=window)
        df = pd.concat([df, adx_df], axis=1)
        
        return df
    except Exception as e:
        print(f"Error calculating DMI: {e}")
        return df


def update_row(df: pd.DataFrame, index: int, check1: str, check2: str, remarks: str, further_checks: str):
    """Helper function to update a row in the DataFrame."""
    df.loc[df.index[index], ['Check 1', 'Check 2', 'Remarks', 'Further checks']] = [check1, check2, remarks, further_checks]

def check_adxconditions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Check conditions and add remarks to the DataFrame.
    
    Args:
    df (pd.DataFrame): Input DataFrame with DMI indicators.
    
    Returns:
    pd.DataFrame: DataFrame with added remarks.
    """
    try:
        df['Check 1'] = ''
        df['Check 2'] = ''
        df['Remarks'] = ''
        df['Further checks'] = ''
        
        for i in range(1, len(df)):
            adx_current, adx_previous = df['ADX_14'].iloc[i], df['ADX_14'].iloc[i-1]
            dmp_current, dmn_current = df['DMP_14'].iloc[i], df['DMN_14'].iloc[i]
            dmp_previous, dmn_previous = df['DMP_14'].iloc[i-1], df['DMN_14'].iloc[i-1]
            
            if 15 <= adx_current <= 60:
                if adx_current > adx_previous:
                    update_row(df, i, 'Uptick', 'ADX value between 15 to 60', 'V.Good', 'No further checks needed')
                elif dmp_current > dmn_current and dmp_current > dmp_previous and dmn_current < dmn_previous:
                    update_row(df, i, 'No Uptick', 'ADX value between 15 to 60', 'V.Good', 'No further checks needed')
                elif dmp_current > dmn_current:
                    update_row(df, i, 'No Uptick', 'ADX value between 15 to 60', 'Good', 'No further checks needed')
            elif 10 <= adx_current < 15:
                update_row(df, i, 'Uptick', 'ADX value between 10 to 15', 'Radar', 'Future can give very big breakout, if it goes above 15 after uptick')
            elif adx_current < 10:
                update_row(df, i, 'No Uptick', 'ADX value below 10', 'Very bad and do not do anything', '-')
    except Exception as e:
        print(f"Error checking conditions: {e}")
    return df




# def calculate_dmi(df, window=14):
#     """
#     Calculate Directional Movement Index (DMI) for a given DataFrame.
    
#     Args:
#     - df (pd.DataFrame): DataFrame containing 'High', 'Low', 'Close' prices
#     - window (int): Window period for DMI calculation (default is 14)
    
#     Returns:
#     - pd.DataFrame: DataFrame with added DMI columns
#     """
#     df = df.copy()
    
#     # Calculate True Range (TR)
#     df['H-L'] = df['High'] - df['Low']
#     df['H-PC'] = np.abs(df['High'] - df['Close'].shift(1))
#     df['L-PC'] = np.abs(df['Low'] - df['Close'].shift(1))
#     df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    
#     # Calculate Directional Movement (+DM and -DM)
#     df['+DM'] = np.where((df['High'] - df['High'].shift(1)) > (df['Low'].shift(1) - df['Low']), 
#                          np.maximum(df['High'] - df['High'].shift(1), 0), 0)
#     df['-DM'] = np.where((df['Low'].shift(1) - df['Low']) > (df['High'] - df['High'].shift(1)), 
#                          np.maximum(df['Low'].shift(1) - df['Low'], 0), 0)
    
#     # Smoothed versions of TR, +DM, and -DM
#     df['TR14'] = df['TR'].rolling(window=window).sum()
#     df['+DM14'] = df['+DM'].rolling(window=window).sum()
#     df['-DM14'] = df['-DM'].rolling(window=window).sum()
    
#     # Calculate +DI and -DI
#     df['+DI14'] = 100 * df['+DM14'] / df['TR14']
#     df['-DI14'] = 100 * df['-DM14'] / df['TR14']
    
#     # Calculate DX
#     df['DX'] = 100 * np.abs(df['+DI14'] - df['-DI14']) / (df['+DI14'] + df['-DI14'])
    
#     # Calculate ADX
#     df['ADX'] = df['DX'].rolling(window=window).mean()
    
#     return df

# def identify_dmi_conditions(df, adx_threshold=15):
#     """
#     Identify DMI conditions in the DataFrame.
    
#     Args:
#     - df (pd.DataFrame): DataFrame containing DMI columns
#     - adx_threshold (float): Threshold for ADX value (default is 15)
    
#     Returns:
#     - pd.DataFrame: DataFrame with added DMI condition columns
#     """
#     df['ADX_Uptick'] = df['ADX'] > df['ADX'].shift(1)
    
#     bins = [-float('inf'), 15, 40, float('inf')]
#     labels = ['Less than 15', 'Greater than 15 but less than 40', 'Greater than 40']
#     df['ADX_Good'] = pd.cut(df['ADX'], bins=bins, labels=labels, right=False)
    
#     return df

# def check_ADX_Forming_Ungli(df):
#     """
#     Check for ADX Forming Ungli condition in the DataFrame.
    
#     Args:
#     - df (pd.DataFrame): DataFrame containing DMI condition columns and 'Ripple_Status'
    
#     Returns:
#     - pd.DataFrame: DataFrame with added 'ADX_Forming_Ungli' column
#     """
#     df['ADX_Forming_Ungli'] = (
#         ((df['ADX_Good'] == 'Greater than 15 but less than 40') & (df['ADX_Uptick'] == True) & (df['Ripple_Status'] == True))
#         |
#         ((df['ADX_Good'] == 'Greater than 40') & (df['Ripple_Status'] == True))
#     )
#     return df