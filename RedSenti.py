import praw
import os
from datetime import datetime, timezone
from textblob import TextBlob

client_id = os.getenv('REDDIT_CLIENT_ID')
client_secret = os.getenv('REDDIT_CLIENT_SECRET')
user_agent = os.getenv('REDDIT_USER_AGENT')

# PRAW
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent
)

# Function to get and process Reddit posts
def fetch_reddit_posts(subreddit_name, limit=1000):
    subreddit = reddit.subreddit(subreddit_name)
    posts = subreddit.new(limit=limit)
    posts_data = []

    for post in posts:
        post_data = {
            "title": post.title,
            "url": post.url,
            "created_utc": datetime.fromtimestamp(post.created_utc, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
            "selftext": post.selftext
        }
        posts_data.append(post_data)
    
    return posts_data

# Function to perform sentiment analysis
def analyze_sentiment(posts_data):
    sentiments = []

    for post in posts_data:
        text = post['title'] + " " + post['selftext']
        blob = TextBlob(text)
        sentiment = blob.sentiment
        sentiments.append({
            "title": post['title'],
            "url": post['url'],
            "created_utc": post['created_utc'],
            "polarity": sentiment.polarity,
            "subjectivity": sentiment.subjectivity,
            "text": text
        })
    
    return sentiments

# Summarize sentiment analysis
def summarize_sentiments(sentiments):
    positive_posts = [post for post in sentiments if post['polarity'] > 0]
    negative_posts = [post for post in sentiments if post['polarity'] < 0]
    neutral_posts = [post for post in sentiments if post['polarity'] == 0]

    summary = {
        "total_posts": len(sentiments),
        "positive_posts": len(positive_posts),
        "negative_posts": len(negative_posts),
        "neutral_posts": len(neutral_posts),
        "average_polarity": sum(post['polarity'] for post in sentiments) / len(sentiments) if sentiments else 0,
        "average_subjectivity": sum(post['subjectivity'] for post in sentiments) / len(sentiments) if sentiments else 0,
        "positive_stocks": [post['title'] for post in positive_posts]
    }

    return summary

# process Reddit posts
try:
    posts_data = fetch_reddit_posts('wallstreetbets')

    # sentiment analysis
    sentiments = analyze_sentiment(posts_data)

    # Summarize sentiment analysis
    summary = summarize_sentiments(sentiments)
    print(f"Summary of sentiment analysis:\n{summary}")
    print("\nList of positively summarized stocks:")
    for stock in summary['positive_stocks']:
        print(stock)

except Exception as e:
    print(f"An error occurred: {e}")
