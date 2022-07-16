import numpy as np
import pandas as pd

def calc_value_growth_history(daily_prices, start_date, init_capital=10_000):
    """ Calculate daily investment values.
    
    Arguments:
    daily_prices -- pandas Series. 
    start_date -- datetime or string. Investment start date. A date string like 
        '2022-06-15' works. 
    init_capital -- numeric. How much money did you start with? Default is $10,000.
    """
        
    # calculate log returns
    logret_his = np.log(daily_prices / daily_prices.shift(1)).dropna()
    logret_his.name = 'logret'
    
    # can't start after the last day of available historical returns
    last_day = logret_his.index[-1]
    assert pd.to_datetime(start_date) <= last_day 

    # select historical daily log returns after investment start data
    print("Investment started on", start_date, '\n')
    chosen_logret_his = logret_his.loc[pd.to_datetime(start_date) + pd.Timedelta(days=1):]
    # print(chosen_logret_his.head())
    
    # calc value of investment at each time index
    values_his = init_capital * chosen_logret_his.cumsum().apply(np.exp)
    values_his.name = 'value'

    # create a row of data for initial investment 
    t0 = values_his.index[0] - pd.Timedelta(days=1)
    value_genesis = pd.Series({t0: init_capital})
    value_genesis.name = 'value'
    
    # stack and return
    return pd.concat([value_genesis, values_his])
