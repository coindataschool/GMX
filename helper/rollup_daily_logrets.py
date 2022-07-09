def rollup_daily_logrets(daily_logrets):
    """ Aggregate the daily log returns to weekly and monthly levels.

    Arguments:
    daily_logrets -- a series of daily log returns.

    Returns
    -------
    A dictionary of daily, weekly and monthly log returns.
    """

    ha = (daily_logrets.reset_index(level='date')
            .assign(month = lambda x: x.date.dt.to_period('M'),
                    week = lambda x: x.date.dt.to_period('W')))
    # ha.head()
    logret_monthly = ha.groupby([ha.index, ha.month]).logret.sum()
    logret_weekly = ha.groupby([ha.index, ha.week]).logret.sum()
    # simply put the daily returns in the same format as the monthly and weekly;
    # doesn't aggregate since each row of ha is already at daily level. 
    logret_daily = ha.groupby([ha.index, ha.date]).logret.sum() 
    
    return {'daily':logret_daily, 'weekly':logret_weekly, 'monthly':logret_monthly}