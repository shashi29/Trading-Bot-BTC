import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, time
from config import config
from scanner import StockScanner
from data.fetcher import fetch_data
from data.processor import calculate_heikin_ashi
from indicators.ema import calculate_ema, calculate_ema_ripple
from indicators.bollinger_bands import calculate_bollinger_bands, check_bollinger_band_condition
from indicators.rsi import calculate_rsi, check_rsi_conditions
from indicators.adx import calculate_adx, check_adx_conditions
from indicators.stochastic import calculate_stochastic, check_stochastic_conditions
from indicators.fb_618 import predict_below_618
from patterns.candlestick_patterns import check_bullish_candlestick_pattern
from analysis.tide_analysis import analyze_tide
from analysis.wave_analysis import analyze_wave
from analysis.ripple_analysis import analyze_ripple
from utils.excel_writer import ExcelWriter

# Initialize the StockScanner
scanner = StockScanner(config)

def plot_candlestick(df):
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
        template="plotly_white"
    )
    
    return fig

def process_tide(ticker):
    try:
        df_Tide = scanner.process_tide_data(ticker)
        tide_status_dates = df_Tide[df_Tide['HA_Green']]['Date'].unique()
        return df_Tide, tide_status_dates
    except Exception as e:
        st.error(f"Error processing tide data for {ticker}: {e}")
        return pd.DataFrame(), []

def process_wave(ticker, date):
    try:
        df_Wave = scanner.process_wave_data(ticker)
        wave_status_dates = []
        
        if not df_Wave.empty:
            df_Wave['Wave_Status'] = False
            date_to_filter = pd.to_datetime(date).date()
            
            df_Wave['Wave_Status'] = np.where(
                (df_Wave['Datetime'].dt.date == date_to_filter) &
                (df_Wave['HA_Green']) &
                (df_Wave['EMA_Slope'] > 0) &
                (df_Wave['EMA_Slope_Up']),
                True, df_Wave['Wave_Status']
            )
            
            wave_status_dates = df_Wave[df_Wave['Wave_Status']]['Datetime'].unique()
        
        return df_Wave, wave_status_dates
    except Exception as e:
        st.error(f"Error processing wave data for {ticker} on {date}: {e}")
        return pd.DataFrame(), []

def process_ripple(ticker, datetime_range):
    try:
        df_Ripple = scanner.process_ripple_data(ticker)
        
        if not df_Ripple.empty:
            df_Ripple['Ripple_Status'] = False
            start_time, end_time = datetime_range
            
            df_Ripple['Ripple_Status'] = np.where(
                (df_Ripple['Datetime'].between(start_time, end_time)) &
                (df_Ripple['HA_Green']) &
                (df_Ripple['Price_Above_EMA']) &
                (~df_Ripple['FBD_Signal']),
                True, df_Ripple['Ripple_Status']
            )
            
            ripple_status_dates = df_Ripple[df_Ripple['Ripple_Status']]['Datetime'].unique()
            
            df_Ripple = check_bollinger_band_condition(df_Ripple)
            df_Ripple = check_bullish_candlestick_pattern(df_Ripple)
            df_Ripple = check_rsi_conditions(df_Ripple)
            df_Ripple = check_adx_conditions(df_Ripple)
            df_Ripple = check_stochastic_conditions(df_Ripple)
            df_Ripple = predict_below_618(df_Ripple)
            
            return df_Ripple, ripple_status_dates
        
        return df_Ripple, []
    except Exception as e:
        st.error(f"Error processing ripple data for {ticker} and datetime range {datetime_range}: {e}")
        return pd.DataFrame(), []

def check_buy_conditions(ticker):
    try:
        df_Tide, tide_status_dates = process_tide(ticker)
        
        if tide_status_dates.size > 0:
            for tide_date in tide_status_dates:
                df_Wave, wave_status_dates = process_wave(ticker, tide_date)
                
                if wave_status_dates.size > 0:
                    for wave_datetime in wave_status_dates:
                        datetime_range = (wave_datetime + pd.Timedelta(hours=1), wave_datetime + pd.Timedelta(hours=2))
                        df_Ripple, ripple_status_dates = process_ripple(ticker, datetime_range)
                        
                        if ripple_status_dates.size > 0:
                            return df_Tide, df_Wave, df_Ripple
        return df_Tide, pd.DataFrame(), pd.DataFrame()
    except Exception as e:
        st.error(f"Error checking buy conditions for {ticker}: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def show_buy_recommendations(tickers_list):
    st.title("Buy Recommendations")

    current_time = datetime.now().time()
    current_datetime = datetime.combine(datetime.now().date(), current_time)
    
    for ticker in tickers_list:
        try:
            df_Tide, df_Wave, df_Ripple = check_buy_conditions(ticker)
            
            if not df_Ripple.empty:
                last_entry = df_Ripple.iloc[-1]
                
                if last_entry['HA_Green'] and last_entry['Ripple_Status']:
                    st.subheader(f"{ticker}: Buy Recommendation")
                    st.dataframe(df_Ripple.loc[df_Ripple.index[-1]])
        except Exception as e:
            st.error(f"An error occurred while processing {ticker}: {e}")

def generate_final_report(tickers_list):
    st.title("Final Report")

    for ticker in tickers_list:
        try:
            df_Tide, df_Wave, df_Ripple = check_buy_conditions(ticker)
            
            if not df_Ripple.empty:
                st.subheader(f"Results for {ticker}")
                st.dataframe(df_Ripple)
                # Add more details or visualizations as needed
        except Exception as e:
            st.error(f"An error occurred while processing {ticker}: {e}")

def main():
    st.title("Stock Scanner App")

    # Input for stock tickers
    tickers = st.text_area("Enter Stock Tickers (comma-separated):", "DIXON.NS, TCS.NS, INFY.NS")
    flag_date = st.date_input("Select Date", datetime.now().date())
    flag_time = st.time_input("Select Time", time(9, 0))
    flag_datetime = datetime.combine(flag_date, flag_time)
    
    tickers_list = [ticker.strip() for ticker in tickers.split(",")]

    page = st.sidebar.selectbox("Select a page", ["Scan Stocks", "Buy Recommendations", "Final Report"])

    if page == "Scan Stocks":
        st.title("Stock Scanner App")
        if st.button("Scan Stocks"):
            for ticker in tickers_list:
                with st.spinner(f"Scanning {ticker}..."):
                    df_Tide, df_Wave, df_Ripple = check_buy_conditions(ticker)
                
                if not df_Ripple.empty:
                    df_Ripple['Date'] = df_Ripple['Datetime'].dt.date
                    daily_data = df_Ripple[df_Ripple['Date'] == flag_date]
                    
                    st.subheader(f"Results for {ticker} on {flag_date}")
                    st.subheader("Candles for the Day (Ripple_Status = True)")
                    st.dataframe(daily_data)
                    
                    # Plot candlestick chart
                    fig = plot_candlestick(daily_data)
                    st.plotly_chart(fig)
                else:
                    st.info(f"No buy signals detected for {ticker} on {flag_date} (No rows with Ripple_Status = True).")
    elif page == "Buy Recommendations":
        show_buy_recommendations(tickers_list)
    elif page == "Final Report":
        generate_final_report(tickers_list)

    # Add JavaScript for Refresh
    st.markdown(
        """
        <script>
        setTimeout(function() {
            window.location.reload();
        }, 960000); // 16 minutes in milliseconds
        </script>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
