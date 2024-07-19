import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import logging
from typing import Tuple
from config import config
from scanner import StockScanner
from trading_strategy.sell_strategy import *
from nsepythonserver import *

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Chart plotter
class ChartPlotter:
    @staticmethod
    def plot_candlestick(df: pd.DataFrame) -> go.Figure:
        date_column = "Datetime" if "Datetime" in df.columns else "Date"
        fig = go.Figure(data=[go.Candlestick(
            x=df[date_column],
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
            xaxis_type='category'
        )
        
        return fig

# Stock analyzer
class StockAnalyzer:
    def __init__(self, scanner: StockScanner):
        self.scanner = scanner

    def analyze_stock(self, ticker: str, flag_date: datetime.date, period_tide: str, interval_tide: str, 
                      period_wave: str, interval_wave: str, period_ripple: str, interval_ripple: str, 
                      setting: str = "Ripple 15min") -> Tuple[pd.DataFrame, pd.DataFrame]:
        try:
            logger.info(f"Processing {ticker}...")
            df_Tide = self.scanner.process_tide_data(ticker, period=period_tide, interval=interval_tide)
            df_Wave = self.scanner.process_wave_data(ticker, period=period_wave, interval=interval_wave)
            df_Ripple = self.scanner.process_ripple_data(ticker, period=period_ripple, interval=interval_ripple)
            
            if setting == "Ripple 15min":
                df_Tide, df_Wave, df_Ripple = self.scanner.Check_buy_condition(ticker, df_Tide, df_Wave, df_Ripple)
                df_Ripple['Date'] = df_Ripple['Datetime'].dt.date
                daily_ripple = df_Ripple[df_Ripple['Date'] >= flag_date]
                df_Wave['Date'] = df_Wave['Datetime'].dt.date
                daily_wave = df_Wave[df_Wave['Date'] >= flag_date]
            else:
                df_Tide, df_Wave, df_Ripple = self.scanner.Check_buy_condition_ripple_1hr(ticker, df_Tide, df_Wave, df_Ripple)
                df_Ripple['Date'] = df_Ripple['Datetime'].dt.date
                daily_ripple = df_Ripple[df_Ripple['Date'] >= flag_date]
                flag_date = pd.to_datetime(flag_date)
                daily_wave = df_Wave[df_Wave['Datetime'] >= flag_date]
                logger.info(f"Shape of Wave data {daily_wave.shape} and Ripple Data {daily_ripple.shape}")
            
            return daily_ripple, daily_wave
        except Exception as e:
            logger.error(f"Error analyzing stock {ticker}: {str(e)}", exc_info=True)
            raise

# Streamlit UI
class StockAnalysisApp:
    def __init__(self, analyzer: StockAnalyzer):
        self.analyzer = analyzer
        self.buy_summary = []


    def run(self):
        st.set_page_config(page_title="Stock Analysis Dashboard", layout="wide")
        st.title("Stock Analysis Dashboard")

        # Sidebar
        self.sidebar_controls()

        # Main content area
        tab1, tab2, tab3 = st.tabs([
            "Overview", "Stock Scanner", "Real-time Monitoring"
        ])

        with tab1:
            self.overview_tab()
        with tab2:
            self.stock_scanner_tab()
        with tab3:
            self.realtime_monitoring_tab()



    def sidebar_controls(self):
        st.sidebar.header("Analysis Settings")
        self.setting = st.sidebar.radio("Select Setting:", ["Ripple 15min", "Ripple 1h"])
        self.strategies = st.sidebar.multiselect(
            "Select Strategies:", 
            ["Wave", "Ripple", "EMA"],
            default=["Wave", "Ripple", "EMA"]
        )
        self.view_option = st.sidebar.radio(
        "Select View:",["Detailed Metrics", "Buy Summary DataFrame"])

    def overview_tab(self):
        st.header("Market Overview")
        st.write("This tab will display a summary of current market trends and top opportunities.")

        # Display top gainers
        top_gainers = self.get_top_gainers()
        st.subheader("Top Gainers")
        st.dataframe(top_gainers, use_container_width=True)
        
        # Display top losers
        top_losers = self.get_top_losers()
        st.subheader("Top Losers")
        st.dataframe(top_losers, use_container_width=True)

        # Display most active stocks
        most_active = self.get_most_active()
        st.subheader("Most Active Stocks")
        st.dataframe(most_active, use_container_width=True)
        
    def get_top_losers(self):
        losers = nse_get_top_losers()
        df_losers = pd.DataFrame(losers)
        df_losers = df_losers[['symbol', 'lastPrice', 'change', 'pChange', 'totalTradedVolume', 
                               'yearHigh', 'yearLow', 'open', 'dayHigh', 'dayLow', 'previousClose']]
        df_losers.columns = ['Symbol', 'Last Price (INR)', 'Change (INR)', 'Change (%)', 'Total Traded Volume', 
                             'Year High (INR)', 'Year Low (INR)', 'Open (INR)', 'Day High (INR)', 
                             'Day Low (INR)', 'Previous Close (INR)']
        return df_losers

    def get_top_gainers(self):
        gainers = nse_get_top_gainers()
        df_gainers = pd.DataFrame(gainers)
        df_gainers = df_gainers[['symbol', 'lastPrice', 'change', 'pChange', 'totalTradedVolume', 
                                 'yearHigh', 'yearLow', 'open', 'dayHigh', 'dayLow', 'previousClose']]
        df_gainers.columns = ['Symbol', 'Last Price (INR)', 'Change (INR)', 'Change (%)', 'Total Traded Volume', 
                              'Year High (INR)', 'Year Low (INR)', 'Open (INR)', 'Day High (INR)', 
                              'Day Low (INR)', 'Previous Close (INR)']
        return df_gainers

    def get_most_active(self):
        active_stocks = nse_most_active()
        df_active = pd.DataFrame(active_stocks)
        df_active = df_active[['symbol', 'identifier', 'lastPrice', 'pChange', 'quantityTraded',
                               'totalTradedVolume', 'totalTradedValue', 'previousClose', 'yearHigh', 
                               'yearLow', 'change', 'open', 'closePrice', 'dayHigh', 'dayLow', 
                               'lastUpdateTime']]
        df_active.columns = ['Symbol', 'Identifier', 'Last Price (INR)', 'Change (%)', 'Quantity Traded', 
                             'Total Traded Volume', 'Total Traded Value (INR)', 'Previous Close (INR)', 
                             'Year High (INR)', 'Year Low (INR)', 'Change (INR)', 'Open (INR)', 
                             'Close Price (INR)', 'Day High (INR)', 'Day Low (INR)', 'Last Update Time']
        return df_active
    
    
    
    def stock_scanner_tab(self):
        st.header("Stock Scanner")
        tickers = st.text_area("Enter Stock Tickers (comma-separated):", "RELIANCE, INFY")
        flag_date = st.date_input("Select Date")
        
        if st.button("Scan Stocks"):
            self.scan_stocks(tickers, flag_date)

    def realtime_monitoring_tab(self):
        st.header("Real-time Monitoring")
        st.write("This tab will display real-time updates for selected stocks and signals.")
        # Placeholder for real-time monitoring



    def scan_stocks(self, tickers: str, flag_date: datetime.date):
        tickers_list = [ticker.strip() + ".NS" for ticker in tickers.split(",")]
        results_placeholder = st.empty()

        for ticker in tickers_list:
            try:
                with st.spinner(f"Scanning {ticker}..."):
                    daily_data, daily_wave = self.analyzer.analyze_stock(
                        ticker, flag_date, "1mo", "1d", "1mo", "1h", "1mo", "15m", self.setting
                    )
                if daily_data['Ripple_Status'].any():
                    self.display_stock_analysis(ticker, flag_date, daily_data, daily_wave)
                else:
                    results_placeholder.write(f"No buy signals detected for {ticker} on {flag_date}.")
            except Exception as e:
                logger.error(f"Error analyzing stock {ticker}: {str(e)}", exc_info=True)
                results_placeholder.write(f"Error processing {ticker}. Check logs for details.")

    def analyze_single_stock(self, ticker: str):
        try:
            flag_date = datetime.now().date() - timedelta(days=30)  # Analyze last 30 days
            daily_data, daily_wave = self.analyzer.analyze_stock(
                ticker, flag_date, "1mo", "1d", "1mo", "1h", "1mo", "15m", self.setting
            )
            self.display_stock_analysis(ticker, flag_date, daily_data, daily_wave)
        except Exception as e:
            logger.error(f"Error analyzing stock {ticker}: {str(e)}", exc_info=True)
            st.error(f"Error processing {ticker}. Check logs for details.")

    def display_stock_analysis(self, ticker: str, flag_date: datetime.date, daily_data: pd.DataFrame, daily_wave: pd.DataFrame):
        st.header(f"Analysis for {ticker}")

        tab1, tab2, tab3 = st.tabs(["Charts", "Data Tables", "Strategy Results"])
        
        with tab1:
            st.subheader("Candlestick Charts")
            st.plotly_chart(ChartPlotter.plot_candlestick(daily_data), use_container_width=True)
            st.plotly_chart(ChartPlotter.plot_candlestick(daily_wave), use_container_width=True)

        with tab2:
            st.subheader("Ripple Data")
            st.dataframe(daily_data)
            st.subheader("Wave Data")
            st.dataframe(daily_wave)

        with tab3:            
            if self.view_option == "Detailed Metrics":
                for strategy_name in self.strategies:
                    strategy = self.get_strategy(strategy_name)
                    trade_log, win_ratio, profit_percentage = strategy.execute(daily_data, daily_wave)
                    
                    st.subheader(f"{strategy_name} Strategy Results")
                    st.dataframe(trade_log)
                    
                    col1, col2 = st.columns(2)
                    col1.metric("Win Ratio", f"{win_ratio:.2f}%")
                    col2.metric("Profit Percentage", f"{profit_percentage:.2f}%")
                    
                    self.buy_summary.append({
                        "Ticker": ticker,
                        "Strategy": strategy_name,
                        "Win Ratio": win_ratio,
                        "Profit Percentage": profit_percentage
                    })
                
            elif self.view_option == "Buy Summary DataFrame":
                for strategy_name in self.strategies:
                    strategy = self.get_strategy(strategy_name)
                    trade_log, win_ratio, profit_percentage = strategy.execute(daily_data, daily_wave)
                    self.buy_summary.append({
                        "Ticker": ticker,
                        "Strategy": strategy_name,
                        "Win Ratio": win_ratio,
                        "Profit Percentage": profit_percentage
                    })
                buy_summary_df = pd.DataFrame(self.buy_summary)
                st.subheader("Buy Summary")
                st.dataframe(buy_summary_df)
        


    def get_strategy(self, strategy_name: str):
        if strategy_name == "Wave":
            return WaveSellStrategy() if self.setting == "Ripple 15min" else WaveSellStrategyRipple1hr()
        elif strategy_name == "Ripple":
            return RippleSellStrategy() if self.setting == "Ripple 15min" else RippleSellStrategyRipple1hr()
        elif strategy_name == "EMA":
            return EMACrossStrategy() if self.setting == "Ripple 15min" else EMACrossStrategyRipple1hr()
        else:
            raise ValueError(f"Unknown strategy: {strategy_name}")

def main():
    try:
        scanner = StockScanner(config)
        analyzer = StockAnalyzer(scanner)
        app = StockAnalysisApp(analyzer)
        app.run()
    except Exception as e:
        logger.error(f"An error occurred in the main function: {str(e)}")
        st.error("An unexpected error occurred. Please try again later.")

if __name__ == "__main__":
    main()