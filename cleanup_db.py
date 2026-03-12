import sqlite3
import os

# Explicit absolute path
db_path = r"e:\Project\AI Stock News Sentiment\stock_sentiment.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Identify non-Indian stocks (ones without .NS or .BO)
    c.execute("SELECT id, name, ticker FROM companies WHERE ticker NOT LIKE '%.NS' AND ticker NOT LIKE '%.BO'")
    bad_companies = c.fetchall()
    
    print(f"Found {len(bad_companies)} non-Indian market entities to remove.")
    for cid, name, ticker in bad_companies:
        print(f" - Removing: {name} ({ticker})")
        c.execute("DELETE FROM news WHERE company_id = ?", (cid,))
        c.execute("DELETE FROM companies WHERE id = ?", (cid,))
    
    conn.commit()
    conn.close()
    print("Database cleanup complete.")
else:
    print(f"Database not found at {db_path}")
