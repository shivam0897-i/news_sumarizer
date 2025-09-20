from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from typing import List
import nltk

class NewsSummarizer:
    def __init__(self, language: str = "english"):
        self.language = language
        self.stemmer = Stemmer(language)
        self.stop_words = get_stop_words(language)
        
    def summarize_text(self, text: str, 
                      sentences_count: int = 3,
                      method: str = "textrank") -> str:
        """
        Summarize text using specified method
        Methods: textrank, lsa, lexrank
        """
        if not text or len(text) < 100:
            return text
            
        parser = PlaintextParser.from_string(text, Tokenizer(self.language))
        
        if method == "lsa":
            summarizer = LsaSummarizer(self.stemmer)
        elif method == "lexrank":
            summarizer = LexRankSummarizer(self.stemmer)
        else:  # textrank
            summarizer = TextRankSummarizer(self.stemmer)
        
        summarizer.stop_words = self.stop_words
        
        try:
            summary_sentences = summarizer(parser.document, sentences_count)
            return ' '.join([str(sentence) for sentence in summary_sentences])
        except:
            # Fallback to simple extraction
            sentences = text.split('.')[:sentences_count]
            return '. '.join(sentences) + '.'
    
    def extract_key_sentences(self, text: str, num_sentences: int = 5) -> List[str]:
        """Extract key sentences from text"""
        parser = PlaintextParser.from_string(text, Tokenizer(self.language))
        summarizer = TextRankSummarizer(self.stemmer)
        summarizer.stop_words = self.stop_words
        
        try:
            sentences = summarizer(parser.document, num_sentences)
            return [str(sentence) for sentence in sentences]
        except:
            return text.split('.')[:num_sentences]