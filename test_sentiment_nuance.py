from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("HF_TOKEN")
client = InferenceClient(token=token)

texts = [
    "Reliance Industries share price rises after Trump refinery announcement: Can it hit ₹1,500 in near-term? Reliance Industries shares rose 1.5% after Trump announced a new Texas oil refinery project backed by the company. Despite recent declines, analysts remain optimistic about long-term growth, projecting a target price of ₹1,730 amid improving valuations and potential catalysts like a Jio IPO.",
    "Shares of India’s most valuable company dipped after President Donald Trump touted Reliance Industries’ involvement in a $300 billion US refinery, even as the company declined to confirm its role and experts questioned the deal’s scale."
]

model_id = "yiyanghkust/finbert-tone"

for text in texts:
    print(f"\nText: {text[:100]}...")
    results = client.text_classification(text, model=model_id)
    print(f"Results: {results}")
