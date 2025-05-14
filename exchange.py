import streamlit as st
import ccxt

@st.cache_resource
def init_exchange():
    api_key    = st.secrets["OKX_API_KEY"]
    api_secret = st.secrets["OKX_API_SECRET"]
    passphrase = st.secrets["OKX_PASSPHRASE"]
    exchange = ccxt.okx({
        "apiKey": api_key,
        "secret": api_secret,
        "password": passphrase,
        "enableRateLimit": True,
    })
    exchange.load_markets()
    return exchange
