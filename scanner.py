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

from concurrent.futures import ThreadPoolExecutor, as_completed

# Helper function to get the next trading day after Friday
def get_next_monday(date):
    days_ahead = 7 - date.weekday()  # Monday is 0 and Sunday is 6
    return date + pd.Timedelta(days=days_ahead)

def trading_strategy(df, df_wave):
    initial_capital = 100000
    capital = initial_capital
    position = 0
    buy_price = 0
    trade_log = []

    for index, row in df.iterrows():
        wave = df_wave[(df_wave['Datetime'] == row['Datetime']) & (df_wave['Wave_Status'] == False)]
        if row['Ripple_Status'] and row['HA_Type'] == 'Solid Green' and position == 0:
            position = capital / row['Close']
            buy_price = row['Close']
            capital = 0
            trade_log.append({
                'Buy Time': row['Datetime'],
                'Buy Price': buy_price,
                # 'Stop Loss': stop_loss_price,
                # 'Target Price': target_price,
                'Win/Loss': ''  # Initialize 'Win/Loss' key
            })
        elif len(wave) and position > 0:
            sell_price = row['Close']
            capital = position * sell_price
            position = 0
            profit_loss = sell_price - buy_price
            win_loss = 'Win' if profit_loss > 0 else 'Loss'
            trade_log[-1].update({
                'Sell Time': row['Datetime'],
                'Sell Price': sell_price,
                'Profit/Loss': profit_loss,
                'Win/Loss': win_loss
            })

    # After exiting the loop, ensure all entries in trade_log have 'Win/Loss' key
    for trade in trade_log:
        if 'Win/Loss' not in trade:
            trade['Win/Loss'] = ''  # Handle cases where 'Win/Loss' key was not updated

    final_value = capital + (position * df.iloc[-1]['Close'])

    num_trades = len(trade_log)
    wins = sum(1 for trade in trade_log if trade['Win/Loss'] == 'Win')
    #total_profit = sum(trade['Profit/Loss'] for trade in trade_log)

    win_ratio = wins / num_trades if num_trades > 0 else 0
    profit_percentage = (final_value - initial_capital) / initial_capital * 100

    return pd.DataFrame(trade_log), win_ratio, profit_percentage


class StockScanner:
    def __init__(self, config):
        self.config = config
        self.excel_writer = ExcelWriter()
        # Define the start and end time for the trading window
        self.start_trading_time = pd.to_datetime("09:15").time()
        self.end_trading_time = pd.to_datetime("15:15").time()

    def scan(self):
        results = {}
        trade_log_list = list()
        for ticker in self.config.get_tickers():
            ticker = ticker + ".NS"
            try:
                print(f"Processing {ticker}...")
                df_Tide, df_Wave, df_Ripple = self.Check_buy_condition(ticker)
                #self.write_to_excel(ticker, df_Tide, df_Wave, df_Ripple)
                trade_log, win_ratio, profit_percentage = trading_strategy(df_Ripple, df_Wave)
                trade_log['Ticker'] = ticker
                trade_log_list.append(trade_log)
            except Exception as ex:
                continue
            # print(trade_log)
            # print(f"Win Ratio: {win_ratio}")
            # print(f"Profit Percentage: {profit_percentage}%")
            #df_Tide, df_Wave, df_Ripple = self.Check_sell_condition(ticker)
        combined_df = pd.concat(trade_log_list, ignore_index=True)
        combined_df.to_csv("Trade_log_combine.csv", index=False)
        

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
            next_date_to_filter = date_to_filter + pd.Timedelta(days=1)

            #Create Wave Green Status for next full day
            df_Wave['Wave_Status'] = np.where(
                (df_Wave['Datetime'].dt.date.isin([date_to_filter, next_date_to_filter])) &
                (df_Wave['HA_Green'] == True) &
                (df_Wave['EMA_Slope'] > 0) &
                (df_Wave['EMA_Slope_Up'] == True),
                True, df_Wave['Wave_Status']
            )
            
            wave_status_date_list = df_Wave[(df_Wave['Wave_Status'] == True) & \
                                            (df_Wave['Datetime'].dt.date.isin([date_to_filter, next_date_to_filter]))]['Datetime'].unique()
                        
            for wave_status_date in wave_status_date_list:            
                if wave_status_date.time() == self.end_trading_time:
                    if wave_status_date.weekday() == 4:  # If Friday
                        next_monday = get_next_monday(wave_status_date)
                        start_time = next_monday + pd.Timedelta(hours=9)
                        end_time = next_monday + pd.Timedelta(hours=10)
                    else:
                        start_time = wave_status_date + pd.Timedelta(hours=18)
                        end_time = wave_status_date + pd.Timedelta(hours=19)
                else:
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
                
            #     for ripple_status_date in ripple_status_date_list:
            #         print(f"Buy at {ripple_status_date} on {ticker}")
            # print("-----------------------------------------------------------------------------------------")

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

    def write_to_excel(self, ticker, df_Tide, df_Wave, df_Ripple):
        self.excel_writer.write(ticker, {
            'Tide': df_Tide,
            'Wave': df_Wave,
            'Ripple': df_Ripple
        })
# Usage
if __name__ == "__main__":
    from config import config
    scanner = StockScanner(config)
    scanner.scan()
    


'''
Stock Datetime TF_Tide, TF_Wave, TF_Ripple, 


'''