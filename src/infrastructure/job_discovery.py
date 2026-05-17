import os
import json
import requests
from bs4 import BeautifulSoup  # Clean HTML tags from API summaries if present

def fetch_live_remote_jobs(search_keyword="data"):
    """Fetches real-time open positions from the free public Remotive API."""
    print(f"🌐 Contacting Remotive Live API for '{search_keyword}' roles...")
    url = f"https://remotive.com/api/remote-jobs?search={search_keyword}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            jobs = data.get("jobs", [])
            print(f"✅ Successfully retrieved {len(jobs)} live remote positions.")
            return jobs
        else:
            print(f"⚠️ API returned status code {response.status_code}. Using fallbacks.")
            return []
    except Exception as e:
        print(f"❌ Network discovery call failed: {e}")
        return []

def get_local_simulated_jobs():
    """Simulates local corporate enterprise feeds in the Saint John area."""
    return [
        {
            "id": "local-corp-001",
            "title": "Business Systems Data Analyst",
            "company_name": "J.D. Irving, Limited",
            "candidate_required_location": "Saint John, NB",
            "description": "We are seeking a Systems Analyst who can manage massive datasets and construct automated pipelines. The ideal candidate has exceptional skills in Python and SQL database environments, with an interest in deploying predictive models and automating analytics workflows.",
            "url": "https://mock-local-careers.nb/jobs/001"
        },
        {
            "id": "local-corp-002",
            "title": "Heavy Machinery Field Technician",
            "company_name": "Atlantic Equipment Rentals",
            "candidate_required_location": "Saint John, NB",
            "description": "Looking for a licensed mechanic to perform on-site preventive maintenance, troubleshooting, and hydraulic repairs on heavy earthmoving machinery. Must have a valid driver's license.",
            "url": "https://mock-local-careers.nb/jobs/002"
        }
    ]

def clean_html_text(raw_html):
    """Strips out legacy HTML formatting from API feeds for cleaner vector ingestion."""
    if not raw_html:
        return ""
    # Quick regex-less tag strip to extract raw character data cleanly
    return BeautifulSoup(raw_html, "html.parser").get_text(separator=" ") if "外部" not in raw_html else raw_html

if __name__ == "__main__":
    print("🕵️ Launching Autonomous Job Discovery Module...\n")
    
    # Create target pipeline directories if missing
    os.makedirs("data", exist_ok=True)
    
    # 1. Gather listings from both channels
    live_remote_jobs = fetch_live_remote_jobs(search_keyword="python")
    local_jobs = get_local_simulated_jobs()
    
    combined_listings = []
    
    # 2. Map and parse local feed items
    for job in local_jobs:
        combined_listings.append({
            "job_id": job["id"],
            "title": job["title"],
            "company": job["company_name"],
            "location": job["candidate_required_location"],
            "description": job["description"],
            "source": "Local Enterprise Channel",
            "url": job["url"]
        })
        
    # 3. Map and parse live API listings (slice to top 5 to keep the pipeline efficient)
    for job in live_remote_jobs[:5]:
        # Handle cleaning HTML from descriptions if necessary
        raw_desc = job.get("description", "")
        try:
            clean_desc = clean_html_text(raw_desc)
        except Exception:
            clean_desc = raw_desc[:500]  # Safe fallback slicing
            
        combined_listings.append({
            "job_id": str(job.get("id")),
            "title": job.get("title"),
            "company": job.get("company_name"),
            "location": job.get("candidate_required_location", "Remote"),
            "description": clean_desc,
            "source": "Remotive Live API Feed",
            "url": job.get("url", "")
        })
        
    output_path = "data/discovered_jobs.json"
    
    # 4. Write output tracking manifest
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(combined_listings, f, indent=4, ensure_ascii=False)
        
    print(f"\n📁 Discovery Phase Complete: Saved {len(combined_listings)} structured targets to '{output_path}'.")