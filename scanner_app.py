import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import logging
from abc import ABC, abstractmethod
from typing import List, Tuple, Dict
from config import config
from scanner import StockScanner

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Strategy interface
class TradingStrategy(ABC):
    @abstractmethod
    def execute(self, df: pd.DataFrame, df_wave: pd.DataFrame) -> Tuple[pd.DataFrame, float, float]:
        pass

# Concrete strategy implementations
class WaveSellStrategy(TradingStrategy):
    def execute(self, df: pd.DataFrame, df_wave: pd.DataFrame) -> Tuple[pd.DataFrame, float, float]:
        initial_capital = 100000000000
        capital = initial_capital
        position = 0
        buy_price = 0
        trade_log = []

        # Convert 'Datetime' to datetime objects
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        df_wave['Datetime'] = pd.to_datetime(df_wave['Datetime'])

        for index, row in df.iterrows():
            wave = df_wave[(df_wave['Datetime'] == row['Datetime']) & (df_wave['HA_Type'] == "Solid Red")]

            if row['Ripple_Status'] and row['HA_Type'] == 'Solid Green' and position == 0:
                position = capital / row['Close']
                buy_price = row['Close']
                capital = 0
                trade_log.append({
                    'Buy Time': row['Datetime'],
                    'Buy Price': buy_price,
                    'Win/Loss': ''  # Initialize 'Win/Loss' key
                })
            elif len(wave) and position > 0:
                sell_price = row['Close']
                capital = position * sell_price
                position = 0
                profit_loss = sell_price - buy_price
                profit_percentage = (profit_loss / buy_price) * 100
                win_loss = 'Win' if profit_loss > 0 else 'Loss'
                trade_log[-1].update({
                    'Sell Time': row['Datetime'],
                    'Sell Price': sell_price,
                    'Profit/Loss': profit_loss,
                    'Profit Percentage': profit_percentage,
                    'Win/Loss': win_loss
                })

            # Check if it's the last time frame of the day and we have an open position
            if row['Datetime'].time() == pd.Timestamp('15:15:00').time() and position > 0:
                sell_price = row['Close']
                sell_time = row['Datetime']
                profit_loss = sell_price - buy_price
                profit_percentage = (profit_loss / buy_price) * 100
                win_loss = 'Win' if profit_loss > 0 else 'Loss'
                capital = position * sell_price
                position = 0
                trade_log[-1].update({
                    'Sell Time': sell_time,
                    'Sell Price': sell_price,
                    'Profit/Loss': profit_loss,
                    'Profit Percentage': profit_percentage,
                    'Win/Loss': win_loss
                })

        # After exiting the loop, ensure all entries in trade_log have 'Win/Loss' key
        for trade in trade_log:
            if 'Win/Loss' not in trade:
                trade['Win/Loss'] = ''  # Handle cases where 'Win/Loss' key was not updated

        final_value = capital + (position * df.iloc[-1]['Close'])

        num_trades = len(trade_log)
        wins = sum(1 for trade in trade_log if trade['Win/Loss'] == 'Win')

        win_ratio = wins / num_trades if num_trades > 0 else 0
        profit_percentage = (final_value - initial_capital) / initial_capital * 100

        return pd.DataFrame(trade_log), win_ratio, profit_percentage

class RippleSellStrategy(TradingStrategy):
    def execute(self, df: pd.DataFrame, df_wave: pd.DataFrame) -> Tuple[pd.DataFrame, float, float]:
        initial_capital = 100000000000
        capital = initial_capital
        position = 0
        buy_price = 0
        trade_log = []

        try:
            # Convert 'Datetime' to datetime objects
            df['Datetime'] = pd.to_datetime(df['Datetime'])
            df_wave['Datetime'] = pd.to_datetime(df_wave['Datetime'])

            for index, row in df.iterrows():
                # Check for buy condition
                if row['Ripple_Status'] and row['HA_Type'] == 'Solid Green' and position == 0:
                    position = capital / row['Close']
                    buy_price = row['Close']
                    capital = 0
                    trade_log.append({
                        'Buy Time': row['Datetime'],
                        'Buy Price': buy_price,
                        'Win/Loss': ''  # Initialize 'Win/Loss' key
                    })
                
                # Check for sell conditions
                elif (not row['Ripple_Status'] or row['HA_Type'] == 'Solid Red') and position > 0:
                    sell_price = row['Close']
                    capital = position * sell_price
                    position = 0
                    profit_loss = sell_price - buy_price
                    profit_percentage = (profit_loss / buy_price) * 100
                    win_loss = 'Win' if profit_loss > 0 else 'Loss'
                    trade_log[-1].update({
                        'Sell Time': row['Datetime'],
                        'Sell Price': sell_price,
                        'Profit/Loss': profit_loss,
                        'Profit Percentage': profit_percentage,
                        'Win/Loss': win_loss
                    })

                # Check for end-of-day sell logic (3:15 PM)
                if row['Datetime'].time() == pd.Timestamp('15:15:00').time() and position > 0:
                    sell_price = row['Close']
                    sell_time = row['Datetime']
                    profit_loss = sell_price - buy_price
                    profit_percentage = (profit_loss / buy_price) * 100
                    win_loss = 'Win' if profit_loss > 0 else 'Loss'
                    capital = position * sell_price
                    position = 0
                    trade_log[-1].update({
                        'Sell Time': sell_time,
                        'Sell Price': sell_price,
                        'Profit/Loss': profit_loss,
                        'Profit Percentage': profit_percentage,
                        'Win/Loss': win_loss
                    })

            # After exiting the loop, ensure all entries in trade_log have 'Win/Loss' key
            for trade in trade_log:
                if 'Win/Loss' not in trade:
                    trade['Win/Loss'] = ''  # Handle cases where 'Win/Loss' key was not updated

            final_value = capital + (position * df.iloc[-1]['Close'])

            num_trades = len(trade_log)
            wins = sum(1 for trade in trade_log if trade['Win/Loss'] == 'Win')

            win_ratio = wins / num_trades if num_trades > 0 else 0
            profit_percentage = (final_value - initial_capital) / initial_capital * 100

            return pd.DataFrame(trade_log), win_ratio, profit_percentage

        except Exception as ex:
            print(f"An error occurred during trading: {str(ex)}")
            return pd.DataFrame(trade_log), 0, 0

class EMACrossStrategy(TradingStrategy):
    def execute(self, df: pd.DataFrame, df_wave: pd.DataFrame) -> Tuple[pd.DataFrame, float, float]:
        initial_capital = 100000000000
        capital = initial_capital
        position = 0
        buy_price = 0
        trade_log = []

        # Convert 'Datetime' to datetime objects
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        df_wave['Datetime'] = pd.to_datetime(df_wave['Datetime'])

        # Calculate 5-day and 13-day EMA
        df['5EMA'] = df['Close'].ewm(span=5, adjust=False).mean()
        df['13EMA'] = df['Close'].ewm(span=13, adjust=False).mean()

        for index, row in df.iterrows():
            #wave = df_wave[(df_wave['Datetime'] == row['Datetime']) & (df_wave['HA_Type'] == "Solid Red")]

            if row['Ripple_Status'] and row['HA_Type'] == 'Solid Green' and position == 0:
                position = capital / row['Close']
                buy_price = row['Close']
                capital = 0
                trade_log.append({
                    'Buy Time': row['Datetime'],
                    'Buy Price': buy_price,
                    '5EMA': row['5EMA'],
                    '13EMA': row['13EMA'],
                    'Win/Loss': ''  # Initialize 'Win/Loss' key
                })
                        
            # Check for EMA crossover to trigger sell
            elif position > 0:
                if row['5EMA'] < row['13EMA']:  # 5EMA crosses below 13EMA
                    sell_price = row['Close']
                    sell_time = row['Datetime']
                    profit_loss = sell_price - buy_price
                    profit_percentage = (profit_loss / buy_price) * 100
                    win_loss = 'Win' if profit_loss > 0 else 'Loss'
                    capital = position * sell_price
                    position = 0
                    trade_log[-1].update({
                        'Sell Time': sell_time,
                        'Sell Price': sell_price,
                        'Profit/Loss': profit_loss,
                        'Profit Percentage': profit_percentage,
                        'Win/Loss': win_loss,
                        '5EMA': row['5EMA'],
                        '13EMA': row['13EMA']
                    })

            # Check if it's the last time frame of the day and we have an open position
            if row['Datetime'].time() == pd.Timestamp('15:15:00').time() and position > 0:
                sell_price = row['Close']
                sell_time = row['Datetime']
                profit_loss = sell_price - buy_price
                profit_percentage = (profit_loss / buy_price) * 100
                win_loss = 'Win' if profit_loss > 0 else 'Loss'
                capital = position * sell_price
                position = 0
                trade_log[-1].update({
                    'Sell Time': sell_time,
                    'Sell Price': sell_price,
                    'Profit/Loss': profit_loss,
                    'Profit Percentage': profit_percentage,
                    'Win/Loss': win_loss,
                    '5EMA': row['5EMA'],
                    '13EMA': row['13EMA']
                })

        # After exiting the loop, ensure all entries in trade_log have 'Win/Loss' key
        for trade in trade_log:
            if 'Win/Loss' not in trade:
                trade['Win/Loss'] = ''  # Handle cases where 'Win/Loss' key was not updated

        final_value = capital + (position * df.iloc[-1]['Close'])

        num_trades = len(trade_log)
        wins = sum(1 for trade in trade_log if trade['Win/Loss'] == 'Win')

        win_ratio = wins / num_trades if num_trades > 0 else 0
        profit_percentage = (final_value - initial_capital) / initial_capital * 100

        return pd.DataFrame(trade_log), win_ratio, profit_percentage
# Chart plotter
class ChartPlotter:
    @staticmethod
    def plot_candlestick(df: pd.DataFrame) -> go.Figure:
        fig = go.Figure(data=[go.Candlestick(
            x=df['Datetime'],
            open=df['HA_Open'],
            high=df['HA_High'],
            low=df['HA_Low'],
            close=df['HA_Close'],
            name='Candlesticks'
        )])
        
        fig.update_layout(
            title="Candlestick Chart",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_white",
            xaxis_type='category',
            xaxis=dict(
                tickformat='%H:%M',
                dtick=1800000,
                tickmode='linear'
            )
        )
        
        return fig

# Stock analyzer
class StockAnalyzer:
    def __init__(self, scanner: StockScanner):
        self.scanner = scanner

    def analyze_stock(self, ticker: str, flag_date: datetime.date) -> Tuple[pd.DataFrame, pd.DataFrame]:
        try:
            df_Tide, df_Wave, df_Ripple = self.scanner.Check_buy_condition(ticker)
            df_Ripple['Date'] = df_Ripple['Datetime'].dt.date
            daily_data = df_Ripple[df_Ripple['Date'] >= flag_date]
            df_Wave['Date'] = df_Wave['Datetime'].dt.date
            daily_wave = df_Wave[df_Wave['Date'] >= flag_date]
            return daily_data, daily_wave
        except Exception as e:
            logger.error(f"Error analyzing stock {ticker}: {str(e)}")
            raise

# Streamlit UI
class StockScannerApp:
    def __init__(self, analyzer: StockAnalyzer):
        self.analyzer = analyzer
        self.buy_summary = list()
        self.ticker = ''

    def run(self):
        st.set_page_config(page_title="Stock Scanner App", layout="wide")
        st.title("Stock Scanner App")

        col1, col2 = st.columns(2)
        with col1:
            tickers = st.text_area("Enter Stock Tickers (comma-separated):", "RELIANCE, INFY")
        with col2:
            flag_date = st.date_input("Select Date", datetime.now().date())

        if st.button("Scan Stocks", key="scan_button"):
            self.scan_stocks(tickers, flag_date)

    def scan_stocks(self, tickers: str, flag_date: datetime.date):
        tickers_list = [ticker.strip() + ".NS" for ticker in tickers.split(",")]
        
        for ticker in tickers_list:
            try:
                with st.spinner(f"Scanning {ticker}..."):
                    self.ticker = ticker
                    daily_data, daily_wave = self.analyzer.analyze_stock(ticker, flag_date)

                if daily_data['Ripple_Status'].any():
                    self.display_stock_analysis(ticker, flag_date, daily_data, daily_wave)
                else:
                    st.info(f"No buy signals detected for {ticker} on {flag_date}.")
            except Exception as e:
                st.error(f"Error processing {ticker}: {str(e)}")
                
        #Display the overall summary
        buy_summary = pd.DataFrame(self.buy_summary)
        st.subheader("Overall Profit with Strategy")
        st.dataframe(buy_summary, use_container_width=True)

    def display_stock_analysis(self, ticker: str, flag_date: datetime.date, daily_data: pd.DataFrame, daily_wave: pd.DataFrame):
        st.subheader(f"Results for {ticker} on {flag_date}")

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Candlestick Chart", "Buy Signals", "Wave Sell Strategy", "Ripple Sell Strategy", "EMA Sell Strategy"])

        with tab1:
            fig = ChartPlotter.plot_candlestick(daily_data)
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.dataframe(daily_data, use_container_width=True)

        with tab3:
            strategy = WaveSellStrategy()
            self.display_strategy_results(strategy, daily_data, daily_wave, "Wave Sell Strategy")

        with tab4:
            strategy = RippleSellStrategy()
            self.display_strategy_results(strategy, daily_data, daily_wave, "Ripple Sell Strategy")
        
        with tab5:
            strategy = EMACrossStrategy()
            self.display_strategy_results(strategy, daily_data, daily_wave, "EMA Sell Strategy")

    def display_strategy_results(self, strategy: TradingStrategy, daily_data: pd.DataFrame, daily_wave: pd.DataFrame, strategy_name: str):
        trade_log, win_ratio, profit_percentage = strategy.execute(daily_data, daily_wave)
        self.buy_summary.append({
            "Ticker": self.ticker,
            "Sell Strategy": strategy_name,
            "Win Ratio": win_ratio,
            "Profit Percentage": profit_percentage
        })
        st.subheader(f"Trade Log - {strategy_name}")
        st.dataframe(trade_log, use_container_width=True)
        col1, col2 = st.columns(2)
        col1.metric("Win Ratio", f"{win_ratio}%")
        col2.metric("Profit Percentage", f"{profit_percentage}%")

def main():
    try:
        scanner = StockScanner(config)
        analyzer = StockAnalyzer(scanner)
        app = StockScannerApp(analyzer)
        app.run()
    except Exception as e:
        logger.error(f"An error occurred in the main function: {str(e)}")
        st.error("An unexpected error occurred. Please try again later.")

if __name__ == "__main__":
    main()