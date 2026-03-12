import os
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./stock_sentiment.db")

Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    ticker = Column(String, unique=True, index=True)
    sector = Column(String, index=True)

    news = relationship("News", back_populates="company")

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    headline = Column(String, index=True)
    summary = Column(Text)
    content = Column(Text)
    sentiment = Column(String)  # Positive, Negative, Neutral
    sentiment_score = Column(Float)
    source = Column(String)
    url = Column(String, unique=True)
    published_date = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="news")

# Database connection setup
from sqlalchemy import create_engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
