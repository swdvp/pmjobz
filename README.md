# AI-Powered Product Management Job Search by Skill

## The Problem
Job seekers manually review hundreds of generic "Product Manager" listings to find the < 10% of positions that actually align with their domain expertise. Traditional job boards rely on keyword-stuffed descriptions, making keyword-based filtering highly inefficient.

## The Solution
A hands-on, programmatic data pipeline and UI designed to eliminate the noise of modern job boards by dynamically parsing and tagging PM roles based on actual skills, e.g., Platform, AI, Fintech, Ecommerce, API, etc.

## Live Demo
[View the Live Prototype](http://pmjobz.com)

## How It Works
1. **Ingestion:** A Python pipeline programmatically scrapes active jobs directly from employer applicant tracking systems (Greenhouse, Lever, Ashby).
2. **AI Semantic Parsing:** Raw job text is passed to OpenAI's API using strict JSON schemas to cleanly isolate target functional skill arrays (e.g., Platform, AI, Fintech, Ecommerce, API, etc).
3. **Data Quality & Storage:** Defensive parsing gateways sanitize messy inputs, resolve missing metadata, and handle API exception failures before persisting clean data streams into a Neon PostgreSQL database.
4. **Delivery:** A lightweight Streamlit UI provides end-users with interactive multi-select skill filters to cut discovery time down from hours to minutes.

## The Architectural Innovation

Instead of building a simple full-stack app with mock data, **PM Match** bridges an active AI-driven scraping pipeline directly to a lightweight mobile client. 

## System Architecture

```text
┌────────────────────────┐      ┌────────────────────────┐      ┌────────────────────────┐
│  AI Ingestion Engine   │ ───> │ Neon PostgreSQL Cloud  │ ───> │ FastAPI Backend Server │
│ (Scrapes & Categorizes)│      │  (Data Rich Text API)  │      │  (CORS & SQL Filtering)│
└────────────────────────┘      └────────────────────────┘      └────────────────────────┘
                                                                             │
                                                                             ▼
                                                                ┌────────────────────────┐
                                                                │ Mobile-First UI Client │
                                                                │  (Dynamic Pill Cloud)  │
                                                                └────────────────────────┘

```

## Tech Stack
- **Frontend:** Mobile-first responsive UI built with Tailwind CSS, running vanilla JavaScript and Inter font typography. Optimized for lightning-fast DOM rendering cycles.
- **Backend:** FastAPI (Python) web framework leveraging Uvicorn ASGI protocol interfaces.
- **Database Object Mapping:** Managed with psycopg2 using a RealDictCursor factory to stream native JSON collections directly to web fetch handlers.
- **Cloud Storage Tier:** Neon Serverless PostgreSQL.

## Local Installation and Setup
1. Clone the Repository
```bash
git clone https://github.com/swdvp/pm-match.git
cd pm-match
```

2. Configure the Backend Server
Create a virtual python environment and install the required service packages:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Set up your local system context to connect to your remote Neon Cluster database string:

```bash
export DATABASE_URL="postgresql://[user]:[password]@[cluster].neon.tech/neondb?sslmode=require"
```

4. Boot the API engine locally on port 8000:

```bash
uvicorn main:app --reload
```

5. Open the Client UI Dashboard
Open your local index.html file inside any modern desktop or mobile browser environment to see the pipeline actively stream production job information.
# pmjobz
