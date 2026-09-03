import os

# Database Path Configuration
DB_NAME = "news_collection.db"
DATABASE_URL = f"sqlite:///{DB_NAME}"

# Retention Policy Settings
DEFAULT_RETENTION_DAYS = 14
DEFAULT_ARTICLES_PER_OUTLET = 3

# Configured Target News RSS Feeds
RSS_FEEDS = {
    # Indian Outlets
    'NDTV': 'https://feeds.feedburner.com/ndtvnews-top-stories',
    'Times of India': 'https://timesofindia.indiatimes.com/rssfeedstopstories.cms',
    'The Indian Express': 'https://indianexpress.com/section/india/feed/',
    'The Hindu': 'https://www.thehindu.com/news/national/feeder/default.rss',
    'India Today': 'https://www.indiatoday.in/rss/home',
    
    # Global Outlets
    'BBC': 'http://feeds.bbci.co.uk/news/rss.xml',
    'Reuters': 'https://www.reutersagency.com/feed/?best-topics=top-news&post_type=best'
}
