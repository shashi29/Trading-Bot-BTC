import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, time
from config import config
from scanner import StockScanner

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

def main():
    st.title("Stock Scanner App")

    # Input for stock tickers
    tickers = st.text_area("Enter Stock Tickers (comma-separated):", "RELIANCE.NS, INFY.NS")
    flag_date = st.date_input("Select Date", datetime.now().date())
    # flag_time = st.time_input("Select Time", time(9, 0))
    # flag_datetime = datetime.combine(flag_date, flag_time)
    
    tickers_list = [ticker.strip() for ticker in tickers.split(",")]

    if st.button("Scan Stocks"):
        for ticker in tickers_list:
            try:
                with st.spinner(f"Scanning {ticker}..."):
                    df_Tide, df_Wave, df_Ripple = scanner.Check_buy_condition(ticker)

                # Filter the DataFrame to include only rows for the selected date
                df_Ripple['Date'] = df_Ripple['Datetime'].dt.date
                daily_data = df_Ripple[df_Ripple['Date'] == flag_date]

                # Check if any Ripple_Status is True on the selected date
                if daily_data['Ripple_Status'].any():
                    #buy_signals = daily_data[daily_data['Ripple_Status'] == True]
                    buy_signals = daily_data[['Datetime', 'HA_Open', 'HA_High', 'HA_Low', 'HA_Close', 'Volume', 'HA_Type', 'HA_Green', 'HA_Red', 'Pattern','Price_Above_EMA', 'RSI_Type', 'ADX_14', 'ADX Status', 'Stochastic_PCO', 'Stochastic_Oversold', 'Stochastic_PC_from_Oversold', 'Below_618']]
                    
                    st.subheader(f"Results for {ticker} on {flag_date}")
                    st.subheader("Candles for the Day (Ripple_Status = True)")
                    st.dataframe(buy_signals)
                    
                    # Plot candlestick chart
                    fig = plot_candlestick(daily_data)
                    st.plotly_chart(fig)
                else:
                    st.info(f"No buy signals detected for {ticker} on {flag_date} (No rows with Ripple_Status = True).")
            except Exception as ex:
                st.info(f"Error for {ticker} on {flag_date}")


if __name__ == "__main__":
    main()
