import pandas as pd
import numpy as np

def simulate_bitcoin_prices(days=60, start_price=60000, volatility=0.04):
    """Simulate Bitcoin prices using Geometric Brownian Motion"""
    # Seed for consistent testing, but can be removed for pure randomness
    np.random.seed(2)
    prices = [start_price]
    for _ in range(1, days):
        shock = np.random.normal(0, volatility)
        price = prices[-1] * np.exp(shock)
        prices.append(price)

    dates = pd.date_range(start='2024-01-01', periods=days, freq='D')
    df = pd.DataFrame({'Date': dates, 'Price': prices})
    return df

def calculate_moving_averages(df):
    """Calculate 7-day and 30-day Moving Averages"""
    df['7_MA'] = df['Price'].rolling(window=7).mean()
    df['30_MA'] = df['Price'].rolling(window=30).mean()
    return df

def run_trading_simulation(df, initial_capital=10000):
    """Run Golden Cross trading algorithm"""
    capital = initial_capital
    btc_held = 0
    ledger = []

    prev_7_ma = None
    prev_30_ma = None

    for index, row in df.iterrows():
        date = row['Date'].strftime('%Y-%m-%d')
        price = row['Price']
        ma_7 = row['7_MA']
        ma_30 = row['30_MA']

        if pd.notna(ma_7) and pd.notna(ma_30) and pd.notna(prev_7_ma) and pd.notna(prev_30_ma):
            # Golden Cross: 7-day MA crosses above 30-day MA
            if prev_7_ma <= prev_30_ma and ma_7 > ma_30:
                if capital > 0:
                    btc_bought = capital / price
                    btc_held += btc_bought
                    ledger.append(f"{date}: BUY  - Price: ${price:.2f}, BTC: {btc_bought:.6f}, Cost: ${capital:.2f}")
                    capital = 0
            # Death Cross (Sell): 7-day MA crosses below 30-day MA
            elif prev_7_ma >= prev_30_ma and ma_7 < ma_30:
                if btc_held > 0:
                    revenue = btc_held * price
                    capital += revenue
                    ledger.append(f"{date}: SELL - Price: ${price:.2f}, BTC: {btc_held:.6f}, Revenue: ${revenue:.2f}")
                    btc_held = 0

        prev_7_ma = ma_7
        prev_30_ma = ma_30

    final_value = capital + (btc_held * df.iloc[-1]['Price'])
    return ledger, initial_capital, final_value, capital, btc_held

if __name__ == "__main__":
    df = simulate_bitcoin_prices(60)
    df = calculate_moving_averages(df)

    ledger, initial, final, end_capital, end_btc = run_trading_simulation(df)

    print("Daily Ledger of Trades:")
    if not ledger:
        print("No trades executed (no crossover detected or not enough data).")
    else:
        for entry in ledger:
            print(entry)

    print("\n" + "="*50 + "\n")
    print("Final Portfolio Performance:")
    print(f"Initial Capital: ${initial:.2f}")
    print(f"Final Capital:   ${end_capital:.2f}")
    print(f"Final BTC Held:  {end_btc:.6f}")
    print(f"Final Portfolio Value: ${final:.2f}")

    roi = ((final - initial) / initial) * 100
    print(f"Return on Investment (ROI): {roi:.2f}%")
