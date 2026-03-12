import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuration
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Stock News Sentiment - NSE/BSE",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Pure Light" high-contrast look
st.markdown("""
<style>
    /* 1. Global App Surface - Pure White */
    .stApp, .main, [data-testid="stSidebar"], .stApp > header {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* 2. Universal Text - Bold Black */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, span {
        color: #000000 !important;
    }

    /* 3. Metrics - Light Grey Box with Dark Text */
    div[data-testid="stMetric"] {
        background-color: #f8f9fa !important;
        padding: 25px !important;
        border-radius: 12px !important;
        border: 2px solid #dee2e6 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }
    div[data-testid="stMetric"] * {
        color: #000000 !important;
    }

    /* 4. News Cards - Light Theme */
    .news-card {
        background-color: #f8f9fa !important;
        padding: 25px !important;
        border-radius: 15px !important;
        margin-bottom: 20px !important;
        border: 2px solid #dee2e6 !important;
    }
    .news-card:hover {
        background-color: #f1f3f5 !important;
        border-color: #ced4da !important;
    }
    
    /* Force all text inside news cards to be dark */
    .news-card *, .news-card p, .news-card span {
        color: #000000 !important;
    }
    
    .news-title {
        color: #0056b3 !important; /* Professional Blue Link */
        font-size: 1.3rem !important;
        font-weight: 800 !important;
        text-decoration: none !important;
        display: block !important;
        margin-bottom: 8px !important;
    }
    .news-title:hover {
        text-decoration: underline !important;
        color: #003d80 !important;
    }
    
    .news-meta {
        color: #495057 !important;
        font-size: 0.95rem !important;
        margin-bottom: 10px !important;
        font-weight: 600 !important;
    }
    
    .news-summary {
        color: #212529 !important;
        font-size: 1.05rem !important;
        line-height: 1.6 !important;
    }

    .sentiment-Positive { border-left: 8px solid #28a745 !important; }
    .sentiment-Negative { border-left: 8px solid #dc3545 !important; }
    .sentiment-Neutral { border-left: 8px solid #6c757d !important; }

    /* 5. Sidebar Styling - Integrated Pure White */
    [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
        background-color: #ffffff !important;
        border-right: 2px solid #dee2e6 !important;
    }
    
    /* Force all text in sidebar to be BLACK */
    [data-testid="stSidebar"] *, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] .stMarkdown {
        color: #000000 !important;
    }
    
    /* Sidebar Selectbox Inputs */
    [data-testid="stSidebar"] .stSelectbox div {
        background-color: #f8f9fa !important;
        border: 1px solid #ced4da !important;
        color: #000000 !important;
    }
    
    /* Sidebar Buttons - White background, Black text */
    [data-testid="stSidebar"] button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        font-weight: 700 !important;
        padding: 10px !important;
    }
    [data-testid="stSidebar"] button:hover {
        background-color: #f8f9fa !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
        border-color: #333333 !important;
    }

    /* Info Box in Sidebar - LightGrey Card on White Sidebar */
    [data-testid="stSidebar"] .stAlert {
        background-color: #f8f9fa !important;
        color: #000000 !important;
        border: 2px solid #dee2e6 !important;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("📈 Stock Sentiment")
st.sidebar.markdown("---")

def fetch_companies(has_news=True):
    try:
        response = requests.get(f"{API_URL}/companies?has_news={str(has_news).lower()}")
        return response.json()
    except:
        return []

# Try fetching companies with news
companies = fetch_companies(has_news=True)
is_empty_state = False

if not companies:
    # If none have news, just fetch all available companies
    companies = fetch_companies(has_news=False)
    is_empty_state = True

if not companies:
    # If still no companies, then it's a connection or initialization error
    st.sidebar.error("⚠️ Connection Error: Backend not responding or database not initialized.")
    if st.sidebar.button("🔄 Retry Connection"):
        st.rerun()
    st.stop()

company_names = {f"{c['name']} ({c['ticker']})": c for c in companies}
selected_name = st.sidebar.selectbox("Select a Company", list(company_names.keys()))
selected_company = company_names[selected_name]

if st.sidebar.button("🚀 Refresh News Analysis"):
    with st.spinner(f"Analyzing latest news for {selected_company['name']}..."):
        try:
            res = requests.post(f"{API_URL}/analyze/{selected_company['ticker']}")
            if res.status_code == 200:
                st.sidebar.success("Analysis triggered!")
            else:
                st.sidebar.error("Failed to trigger analysis.")
        except:
            st.sidebar.error("Connection error.")

if st.sidebar.button("🔍 Discover Target Companies"):
    with st.spinner("Scanning financial feeds for new companies..."):
        try:
            res = requests.post(f"{API_URL}/discover")
            if res.status_code == 200:
                st.sidebar.success("Discovery started! Refresh in a minute.")
            else:
                st.sidebar.error("Discovery failed.")
        except:
            st.sidebar.error("Connection error.")

st.sidebar.markdown("---")
st.sidebar.info("""
**About AI Sentiment**
This system uses **FinBERT**, a state-of-the-art transformer model trained specifically for financial text analysis.
""")

# Main Content
st.title(f"Sentiment Analysis: {selected_company['name']}")
st.subheader(f"NSE Ticker: {selected_company['ticker']} | Sector: {selected_company['sector']}")

if is_empty_state:
    st.warning("📊 **Welcome!** No analyzed news found in the database. Use the sidebar to **Discover** or **Refresh** news for this company.")

# Fetch Data
def get_data(ticker):
    news = requests.get(f"{API_URL}/news/{ticker}").json()
    sentiment = requests.get(f"{API_URL}/sentiment/{ticker}").json()
    return news, sentiment

news_data, sentiment_summary = get_data(selected_company['ticker'])

if not news_data:
    st.warning("No news data available for this company. Click 'Refresh News Analysis' to fetch.")
else:
    # Summary Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    score = sentiment_summary['sentiment_score']
    if score > 0.1:
        color = "normal"
        label = "Bullish"
    elif score < -0.1:
        color = "inverse"
        label = "Bearish"
    else:
        color = "off"
        label = "Neutral"

    col1.metric("Overall Sentiment", label, delta=f"{score:+.2f}", delta_color=color)
    col2.metric("News Count", sentiment_summary['total_news_analyzed'])
    col3.metric("Positive", sentiment_summary['distribution']['Positive'])
    col4.metric("Negative", sentiment_summary['distribution']['Negative'])

    st.markdown("---")

    # Visualizations
    vcol1, vcol2 = st.columns([1, 1])

    with vcol1:
        st.write("### Sentiment Distribution")
        df_dist = pd.DataFrame([
            {"Sentiment": k, "Count": v} for k, v in sentiment_summary['distribution'].items()
        ])
        fig = px.pie(df_dist, values='Count', names='Sentiment', 
                     color='Sentiment',
                     color_discrete_map={'Positive': '#238636', 'Negative': '#da3633', 'Neutral': '#8b949e'},
                     hole=0.4)
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=True, height=300)
        st.plotly_chart(fig, use_container_width=True)

    with vcol2:
        st.write("### Weekly Sentiment Trend")
        df_news = pd.DataFrame(news_data)
        # Use flexible parsing for mixed date formats
        df_news['published_date'] = pd.to_datetime(df_news['published_date'], errors='coerce')
        df_news['date_only'] = df_news['published_date'].dt.date
        
        trend = df_news.groupby('date_only')['sentiment_score'].mean().reset_index()
        fig_trend = px.line(trend, x='date_only', y='sentiment_score', markers=True)
        fig_trend.update_traces(line_color='#0056b3') # Professional Blue for Light Theme
        fig_trend.update_layout(height=300, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("---")

    # News Feed
    st.write("### Recent News Feed")
    for news in news_data[:15]: # Show top 15
        sentiment_class = news['sentiment']
        st.markdown(f"""
            <div class="news-card sentiment-{sentiment_class}">
                <div class="news-meta">
                    {news['source']} | {news['published_date'][:10]} | 
                    <span class="news-sentiment bg-{sentiment_class}">{sentiment_class}</span>
                </div>
                <a href="{news['url']}" target="_blank" class="news-title">
                    {news['headline']}
                </a>
                <p class="news-summary">
                    {news['summary'] if news['summary'] else 'No summary available.'}
                </p>
            </div>
        """, unsafe_allow_html=True)
