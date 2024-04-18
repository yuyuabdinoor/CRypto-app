import streamlit as st
from PIL import Image
import pandas as pd
import base64
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import json
import re
import time



## Page expands to full width
st.set_page_config(layout="wide")

image = Image.open('logo.jpg')
st.image(image, width = 500)

st.title('Crypto Price App')
st.markdown("""
This app retrieves cryptocurrency prices for the top 100 cryptocurrency from the **CoinMarketCap**!

""")

# About
expander_bar = st.expander("About")
expander_bar.markdown("""
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn, BeautifulSoup, requests, json, time
* **Data source:** [CoinMarketCap](http://coinmarketcap.com).

""")

## Divide page to 3 columns (col1 = sidebar, col2 and col3 = page contents)
col1 = st.sidebar
col2, col3 = st.columns((2,1))

#---------------------------------#
# Sidebar + Main panel
col1.header('Input Options')

## Sidebar - Currency price unit
currency_price_unit = col1.selectbox('Select currency for price', ('USD', 'BTC', 'ETH'))

# Web scraping of CoinMarketCap data
import requests

API_KEY = '5681d20e-4c1a-4099-8c88-ea7bf61a5305'

def load_data():
    headers = {
        'X-CMC_PRO_API_KEY': API_KEY,
        'Accept': 'application/json'
    }
    params = {
        'limit': 100  # Retrieve data for the top 100 cryptocurrencies
    }
    response = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest', headers=headers, params=params)
    data = response.json()
    
    if 'data' not in data:
        raise Exception('Error retrieving cryptocurrency data from the API')
    
    listings = data['data']
    
    # Extract data for selected cryptocurrencies
    
    coin_name = []
    coin_symbol = []

    
    for coin in listings:
        coin_name.append(coin['name'])
        coin_symbol.append(coin['symbol'])
  
    
    
    df = pd.DataFrame({
        'coin_name': coin_name,
        'coin_symbol': coin_symbol,
    
    })
    return df

# Load data using the API
df = load_data()


## Sidebar - Cryptocurrency selections
sorted_coin = sorted( df['coin_symbol'] )
selected_coin = col1.multiselect('Cryptocurrency', sorted_coin, sorted_coin)

df_selected_coin = df[ (df['coin_symbol'].isin(selected_coin)) ] # Filtering data

## Sidebar - Number of coins to display
num_coin = col1.slider('Display Top N Coins', 1, 100, 100)
df_coins = df_selected_coin[:num_coin]

## Sidebar - Percent change timeframe
percent_timeframe = col1.selectbox('Percent change time frame',
                                    ['7d','24h', '1h'])
percent_dict = {"7d":'percent_change_7d',"24h":'percent_change_24h',"1h":'percent_change_1h'}
selected_percent_timeframe = percent_dict[percent_timeframe]

## Sidebar - Sorting values
sort_values = col1.selectbox('Sort values?', ['Yes', 'No'])

col2.subheader('Price Data of Selected Cryptocurrency')
col2.write('Data Dimension: ' + str(df_selected_coin.shape[0]) + ' rows and ' + str(df_selected_coin.shape[1]) + ' columns.')

col2.dataframe(df_coins)


def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="crypto.csv">Download CSV File</a>'
    return href

col2.markdown(filedownload(df_selected_coin), unsafe_allow_html=True)

#---------------------------------#
# Preparing data for Bar plot of % Price change

col2.subheader('Table of % Price Change')

# Check if the column exists in the DataFrame
if 'percent_change_7d' not in df.columns:
    st.error('Error: "percent_change_7d" column not found in the DataFrame.')
else:
    # Selecting the required columns
    df_change = df_coins[['coin_symbol', 'percent_change_7d']].set_index('coin_symbol')

    # Adding a column for positive percent change
    df_change['positive_percent_change'] = df_change['percent_change_7d'] > 0

    # Displaying the DataFrame
    col2.dataframe(df_change)

    # Conditional creation of Bar plot (time frame)
    col3.subheader('Bar plot of % Price Change')

    if sort_values == 'Yes':
        df_change = df_change.sort_values(by='percent_change_7d')

    col3.write('*7 days period*')
    plt.figure(figsize=(5, 25))
    plt.subplots_adjust(top=1, bottom=0)
    df_change['percent_change_7d'].plot(kind='barh', color=df_change['positive_percent_change'].map({True: 'g', False: 'r'}))
    col3.pyplot(plt)
