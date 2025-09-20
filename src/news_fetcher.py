import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json

class NewsFetcher:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://gnews.io/api/v4"
        
    def get_top_headlines(self, 
                         country: str = "us", 
                         category: Optional[str] = None,
                         page_size: int = 10) -> Dict:
        """
        Fetch top headlines from GNews API
        Categories: general, world, nation, business, technology, entertainment, sports, science, health
        """
        endpoint = f"{self.base_url}/top-headlines"
        params = {
            'token': self.api_key,
            'country': country,
            'max': min(page_size, 10),  # GNews API max is 10 for free tier
            'lang': 'en'
        }
        
        if category and category != 'general':
            params['category'] = category
            
        try:
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Check if the response contains an error message
            if 'error' in data:
                return {
                    "articles": [], 
                    "status": "error", 
                    "message": data.get('error', 'Unknown error from GNews API')
                }
            
            # Convert GNews format to NewsAPI-like format for compatibility
            return {
                'status': 'ok',
                'totalResults': data.get('totalArticles', 0),
                'articles': self._convert_gnews_articles(data.get('articles', []))
            }
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP Error {e.response.status_code}: {e.response.text}"
            print(f"Error fetching news: {error_msg}")
            return {"articles": [], "status": "error", "message": error_msg}
        except requests.exceptions.RequestException as e:
            print(f"Error fetching news: {e}")
            return {"articles": [], "status": "error", "message": str(e)}
    
    def search_news(self, 
                   query: str, 
                   from_date: Optional[str] = None,
                   sort_by: str = "relevancy") -> Dict:
        """
        Search for specific news articles using GNews API
        sort_by: relevancy, publishedAt
        """
        endpoint = f"{self.base_url}/search"
        
        params = {
            'token': self.api_key,
            'q': query,
            'lang': 'en',
            'max': 10  # GNews API max is 10 for free tier
        }
        
        # GNews API uses different sort parameter values
        if sort_by == 'relevancy':
            params['sortby'] = 'relevance'
        elif sort_by == 'publishedAt':
            params['sortby'] = 'publishedAt'
        
        # Only add from_date if provided (GNews might be sensitive to this)
        if from_date:
            params['from'] = from_date
            
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Check if the response contains an error message
            if 'error' in data:
                return {
                    "articles": [], 
                    "status": "error", 
                    "message": data.get('error', 'Unknown error from GNews API')
                }
            
            # Convert GNews format to NewsAPI-like format for compatibility
            return {
                'status': 'ok',
                'totalResults': data.get('totalArticles', 0),
                'articles': self._convert_gnews_articles(data.get('articles', []))
            }
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP Error {e.response.status_code}: {e.response.text}"
            print(f"Error searching news: {error_msg}")
            return {"articles": [], "status": "error", "message": error_msg}
        except requests.exceptions.RequestException as e:
            print(f"Error searching news: {e}")
            return {"articles": [], "status": "error", "message": str(e)}
    
    def get_sources(self, category: Optional[str] = None) -> Dict:
        """Get available news sources - Note: GNews doesn't have a sources endpoint"""
        # GNews doesn't have a sources endpoint, so we'll return a mock response
        # The category parameter is kept for API compatibility but not used
        return {
            "status": "ok",
            "sources": [
                {"id": "gnews", "name": "GNews", "description": "GNews aggregated sources"}
            ]
        }
    
    def _convert_gnews_articles(self, gnews_articles: List[Dict]) -> List[Dict]:
        """Convert GNews article format to NewsAPI-like format for compatibility"""
        converted_articles = []
        
        for article in gnews_articles:
            converted_article = {
                'source': {
                    'id': None,
                    'name': article.get('source', {}).get('name', 'Unknown')
                },
                'author': None,  # GNews doesn't provide author info
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'url': article.get('url', ''),
                'urlToImage': article.get('image', ''),
                'publishedAt': article.get('publishedAt', ''),
                'content': article.get('content', article.get('description', ''))
            }
            converted_articles.append(converted_article)
            
        return converted_articles