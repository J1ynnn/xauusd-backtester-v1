import numpy as np
import pandas as pd

import config
import data_loader
import indicators
import signals

#function to execute backtesting of strategy and produce list of trades
def run_backtest(df):
    
    # converting the data columns into numpy arrays for faster reading
    price_open  = df['open'].to_numpy()
    price_close = df['close'].to_numpy()
    price_high = df['high'].to_numpy()
    price_low = df['low'].to_numpy()
    ema_fast = df['ema_fast'].to_numpy()
    ema_slow = df['ema_slow'].to_numpy()
    rsi = df['rsi'].to_numpy()
    rsi_ma = df['rsi_ma'].to_numpy()
    buy_signal = df['buy_signal'].to_numpy()
    sell_signal = df['sell_signal'].to_numpy()
    timestamps = df.index.to_numpy()
    
    # variable to store trade
    trades = []
    in_trade = False # not in trade
    lookback = config.candle_look_back
    reward = config.reward_ratio
    
    
    for i in range(lookback, len(df)): 
        if not in_trade: # we are not in trade = open position
            if buy_signal[i -1]: # if previous candle close shows a buy signal
                trade_entry = price_open[i]
                trade_sl = price_low[i - lookback : i].min() #stop loss calculation (lowest of past 10 candles)
                
                # Risk check: if price gapped to/past the stop before entry, risk <= 0
                # (R would divide by zero, target would land on the wrong side) -> not a real trade.
                # `continue` skips it BEFORE in_trade is set, so nothing is opened or recorded.
                risk = trade_entry - trade_sl 
                
                if risk <= 0: #skip the invalid trade
                    continue 
                
                in_trade = True 
                time_entry = timestamps[i]
                trade_tp = price_open[i] + (reward * risk)
                trade_direction = 'buy' # recording trade direction
                
            elif sell_signal[i -1]: #if previous candle close shows a sell signal
                trade_entry = price_open[i]
                trade_sl = price_high[i - lookback : i].max()
                risk = trade_sl - trade_entry
                
                if risk <= 0:
                    continue
                
                in_trade = True 
                time_entry = timestamps[i]
                trade_tp = price_open[i] - (reward * risk)
                trade_direction = 'sell'
                
            else:  # if we were 'not in the trade' and the candle close shows neither position, we do nothing
                continue
            
        if in_trade: # after trade is executed, begin checking the candle
            # if hit both tp and sl in same candle, we will assume it is a loss 
            
            if trade_direction == 'buy': # Case 1: buy position
                if trade_sl >= price_low[i]: #stop loss triggered (price close can be price that isn't lowerst)
                    
                    in_trade = False
                    time_exit = timestamps[i]
                    trade_exit = trade_sl #will only consider stopping at sl, no slippage yet that is for refinement
                    result = 'loss'
                    R = (trade_exit - trade_entry) / risk
                    
                elif trade_tp <= price_high[i]: # take profit triggered, tp may not be at high
                    
                    in_trade = False
                    time_exit = timestamps[i]
                    trade_exit = trade_tp
                    result = 'win'
                    R = (trade_exit - trade_entry) / risk
                    
                else: #doesnt hit both tp or sl
                    continue
            
            elif trade_direction == 'sell': # Case 2: sell position
                if trade_sl <= price_high[i]: #stop loss triggered (price close can be price that isn't highest)
                    
                    in_trade = False
                    time_exit = timestamps[i]
                    trade_exit = trade_sl #will only consider stopping at sl, no slippage yet that is for refinemen
                    result = 'loss'
                    R = (trade_entry - trade_exit) / risk
                                   
                elif trade_tp >= price_low[i]: # take profit triggered, close price may not be price_low
                    
                    in_trade = False
                    time_exit = timestamps[i]
                    trade_exit = trade_tp
                    result = 'win'
                    R = (trade_entry - trade_exit) / risk
         
                else: #doesnt hit both tp or sl
                    continue
                
            # recording the trade
            trades.append({'time_of_entry': time_entry, 'entry_price': trade_entry, 'time_of_exit': time_exit,
                           'trade_exit': trade_exit, 'stop_loss': trade_sl, 'target': trade_tp, 'R': R,
                           'outcome': result, 'trade_direction': trade_direction})
    trades_log = pd.DataFrame(trades)
   
    return trades_log

            
                            
# Test block
# will split the data and only use from July 2022 to June 2025 for development
# data from June 2025 to October 2026 will be used for 'live testing' and ML
if __name__ == '__main__':
    df = data_loader.load_data(config.xauusd_data) #download full data
    
    # putting indicators on dev data
    df_indicators = indicators.add_indicators(df)
    
    # adding signals on dev data
    full_df = signals.add_signals(df_indicators)
    
    # split the data for development period
    df_dev_data = full_df.loc[config.dev_start : config.dev_end] 
    
    #call the test on small set of data
    test = run_backtest(df_dev_data.iloc[: 10000])
    print(test.iloc[:50])
    
    