import os
import time
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

try:
    import spacy
    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False

class NLPEngine:
    def __init__(self):
        self.hf_token = os.getenv("HF_TOKEN")
        # Use InferenceClient for more robust API access
        self.client = InferenceClient(token=self.hf_token)
        # Upgraded to a more refined model for better financial nuance
        self.model_id = "yiyanghkust/finbert-tone"
        
        # spaCy for NER
        self.nlp = None
        if HAS_SPACY:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except:
                self.nlp = None

    def extract_companies(self, text):
        """Extract ORGANIZATION entities from text with financial term filtering"""
        if not self.nlp:
            return []
        
        # Blacklist of common financial terms that NER often confuses with companies
        FIN_STOP_WORDS = {
            "QoQ", "YoY", "Net Profit", "Revenue", "Dividend", "EBITDA", 
            "Sensex", "Nifty", "BSE", "NSE", "Quarter", "Fiscal", "Financial",
            "Growth", "Market", "Investment", "Trading", "Stock", "Shares"
        }
        
        try:
            doc = self.nlp(text)
            entities = []
            for ent in doc.ents:
                if ent.label_ == "ORG" and ent.text.strip() not in FIN_STOP_WORDS:
                    # Filter out very short strings or those that are just numbers/symbols
                    if len(ent.text.strip()) > 2:
                        entities.append(ent.text.strip())
            return list(set(entities))
        except:
            return []

    def get_sentiment(self, text):
        """Perform sentiment analysis with highest precision using FinancialBERT"""
        if not text or len(text.strip()) == 0:
            return "Neutral", 0.0
            
        # Focus on the first part of the text which usually contains the main sentiment
        clean_text = text[:1000].strip()
        
        # Best financial sentiment model identified via testing
        target_model = "ahmedrachid/FinancialBERT-Sentiment-Analysis"
        
        try:
            for attempt in range(3):
                try:
                    results = self.client.text_classification(clean_text, model=target_model)
                    
                    if results and len(results) > 0:
                        # Find the label with the highest confidence
                        top_prediction = max(results, key=lambda x: x.score)
                        label = top_prediction.label.lower()
                        score = top_prediction.score
                        
                        # Direct mapping from FinancialBERT labels
                        if label == "positive": return "Positive", score
                        if label == "negative": return "Negative", score
                        
                        # If the top is neutral but score is low, check second best
                        if label == "neutral" and score < 0.6:
                            second_best = sorted(results, key=lambda x: x.score, reverse=True)[1]
                            if second_best.score > 0.3:
                                if second_best.label == "positive": return "Positive", second_best.score
                                if second_best.label == "negative": return "Negative", second_best.score
                        
                        return "Neutral", score
                except Exception as api_err:
                    if "loading" in str(api_err).lower():
                        time.sleep(5)
                        continue
                    raise api_err
        except Exception as e:
            print(f"Deep Sentiment Analysis Error: {e}")
            # Fallback to simple fallback or neutral
            
        return "Neutral", 0.0
