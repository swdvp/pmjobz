cat << 'EOF' > ingest.py
import os
import requests
import psycopg2
from dotenv import load_dotenv

# Load credentials
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

def fetch_and_ingest_jobs():
    print("Initializing Google Job Search Ingestion...")
    
    # Check setup
    if not all([DATABASE_URL, GOOGLE_API_KEY, GOOGLE_CSE_ID]):
        print("Error: Missing environmental credentials in .env file.")
        return

    # Google Custom Search API Setup
    query = '"product manager" "e-commerce" "San Francisco"'
    url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}&q={query}"
    
    try:
        response = requests.get(url).json()
        items = response.get("items", [])
    except Exception as e:
        print(f"Failed to fetch data from Google API: {e}")
        return

    if not items:
        print("No new job listings found matching the query parameters.")
        return

    # Connect and Ingest into Database
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        new_records = 0
        for item in items:
            title = item.get("title")
            link = item.get("link")
            snippet = item.get("snippet")
            
            # Prevent duplicates using ON CONFLICT clause
            query_db = """
                INSERT INTO raw_job_listings (job_title, application_url, job_snippet)
                VALUES (%s, %s, %s)
                ON CONFLICT (application_url) DO NOTHING;
            """
            cur.execute(query_db, (title, link, snippet))
            if cur.rowcount > 0:
                new_records += cur.rowcount
                
        conn.commit()
        cur.close()
        conn.close()
        print(f"Success! Committed {new_records} new job records to the database.")
        
    except Exception as e:
        print(f"Database error encountered: {e}")

if __name__ == "__main__":
    fetch_and_ingest_jobs()
EOF