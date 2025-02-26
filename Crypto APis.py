import requests
import pandas as pd
from io import StringIO
import json
cumulative_response = ""

# url = "https://api.coingecko.com/api/v3/coins/bitcoin/tickers?exchange_ids=binance&x_cg_demo_api_key=CG-1v2X7ox5hiAB1NTZNGH87Xe6"
# headers = {"accept": "application/json"}
# response1 = requests.get(url, headers=headers)
# cumulative_response += response1.text
#
# meme coins
# url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category=meme-token&price_change_percentage=1h&x_cg_demo_api_key=CG-1v2X7ox5hiAB1NTZNGH87Xe6"
# headers = {"accept": "application/json"}
# response2_meme = requests.get(url, headers=headers)
# cumulative_response += response2_meme.text
#
# #ai agent coins
# url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category=ai-agents&price_change_percentage=1h&x_cg_demo_api_key=CG-1v2X7ox5hiAB1NTZNGH87Xe6"
# headers = {"accept": "application/json"}
# response3_aiagent = requests.get(url, headers=headers)
# cumulative_response += response3_aiagent.text
#
# # ai app coins
# url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category=ai-application&price_change_percentage=1h&x_cg_demo_api_key=CG-1v2X7ox5hiAB1NTZNGH87Xe6"
# headers = {"accept": "application/json"}
# response4_aiapp = requests.get(url, headers=headers)
# cumulative_response += response4_aiapp.text
#
# ai meme coins
# url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category=ai-meme-coins&price_change_percentage=1h&x_cg_demo_api_key=CG-1v2X7ox5hiAB1NTZNGH87Xe6"
# headers = {"accept": "application/json"}
# response5_aimeme = requests.get(url, headers=headers)
# cumulative_response += response5_aimeme.text

# #trending coins
url = "https://api.coingecko.com/api/v3/search/trending?x_cg_demo_api_key=CG-1v2X7ox5hiAB1NTZNGH87Xe6"
headers = {"accept": "application/json"}
response6_trend = requests.get(url, headers=headers)
cumulative_response += response6_trend.text
# print(cumulative_response)

cumres_json = json.loads(cumulative_response)
for coin in cumres_json["coins"]:
    print(coin)

# # print(cumres_json)
# shortlist = ""
# for coin in cumres_json["coins"]:
#     shortlist += coin["item"]["id"]
#     print(coin["item"]["id"]["data"]

# for coin in cumres_json["coins"]:
#     # if isinstance(coin, dict):  # Ensure the item is a dictionary
#     item_id = coin["item"]["id"]  # Directly access 'id' from 'item'
#     price = item_id["data"]["price"]  # Directly access 'price' from 'data'
#     print(f"ID: {item_id}, Price: {price}")

# for nft in cumres_json["nfts"]:
#     shortlist += nft["id"]
# print(shortlist)
# first_dict = cumulative_response[14]
# first_value = list(first_dict.values())[0]
# print(first_dict)
# # consolidated list
#
# cumresdf = pd.read_csv(StringIO(cumulative_response))
# print(cumresdf)
# #
