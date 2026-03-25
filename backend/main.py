from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
import os
import threading
from database import engine, get_db, Company, News, init_db, SessionLocal
from scraper import NewsScraper
from nlp_engine import NLPEngine

app = FastAPI(title="AI Stock News Sentiment API")

# Initialize models
scraper = NewsScraper()
nlp = NLPEngine()

@app.on_event("startup")
def startup_event():
    init_db()
    # Trigger discovery automatically on startup in a background thread
    thread = threading.Thread(target=discover_on_startup)
    thread.daemon = True
    thread.start()

def discover_on_startup():
    """Wrapper for startup discovery to handle own DB session"""
    db = SessionLocal()
    try:
        discover_and_process_news(db)
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Stock News Sentiment Analysis API"}

@app.get("/companies")
def get_companies(has_news: bool = False, db: Session = Depends(get_db)):
    query = db.query(Company)
    if has_news:
        # Filter companies that have at least one news record
        query = query.join(News).distinct()
    return query.all()

def discover_and_process_news(db: Session):
    print("Starting News Discovery Process...")
    discovery_articles = scraper.fetch_discovery_news()
    print(f"Fetched {len(discovery_articles)} articles for discovery.")
    
    for art in discovery_articles:
        # 1. Check if article already exists
        existing_news = db.query(News).filter(News.url == art['url']).first()
        if existing_news:
            continue
            
        # 2. Detect companies in headline/summary
        text = f"{art['headline']}. {art['summary']}"
        detected_companies = nlp.extract_companies(text)
        
        for company_name in detected_companies:
            # 3. Check if company exists by name
            company = db.query(Company).filter(Company.name.ilike(f"%{company_name}%")).first()
            
            if not company:
                # 4. Try to find ticker if it's a new company
                ticker = scraper.search_ticker(company_name)
                # STRICT REQUIREMENT: Only accept Indian Stock Market tickers
                if ticker and (ticker.endswith('.NS') or ticker.endswith('.BO')):
                    # Check if ticker already exists even if name search failed
                    existing_company = db.query(Company).filter(Company.ticker == ticker).first()
                    if existing_company:
                        company = existing_company
                    else:
                        print(f"Discovered new Indian company: {company_name} ({ticker})")
                        company = Company(name=company_name, ticker=ticker, sector="Discovered")
                        db.add(company)
                        try:
                            db.commit()
                            db.refresh(company)
                        except Exception as e:
                            db.rollback()
                            print(f"Database error saving company {company_name}: {e}")
                            continue
                else:
                    # Skip noise (Global stocks, people, sports teams)
                    continue
            
            if company:
                # 5. Process news for this company
                sentiment, score = nlp.get_sentiment(text)
                
                try:
                    pub_date = datetime.fromisoformat(art['published_date'].replace('Z', '+00:00'))
                except:
                    pub_date = datetime.utcnow()
                
                new_news = News(
                    company_id=company.id,
                    headline=art['headline'],
                    summary=art['summary'],
                    content=art['content'],
                    sentiment=sentiment,
                    sentiment_score=score,
                    source=art['source'],
                    url=art['url'],
                    published_date=pub_date
                )
                db.add(new_news)
                try:
                    db.commit()
                except:
                    db.rollback()

    print("News Discovery Process Completed.")

@app.post("/discover")
async def trigger_discovery(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    background_tasks.add_task(discover_and_process_news, db)
    return {"message": "News discovery started in background."}

@app.get("/news/{ticker}")
def get_company_news(ticker: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.ticker == ticker).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    return db.query(News).filter(News.company_id == company.id).order_by(News.published_date.desc()).all()

@app.get("/sentiment/{ticker}")
def get_company_sentiment(ticker: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.ticker == ticker).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    news_items = db.query(News).filter(News.company_id == company.id).all()
    if not news_items:
        return {"ticker": ticker, "sentiment_score": 0, "status": "No news available"}
    
    positive_count = sum(1 for item in news_items if item.sentiment == "Positive")
    negative_count = sum(1 for item in news_items if item.sentiment == "Negative")
    total = len(news_items)
    
    # Formula: (positive_count - negative_count) / total_news
    sentiment_score = (positive_count - negative_count) / total if total > 0 else 0
    
    return {
        "ticker": ticker,
        "name": company.name,
        "sentiment_score": round(sentiment_score, 2),
        "total_news_analyzed": total,
        "distribution": {
            "Positive": positive_count,
            "Negative": negative_count,
            "Neutral": total - (positive_count + negative_count)
        }
    }

def process_company_news(ticker: str, company_id: int, company_name: str, db: Session):
    print(f"Starting analysis for {company_name} ({ticker})")
    articles = scraper.scrape_all(company_name, ticker)
    
    # Deduplicate articles by URL before processing to avoid IntegrityErrors
    seen_urls = set()
    unique_articles = []
    for art in articles:
        if art['url'] not in seen_urls:
            unique_articles.append(art)
            seen_urls.add(art['url'])

    for art in unique_articles:
        # Check if news already exists in DB
        existing = db.query(News).filter(News.url == art['url']).first()
        if existing:
            continue
            
        # Get sentiment
        # We analyze both headline and summary for better results
        text_to_analyze = f"{art['headline']}. {art['summary']}"
        sentiment, score = nlp.get_sentiment(text_to_analyze)
        
        # Parse date
        try:
            if isinstance(art['published_date'], str):
                pub_date = datetime.fromisoformat(art['published_date'].replace('Z', '+00:00'))
            else:
                pub_date = art['published_date']
        except:
            pub_date = datetime.utcnow()

        new_news = News(
            company_id=company_id,
            headline=art['headline'],
            summary=art['summary'],
            content=art['content'],
            sentiment=sentiment,
            sentiment_score=score,
            source=art['source'],
            url=art['url'],
            published_date=pub_date
        )
        db.add(new_news)
    
    db.commit()
    print(f"Finished analysis for {company_name}")

@app.post("/analyze/{ticker}")
async def trigger_analysis(ticker: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.ticker == ticker).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    background_tasks.add_task(process_company_news, company.ticker, company.id, company.name, db)
    return {"message": f"Analysis started in background for {company.name}"}

@app.post("/analyze_all")
async def analyze_all_companies(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    companies = db.query(Company).all()
    for company in companies:
        background_tasks.add_task(process_company_news, company.ticker, company.id, company.name, db)
    
    return {"message": f"Analysis started for {len(companies)} companies"}
