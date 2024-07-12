import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
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
        template="plotly_white",
        xaxis_type='category',
        xaxis=dict(
            tickformat='%H:%M',
            dtick=1800000,
            tickmode='linear'
        )
    )
    
    return fig

def trading_strategy(df, stop_loss_percentage=0.05, target_profit_factor=1.5):
    initial_capital = 100000
    capital = initial_capital
    position = 0
    buy_price = 0
    stop_loss = stop_loss_percentage
    target_gain = target_profit_factor * stop_loss_percentage
    trade_log = []

    try:
        for index, row in df.iterrows():
            if row['Ripple_Status'] and row['HA_Type'] == 'Solid Green' and position == 0:
                position = capital / row['Close']
                buy_price = row['Close']
                stop_loss_price = buy_price - stop_loss
                target_price = buy_price + target_gain
                capital = 0
                trade_log.append({
                    'Buy Time': row['Datetime'],
                    'Buy Price': buy_price,
                    'Stop Loss': stop_loss_price,
                    'Target Price': target_price,
                    'Win/Loss': ''  # Initialize 'Win/Loss' key
                })
            elif (not row['Ripple_Status'] or row['HA_Type'] == 'Solid Red') and position > 0:
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
        total_profit = sum(trade['Profit/Loss'] for trade in trade_log)

        win_ratio = wins / num_trades if num_trades > 0 else 0
        profit_percentage = (final_value - initial_capital) / initial_capital * 100

        return trade_log, win_ratio, profit_percentage

    except Exception as ex:
        st.error(f"An error occurred during trading: {str(ex)}")
        return [], 0, 0


def main():
    st.title("Stock Scanner App")

    tickers = st.text_area("Enter Stock Tickers (comma-separated):", "RELIANCE.NS, INFY.NS")
    flag_date = st.date_input("Select Date", datetime.now().date())
    stop_loss_percentage = st.number_input("Stop Loss Percentage", min_value=0.01, max_value=0.1, value=0.05, step=0.01)
    target_profit_factor = st.number_input("Target Profit Factor", min_value=1.0, max_value=2.0, value=1.5, step=0.1)
    
    tickers_list = [ticker.strip() for ticker in tickers.split(",")]

    if st.button("Scan Stocks"):
        for ticker in tickers_list:
            try:
                with st.spinner(f"Scanning {ticker}..."):
                    df_Tide, df_Wave, df_Ripple = scanner.Check_buy_condition(ticker)

                df_Ripple['Date'] = df_Ripple['Datetime'].dt.date
                daily_data = df_Ripple[df_Ripple['Date'] >= flag_date]

                if daily_data['Ripple_Status'].any():
                    buy_signals = daily_data[['Datetime', 'HA_Open', 'HA_High', 'HA_Low', 'HA_Close', 'Volume', 'HA_Type', 'HA_Green', 'HA_Red', 'Pattern', 'Price_Above_EMA', 'RSI_Type', 'ADX_14', 'ADX Status', 'Stochastic_PCO', 'Stochastic_Oversold', 'Stochastic_PC_from_Oversold', 'Below_618']]
                    
                    st.subheader(f"Results for {ticker} on {flag_date}")
                    st.subheader("Candles for the Day (Ripple_Status = True)")
                    st.dataframe(buy_signals)
                    
                    fig = plot_candlestick(daily_data)
                    st.plotly_chart(fig)

                    trade_log, win_ratio, profit_percentage = trading_strategy(daily_data, stop_loss_percentage, target_profit_factor)
                    trade_log_df = pd.DataFrame(trade_log)

                    st.subheader("Trade Log")
                    st.dataframe(trade_log_df)

                    st.write(f"Win Ratio: {win_ratio}")
                    st.write(f"Profit Percentage: {profit_percentage}%")
                else:
                    st.info(f"No buy signals detected for {ticker} on {flag_date} (No rows with Ripple_Status = True).")
            except Exception as ex:
                st.error(f"Error processing {ticker}: {str(ex)}")

if __name__ == "__main__":
    main()
