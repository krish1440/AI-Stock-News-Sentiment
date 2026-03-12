from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("HF_TOKEN")
client = InferenceClient(token=token)

# Sample texts from user
texts = [
    "Reliance Industries share price rises after Trump refinery announcement: Can it hit ₹1,500 in near-term?",
    "Shares of India’s most valuable company dipped after President Donald Trump touted Reliance Industries’ involvement in a $300 billion US refinery."
]

models = [
    "yiyanghkust/finbert-tone",
    "ProsusAI/finbert",
    "ahmedrachid/FinancialBERT-Sentiment-Analysis"
]

for model_id in models:
    print(f"\n--- Testing Model: {model_id} ---")
    for text in texts:
        try:
            results = client.text_classification(text, model=model_id)
            top = max(results, key=lambda x: x.score)
            print(f"Text: {text[:50]}...")
            print(f"Result: {top.label} ({top.score:.4f})")
        except Exception as e:
            print(f"Error with {model_id}: {e}")
