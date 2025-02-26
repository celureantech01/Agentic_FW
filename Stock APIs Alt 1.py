import requests
import pandas as pd
STOCK_TKR = "IBM"
COMPANY_NAME = "IBM Inc"
ANALYZE_FROM = "2024-01-01"
#check if declaring date as string is a problem

#api for stock related tech and financial data
STOCKDATA_EP = "https://www.alphavantage.co/query"
STOCKDATA_API_KEY = "WXAZUCPJ1A94Y1WB"

#api for stock related news
STOCKNEWS_EP = "https://newsapi.org/v2/everything"
STOCKNEWS_API_KEY ="52a78d615dcb4eaab7cbe917db3d6f0b"

#get stock data
stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol" : STOCK_TKR,
    "apikey" : STOCKDATA_API_KEY,
}

response = requests.get(STOCKDATA_EP, params=stock_params)
datatable = pd.json_normalize(response.json())
datadf = pd.DataFrame(datatable)
print(datadf)
#to do - covert to float, format data frame  and save


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