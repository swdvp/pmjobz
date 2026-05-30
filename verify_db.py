import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Force load and sanitize configurations
load_dotenv(override=True)
db_url = os.getenv("DATABASE_URL", "").strip().strip('"').strip("'")

def review_warehouse_state():
    print("Connecting to Neon PostgreSQL Data Warehouse...")
    try:
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        
        # 1. Total Metrics Breakdown
        cur.execute("SELECT COUNT(*) as total FROM job_listings;")
        total_records = cur.fetchone()['total']
        
        print("\n=============================================")
        print(f"📊 DATA WAREHOUSE INTEGRITY REPORT")
        print(f"   Total Distinct Records Stored: {total_records}")
        print("=============================================")
        
        if total_records == 0:
            print("The warehouse is currently empty.")
            return

        # 2. Distribution across Functional Domains
        print("\n🗂️ DISTRIBUTION BY FUNCTIONAL DOMAIN:")
        cur.execute("""
            SELECT functional_domain, COUNT(*) as cnt 
            FROM job_listings 
            GROUP BY functional_domain 
            ORDER BY cnt DESC;
        """)
        for row in cur.fetchall():
            print(f"  • {row['functional_domain']:<30} : {row['cnt']} jobs")

        # 3. Sample Matrix Records (Top 5 Recent entries)
        print("\n🔍 SAMPLE CLASSIFIED RECORDS IN WAREHOUSE:")
        cur.execute("""
            SELECT title, company, functional_domain, audience_scope, technical_depth, ai_confidence 
            FROM job_listings 
            ORDER BY id DESC 
            LIMIT 5;
        """)
        
        for idx, row in enumerate(cur.fetchall(), 1):
            print(f"\n  [{idx}] {row['title']} @ {row['company']}")
            print(f"      ├─ Domain:    {row['functional_domain']}")
            print(f"      ├─ Scope:     {row['audience_scope']}")
            print(f"      ├─ Depth:     {row['technical_depth']}")
            print(f"      └─ Match Conf: {int(row['ai_confidence'] * 100)}%")
            
        cur.close()
        conn.close()
        print("\n=============================================")
        
    except Exception as e:
        print(f"❌ Failed to query database: {e}")

if __name__ == "__main__":
    review_warehouse_state()