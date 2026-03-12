import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/ProsusAI/finbert"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

test_texts = [
    "Reliance reports record profit, stock surge 10%",
    "Tata Motors facing supply chain issues, delivery delayed",
    "Markets consolidate as investors wait for quarterly results",
    "Adani Ent shares fall as short-seller report emerges"
]

for text in test_texts:
    print(f"\nAnalyzing: {text}")
    res = requests.post(API_URL, headers=headers, json={"inputs": text})
    print(f"Response: {res.json()}")
