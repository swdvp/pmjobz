import psycopg2
import os
from dotenv import load_dotenv

load_dotenv(override=True)
db_url = os.getenv("DATABASE_URL", "").strip().strip('"').strip("'")

def reset_database():
    """
    Drops old tables and provisions clean multi-tag array schemas for v1.1 matrix profiles.
    """
    drop_query = "DROP TABLE IF EXISTS job_listings CASCADE;"
    
    create_query = """
    CREATE TABLE job_listings (
        id SERIAL PRIMARY KEY,
        title VARCHAR(500) NOT NULL,
        company VARCHAR(255) NOT NULL,
        url TEXT UNIQUE NOT NULL,
        raw_snippet TEXT,
        functional_domains TEXT[],         -- 🚀 Array field for multiple functional domains
        audience_scopes TEXT[],           -- 🚀 Array field for multiple audience parameters
        technical_depth_profiles TEXT[],  -- 🚀 Array field for multiple technical profiles
        ai_confidence INTEGER DEFAULT 0,
        listing_depth VARCHAR(100) DEFAULT 'Direct Role Link',
        extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    try:
        print("🔄 Connecting to Neon PostgreSQL...")
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        print("🧼 Dropping old job listings architecture...")
        cur.execute(drop_query)
        
        print("🏗️ Provisioning clean v1.1 Multi-Axis Database Schema...")
        cur.execute(create_query)
        
        conn.commit()
        print("🎯 Database table structures successfully upgraded to 3D Array Matrix specs!")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Failed to reset database: {e}")

if __name__ == "__main__":
    reset_database()