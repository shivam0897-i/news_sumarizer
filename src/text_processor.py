import re
import spacy
from typing import List, Dict, Tuple
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

class TextProcessor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.stop_words = set(stopwords.words('english'))
        
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)
        
        # Remove HTML tags
        text = re.sub(r'<.*?>', '', text)
        
        # Remove special characters but keep sentence structure
        text = re.sub(r'[^\w\s\.\!\?\,\;\:\-]', '', text)
        
        # Remove extra whitespaces
        text = ' '.join(text.split())
        
        return text
    
    def extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text"""
        return sent_tokenize(text)
    
    def extract_important_words(self, text: str, top_n: int = 10) -> List[Dict]:
        """Extract important words with their properties"""
        doc = self.nlp(text)
        
        # Extract entities and important words
        important_words = []
        
        # Named entities
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        
        # Nouns and verbs (excluding stop words)
        words = []
        for token in doc:
            if (token.pos_ in ['NOUN', 'VERB', 'PROPN'] and 
                token.text.lower() not in self.stop_words and
                len(token.text) > 2):
                words.append(token.text.lower())
        
        # Calculate word frequency
        word_freq = Counter(words)
        
        # Get top words
        for word, freq in word_freq.most_common(top_n):
            important_words.append({
                'word': word,
                'frequency': freq,
                'importance_score': freq / len(words)
            })
        
        return important_words, entities
    
    def calculate_tfidf(self, documents: List[str]) -> Dict:
        """Calculate TF-IDF scores for words across documents"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        vectorizer = TfidfVectorizer(
            max_features=20,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(documents)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get scores for each document
            scores = {}
            for doc_idx, doc in enumerate(documents):
                doc_scores = tfidf_matrix[doc_idx].toarray()[0]
                scores[doc_idx] = {
                    feature_names[i]: score 
                    for i, score in enumerate(doc_scores) 
                    if score > 0
                }
            
            return scores
        except:
            return {}