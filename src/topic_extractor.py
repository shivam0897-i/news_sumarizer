from typing import List, Dict
from collections import Counter
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np

class TopicExtractor:
    def __init__(self):
        self.vectorizer = CountVectorizer(
            max_features=50,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
    def extract_topics_lda(self, documents: List[str], 
                           n_topics: int = 3,
                           words_per_topic: int = 5) -> List[Dict]:
        """Extract topics using LDA"""
        if not documents or len(documents) < 2:
            return []
        
        try:
            # Vectorize documents
            doc_term_matrix = self.vectorizer.fit_transform(documents)
            
            # Apply LDA
            lda = LatentDirichletAllocation(
                n_components=n_topics,
                random_state=42,
                max_iter=10
            )
            lda.fit(doc_term_matrix)
            
            # Get feature names
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Extract topics
            topics = []
            for topic_idx, topic in enumerate(lda.components_):
                top_indices = topic.argsort()[-words_per_topic:][::-1]
                top_words = [feature_names[i] for i in top_indices]
                
                topics.append({
                    'topic_id': topic_idx,
                    'words': top_words,
                    'weight': float(topic[top_indices].mean())
                })
            
            return topics
        except Exception as e:
            print(f"Error in LDA: {e}")
            return []
    
    def extract_key_phrases(self, text: str, top_n: int = 5) -> List[str]:
        """Extract key phrases from text"""
        # Simple noun phrase extraction
        phrases = []
        
        # Pattern for noun phrases
        pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        matches = re.findall(pattern, text)
        
        # Count frequency
        phrase_freq = Counter(matches)
        
        # Get top phrases
        return [phrase for phrase, _ in phrase_freq.most_common(top_n)]
    
    def categorize_article(self, text: str) -> str:
        """Simple category detection based on keywords"""
        categories = {
            'technology': ['tech', 'software', 'ai', 'computer', 'digital', 'internet', 'app'],
            'business': ['business', 'economy', 'market', 'finance', 'stock', 'trade', 'company'],
            'politics': ['politics', 'government', 'election', 'president', 'congress', 'law', 'policy'],
            'sports': ['sports', 'game', 'team', 'player', 'match', 'score', 'championship'],
            'health': ['health', 'medical', 'doctor', 'disease', 'treatment', 'hospital', 'covid'],
            'science': ['science', 'research', 'study', 'discovery', 'experiment', 'scientist'],
            'entertainment': ['movie', 'music', 'celebrity', 'film', 'actor', 'singer', 'show']
        }
        
        text_lower = text.lower()
        scores = {}
        
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[category] = score
        
        if scores:
            return max(scores, key=scores.get)
        return 'general'