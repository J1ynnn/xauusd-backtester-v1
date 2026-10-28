import pandas as pd

import config
import data_loader
import indicators

def add_signals(df):
    df = df.copy()
    
    # creating an uptrend/downtrend signal
    df['uptrend'] = (df['ema_fast'] > df['ema_slow']) 
    # "Price > EMA 50 condition removed: it left only 2 buys in four years,
    # because oversold pullbacks almost always push price below EMA 50."
    df['downtrend'] = (df['ema_fast'] < df['ema_slow'])  
    
    # creating overbought/oversold signal
    df['armed_oversold'] = ((df['rsi'].shift(1) < config.oversold) 
                            & (df['rsi_ma'].shift(1) <config.oversold))
    df['armed_overbought'] = ((df['rsi'].shift(1) > config.overbought) 
                              & (df['rsi_ma'].shift(1) > config.overbought))
    
    # creating cross-up/cross-down signal 
    df['cross_up']   = ((df['rsi'] > config.oversold) 
                        & (df['rsi'].shift(1) <= config.oversold))
    df['cross_down'] = ((df['rsi'] < config.overbought) 
                        & (df['rsi'].shift(1) >= config.overbought))
    
    # creating buy/sell signal
    df['buy_signal'] = (df['armed_oversold']  & df['cross_up'] & df['uptrend']) 
    df['sell_signal'] = (df['armed_overbought']  & df['cross_down'] & df['downtrend']) 

    return df 

# Test block:
if __name__ == '__main__':
    df = data_loader.load_data(config.xauusd_data)
    full_df = indicators.add_indicators(df)
    signal_test = add_signals(full_df)
    print(full_df.head())
    print(full_df.columns)
    print(signal_test['buy_signal'].sum())
    print(signal_test['sell_signal'].sum())
    
    
