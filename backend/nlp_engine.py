import os
import time
from typing import List, Tuple, Optional, Dict, Any
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

try:
    import spacy
    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False

class NLPEngine:
    # Blacklist of common financial terms that NER often confuses with companies
    FIN_STOP_WORDS = {
        "QoQ", "YoY", "Net Profit", "Revenue", "Dividend", "EBITDA", 
        "Sensex", "Nifty", "BSE", "NSE", "Quarter", "Fiscal", "Financial",
        "Growth", "Market", "Investment", "Trading", "Stock", "Shares"
    }
    
    # Best financial sentiment model identified via testing
    SENTIMENT_MODEL = "ahmedrachid/FinancialBERT-Sentiment-Analysis"
    
    def __init__(self):
        self.hf_token: Optional[str] = os.getenv("HF_TOKEN")
        # Use InferenceClient for more robust API access
        self.client = InferenceClient(token=self.hf_token)
        # Upgraded to a more refined model for better financial nuance
        self.model_id: str = "yiyanghkust/finbert-tone"
        
        # spaCy for NER
        self.nlp = None
        if HAS_SPACY:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                self.nlp = None

    def extract_companies(self, text: str) -> List[str]:
        """Extract ORGANIZATION entities from text with financial term filtering"""
        if not self.nlp or not text:
            return []
        
        try:
            doc = self.nlp(text)
            entities = []
            for ent in doc.ents:
                if ent.label_ == "ORG" and ent.text.strip() not in self.FIN_STOP_WORDS:
                    # Filter out very short strings or those that are just numbers/symbols
                    if len(ent.text.strip()) > 2:
                        entities.append(ent.text.strip())
            return list(set(entities))
        except Exception:
            return []

    def get_sentiment(self, text: str) -> Tuple[str, float]:
        """Perform sentiment analysis with highest precision using FinancialBERT"""
        if not text or len(text.strip()) == 0:
            return "Neutral", 0.0
            
        # Focus on the first part of the text which usually contains the main sentiment
        clean_text = text[:1000].strip()
        
        try:
            for attempt in range(3):
                try:
                    results = self.client.text_classification(clean_text, model=self.SENTIMENT_MODEL)
                    
                    if results and len(results) > 0:
                        # Find the label with the highest confidence
                        top_prediction = max(results, key=lambda x: x.score)
                        label = top_prediction.label.lower()
                        score = top_prediction.score
                        
                        # Direct mapping from FinancialBERT labels
                        if label == "positive": return "Positive", float(score)
                        if label == "negative": return "Negative", float(score)
                        
                        # If the top is neutral but score is low, check second best
                        if label == "neutral" and score < 0.6:
                            sorted_results = sorted(results, key=lambda x: x.score, reverse=True)
                            if len(sorted_results) > 1:
                                second_best = sorted_results[1]
                                if second_best.score > 0.3:
                                    if second_best.label == "positive": return "Positive", float(second_best.score)
                                    if second_best.label == "negative": return "Negative", float(second_best.score)
                        
                        return "Neutral", float(score)
                except Exception as api_err:
                    if "loading" in str(api_err).lower():
                        time.sleep(5)
                        continue
                    raise api_err
        except Exception as e:
            print(f"Deep Sentiment Analysis Error: {e}")
            
        return "Neutral", 0.0
