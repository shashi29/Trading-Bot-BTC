from data.fetcher import fetch_data
from data.processor import calculate_heikin_ashi
from indicators.ema import calculate_ema, calculate_ema_ripple
from indicators.bollinger_bands import calculate_bollinger_bands, check_bollinger_band_condition
from indicators.rsi import calculate_rsi, check_rsi_conditions
# from indicators.dmi import calculate_dmi, identify_dmi_conditions, check_ADX_Forming_Ungli
from indicators.adx import calculate_adx, check_adx_conditions
from indicators.stochastic import calculate_stochastic, check_stochastic_conditions
from indicators.fb_618 import predict_below_618
from patterns.candlestick_patterns import check_bullish_candlestick_pattern
from analysis.tide_analysis import analyze_tide
from analysis.wave_analysis import analyze_wave
from analysis.ripple_analysis import analyze_ripple
from utils.excel_writer import ExcelWriter
import numpy as np
import pandas as pd

class StockScanner:
    def __init__(self, config):
        self.config = config
        self.excel_writer = ExcelWriter()

    def scan(self):
        results = {}
        for ticker in self.config.get_tickers():
            print(f"Processing {ticker}...")
            df_Tide, df_Wave, df_Ripple = self.Check_buy_condition(ticker)
            #df_Tide, df_Wave, df_Ripple = self.Check_sell_condition(ticker)

    def Check_buy_condition(self, ticker):
        df_Tide = self.process_tide_data(ticker)
        df_Wave = self.process_wave_data(ticker)
        df_Ripple = self.process_ripple_data(ticker)

        #Filter date for those tide is green
        tide_status_date_list = df_Tide[df_Tide['HA_Green'] == True]['Date'].unique()

        df_Wave['Wave_Status'] = False
        df_Ripple['Ripple_Status'] = False

        for tide_status_date in tide_status_date_list:
            date_to_filter = pd.to_datetime(tide_status_date).date()
            #Create Wave Green Status for next full day
            df_Wave['Wave_Status'] = np.where(
                (df_Wave['Datetime'].dt.date == date_to_filter) &
                (df_Wave['HA_Green'] == True) &
                (df_Wave['EMA_Slope'] > 0) &
                (df_Wave['EMA_Slope_Up'] == True),
                True, df_Wave['Wave_Status']
            )
            
            wave_status_date_list = df_Wave[
                (df_Wave['Wave_Status'] == True) & 
                (df_Wave['Datetime'].dt.date == date_to_filter)]['Datetime'].unique()
            
            for wave_status_date in wave_status_date_list:            
                start_time = wave_status_date + pd.Timedelta(hours=1)
                end_time = wave_status_date + pd.Timedelta(hours=2)

                # Check conditions and assign Ripple_Status using numpy where
                df_Ripple['Ripple_Status'] = np.where(
                    (df_Ripple['Datetime'].between(start_time, end_time)) &
                    (df_Ripple['HA_Green']) &
                    (df_Ripple['Price_Above_EMA']) &
                    (df_Ripple['FBD_Signal'] == False),
                    True, df_Ripple['Ripple_Status']
                )
                
                ripple_status_date_list = df_Ripple[
                    (df_Ripple['Ripple_Status'] == True) & 
                    (df_Ripple['Datetime'].between(start_time, end_time))]['Datetime'].unique()
                
                for ripple_status_date in ripple_status_date_list:
                    print(f"Buy at {ripple_status_date} on {ticker}")
            print("-----------------------------------------------------------------------------------------")

        #Buy Condition 2: 
        df_Ripple = check_bollinger_band_condition(df_Ripple)
        #Buy Condition 3: Ripple Bullish Candlestick pattern
        df_Ripple = check_bullish_candlestick_pattern(df_Ripple)
        #Buy Condition 4: Ripple RSI
        df_Ripple = check_rsi_conditions(df_Ripple)
        #Buy Condition 5: Ripple ADX Forming Ungli
        df_Ripple = check_adx_conditions(df_Ripple)
        #Buy Condition 6: •	Ripple Stochastic PCO
        df_Ripple = check_stochastic_conditions(df_Ripple)
        #Buy Condition 7: Fib < 61.8% of last wave
        df_Ripple = predict_below_618(df_Ripple)

        self.excel_writer.write(ticker, {
            'Tide': df_Tide,
            'Wave': df_Wave,
            'Ripple': df_Ripple
        })
        return df_Tide, df_Wave, df_Ripple
  

    def process_tide_data(self, ticker):
        tide_config = self.config.get_time_frame('TIDE')
        df = fetch_data(ticker, **tide_config)
        df = calculate_heikin_ashi(df)
        return df

    def process_wave_data(self, ticker):
        wave_config = self.config.get_time_frame('WAVE')
        df = fetch_data(ticker, **wave_config)
        df = calculate_heikin_ashi(df)
        df = calculate_ema(df, self.config.get_indicator_params('EMA')['period'])
        return df

    def process_ripple_data(self, ticker):
        ripple_config = self.config.get_time_frame('RIPPLE')
        df = fetch_data(ticker, **ripple_config)
        df = calculate_heikin_ashi(df)
        df = calculate_ema_ripple(df, self.config.get_indicator_params('EMA')['period'])
        df = calculate_bollinger_bands(df, **self.config.get_indicator_params('BOLLINGER_BANDS'))
        df = calculate_rsi(df, **self.config.get_indicator_params('RSI'))
        df = calculate_adx(df, **self.config.get_indicator_params('DMI'))
        df = calculate_stochastic(df, **self.config.get_indicator_params('STOCHASTIC'))
        return df

# Usage
if __name__ == "__main__":
    from config import config
    scanner = StockScanner(config)
    scanner.scan()
    


'''
Stock Datetime TF_Tide, TF_Wave, TF_Ripple, 


'''