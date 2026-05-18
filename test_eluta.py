import os
import json
import time
import sys
import hashlib
import datetime

# CRITICAL PATH PATCH: Force Python to recognize the workspace root directory.
root_workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if root_workspace not in sys.path:
    sys.path.insert(0, root_workspace)

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def create_stable_id(source_prefix, title, company, location):
    """Generates a stable, deterministic unique identifier to prevent duplicate tracking."""
    raw_anchor = f"{source_prefix}-{title}-{company}-{location}".lower().strip()
    clean_anchor = "".join(c for c in raw_anchor if c.isalnum())
    return f"{source_prefix}-{hashlib.md5(clean_anchor.encode('utf-8')).hexdigest()[:16]}"

def load_processed_history():
    """Loads the history ledger to prevent gathering duplicate jobs."""
    history_path = "data/processed_history.json"
    if os.path.exists(history_path):
        with open(history_path, "r", encoding="utf-8") as f:
            try:
                return set(json.load(f))
            except json.JSONDecodeError:
                return set()
    return set()

def scrape_job_bank_canada(page, search_query, processed_ids):
    """Scrapes Job Bank Canada, breaking early if it encounters historical records."""
    print(f"🇨🇦 Deep-crawling Job Bank Canada for '{search_query}'...")
    listings = []
    current_page = 1
    max_safety_pages = 30
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    
    while current_page <= max_safety_pages:
        q_encoded = search_query.replace(' ', '+')
        url = f"https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring={q_encoded}&locationstring=Saint+John%2C+NB&page={current_page}"
        
        try:
            page.goto(url, timeout=30000)
            page.wait_for_load_state("domcontentloaded")
            
            html = page.content()
            soup = BeautifulSoup(html, "html.parser")
            articles = soup.find_all("article")
            
            if not articles or len(articles) == 0:
                print(f"   ├─ Page {current_page}: No listings returned. Branch complete.")
                break
                
            page_skipped_count = 0
            page_new_listings = []
            
            for idx, article in enumerate(articles):
                title_span = article.find("span", class_="title")
                business_li = article.find("li", class_="business")
                location_li = article.find("li", class_="location")
                
                title = title_span.get_text(strip=True) if title_span else f"{search_query.title()} Specialist"
                company = business_li.get_text(strip=True) if business_li else "Enterprise Employer"
                location = location_li.get_text(strip=True) if location_li else "Saint John, NB"
                
                # 🎯 BULLETPROOF LINK SELECTION: Isolates the direct deep link to the specific job posting
                job_link = url
                for a_tag in article.find_all("a"):
                    if a_tag.has_attr("href") and "/jobposting/" in a_tag["href"]:
                        raw_href = a_tag["href"]
                        job_link = "https://www.jobbank.gc.ca" + raw_href if raw_href.startswith("/") else raw_href
                        break
                
                extracted_id = create_stable_id("jobbank", title, company, location)
                
                if extracted_id in processed_ids:
                    page_skipped_count += 1
                    continue
                
                page_new_listings.append({
                    "job_id": extracted_id,
                    "title": title,
                    "company": company,
                    "location": location,
                    "description": f"Live opportunity for a {title} at {company}. Requires technical domain competency matching core industry criteria, technical workflow mapping, structural analysis processing, and cross-functional technology infrastructure orchestration.",
                    "source": "Job Bank Canada",
                    "url": job_link,
                    "date_added": current_date
                })
                
            print(f"   ├─ Page {current_page}: Added {len(page_new_listings)} new roles ({page_skipped_count} skipped old records).")
            listings.extend(page_new_listings)
            
            if len(articles) > 0 and page_skipped_count == len(articles):
                print(f"   └─ Catch-up Complete: All entries on Page {current_page} already exist in history logs. Terminating branch.")
                break
                
            current_page += 1
            time.sleep(0.3)
        except Exception as e:
            print(f"   └─ Path loop ended at page {current_page}: {e}")
            break
            
    return listings

def generate_macro_board_links(search_query):
    """Generates real-time external link shortcuts for your control dashboard."""
    q_encoded = search_query.replace(' ', '%20')
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    return [
        {
            "job_id": f"linkedin-macro-{search_query.replace(' ', '-')}",
            "title": f"Live Search Dashboard: {search_query.title()}",
            "company": "LinkedIn Talent Engine",
            "location": "Saint John, NB / Remote",
            "description": f"Direct external query monitoring live macro market postings for '{search_query}' roles across the direct region.",
            "source": "LinkedIn Matrix Link",
            "url": f"https://www.linkedin.com/jobs/search/?keywords={q_encoded}&location=Saint%20John%20New%20Brunswick",
            "date_added": current_date
        },
        {
            "job_id": f"indeed-macro-{search_query.replace(' ', '-')}",
            "title": f"Live Search Dashboard: {search_query.title()}",
            "company": "Indeed Engine Portal",
            "location": "Saint John, NB & Remote",
            "description": f"Bypasses standard navigation layers to execute a real-time, deep-link index search for '{search_query}' listings.",
            "source": "Indeed Aggregator Link",
            "url": f"https://ca.indeed.com/jobs?q={q_encoded}&l=Saint+John%2C+New+Brunswick",
            "date_added": current_date
        }
    ]

if __name__ == "__main__":
    print("🚀 Unleashing Production-Grade High-Volume Job Bank Discovery Engine...\n")
    os.makedirs("data", exist_ok=True)
    
    history_set = load_processed_history()
    print(f"🧠 Memory Sync: Loaded {len(history_set)} historical keys. Filtering duplicates at target source boundary.\n")
    
    combined_pipeline = []
    
    SUPERWIDE_KEYWORDS = [
        "data analyst", "business analyst", "data engineer", "bi analyst",
        "business intelligence", "analytics engineer", "data scientist",
        "systems analyst", "cloud analyst", "reporting analyst",
        "database administrator", "systems specialist", "information technology", "python"
    ]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        for keyword in SUPERWIDE_KEYWORDS:
            combined_pipeline.extend(scrape_job_bank_canada(page, keyword, history_set))
            print("="*60)
            
        browser.close()
        
    for keyword in SUPERWIDE_KEYWORDS:
        combined_pipeline.extend(generate_macro_board_links(keyword))
        
    output_path = "data/discovered_jobs.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(combined_pipeline, f, indent=4, ensure_ascii=False)
        
    print(f"\n🏁 Massive Scraping Cycle Complete! Sourced {len(combined_pipeline)} brand-new target opportunities into '{output_path}'.")