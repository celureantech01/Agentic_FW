import requests
import pandas as pd
STOCK_TKR = "IBM"
COMPANY_NAME = "IBM Inc"
ANALYZE_FROM = "2024-01-01"
#optional parameter in news i think but check if declaring date as string is a problem

#api for stock related tech and financial data
STOCKDATA_EP = "https://www.alphavantage.co/query"
STOCKDATA_API_KEY = "WXAZUCPJ1A94Y1WB"
STOCK_FUNCTIONS =  ["TIME_SERIES_DAILY", "TIME_SERIES_INTRADAY", "TIME_SERIES_DAILY_ADJUSTED", "REALTIME OPTIONS", "NEWS_SENTIMENT", "TOP_GAINERS_LOSERS", "INSIDER_TRANSACTIONS", "OVERVIEW", "INCOME_STATEMENT", "BALANCE_SHEET", "MACD", "RSI"]
# TOTAL_FUNCTIONS = len(STOCK_FUNCTIONS) if if else statement based on len tatic is needed
# few of functions taken from URL excep inventory. Many more under same API umnrella available in excel, can add later
# most of the functions have same API EP and parameters except a few, so using same API and for looping through stock functions list as "functions" parameter in stock params dict

#api for stock related news
STOCKNEWS_EP = "https://newsapi.org/v2/everything"
STOCKNEWS_API_KEY ="52a78d615dcb4eaab7cbe917db3d6f0b"

#get stock data
for PASSED_S_F in STOCK_FUNCTIONS:
    stock_params = {
        "function": PASSED_S_F,
        "symbol" : STOCK_TKR,
        "apikey" : STOCKDATA_API_KEY,
    }

response = requests.get(STOCKDATA_EP, params=stock_params)
#pass functions from the functions list and get APIs executed one by one and all data is gathered. Skip where API calls fail or error.
# Most likely exceptions are because API params dont match with requirements. We can make specific API calls later as this is for demo only

datatable = pd.json_normalize(response.json())
datadf = pd.DataFrame(datatable)
print(datadf)
#to do - covert to float, format data frame  and save
#convert data in floats where applicable (need automated conversion agnostic of use case)
# auto merge of common fields coming from various APIs and append new ones to the stock record


#get stock news
stocknews_params = {
    "q": "COMPANY_NAME",
    "from": "ANALYZE_FROM",
    "apiKey" : STOCKNEWS_API_KEY,
}

responsenews = requests.get(STOCKNEWS_EP, params=stocknews_params)
newstable = pd.json_normalize(responsenews.json())
newsdf = pd.DataFrame(newstable)
print(newsdf)

#to do - cleanse data, format data frame  and save
#figure out data architecture, storage, MPP/clusters
# JSON structure usually contains lists with lists and/or dictionaries having sub disctionaries with key value pairs
