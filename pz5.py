#Відео-захист: https://youtu.be/ucMY710GGBQ
import tweepy
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Bearer Token
bearer_token = "AAAAAAAAAAAAAAAAAAAAAGQ40wEAAAAAqcE%2Blo%2FnSPLlSLm4BJCHYvzaTis%3D8mrRXOxAaVwHJ1bgrQcuonKoE5UwKRAd7SUkjDeeYERDjzwjOG"

# Ініціалізація клієнта API v2
client = tweepy.Client(bearer_token=bearer_token)

# Пошук твітів за ключовим словом
response = client.search_recent_tweets(query="data science", max_results=10, tweet_fields=["lang", "text"])

def clean_text(text):
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"@[A-Za-z0-9_]+", "", text)
    text = re.sub(r"[^A-Za-z0-9\s]", "", text)
    return text

def get_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    score = analyzer.polarity_scores(text)
    return score['compound']

# Аналіз результатів
for tweet in response.data:
    text = tweet.text
    clean = clean_text(text)
    sentiment = get_sentiment(clean)
    print(f"Tweet: {clean}\nSentiment: {sentiment}\n")
