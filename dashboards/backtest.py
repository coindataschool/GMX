import os
import numpy as np
import pandas as pd
from duda import dune
import streamlit as st
from strats import bt_strat1, bt_strat2, bt_strat3, bt_strat4, bt_strat5
import plotly.express as px

# define helper function
def extract_frame_from_dune_data(dune_data):    
    dd = dune_data['data']['get_result_by_result_id']
    df = pd.json_normalize(dd, record_prefix='')
    df = df.loc[:, df.columns.str.startswith('data')]
    df.columns = df.columns.str.replace('data.', '', regex=False)
    # set `day` as index
    df['date'] = pd.to_datetime(df.day.str.replace('T.*', '', regex=True))
    del df['day']
    df = df.set_index('date')
    # drop the last row cuz it may not always be a full day
    return df.iloc[:-1, :]

def run_app(chain):
    reward_token = 'AVAX' if chain == 'Avalanche' else 'ETH'
    qid_price_yield = 1105079 if chain == 'Arbitrum' else 1109126
    qid_swap_cost = 1095373 if chain == 'Arbitrum' else 1101895
    qid_claim_cost = 1092684 if chain == 'Arbitrum' else 1102122 
    qid_mint_cost = 1069676 if chain == 'Arbitrum' else 1102319 

    # read data from Dune
    dune.login()
    dune.fetch_auth_token()

    # fetch query result
    price_yield = dune.query_result(dune.query_result_id(query_id=qid_price_yield))
    swap_cost = dune.query_result(dune.query_result_id(query_id=qid_swap_cost))
    claim_cost = dune.query_result(dune.query_result_id(query_id=qid_claim_cost))
    mint_cost = dune.query_result(dune.query_result_id(query_id=qid_mint_cost))

    # extract data frames
    df_price_yield = extract_frame_from_dune_data(price_yield)
    df_swap_cost = extract_frame_from_dune_data(swap_cost)
    df_claim_cost = extract_frame_from_dune_data(claim_cost)
    df_mint_cost = extract_frame_from_dune_data(mint_cost)

    # prep data
    df_price_yield['yield_per_share_usd'] = \
        df_price_yield.yield_usd / df_price_yield.cumu_glp_supply
    if chain == 'Arbitrum':
        df_price_yield['yield_per_share_eth'] = \
            df_price_yield.yield_eth / df_price_yield.cumu_glp_supply
    else:
        df_price_yield['yield_per_share_avax'] = \
            df_price_yield.yield_avax / df_price_yield.cumu_glp_supply

    # the 4 frames may have different last date, so we pick the smallest
    end_date = np.min([df_price_yield.index[-1], df_swap_cost.index[-1], 
                       df_claim_cost.index[-1], df_mint_cost.index[-1]])

    # --- Set up --- #

    # user inputs    
    st.header("Enter your numbers:")
    c1, c2, c3 = st.columns(3)
    with c1:
        if chain=='Arbitrum':
            start_date = st.text_input('Start Date [enter a date after 2021-08-31]', '2021-08-31') 
        else: 
            start_date = st.text_input('Start Date [enter a date after 2022-01-06]', '2022-01-06')
    with c2:
        start_capital = st.number_input('Investment ($ USD)', 10_000)
    with c3:
        start_reserve = st.number_input('Gas Money ($ USD)', 1600)

    # important days
    day1 = pd.to_datetime(start_date)
    day2 = day1 + pd.Timedelta(1, 'day')
    # day_before_end = end_date - pd.Timedelta(1, 'day')
    # print('Start:', start_date)
    # print('Day 2:', day2.strftime('%Y-%m-%d'))
    # print('Day before last day:', day_before_end.strftime('%Y-%m-%d'))
    # print('End:', end_date.strftime('%Y-%m-%d'))

    # beginning account value before any tx 
    total_value_day1 = pd.Series(start_capital+start_reserve, index=pd.Index({day1}, name='date'))

    # buy GLP with capital. what's the purchase price and tx cost?
    init_price = df_price_yield.loc[start_date, 'glp_price']
    init_fee_bp = df_mint_cost.loc[start_date, 'fee_bp']
    init_fee = start_capital * init_fee_bp/1e4 # platform fee
    init_gas = df_mint_cost.loc[start_date, 'gas_usd']

    # pay tx cost
    capital = start_capital - init_fee 
    reserve = start_reserve - init_gas # always pay gas from reserve funds

    # how many shares of GLP did we buy?
    init_shares = capital / init_price

    # --- backtest strategies --- #

    res = dict()
    # strat1 
    name = 'Accumulate {} rewards, Claim them once on last day and Sell into USD'.format(reward_token)
    res[name] = bt_strat1(chain, df_price_yield, day2, end_date, init_shares, 
                          reserve, df_claim_cost, df_swap_cost, total_value_day1)
    # strat2
    name = 'Claim and Sell {} Rewards into USD Daily'.format(reward_token)
    res[name] = bt_strat2(df_price_yield, day2, end_date, init_shares, reserve,
                          df_claim_cost, df_swap_cost, total_value_day1)
    # strat3
    name = 'Reinvest {} Rewards into GLP Daily'.format(reward_token)
    res[name] = bt_strat3(df_price_yield, day2, end_date, init_shares, reserve,
                          df_claim_cost, df_mint_cost, total_value_day1)
    # strat4
    name = 'Claim and Sell {} Rewards into USD Weekly'.format(reward_token)
    res[name] = bt_strat4(df_price_yield, day2, end_date, init_shares, reserve,
                          df_claim_cost, df_swap_cost, total_value_day1)
    # strat5
    name = 'Reinvest {} Rewards into GLP Weekly'.format(reward_token)
    res[name] = bt_strat5(df_price_yield, day2, end_date, init_shares, reserve,
                          df_claim_cost, df_mint_cost, total_value_day1)

    # --- Compare --- #

    df = pd.DataFrame(res)
    df_long = df.stack().to_frame().reset_index()
    df_long.columns = ['Date', 'Strategy', 'Account Value']

    # --- app --- #

    # gb_referred = GridOptionsBuilder.from_dataframe(df_long)
    # gb_referred.configure_grid_options(domLayout='normal')
    # go_referred = gb_referred.build()

    # AgGrid(df_long,
    #        key = np.random.uniform(0), # crucial, otherwise duplicated key error
    #        gridOptions=go_referred,
    #        height=150, 
    #        allow_unsafe_jscode=False # True to allow jsfunction to be injected
    # )
    
    st.header(chain)
    fig = px.line(df_long, x='Date', y='Account Value', color='Strategy',
        labels=dict(Date=""))
    fig.update_layout(plot_bgcolor="white", yaxis_tickprefix = '$', 
        yaxis_tickformat = ',.2f',
        legend=dict(orientation="h")
    )
    st.plotly_chart(fig, use_container_width=True)
    