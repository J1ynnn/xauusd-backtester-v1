import pandas as pd

import config

# cleaning up the files

def load_data(path):
    # the csv heading is separated by tabs
    df = pd.read_csv(path, sep = '\t') 
    
    # removing '<>' from the header and lower case the column so easier to use in the future
    df.columns = df.columns.str.strip('<>').str.lower() 
    
    # combining date+time into 1 column, converting the text into real timedates that are comparable
    # for indexing and such, this is broker's server time right now
    df['when'] = pd.to_datetime(df['date'] + ' ' + df['time'], format = '%Y.%m.%d %H:%M:%S')
    
    # converting to UTC, the time in the data is not standard UTC but New York + 7 
    # which is affected by daylight saving
    df['time_utc'] = ((df['when'] - pd.Timedelta(hours = config.server_hours_ahead_of_NY))
                     .dt.tz_localize('America/New_York')
                     .dt.tz_convert('UTC'))
    
    # making the time_utc the index and dropping unnecessary columns such as 
    # original date, time, when and vol (since vol is over 'exchange' but gold is by broker is always 0)
    # tick volume is the important one not the volume itself
    df = df.set_index('time_utc')
    df = df.drop(columns = ['date', 'time', 'when', 'vol'])
    
    
    
    return df


# Test block: only runs when THIS file is run directly (python data_loader.py).

if __name__ == '__main__':
    df = load_data(config.xauusd_data)
    print(df.head())
    print(df.columns)
    print(df.shape)                            # rows, columns
    print(df.index[0], df.index[-1])           # first and last timestamp
    print(df.index.is_monotonic_increasing)    # True = sorted oldest data first
    print(df.index.duplicated().sum())         # number of duplicate timestamps
    print(df.isna().sum().sum())               # total missing values in the table
    




