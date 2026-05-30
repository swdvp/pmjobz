import os
import psycopg2
from dotenv import load_dotenv

# Load configurations from .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def init_database():
    if not DATABASE_URL:
        print("❌ Error: DATABASE_URL not found in environment variables.")
        return

    # SQL command to construct our matrix-based job table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS job_listings (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        company VARCHAR(255),
        url TEXT UNIQUE NOT NULL,
        raw_snippet TEXT,
        functional_domain VARCHAR(100),
        audience_scope VARCHAR(50),
        technical_depth VARCHAR(50),
        ai_confidence NUMERIC(3, 2),
        discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX IF NOT EXISTS idx_domain ON job_listings(functional_domain);
    CREATE INDEX IF NOT EXISTS idx_scope ON job_listings(audience_scope);
    CREATE INDEX IF NOT EXISTS idx_depth ON job_listings(technical_depth);
    """

    try:
        print("🔄 Connecting to Neon PostgreSQL...")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("🏗️ Creating job_listings table and engineering database indexes...")
        cur.execute(create_table_query)
        
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Database successfully initialized with 3D classification support!")
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    init_database()