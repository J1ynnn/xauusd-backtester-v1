import pandas as pd

import config
import data_loader
import indicators
import signals
import backtest
 
# raw win rate calculator = no of wins/total trades taken
def win_rate_calculator(trades):
    win_count = (trades['outcome'] == 'win').sum()
    return win_count/ len(trades)

# calculating net_R 
def net_R_calculator(trades):
    return trades['R'].sum()

#calculate R expectancy
def R_expectancy_calculator(trades):
    return trades['R'].mean()

#equity curve tracking total earnings by summing all R
def equity_curve(trades):
    return trades['R'].cumsum().rename('equity')

#calculate max drawdowns from peak equity 
def max_drawdowns(trades):
    net_equity = equity_curve(trades)
    peak_equity = net_equity.cummax()
    return (net_equity - peak_equity).min()

# counting number of win and lose streak to find max wins and max lose streaks
def streak_counter(trades):
    current_win = current_loss = 0
    win_streak = [] #contain win streaks before resets so will only append before counter reset
    lose_streak = [] #contain lose streaks before resets so will only append before counter reset
    
    for r in trades['outcome']:
        
        # initial count
        if current_win == 0 and current_loss == 0:
            if r == 'win':
                current_win = current_win + 1
            elif r == 'loss':
                current_loss= current_loss + 1
            
        #if we are on a winstreak
        elif current_win > 0 and current_loss == 0:
            if r == 'win':
                current_win = current_win + 1
            elif r == 'loss': # win streak broken
                win_streak.append(current_win)
                current_win = 0 #reset counter
                current_loss = current_loss + 1
        
        #if we are on a lose streak     
        elif current_win == 0 and current_loss > 0:
            if r == 'win': #lose streak broken
                lose_streak.append(current_loss)
                current_loss = 0 #reset counter
                current_win = current_win + 1
                
            elif r == 'loss':
                current_loss = current_loss + 1
        
        # counting final streak when loop ends that would not be counted since it isn't 'broken'
    if current_win > 0:
        win_streak.append(current_win)
    if current_loss > 0:
        lose_streak.append(current_loss)
    
    #counting max win/loss
    max_win_streak, max_lose_streak = max(win_streak), max(lose_streak)
    return max_win_streak, max_lose_streak

#  breaking down traades by direction, counting net R for 'buying' and 'selling'
def direction_breakdown(trades):
    return trades.groupby('trade_direction')['R'].agg(['count', 'sum'])

# breaking down trades by year, counting trades taken in a year and net R
def year_breakdown(trades):
    return trades.groupby(trades['time_of_exit'].dt.year)['R'].agg(['count', 'sum'])


# summary function containing key information
def create_summary(trades):
    longest_win_streak, longest_lose_streak = streak_counter(trades)
    summary = pd.Series({'number of trades': len(trades),
                            'win_rate': win_rate_calculator(trades), 
                            'net R': net_R_calculator(trades),
                            'R expectancy': R_expectancy_calculator(trades),
                            'max_drawdowns': max_drawdowns(trades),
                            'longest_win_streak': longest_win_streak,
                            'longest_lose_streak': longest_lose_streak
                            })          
    return summary

if __name__ == '__main__':
    df = data_loader.load_data(config.xauusd_data) #download full data
    
    # putting indicators on data
    df_indicators = indicators.add_indicators(df)
    
    # adding signals on dev data
    full_df = signals.add_signals(df_indicators)
    
    # split the data for development period
    df_dev_data = full_df.loc[config.dev_start : config.dev_end] 
    test = backtest.run_backtest(df_dev_data)
    
    #testing and printing metrics
    print(create_summary(test))
