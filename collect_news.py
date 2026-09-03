import hashlib
from datetime import datetime, timedelta
import feedparser
import pandas as pd
from newspaper import Article
from sqlalchemy import create_engine, Column, String, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Set up Database Schema (SQLite)
Base = declarative_base()

class NewsArticle(Base):
	__tablename__ = 'articles'
    
	article_id = Column(String(64), primary_key=True)
	topic_label = Column(String(100), nullable=False)
	outlet_name = Column(String(100), nullable=False)
	url = Column(String(1000), unique=True, nullable=False)
	title = Column(Text, nullable=False)
	author = Column(String(255))
	published_at = Column(DateTime)
	full_text = Column(Text, nullable=False)
	scraped_at = Column(DateTime, default=datetime.utcnow)
    
	# Flag to keep data permanently if requested by a user
	is_saved = Column(Boolean, default=False)

# Initialize database file
engine = create_engine('sqlite:///news_collection.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# 2. RSS Feeds for Global & Indian News Outlets
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

def extract_article_content(url):
	"""Extracts raw text and metadata using newspaper4k."""
	try:
		article = Article(url)
		article.download()
		article.parse()
		return {
			'title': article.title,
			'authors': ", ".join(article.authors) if article.authors else None,
			'published_at': article.publish_date,
			'full_text': article.text
		}
	except Exception as e:
		print(f"--> [Warning] Could not parse {url}: {e}")
		return None

def cleanup_old_articles(days_to_keep=14):
	"""Deletes unsaved articles older than specified retention period (default: 14 days)."""
	session = Session()
	cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
    
	deleted_count = session.query(NewsArticle).filter(
		NewsArticle.scraped_at < cutoff_date,
		NewsArticle.is_saved == False
	).delete()
    
	session.commit()
	session.close()
	if deleted_count > 0:
		print(f"[Cleanup] Automatically deleted {deleted_count} unsaved articles older than {days_to_keep} days.")

def run_scraper(topic_label="general_headlines", limit_per_outlet=3):
	"""Scrapes news feeds, deduplicates links, and stores data in SQLite DB."""
	session = Session()
	total_saved = 0
    
	for outlet, feed_url in RSS_FEEDS.items():
		print(f"\nFetching RSS feed for: {outlet}...")
		parsed_feed = feedparser.parse(feed_url)
        
		count = 0
		for entry in parsed_feed.entries:
			if count >= limit_per_outlet:
				break
                
			link = entry.link
			url_hash = hashlib.sha256(link.encode('utf-8')).hexdigest()
            
			if session.query(NewsArticle).filter_by(article_id=url_hash).first():
				print(f"  [Skipped] Already exists: {link[:50]}...")
				continue
            
			print(f"  Scraping...")
			content = extract_article_content(link)
            
			if not content or not content['full_text']:
				continue
                
			published_date = content['published_at']
			if not published_date and hasattr(entry, 'published_parsed'):
				published_date = datetime(*entry.published_parsed[:6])
                
			record = NewsArticle(
				article_id=url_hash,
				topic_label=topic_label,
				outlet_name=outlet,
				url=link,
				title=content['title'] or entry.title,
				author=content['authors'],
				published_at=published_date,
				full_text=content['full_text'],
				is_saved=False
			)
            
			session.add(record)
			count += 1
			total_saved += 1
            
	session.commit()
	session.close()
	print(f"\n=== Scraping Completed! New Articles Saved: {total_saved} ===")

def mark_article_as_saved(article_id):
	"""Utility function to protect a specific article from automated deletion."""
	session = Session()
	article = session.query(NewsArticle).filter_by(article_id=article_id).first()
	if article:
		article.is_saved = True
		session.commit()
		print(f"[Saved] Article '{article.title}' is now preserved permanently.")
	session.close()

if __name__ == "__main__":
	# 1. Automatically delete unsaved articles older than 14 days
	cleanup_old_articles(days_to_keep=14)
    
	# 2. Run the ingestion scraper across Indian and Global sources
	run_scraper(topic_label="indian_and_global_news", limit_per_outlet=3)
