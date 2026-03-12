import sqlite3
from pathlib import Path

db_path = Path("stock_sentiment.db")
if not db_path.exists():
    print("Database not found")
else:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute("SELECT id, name, ticker FROM companies")
    companies = c.fetchall()
    
    print("Database Summary:")
    for cid, name, ticker in companies:
        c.execute("SELECT COUNT(*) FROM news WHERE company_id = ?", (cid,))
        count = c.fetchone()[0]
        print(f" - {name} ({ticker}): {count} articles")
    
    conn.close()
