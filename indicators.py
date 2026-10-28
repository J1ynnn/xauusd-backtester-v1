import pandas as pd

import config
import data_loader

# ema calculation function
def my_ema(series, length):
    result = series.ewm(span = length, adjust = False).mean()
    return result

# rsi calculation function 
# LLM assist with cleaning the function compared to v1, v1 is in the practice folder

def my_rsi(series, n):
    
    # Step 1: change from the previous close (row 0 -> NaN)
    #   loop version: change = series - series.shift(1)
    change = series.diff()

    # Step 2: split into gains and losses, both positive, row 0 filled with 0
    #   loop version: the if / elif / else chain with append
    gain = change.clip(lower=0).fillna(0)       # falls become 0
    loss = (-change).clip(lower=0).fillna(0)    # flip sign, so falls are positive; rises become 0

    # Step 3: Wilder smoothing, weight 1/length
    #   loop version: the zip loop with yest_gain / yest_loss
    avg_gain = gain.ewm(alpha=1/n, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/n, adjust=False).mean()

    # Step 4: RSI = share of movement that went up, on a 0-100 scale
    #   loop version: rs = gain / loss, then 100 - 100 / (1 + rs)
    #   rearranged so there's no division by zero to handle:
    #   100 - 100/(1 + G/L) = 100 * G / (G + L)
    #   row 0: 0 / 0 -> NaN automatically (no reading, as it should be)
    return 100 * avg_gain / (avg_gain + avg_loss)

# adding new columns for ema, rsi and rsi ma
def add_indicators(df):
    
    df = df.copy()
    df['ema_fast'] = my_ema(df['close'], config.ema_fast)
    df['ema_slow'] = my_ema(df['close'], config.ema_slow)
    df['rsi'] = my_rsi(df['close'], config.rsi_length)
    df['rsi_ma'] = df['rsi'].rolling(window = config.rsi_ma_length).mean()
    
    return df

# Test block
if __name__ == '__main__':
    df = data_loader.load_data(config.xauusd_data)
    result_ema_fast = my_ema(df['close'], config.ema_fast)
    result_ema_slow = my_ema(df['close'], config.ema_slow)
    result_rsi = my_rsi(df['close'], config.rsi_length)
    full_df = add_indicators(df)
    print(result_ema_fast.head())
    print(result_ema_slow.head())
    print(full_df.iloc[-1])
    