import praw
from utils.config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT


def fetch_reddit_sentiment(subreddit="CryptoCurrency"):
    reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, user_agent=REDDIT_USER_AGENT)
    hot_posts = reddit.subreddit(subreddit).hot(limit=10)

    sentiment_score = sum(1 for post in hot_posts if "bullish" in post.title.lower()) - sum(
        1 for post in hot_posts if "bearish" in post.title.lower())

    return f"Reddit Sentiment Score: {sentiment_score}"
