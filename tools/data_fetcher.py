import requests
import tweepy
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from utils.config import (
    NEWS_API_KEY,
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_ID_SECRET,
    ALPHAVANTAGE_API_KEY,
    TWELVEDATA_API_KEY,
    TWITTER_API_KEY,
    TWITTER_API_KEY_SECRET,
    TWITTER_BEARER_TOKEN,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    TELEGRAM_BOT_TOKEN,
    DISCORD_BOT_TOKEN
)
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import praw
# import tweepy  # Twitter functionality is temporarily disabled
import telegram
# import discord  # Discord functionality is temporarily disabled
# import asyncio
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Initialize Sentiment Analyzer
analyzer = SentimentIntensityAnalyzer()

# Default values for missing parameters
DEFAULT_CHANNEL_ID = 899729438244208702  # Replace with an actual channel ID (for Discord)
DEFAULT_SUBREDDIT = "CryptoCurrency"
# DEFAULT_TWITTER_HASHTAG = "stock market"
DEFAULT_MESSAGE_COUNT = 5


# Alpha Vantage: Fetch financial data

def fetch_financial_data(ticker):
    """ Fetch stock data from Alpha Vantage API. """
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": ticker,
        "apikey": ALPHAVANTAGE_API_KEY,
        "outputsize": "compact"  # Returns ~100 most recent days
    }

    response = requests.get(base_url, params=params)
    data = response.json()
    # Debugging: Print raw API response to see if the data is returned
    print("\n🔍 Raw Alpha Vantage API Response:")
    print(data)

    if "Time Series (Daily)" not in data:
        # print("⚠️ No time series data found! Check API response.")  # Commented out
        return {}

    return data  # Return the full JSON response

# Debugging: Print the full raw response (formatted for readability)
    try:
        data = response.json()
        # print("\n🔍 RAW API RESPONSE:")  # Commented out
        # print(json.dumps(data, indent=4))  # Pretty print JSON response

        return data
    except Exception as e:
        # print("\n❌ Error parsing JSON response:", str(e))  # Commented out
        # print("\n⚠️ RAW TEXT RESPONSE:", response.text)  # Print raw text if JSON parsing fails
        return None

# Fetch financial news
def fetch_financial_news(company_name):
    """ Fetch financial news using News API """
    url = f"https://newsapi.org/v2/everything?q={company_name}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    articles = response.json().get("articles", [])
    return [(article["title"], article["url"]) for article in articles]


# Reddit Sentiment Analysis
def fetch_reddit_sentiment(subreddit=DEFAULT_SUBREDDIT):
    """ Fetch sentiment from Reddit using PRAW """
    reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_ID_SECRET, user_agent="myBot/0.1")
    hot_posts = reddit.subreddit(subreddit).hot(limit=10)
    sentiment_score = sum(1 for post in hot_posts if "bullish" in post.title.lower()) - sum(
        1 for post in hot_posts if "bearish" in post.title.lower())
    return sentiment_score  # Return numeric sentiment score


# Telegram - Fetch messages from a bot
async def fetch_telegram_messages():
    try:
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        updates = await bot.get_updates(limit=DEFAULT_MESSAGE_COUNT)

        messages = [update.message.text for update in updates if update.message]
        return messages
    except Exception as e:
        # print(f"Error fetching Telegram messages: {e}")  # Commented out
        return "Telegram sentiment unavailable"


# Detect unusual volume in stock data
def detect_unusual_volume(asset, historical_data):
    """ Detects unusual spikes in trading volume """
    historical_data["Volume_MA"] = historical_data["Volume"].rolling(window=20).mean()
    threshold = historical_data["Volume_MA"] * 1.5  # 50% above moving average
    unusual_spikes = historical_data[historical_data["Volume"] > threshold]
    return unusual_spikes


# Analyze sentiment
def analyze_sentiment(text):
    """ Perform sentiment analysis on given text """
    sentiment = analyzer.polarity_scores(text)
    return sentiment["compound"]


# Get sentiment visualization
def get_sentiment_visualization(sentiments, title):
    """ Visualize sentiment analysis results """
    # Check if sentiments is a list or just a single score
    if isinstance(sentiments, list):
        sentiment_scores = sentiments
    else:
        sentiment_scores = [sentiments]  # If a single score, make it a list for consistency

    plt.figure(figsize=(10, 5))
    sns.histplot(sentiment_scores, kde=True, color='blue')
    plt.title(f"{title} Sentiment Distribution")
    plt.xlabel('Sentiment Score')
    plt.ylabel('Frequency')
    plt.show()


# Plot stock price data with sentiment

def plot_price_data_with_sentiment(ticker, sentiment_data):
    """ Plot stock price data with sentiment scores """
    # Fetch stock data from Alpha Vantage
    stock_data = fetch_financial_data(ticker)

    # Check if stock data is available
    if "Time Series (Daily)" in stock_data:
        time_series = stock_data["Time Series (Daily)"]
        # Convert the time series into a DataFrame
        price_data = pd.DataFrame.from_dict(time_series, orient="index")
        price_data = price_data.astype(float)
        price_data.index = pd.to_datetime(price_data.index)

        # Debugging: Check if sentiment_data is empty
        if not sentiment_data:
            print("⚠️ Sentiment data is empty.")
            return

        # Check if sentiment_data has dates corresponding to the stock data
        sentiment_scores = [sentiment_data.get(date, 0) for date in price_data.index]

        # Debugging: Check if sentiment scores are correctly populated
        if len(sentiment_scores) != len(price_data):
            print(
                f"⚠️ Mismatch between stock data and sentiment data. Stock dates: {len(price_data)}, Sentiment scores: {len(sentiment_scores)}")

        # Plot stock data with sentiment
        plt.figure(figsize=(12, 6))
        plt.plot(price_data['4. close'], label='Stock Price')
        plt.plot(price_data.index, sentiment_scores, label='Sentiment Score', alpha=0.7)
        plt.title(f"Stock Price and Sentiment for {ticker}")
        plt.xlabel('Date')
        plt.ylabel('Value')
        plt.legend()
        plt.show()
    else:
        print(f"No data available for {ticker} from Alpha Vantage")
#
# # Twitter Sentiment Analysis
# def fetch_twitter_sentiment(ticker):
#     """ Fetches sentiment from Twitter using tweepy. """
#     try:
#         # Authenticate with Twitter API using Tweepy
#         auth = tweepy.OAuth1UserHandler(
#             consumer_key=TWITTER_API_KEY,
#             consumer_secret=TWITTER_API_KEY_SECRET,
#             access_token=TWITTER_ACCESS_TOKEN,
#             access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
#         )
#         api = tweepy.API(auth)
#
#         tweets = api.search_tweets(q=ticker, count=10, lang="en", tweet_mode="extended")
#         sentiment_score = sum(1 for tweet in tweets if "bullish" in tweet.full_text.lower()) - sum(
#             1 for tweet in tweets if "bearish" in tweet.full_text.lower())
#         return f"Twitter Sentiment Score: {sentiment_score}"
#
#     except tweepy.errors.Forbidden as e:
#         print(f"Twitter API Forbidden: {e}")
#         return "Twitter sentiment unavailable"
#     except Exception as e:
#         print(f"Error fetching Twitter sentiment: {e}")
#         return "Twitter sentiment unavailable"

# Main function to collect all asset data
import pandas as pd

class DataFetcher:
    def __init__(self):
        # Any initialization logic for fetching data
        pass

    async def get_asset_data(self, ticker, company_name):
        """Collect and return all asset data"""
        asset_data = {}

        try:
            # ✅ Fetch stock data from Alpha Vantage
            price_data = fetch_financial_data(ticker)

            if "Time Series (Daily)" in price_data:
                time_series = price_data["Time Series (Daily)"]

                # ✅ Convert the time series into a Pandas DataFrame
                # price_data_df = pd.DataFrame.from_dict(time_series, orient="index", dtype=float)
                # ============reactivate and remove following line============================
                price_data_df = pd.DataFrame.from_dict(time_series, orient="index").astype(float)

                # ✅ Rename columns to standard names
                price_data_df.rename(columns={
                    "1. open": "Open",
                    "2. high": "High",
                    "3. low": "Low",
                    "4. close": "Close",
                    "5. volume": "Volume"
                }, inplace=True)

                # ✅ Ensure index is datetime
                price_data_df.index = pd.to_datetime(price_data_df.index)

                # ✅ Sort data (newest first by default in Alpha Vantage)
                price_data_df = price_data_df.sort_index()

                # ✅ Store DataFrame for analysis
                asset_data["price_data_df"] = price_data_df

                # ✅ Convert for dictionary display (for JSON serialization)
                asset_data["price_data"] = {
                    "Date": price_data_df.index.strftime('%Y-%m-%d').tolist(),
                    "Open": price_data_df["Open"].tolist(),
                    "High": price_data_df["High"].tolist(),
                    "Low": price_data_df["Low"].tolist(),
                    "Close": price_data_df["Close"].tolist(),
                    "Volume": price_data_df["Volume"].tolist(),
                }
            else:
                asset_data["price_data_df"] = pd.DataFrame()
                asset_data["price_data"] = {}

        except Exception as e:
            asset_data["price_data_df"] = pd.DataFrame()
            asset_data["price_data"] = {}

        # ✅ Fetch additional data sources
        try:
            asset_data["financial_news"] = fetch_financial_news(company_name) or []
            asset_data["reddit_sentiment"] = fetch_reddit_sentiment() or 0

            asset_data["telegram_messages"] = await fetch_telegram_messages()  # Await for async function
        except Exception as e:
            asset_data["financial_news"] = []
            asset_data["reddit_sentiment"] = 0
            asset_data["telegram_messages"] = []

        # ✅ Generate Reddit sentiment visualization
        try:
            get_sentiment_visualization(asset_data["reddit_sentiment"], "Reddit Sentiment")
        except Exception as e:
            pass  # We can skip visualizations for now.

        # ✅ Generate Twitter Sentiment Visualization
        # try:
        #     get_sentiment_visualization(asset_data["twitter_sentiment"], "Twitter Sentiment")
        # except Exception as e:
        #     pass  # We can skip visualizations for now.

        return asset_data
