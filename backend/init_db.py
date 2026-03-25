from database import SessionLocal, init_db, Company


def seed_db():
    init_db()
    db = SessionLocal()

    # Check if companies already exist
    if db.query(Company).count() > 0:
        print("Database already seeded.")
        db.close()
        return

    sample_companies = [
        {
            "name": "Reliance Industries Limited",
            "ticker": "RELIANCE.NS",
            "sector": "Energy",
        },
        {
            "name": "Tata Consultancy Services",
            "ticker": "TCS.NS",
            "sector": "Technology",
        },
        {"name": "HDFC Bank", "ticker": "HDFCBANK.NS", "sector": "Banking"},
        {"name": "Infosys", "ticker": "INFY.NS", "sector": "Technology"},
        {"name": "Tata Motors", "ticker": "TATAMOTORS.NS", "sector": "Automotive"},
        {"name": "Adani Enterprises", "ticker": "ADANIENT.NS", "sector": "Diversified"},
        {"name": "SBI", "ticker": "SBIN.NS", "sector": "Banking"},
        {"name": "ICICI Bank", "ticker": "ICICIBANK.NS", "sector": "Banking"},
    ]

    for comp_data in sample_companies:
        company = Company(**comp_data)
        db.add(company)

    db.commit()
    db.close()
    print("Database seeded with sample Indian companies.")


if __name__ == "__main__":
    seed_db()
