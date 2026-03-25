import os
import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from newsapi import NewsApiClient
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

class NewsScraper:
    """
    A comprehensive news scraping engine for financial discovery.
    Coordinates multiple sources including NewsAPI, GNews, yfinance, and RSS feeds.
    """
    
    def __init__(self):
        """Initialize api keys and various news sources."""
        self.newsapi_key: Optional[str] = os.getenv("NEWS_API_KEY")
        self.gnews_key: Optional[str] = os.getenv("GNEWS_API_KEY")
        self.newsapi: Optional[NewsApiClient] = NewsApiClient(api_key=self.newsapi_key) if self.newsapi_key else None
        
        # Free RSS Feeds for Discovery
        self.rss_feeds: List[str] = [
            "https://www.moneycontrol.com/rss/business.xml",
            "https://www.moneycontrol.com/rss/latestnews.xml",
            "https://economictimes.indiatimes.com/news/economy/rssfeedsms.cms",
            "https://www.livemint.com/rss/markets",
            "https://www.livemint.com/rss/companies",
            "https://www.cnbctv18.com/common/rss/market.xml",
            "https://feeds.feedburner.com/reuters/INbusinessNews",
        ]

    def fetch_via_newsapi(self, query: str) -> List[Dict[str, Any]]:
        """
        Fetch news using NewsAPI.org for a specific query.
        
        Args:
            query: The search term or company name.
            
        Returns:
            A list of article dictionaries with standardized keys.
        """
        if not self.newsapi:
            return []
        
        try:
            # Fetch for the last 7 days
            from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            response = self.newsapi.get_everything(
                q=query,
                language='en',
                sort_by='publishedAt',
                from_param=from_date
            )
            
            articles = []
            for art in response.get('articles', []):
                articles.append({
                    'headline': art['title'],
                    'summary': art['description'],
                    'url': art['url'],
                    'source': art['source']['name'],
                    'published_date': art['publishedAt'],
                    'content': art.get('content', '')
                })
            return articles
        except Exception as e:
            print(f"Error fetching from NewsAPI: {e}")
            return []

    def fetch_via_gnews(self, query: str) -> List[Dict[str, Any]]:
        """
        Fetch news using GNews.io for a specific query.
        
        Args:
            query: The search term or company name.
            
        Returns:
            A list of article dictionaries with standardized keys.
        """
        if not self.gnews_key:
            return []
            
        url = f"https://gnews.io/api/v4/search?q={query}&lang=en&country=in&max=10&apikey={self.gnews_key}"
        try:
            response = requests.get(url)
            data = response.json()
            
            articles = []
            for art in data.get('articles', []):
                articles.append({
                    'headline': art['title'],
                    'summary': art['description'],
                    'url': art['url'],
                    'source': art['source']['name'],
                    'published_date': art['publishedAt'],
                    'content': art.get('content', '')
                })
            return articles
        except Exception as e:
            print(f"Error fetching from GNews: {e}")
            return []

    def fetch_via_yfinance(self, ticker: str) -> List[Dict[str, Any]]:
        """
        Fetch news using yfinance specifically for a given stock ticker.
        
        Args:
            ticker: The stock ticker (e.g., 'RELIANCE.NS').
            
        Returns:
            A list of article dictionaries with standardized keys.
        """
        try:
            stock = yf.Ticker(ticker)
            news = stock.news
            
            articles = []
            for art in news:
                raw_date = art.get('providerPublishTime') or art.get('published') or datetime.now()
                pub_date = datetime.fromtimestamp(raw_date) if isinstance(raw_date, int) else raw_date
                
                articles.append({
                    'headline': art.get('title', 'No Title'),
                    'summary': art.get('description', ''),
                    'url': art.get('link'),
                    'source': art.get('publisher', 'yfinance'),
                    'published_date': pub_date,
                    'content': ''
                })
            return articles
        except Exception as e:
            print(f"Error fetching from yfinance for {ticker}: {e}")
            return []

    def fetch_discovery_news(self) -> List[Dict[str, Any]]:
        """
        Automatically discovers general financial news from a pre-defined set of RSS feeds.
        Used for identifying trending market topics.
        
        Returns:
            A list of article dictionaries with standardized keys.
        """
        discovery_articles = []
        for feed_url in self.rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries:
                    discovery_articles.append({
                        'headline': entry.get('title', ''),
                        'summary': entry.get('description', '') or entry.get('summary', ''),
                        'url': entry.get('link', ''),
                        'source': feed.feed.get('title', 'Financial News'),
                        'published_date': entry.get('published', datetime.now().isoformat()),
                        'content': ''
                    })
            except Exception as e:
                print(f"Error fetching RSS {feed_url}: {e}")
        
        # Also fetch general business news from NewsAPI
        if self.newsapi:
            try:
                top_headlines = self.newsapi.get_top_headlines(category='business', language='en', country='in')
                for art in top_headlines.get('articles', []):
                    discovery_articles.append({
                        'headline': art.get('title', ''),
                        'summary': art.get('description', ''),
                        'url': art.get('url', ''),
                        'source': art['source']['name'],
                        'published_date': art['publishedAt'],
                        'content': art.get('content', '')
                    })
            except Exception:
                pass
                
        return discovery_articles

    def search_ticker(self, company_name: str) -> Optional[str]:
        """
        Tries to match a company name to its relevant NSE/BSE stock ticker.
        
        Args:
            company_name: The detected name of the entity.
            
        Returns:
            The ticker symbol with .NS or .BO suffix if found, else None.
        """
        try:
            search_results = yf.Search(company_name, max_results=5).quotes
            if not search_results:
                return None
            
            # Prefer Indian tickers (.NS or .BO)
            for quote in search_results:
                symbol = quote.get('symbol', '')
                if symbol.endswith('.NS') or symbol.endswith('.BO'):
                    return symbol
            
            # Fallback to the first result only if it's a very close name match
            first_quote = search_results[0]
            if company_name.lower() in first_quote.get('shortname', '').lower():
                return first_quote['symbol']
                
        except Exception as e:
            print(f"Ticker Search Error for {company_name}: {e}")
        return None

    def scrape_all(self, company_name: str, ticker: str) -> List[Dict[str, Any]]:
        """
        Aggregates news from all configured sources for a specific company.
        Includes deduplication logic based on article URLs.
        
        Args:
            company_name: The company name to search for.
            ticker: The primary ticker for deep searching.
            
        Returns:
            A deduplicated list of articles across all sources.
        """
        all_articles = []
        
        # 1. NewsAPI
        all_articles.extend(self.fetch_via_newsapi(company_name))
        
        # 2. GNews
        all_articles.extend(self.fetch_via_gnews(company_name))
        
        # 3. yfinance
        all_articles.extend(self.fetch_via_yfinance(ticker))
        
        # Deduplicate by URL
        unique_articles = {art['url']: art for art in all_articles if art.get('url')}.values()
        
        return list(unique_articles)
