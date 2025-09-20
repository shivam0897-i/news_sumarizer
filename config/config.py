import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    GNEWS_API_KEY = os.getenv('GNEWS_API_KEY')
    
    # NewsAPI URLs
    NEWS_API_URL = "https://newsapi.org/v2"
    TOP_HEADLINES = f"{NEWS_API_URL}/top-headlines"
    EVERYTHING = f"{NEWS_API_URL}/everything"
    
    # GNews API URLs
    GNEWS_API_URL = "https://gnews.io/api/v4"
    GNEWS_TOP_HEADLINES = f"{GNEWS_API_URL}/top-headlines"
    GNEWS_SEARCH = f"{GNEWS_API_URL}/search"
    
    # Parameters
    DEFAULT_COUNTRY = "in"
    DEFAULT_PAGE_SIZE = 10
    DEFAULT_LANGUAGE = "en"