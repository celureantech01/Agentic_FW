import requests
import pandas as pd
STOCK_TKR = "IBM"
COMPANY_NAME = "IBM"
ANALYZE_FROM = "2024-01-01"
#optional parameter in news i think but check if declaring date as string is a problem

#api for stock related tech and financial data
STOCKDATA_EP = "https://www.alphavantage.co/query"
STOCKDATA_API_KEY = "WXAZUCPJ1A94Y1WB"
STOCK_FUNCTIONS =  ["TIME_SERIES_DAILY_ADJUSTED", "TIME_SERIES_WEEKLY", "TIME_SERIES_MONTHLY","GLOBAL_QUOTE","REALTIME_OPTIONS", "HISTORICAL_OPTIONS", "INSIDER_TRANSACTIONS", "OVERVIEW", "DIVIDENDS", "SPLITS", "INCOME_STATEMENT","BALANCE_SHEET", "CASH_FLOW", "EARNINGS"]
# TOTAL_FUNCTIONS = len(STOCK_FUNCTIONS) if if else statement based on len tatic is needed
# few of functions taken from URL excep inventory. Many more under same API umnrella available in excel, can add later
# most of the functions have same API EP and parameters except a few, so using same API and for looping through stock functions list as "functions" parameter in stock params dict

#api for stock related news
STOCKNEWS_EP = "https://newsapi.org/v2/everything"
STOCKNEWS_API_KEY ="52a78d615dcb4eaab7cbe917db3d6f0b"
cumulative_response = ""
#get stock data
for PASSED_S_F in STOCK_FUNCTIONS:
    stock_params = {
        "function": PASSED_S_F,
        "symbol" : STOCK_TKR,
        "apikey" : STOCKDATA_API_KEY,
    }

response = requests.get(STOCKDATA_EP, params=stock_params)
total_response = response.text
cumulative_response += total_response


#pass functions from the functions list and get APIs executed one by one and all data is gathered. Skip where API calls fail or error.
# Most likely exceptions are because API params dont match with requirements. We can make specific API calls later as this is for demo only
#
# datatable = pd.json_normalize(response.json())
# datadf = pd.DataFrame(datatable)
# print(datadf)
#to do - covert to float, format data frame  and save
#convert data in floats where applicable (need automated conversion agnostic of use case)
# auto merge of common fields coming from various APIs and append new ones to the stock record

#
# #get stock news
stocknews_params = {
    "q": "COMPANY_NAME",
    "from": "ANALYZE_FROM",
    "apiKey" : STOCKNEWS_API_KEY,
}

responsenews = requests.get(STOCKNEWS_EP, params=stocknews_params)
cumulative_response += responsenews.text
# print(cumulative_response)

stoch_params = {
    "function": "STOCH",
    "symbol" : STOCK_TKR,
    "interval": "monthly",
    "apikey" : STOCKDATA_API_KEY,
}

responsestoch = requests.get(STOCKDATA_EP, params=stoch_params)
cumulative_response += responsestoch.text


rsi_params = {
    "function": "RSI",
    "symbol" : STOCK_TKR,
    "interval": "daily",
    "time_period": "1",
    "series_type": "open",
    "apikey" : STOCKDATA_API_KEY,
}

responsersi = requests.get(STOCKDATA_EP, params=rsi_params)
cumulative_response += responsersi.text

bband_params = {
    "function": "BBANDS",
    "symbol" : STOCK_TKR,
    "interval": "daily",
    "time_period": "10",
    "series_type": "open",
    "apikey" : STOCKDATA_API_KEY,
}

responsebb = requests.get(STOCKDATA_EP, params=bband_params)
cumulative_response += responsebb.text

sma_params = {
    "function": "SMA",
    "symbol" : STOCK_TKR,
    "interval": "daily",
    "time_period": "10",
    "series_type": "open",
    "apikey" : STOCKDATA_API_KEY,
}

responsesma = requests.get(STOCKDATA_EP, params=sma_params)
cumulative_response += responsesma.text

lg_params = {
    "function": "TOP_GAINERS_LOSERS",
    "apikey" : STOCKDATA_API_KEY,
}

responselg = requests.get(STOCKDATA_EP, params=lg_params)
cumulative_response += responselg.text

com_params = {
    "function": "ALL_COMMODITIES",
    "apikey" : STOCKDATA_API_KEY,
    "interval" : "monthly",

}
responsecom = requests.get(STOCKDATA_EP, params=com_params)
cumulative_response += responsecom.text

retail_params = {
    "function": "RETAIL_SALES",
    "apikey" : STOCKDATA_API_KEY,
}
responseret = requests.get(STOCKDATA_EP, params=retail_params)
cumulative_response += responseret.text

unem_params = {
    "function": "UNEMPLOYMENT",
    "apikey" : STOCKDATA_API_KEY,
}
responseunem = requests.get(STOCKDATA_EP, params=unem_params)
cumulative_response += responseunem.text

gdp_params = {
    "function": "REAL_GDP",
    "interval" : "annual",
    "apikey" : STOCKDATA_API_KEY,
}
responsegdp = requests.get(STOCKDATA_EP, params=gdp_params)
cumulative_response += responsegdp.text

infl_params = {
    "function": "INFLATION",
    "apikey" : STOCKDATA_API_KEY,
}
responseinf = requests.get(STOCKDATA_EP, params=infl_params)
cumulative_response += responseinf.text

tres_params = {
    "function": "TREASURY_YIELD",
    # "interval" : "annual"
    # "maturity : "10year"
    "apikey" : STOCKDATA_API_KEY,
}
responsetre = requests.get(STOCKDATA_EP, params=tres_params)
cumulative_response += responsetre.text

sent_params = {
    "function" : "NEWS_SENTIMENT",
    "tickers" :  STOCK_TKR,
    "apikey" : STOCKDATA_API_KEY,
}
responsesent = requests.get(STOCKDATA_EP, params=sent_params)
cumulative_response += responsesent.text

print(cumulative_response)
# newstable = pd.json_normalize(responsenews.json())
# newsdf = pd.DataFrame(newstable)
# print(newsdf)

#to do - cleanse data, format data frame  and save
#figure out data architecture, storage, MPP/clusters
# JSON structure usually contains lists with lists and/or dictionaries having sub disctionaries with key value pairs
