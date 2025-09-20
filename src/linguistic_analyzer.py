from nltk.corpus import wordnet
from typing import List, Dict, Set
import nltk

class LinguisticAnalyzer:
    def __init__(self):
        self.pos_map = {
            'NOUN': wordnet.NOUN,
            'VERB': wordnet.VERB,
            'ADJ': wordnet.ADJ,
            'ADV': wordnet.ADV
        }
    
    def get_synonyms_antonyms(self, word: str, pos: str = None) -> Dict:
        """Get synonyms and antonyms for a word"""
        synonyms = set()
        antonyms = set()
        
        # Get all synsets for the word
        synsets = wordnet.synsets(word)
        
        for synset in synsets:
            # Get synonyms
            for lemma in synset.lemmas():
                synonym = lemma.name().replace('_', ' ')
                if synonym.lower() != word.lower():
                    synonyms.add(synonym)
                
                # Get antonyms
                for antonym in lemma.antonyms():
                    antonyms.add(antonym.name().replace('_', ' '))
        
        return {
            'word': word,
            'synonyms': list(synonyms)[:5],  # Limit to 5
            'antonyms': list(antonyms)[:5]
        }
    
    def analyze_words(self, words: List[str]) -> List[Dict]:
        """Analyze multiple words for synonyms and antonyms"""
        results = []
        for word in words:
            analysis = self.get_synonyms_antonyms(word)
            if analysis['synonyms'] or analysis['antonyms']:
                results.append(analysis)
        return results
    
    def get_word_definition(self, word: str) -> List[str]:
        """Get definitions for a word"""
        definitions = []
        synsets = wordnet.synsets(word)
        
        for synset in synsets[:3]:  # Limit to 3 definitions
            definitions.append(synset.definition())
        
        return definitions