import pandas as pd 

# Strategy 1: Accumulate rewards and Claim once at the end and Swap to USD 
def bt_strat1(chain, df_price_yield, day2, end_date, init_shares, reserve,
              df_claim_cost, df_swap_cost, total_value_day1):

    # from day 2 until the last day
    if chain == 'Arbitrum':
        df = (df_price_yield.loc[day2:end_date, ['eth_price', 'glp_price', 'yield_per_share_eth']]
                .assign(my_glp_shares = init_shares,
                        my_yield_eth = lambda x: x.yield_per_share_eth * x.my_glp_shares,
                        my_cumu_yield_eth = lambda x: x.my_yield_eth.cumsum(),
                        my_cumu_yield_usd = lambda x: x.my_cumu_yield_eth * x.eth_price,
                        my_total_value = lambda x: x.glp_price * x.my_glp_shares + x.my_cumu_yield_usd + reserve))
    else:
        df = (df_price_yield.loc[day2:end_date, ['avax_price', 'glp_price', 'yield_per_share_avax']]
                .assign(my_glp_shares = init_shares,
                        my_yield_avax = lambda x: x.yield_per_share_avax * x.my_glp_shares,
                        my_cumu_yield_avax = lambda x: x.my_yield_avax.cumsum(),
                        my_cumu_yield_usd = lambda x: x.my_cumu_yield_avax * x.avax_price,
                        my_total_value = lambda x: x.glp_price * x.my_glp_shares + x.my_cumu_yield_usd + reserve))

    # on the last day, what's the usd value of all rewards we accumulated?
    rewards_value = df.loc[end_date, 'my_cumu_yield_usd']

    # 1. claim all accumulated rewards. don't pay any fees to the platform, but need to pay gas 
    fee = 0
    gas = df_claim_cost.loc[end_date, 'gas_usd']

    # 2. swap them to usd on the platform. need to pay a fee to the platform and gas 
    fee += rewards_value * (df_swap_cost.loc[end_date, 'fee_bp']/1e4)
    gas += df_swap_cost.loc[end_date, 'gas_usd']

    # update total value on last day
    df.loc[end_date, 'my_total_value'] = df.loc[end_date, 'my_total_value'] - fee - gas

    # return the series of account values; don't forget beginning value
    return pd.concat([total_value_day1, df.my_total_value])

# Strategy 2: Claim and Sell Rewards into USD Daily
def bt_strat2(df_price_yield, day2, end_date, init_shares, reserve,
              df_claim_cost, df_swap_cost, total_value_day1):

    # from day 2 until the last day
    df = (pd.merge(df_price_yield.loc[day2:end_date, ['glp_price', 'yield_per_share_usd']], 
                   df_claim_cost, left_index=True, right_index=True)
            .rename(columns = {'gas_usd': 'gas_claim'}))
    df = (pd.merge(df, df_swap_cost, left_index=True, right_index=True)
            .rename(columns = {'gas_usd': 'gas_swap', 'fee_bp': 'fee_bp_swap'}))
    df = (df.assign(my_glp_shares = init_shares,
                    # no fees are collected by the platform when we claim rewards;
                    # a fee is collected by the platform everytime we sell rewards to usd 
                    my_yield_usd_after_fees = lambda x: x.yield_per_share_usd * x.my_glp_shares * (1-x.fee_bp_swap/1e4),
                    # need to pay gas everytime we claim and everytime we swap
                    reserve = lambda x: reserve - x.gas_claim.cumsum() - x.gas_swap.cumsum(),
                    # finally we calculate total account value each day
                    my_total_value = lambda x: x.glp_price * x.my_glp_shares + x.my_yield_usd_after_fees + x.reserve)
        ) 

    # if df.reserve.loc[end_date] < 0:
    #     print("To implement this strategy, you need at least ${} in reserve to pay gas.".format(np.ceil(reserve + abs(df.reserve.loc[end_date]))))

    # return the series of account values; don't forget beginning value
    return pd.concat([total_value_day1, df.my_total_value])

# Strategy 3: Reinvest Rewards into GLP Daily
def bt_strat3(df_price_yield, day2, end_date, init_shares, reserve,
              df_claim_cost, df_mint_cost, total_value_day1):

    # from day 2 until the last day
    df = (pd.merge(df_price_yield.loc[day2:end_date, ['glp_price', 'yield_per_share_usd']], 
                   df_claim_cost, left_index=True, right_index=True)
            .rename(columns = {'gas_usd': 'gas_claim'}))
    df = (pd.merge(df, df_mint_cost, left_index=True, right_index=True)
            .rename(columns = {'gas_usd': 'gas_mint', 'fee_bp': 'fee_bp_mint'}))
    daily_shares = [init_shares] # init_shares bought on end of day1
    daily_reserve = [reserve] 
    daily_acct_value = [total_value_day1.iloc[0]]

    for i in range(len(df)): # 1st row of df is day2. 
        shares_yesterday = daily_shares[-1] 
        reserve_yesterday = daily_reserve[-1]
        
        # shares_yesterday earn full yield today                               
        yield_today = df.yield_per_share_usd[i] * shares_yesterday 

        # no fees are collected by the platform when we claim rewards;
        # a fee is collected by the platform everytime we mint glp
        yield_today_after_fees = yield_today * (1-df.fee_bp_mint[i]/1e4)
        # reinvest today's yield after fees at today's price
        price_today = df.glp_price[i]
        shares_bought_today = yield_today_after_fees / price_today       
        # how many shares we have at end of today
        shares_today = shares_yesterday + shares_bought_today 

        # also need to pay gas everytime we claim and everytime we mint glp
        reserve_today = reserve_yesterday - df.gas_claim[i] - df.gas_mint[i]

        # calculate account value today
        # note that today's yield after fees was distributed into shares_today, and 
        # reserve_today accounted for gas
        acct_value_today = shares_today * price_today + reserve_today
        
        # collect today's values
        daily_shares.append(shares_today)
        daily_reserve.append(reserve_today)
        daily_acct_value.append(acct_value_today)

    # if daily_reserve[-1] < 0:
    #     print("To implement this strategy, you need at least ${} in reserve to pay gas.".format(np.ceil(start_reserve + abs(daily_reserve[-1]))))
        
    # return the series of account values; don't forget the beginning value
    return pd.Series(daily_acct_value, index=total_value_day1.index.append(df.index))

# Strategy 4: Claim and Sell Rewards into USD Weekly 
def bt_strat4(df_price_yield, day2, end_date, init_shares, reserve,
              df_claim_cost, df_swap_cost, total_value_day1):

    # from day 2 until the last day
    df = (pd.merge(df_price_yield.loc[day2:end_date, ['glp_price', 'yield_per_share_usd']], 
                   df_claim_cost, left_index=True, right_index=True)
            .rename(columns = {'gas_usd': 'gas_claim'}))
    df = (pd.merge(df, df_swap_cost, left_index=True, right_index=True)
            .rename(columns = {'gas_usd': 'gas_swap', 'fee_bp': 'fee_bp_swap'}))

    daily_shares = [init_shares] # init_shares bought on end of day1
    daily_reserve = [reserve] 
    daily_acct_value = [total_value_day1.iloc[0]]
    yield_7d = 0

    for i in range(len(df)): # 1st row of df is day2. 
        shares_yesterday = daily_shares[-1] 
        reserve_yesterday = daily_reserve[-1]    
        price_today = df.glp_price[i]
        yield_today = df.yield_per_share_usd[i] * shares_yesterday # shares_yesterday earn full yield today                               
        yield_7d += yield_today 
        
        # sell rewards into usd every 7 days
        if (i > 0) and (i%7 == 0):
            # no fees are collected by the platform when we claim rewards;
            # a fee is collected by the platform everytime we swap 
            yield_7d_after_fees = yield_7d * (1 - df.fee_bp_swap[i]/1e4)
            # also need to pay gas everytime we claim and everytime we sell them into usd
            reserve_today = reserve_yesterday - df.gas_claim[i] - df.gas_swap[i]
            yield_7d = 0 # reset to get ready for the next 7-day
            # calculate account value today
            shares_today = shares_yesterday
            acct_value_today = shares_today * price_today + yield_7d_after_fees + reserve_today
        else: # no action, just carry through the values
            shares_today = shares_yesterday
            reserve_today = reserve_yesterday
            acct_value_today = shares_today * price_today + yield_today + reserve_today
        
        # collect today's values
        daily_shares.append(shares_today)
        daily_reserve.append(reserve_today)
        daily_acct_value.append(acct_value_today)    
        
    # return the series of account values
    return pd.Series(daily_acct_value, index=total_value_day1.index.append(df.index))

# Strategy 5: Reinvest Rewards into GLP Weekly
def bt_strat5(df_price_yield, day2, end_date, init_shares, reserve,
              df_claim_cost, df_mint_cost, total_value_day1):
    # from day 2 until the last day
    df = (pd.merge(df_price_yield.loc[day2:end_date, ['glp_price', 'yield_per_share_usd']], 
                   df_claim_cost, left_index=True, right_index=True)
            .rename(columns = {'gas_usd': 'gas_claim'}))
    df = (pd.merge(df, df_mint_cost, left_index=True, right_index=True)
            .rename(columns = {'gas_usd': 'gas_mint', 'fee_bp': 'fee_bp_mint'}))

    daily_shares = [init_shares] # init_shares bought on end of day1
    daily_reserve = [reserve] 
    daily_acct_value = [total_value_day1.iloc[0]]
    yield_7d = 0

    for i in range(len(df)): # 1st row of df is day2. 
        shares_yesterday = daily_shares[-1] 
        reserve_yesterday = daily_reserve[-1]    
        price_today = df.glp_price[i]
        yield_today = df.yield_per_share_usd[i] * shares_yesterday # shares_yesterday earn full yield today                               
        yield_7d += yield_today 
        
        # reinvest every 7 days
        if (i > 0) and (i%7 == 0):
            # no fees are collected by the platform when we claim rewards;
            # a fee is collected by the platform everytime we mint glp
            yield_7d_after_fees = yield_7d * (1 - df.fee_bp_mint[i]/1e4)
            # reinvest 7 days of yield after fees at today's price
            shares_bought_today = yield_7d_after_fees / price_today
            shares_today = shares_yesterday + shares_bought_today 
            # also need to pay gas everytime we claim and everytime we mint glp
            reserve_today = reserve_yesterday - df.gas_claim[i] - df.gas_mint[i]
            yield_7d = 0 # reset to get ready for the next 7-day
            # calculate account value today
            acct_value_today = shares_today * price_today + reserve_today
        else: # no action, just carry through the values
            shares_today = shares_yesterday
            reserve_today = reserve_yesterday
            acct_value_today = shares_today * price_today + yield_today + reserve_today
        
        # collect today's values
        daily_shares.append(shares_today)
        daily_reserve.append(reserve_today)
        daily_acct_value.append(acct_value_today)    
        
    # return the series of account values
    return pd.Series(daily_acct_value, index=total_value_day1.index.append(df.index))