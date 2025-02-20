import spacy
import yake
from collections import Counter
from langdetect import detect
from googletrans import Translator
import asyncio

class KeywordExtractor:
    """Extracts important keywords from job descriptions using NLP."""

    def __init__(self, text=None, num_keywords=10, translate_to_en=True):
        self.num_keywords = num_keywords
        self.text = text                
        self.translate_to_en = translate_to_en

    def _translate_to_english(self, text):
        lang = detect(text)
        print(f"Detected language: {lang}")
        if lang != "en":
            googleTranslator = Translator()
            # Run the coroutine to get the translation result.
            text = asyncio.run(googleTranslator.translate(text, dest='en')).text.lower()
        print(f"Translated text: {text}")
        return str(text)


    def extract(self):
        """Extracts relevant keywords from the given text."""
        # Translate to English if necessary
        if self.translate_to_en:
            self.text = self._translate_to_english(self.text)
        # keywords length
        self.num_keywords = len(self.text.split())
        self.nlp = spacy.load("en_core_web_sm")
       
        kw_extractor = yake.KeywordExtractor(n=1, top=self.num_keywords)
        yake_keywords = [kw[0] for kw in kw_extractor.extract_keywords(self.text)]

        doc = self.nlp(self.text)
        spacy_keywords = [chunk.text.lower() for chunk in doc.noun_chunks]

        # Combine and rank keywords
        all_keywords = yake_keywords + spacy_keywords
        keyword_counts = Counter(all_keywords)

        return [kw for kw, _ in keyword_counts.most_common(self.num_keywords)]
