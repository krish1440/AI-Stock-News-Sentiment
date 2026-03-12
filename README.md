# 📉 AI Stock News Sentiment Analysis System (NSE/BSE)

[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=flat-square&logo=streamlit)](https://streamlit.io/)
[![NLP-FinBERT](https://img.shields.io/badge/NLP-FinBERT-blue?style=flat-square)](https://huggingface.co/yiyanghkust/finbert-tone)
[![Python-3.12](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python)](https://www.python.org/)

An advanced, autonomous AI-powered sentiment analysis system specifically engineered for the **Indian Stock Market (NSE/BSE)**. This system automatically discovers trending financial news, detects listed companies using Named Entity Recognition (NER), and performs context-aware sentiment analysis using state-of-the-art transformer models.

---

## 🔥 Key Features

-   **🤖 Autonomous Discovery**: Scans live RSS feeds from Top Indian financial outlets (*MoneyControl, Economic Times, LiveMint*) to detect emerging market trends.
-   **🏢 Intelligent Entity Extraction**: Built with **spaCy NER** to automatically identify company names in raw news text.
-   **🛡️ Strict Market Filtering**: Automatically validates detected companies against NSE/BSE tickers. Only companies with a `.NS` or `.BO` suffix are processed, ensuring zero noise from global markets or irrelevant entities.
-   **💎 Financial-Grade Sentiment**: Leverages **FinBERT** (`yiyanghkust/finbert-tone`) for analysis that understands financial nuances (e.g., distinguishing "profit fell" from "profit was high").
-   **📊 Premium "Pure Light" Dashboard**: A high-contrast, professional Streamlit interface featuring:
    -   Sentiment Distribution Pie Charts.
    -   Weekly Sentiment Trend Lines.
    -   High-visibility News Feed cards with inline sentiment tags.
-   **⚡ Background Tasking**: Heavy scraping and analysis tasks run in background threads to keep the UI snappy and responsive.

---

## 🛠️ Technology Stack

| Component | Technology |
| :--- | :--- |
| **Backend** | FastAPI, SQLAlchemy |
| **Frontend** | Streamlit, Plotly |
| **NLP** | spaCy (NER), FinBERT (Sentiment) |
| **Scraping** | BeautifulSoup4, Feedparser, yfinance |
| **Database** | SQLite |

---

## 🚦 Getting Started

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/krish1440/AI-Stock-News-Sentiment.git
cd AI-Stock-News-Sentiment
```

### 2️⃣ Environment Configuration
Create a `.env` file in the root directory. You can use the provided `.env.example` as a template:

```bash
cp .env.example .env
```

**Required Keys:**
- `NEWS_API_KEY`: Get yours at [newsapi.org](https://newsapi.org/)
- `HF_TOKEN`: Get yours at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) (Read access is enough)

**Example `.env`:**
```env
NEWS_API_KEY=5678...
HF_TOKEN=hf_...
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 4️⃣ Launch the System
**Start the Backend API:**
```bash
uvicorn backend.main:app --reload
```

**Start the Dashboard:**
```bash
streamlit run frontend/dashboard.py
```

---

## 🛰️ API Endpoints Deep Dive

The system exposes a rich set of REST endpoints for integration:

-   `GET /companies?has_news=true`: Retrieve analyzed companies.
-   `POST /discover`: Trigger the autonomous discovery engine.
-   `GET /sentiment/{ticker}`: Get comprehensive sentiment metrics for a specific stock.
-   `POST /analyze/{ticker}`: Force a deep-scrape for a specific company.

---

## 📖 Architecture Overview

The system operates in a three-stage lifecycle:
1.  **Ingestion**: Fetching general news from RSS feeds.
2.  **Validation**: Using NER to extract entities and verifying them against the NSE/BSE stock exchanges via yfinance.
3.  **Synthesis**: Applying transformer-based sentiment analysis and aggregating results into a time-series database.

---

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License
This project is licensed under the MIT License.
