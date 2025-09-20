import streamlit as st
import pandas as pd
from datetime import datetime
import json
from src.news_fetcher import NewsFetcher
from src.text_processor import TextProcessor
from src.summarizer import NewsSummarizer
from src.linguistic_analyzer import LinguisticAnalyzer
from src.topic_extractor import TopicExtractor
from config.config import Config

# Page config
st.set_page_config(
    page_title="News Summarizer",
    page_icon="📰",
    layout="wide"
)

# Initialize components
@st.cache_resource
def init_components():
    fetcher = NewsFetcher(Config.GNEWS_API_KEY)
    processor = TextProcessor()
    summarizer = NewsSummarizer()
    analyzer = LinguisticAnalyzer()
    extractor = TopicExtractor()
    return fetcher, processor, summarizer, analyzer, extractor

def main():
    st.title("📰 Intelligent News Summarizer")
    st.markdown("---")
    
    # Initialize components
    fetcher, processor, summarizer, analyzer, extractor = init_components()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # News source selection
        news_source = st.selectbox(
            "Select News Source",
            ["Top Headlines", "Search News"]
        )
        
        if news_source == "Top Headlines":
            category = st.selectbox(
                "Category",
                ["general", "world", "nation", "business", "technology", "entertainment", "sports", "science", "health"]
            )
            country = st.selectbox(
                "Country",
                ["us", "gb", "ca", "au", "in"]
            )
        else:
            search_query = st.text_input("Search Query")
        
        # Summarization settings
        st.subheader("Summarization Settings")
        summary_method = st.selectbox(
            "Method",
            ["textrank", "lsa", "lexrank"]
        )
        summary_length = st.slider("Summary Sentences", 2, 5, 3)
        
        # Analysis settings
        st.subheader("Analysis Settings")
        num_keywords = st.slider("Number of Keywords", 5, 15, 10)
        show_synonyms = st.checkbox("Show Synonyms/Antonyms", True)
        extract_topics = st.checkbox("Extract Topics", True)
        
        fetch_button = st.button("🔍 Fetch & Analyze News")
    
    # Main content area
    if fetch_button:
        with st.spinner("Fetching news..."):
            # Fetch news
            if news_source == "Top Headlines":
                news_data = fetcher.get_top_headlines(
                    country=country,
                    category=category,
                    page_size=5
                )
            else:
                if search_query:
                    news_data = fetcher.search_news(search_query)
                else:
                    st.error("Please enter a search query")
                    return
            
            # Debug information
            st.write("Debug Info:")
            st.write(f"- GNews API Key present: {bool(Config.GNEWS_API_KEY)}")
            st.write(f"- GNews API Key length: {len(Config.GNEWS_API_KEY) if Config.GNEWS_API_KEY else 0}")
            st.write(f"- Selected country: {country if news_source == 'Top Headlines' else 'N/A'}")
            st.write(f"- Selected category: {category if news_source == 'Top Headlines' else 'N/A'}")
            st.write(f"- Response status: {news_data.get('status', 'No status')}")
            st.write(f"- Number of articles: {len(news_data.get('articles', []))}")
            
            if news_data.get('status') == 'error':
                st.error(f"API Error: {news_data.get('message', 'Unknown error')}")
                st.write("Full response:", news_data)
            
            if news_data['status'] == 'ok' and news_data['articles']:
                articles = news_data['articles']
                
                # Process each article
                for idx, article in enumerate(articles[:3]):  # Limit to 3 articles for demo
                    st.markdown(f"## Article {idx + 1}")
                    
                    # Original content
                    content = article['description'] or article['content'] or ""
                    
                    # Initialize variables
                    clean_content = ""
                    important_words = []
                    entities = []
                    
                    if content:
                        # Clean text
                        clean_content = processor.clean_text(content)
                        
                        # Important words and entities
                        important_words, entities = processor.extract_important_words(
                            clean_content, 
                            num_keywords
                        )
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.subheader(article['title'])
                        st.caption(f"Source: {article['source']['name']} | Published: {article['publishedAt'][:10]}")
                        
                        if content:
                            with st.expander("📄 Original Content"):
                                st.write(content)
                            
                            # Summary
                            st.markdown("### 📝 Summary")
                            summary = summarizer.summarize_text(
                                clean_content, 
                                summary_length, 
                                summary_method
                            )
                            st.info(summary)
                            
                            # Display keywords
                            st.markdown("### 🔑 Key Words")
                            keywords_df = pd.DataFrame(important_words)
                            if not keywords_df.empty:
                                st.dataframe(keywords_df)
                            
                            # Synonyms and Antonyms
                            if show_synonyms and important_words:
                                st.markdown("### 📚 Synonyms & Antonyms")
                                word_list = [w['word'] for w in important_words[:5]]
                                linguistic_analysis = analyzer.analyze_words(word_list)
                                
                                for analysis in linguistic_analysis:
                                    with st.expander(f"Word: **{analysis['word']}**"):
                                        col_syn, col_ant = st.columns(2)
                                        with col_syn:
                                            st.write("**Synonyms:**")
                                            if analysis['synonyms']:
                                                for syn in analysis['synonyms']:
                                                    st.write(f"• {syn}")
                                            else:
                                                st.write("No synonyms found")
                                        
                                        with col_ant:
                                            st.write("**Antonyms:**")
                                            if analysis['antonyms']:
                                                for ant in analysis['antonyms']:
                                                    st.write(f"• {ant}")
                                            else:
                                                st.write("No antonyms found")
                        else:
                            st.warning("No content available for this article")
                    
                    with col2:
                        # Entities
                        if entities:
                            st.markdown("### 👤 Named Entities")
                            entity_df = pd.DataFrame(entities, columns=['Entity', 'Type'])
                            st.dataframe(entity_df)
                        
                        # Topics
                        if extract_topics and clean_content:
                            st.markdown("### 📊 Topics")
                            
                            # Category
                            category = extractor.categorize_article(clean_content)
                            st.metric("Category", category.capitalize())
                            
                            # Key phrases
                            phrases = extractor.extract_key_phrases(clean_content)
                            if phrases:
                                st.write("**Key Phrases:**")
                                for phrase in phrases:
                                    st.write(f"• {phrase}")
                        
                        # Article URL
                        if article.get('url'):
                            st.markdown("### 🔗 Full Article")
                            st.markdown(f"[Read More]({article['url']})")
                    
                    st.markdown("---")
                
                # Overall topic analysis (if multiple articles)
                if extract_topics and len(articles) > 1:
                    st.markdown("## 🎯 Overall Topic Analysis")
                    all_content = [a.get('content', '') or a.get('description', '') 
                                  for a in articles if a.get('content') or a.get('description')]
                    
                    if len(all_content) >= 2:
                        topics = extractor.extract_topics_lda(all_content, n_topics=3)
                        
                        if topics:
                            topic_cols = st.columns(len(topics))
                            for idx, (topic, col) in enumerate(zip(topics, topic_cols)):
                                with col:
                                    st.markdown(f"**Topic {idx + 1}**")
                                    for word in topic['words']:
                                        st.write(f"• {word}")
            else:
                st.error("No articles found or API error occurred")

if __name__ == "__main__":
    main()