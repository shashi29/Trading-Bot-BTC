import pandas as pd
import numpy as np
np.NaN = np.nan  # Patch np.NaN

from pandas_ta.trend import adx
from typing import Dict, Any

def calculate_adx(df: Dict[str, Any], window: int = 14) -> pd.DataFrame:
    """
    Calculate DMI indicators and return the DataFrame.
    
    Args:
    data (Dict[str, Any]): Input data dictionary.
    window (int): Window size for ADX calculation.
    
    Returns:
    pd.DataFrame: DataFrame with DMI indicators.
    """
    try:
        
        adx_df = adx(df['High'], df['Low'], df['Close'], length=window)
        df = pd.concat([df, adx_df], axis=1)
        
        return df
    except Exception as e:
        print(f"Error calculating DMI: {e}")
        return df


def update_row(df: pd.DataFrame, index: int, check1: str, check2: str, remarks: str):
    """Helper function to update a row in the DataFrame."""
    df.loc[df.index[index], ['ADX Uptick/No Uptick', 'ADX Range', 'ADX Status']] = [check1, check2, remarks]

def check_adx_conditions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Check conditions and add remarks to the DataFrame.
    
    Args:
    df (pd.DataFrame): Input DataFrame with DMI indicators.
    
    Returns:
    pd.DataFrame: DataFrame with added remarks.
    """
    try:
        df['ADX Uptick/No Uptick'] = ''
        df['ADX Range'] = ''
        df['ADX Status'] = ''

        for i in range(1, len(df)):
            adx_current, adx_previous = df['ADX_14'].iloc[i], df['ADX_14'].iloc[i-1]
            dmp_current, dmn_current = df['DMP_14'].iloc[i], df['DMN_14'].iloc[i]
            dmp_previous, dmn_previous = df['DMP_14'].iloc[i-1], df['DMN_14'].iloc[i-1]
            ripple_status = df['Ripple_Status'].iloc[i]  # Assuming Ripple_Status is a boolean column
            
            if 15 <= adx_current <= 60:
                if adx_current > adx_previous and ripple_status:
                    update_row(df, i, 'Uptick', 'ADX value between 15 to 60', 'Best')
                elif dmp_current > dmn_current and dmp_current > dmp_previous and dmn_current < dmn_previous and ripple_status:
                    update_row(df, i, 'No Uptick', 'ADX value between 15 to 60', 'Best')
                elif dmp_current > dmn_current and ripple_status:
                    update_row(df, i, 'No Uptick', 'ADX value between 15 to 60', 'Better')
            elif 10 <= adx_current < 15 and ripple_status:
                update_row(df, i, 'Uptick', 'ADX value between 10 to 15', 'Radar')
            else:
                update_row(df, i, 'No Uptick', 'ADX value below 10', 'Bad')
    except Exception as e:
        print(f"Error checking conditions: {e}")
    return df

