import backtest
import streamlit as st

# set_page_config() can only be called once per app, and must be called as the 
# first Streamlit command in your script.
st.set_page_config(page_title='Backtest GLP Strategies', layout='wide', page_icon='📈') 

st.sidebar.title('Choose Chain')
selection = st.sidebar.radio("", ["Arbitrum", "Avalanche"])

st.header('Backtest and Compare GLP Strategies')
backtest.run_app(chain = selection)