import os
import re
import requests
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv(override=True)
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "").strip().strip('"').strip("'"))
serper_key = os.getenv("SERPER_API_KEY", "").strip().strip('"').strip("'")

def sanitize_job_metadata(extracted_company, url, raw_title):
    """Cleans titles and extracts company name from ATS subdomains."""
    # Strip branding artifacts like ' - Greenhouse'
    clean_title = re.sub(r'\s*[@|]\s*.*$', '', raw_title).strip()
    
    # 2. Strip additional branding artifacts like ' - Jobs' or ' - Greenhouse'
    clean_title = re.sub(r'\s*[-\\|•]\s*(Jobs|Greenhouse|Lever|Ashby|Careers).*$', '', clean_title, flags=re.IGNORECASE).strip()

    # Fallback to URL parsing if company name is generic
    url_lower = url.lower()
    cleaned_company = str(extracted_company).strip()
    generic_triggers = ["greenhouse", "lever", "ashby", "unknown", "not specified", "n/a"]

    if any(trigger in cleaned_company.lower() for trigger in generic_triggers):
        match = re.search(r'(?:greenhouse\.io|lever\.co|ashbyhq\.com)/([^/]+)', url_lower)
        if match:
            cleaned_company = match.group(1).replace('-', ' ').title()

    return cleaned_company, clean_title

def classify_job_listing(title, full_job_description):
    """
    Restores v1.4 Classification Engine.
    Forces the LLM to dynamically isolate core requirements using section headers 
    before performing 3D Matrix classification.
    """
    target_headers = [
        "What you should have", "What You'll Be Doing", "Qualifications", "Key Qualifications",
        "Responsibilities", "Key Responsibilities", "Your Responsibilities", "What You’ll Accomplish",
        "Your Expertise", "What You Bring", "Who You Are", "What You will Do", "We Are Looking For",
        "Skills and Experience", "Minimum Qualifications"
    ]
    
    user_content = (
        f"Job Title: {title}\n\n"
        f"Full Job Description Content:\n{full_job_description}\n\n"
        f"Target Headers for Isolation Reference:\n{', '.join(target_headers)}"
    )
    
    try:
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a strict, technical talent intelligence parser. Classify roles into a 3D Taxonomy Matrix.\n\n"
                        "STEP 1: ISOLATE CORE SIGNAL\n"
                        "Scan the provided description and find sections matching the Target Headers. "
                        "Completely ignore company marketing hype, benefits, and cultural introductions.\n\n"
                        "STEP 2: EXTRACT TECHNICAL GROUND TRUTH\n"
                        "Identify the concrete technical stack and responsibilities from the isolated sections only.\n\n"
                        "STEP 3: ENFORCE DETERMINISTIC CLASSIFICATION\n"
                        "Only use the provided Enum domains. Do not hallucinate."
                    )
                },
                {"role": "user", "content": user_content}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "job_matrix_schema_v1_4",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "isolated_sections_summary": {"type": "string"},
                            "technical_keywords_detected": {"type": "array", "items": {"type": "string"}},
                            "company_name": {"type": "string"},
                            "functional_domains": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": [
                                        "Ecommerce", "Ad Tech & MarTech", "Security", "Identity", 
                                        "Pricing & Monetization", "Platform", "AI/ML",
                                        "Data & Analytics", "Fintech", "Payments",
                                        "SaaS", "Growth", "Consumer Monetization",
                                        "API"
                                    ]
                                }
                            }
                        },
                        "required": ["isolated_sections_summary", "technical_keywords_detected", "company_name", "functional_domains"],
                        "additionalProperties": False
                    }
                }
            }
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(f"  ⚠️ OpenAI Matrix Classification Error: {e}")
        return None

def is_review_hub(title):
    """
    Returns True if the job title indicates it's a hub page 
    or a collection of roles rather than a specific position.
    """
    hub_keywords = [
        "talent program", "career", "hub", "jobs board", 
        "opportunities", "hiring", "apply", "careers", 
        "department", "jobs at", "derby", "blog", "article",
        "articles", "http", "[XML]", "Meet the team",
        "open positions", "job openings", "work with us"
    ]
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in hub_keywords)

def run_pipeline():
    search_queries = [
        ('"Product Manager" "Platform"', 'site:greenhouse.io -inurl:jobs'),
        ('"Product Manager" "Platform"', 'site:lever.co -inurl:jobs'),
        ('"Product Manager" "Platform"', 'site:ashbyhq.com -inurl:jobs'),
        ('"Product Manager" "Machine Learning"', 'site:greenhouse.io -inurl:jobs'),
        ('"Product Manager" "Machine Learning"', 'site:lever.co -inurl:jobs'),
        ('"Product Manager" "Machine Learning"', 'site:ashbyhq.com -inurl:jobs'),
        ('"Product Manager" "API"', 'site:greenhouse.io -inurl:jobs'),
        ('"Product Manager" "API"', 'site:lever.co -inurl:jobs'),
        ('"Product Manager" "API"', 'site:ashbyhq.com -inurl:jobs'),
        ('"Product Manager" "ecommerce"', 'site:greenhouse.io -inurl:jobs'),
        ('"Product Manager" "ecommerce"', 'site:lever.co -inurl:jobs'),
        ('"Product Manager" "shopping"', 'site:greenhouse.io -inurl:jobs'),
        ('"Product Manager" "shopping"', 'site:lever.co -inurl:jobs'),
        ('"Product Manager" "shopping"', 'site:ashbyhq.com -inurl:jobs'),
        ('"Product Manager" "payments"', 'site:greenhouse.io -inurl:jobs'),
        ('"Product Manager" "payments"', 'site:lever.co -inurl:jobs'),
        ('"Product Manager" "payments"', 'site:ashbyhq.com -inurl:jobs'),
        ('"Product Manager" "checkout"', 'site:greenhouse.io -inurl:jobs'),
        ('"Product Manager" "checkout"', 'site:lever.co -inurl:jobs'),
        ('"Product Manager" "Identity"', 'site:greenhouse.io -inurl:jobs'),
        ('"Product Manager" "Identity"', 'site:lever.co -inurl:jobs'),
        ('"Product Manager" "Identity"', 'site:ashbyhq.com -inurl:jobs'),
        ('"Product Manager" "Security"', 'site:greenhouse.io -inurl:jobs'),
        ('"Product Manager" "Security"', 'site:lever.co -inurl:jobs'),
        ('"Product Manager" "Security"', 'site:ashbyhq.com -inurl:jobs'),
        ('"Product Manager" "Data Platform"', 'site:greenhouse.io -inurl:jobs'),
        ('"Product Manager" "Data Platform"', 'site:lever.co -inurl:jobs'),
        ('"Product Manager" "Data Platform"', 'site:ashbyhq.com -inurl:jobs'),    ]

    all_jobs = []

    for query in search_queries:
        print(f"🚀 Fetching: {query}")
        response = requests.post("https://google.serper.dev/search", 
                                 headers={'X-API-KEY': serper_key, 'Content-Type': 'application/json'},
                                 json={'q': query, 'num': 10})
        
        results = response.json().get('organic', [])
        
        for item in results:
            matrix = classify_job_listing(item.get('title'), item.get('snippet', ''))
            company, title = sanitize_job_metadata(matrix.get('company_name'), item.get('link'), item.get('title'))

            if is_review_hub(title):
                print(f"⏭️ Skipping hub/collection page: {title}")
                continue

            job_entry = {
                "title": title,
                "company": company.upper(),
                "url": item.get('link'),
                "skills": matrix.get('functional_domains', [])
            }
            all_jobs.append(job_entry)

    with open('jobs.json', 'w') as f:
        json.dump(all_jobs, f, indent=4)
    print(f"✅ Success! {len(all_jobs)} jobs saved to jobs.json.")

if __name__ == "__main__":
    run_pipeline()