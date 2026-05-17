import os
import json
import time
from playwright.sync_api import sync_playwright
from src.agents.Tailor_agent import tailor_application_profile

def execute_automated_applications():
    # Looking at the data folder at the root level
    input_path = "data/qualified_jobs.json"
    
    if not os.path.exists(input_path):
        print(f"❌ Error: Missing '{input_path}'. Run the screener agent first.")
        return
        
    with open(input_path, "r", encoding="utf-8") as f:
        qualified_jobs = json.load(f)
        
    if not qualified_jobs:
        print("📭 No qualified jobs found in the pipeline to apply for.")
        return
        
    print(f"🤖 Action Agent initialized. Preparing to apply for {len(qualified_jobs)} roles...\n")
    
    # Locate our local simulation page absolute path from the root directory
    local_form_path = os.path.abspath("mock_apply_page.html")
    form_url = f"file://{local_form_path}"

    # Launch Playwright Headless Browser Lifecycle
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        for index, job in enumerate(qualified_jobs):
            title = job.get("title")
            company = job.get("company")
            desc = job.get("description")
            
            print(f"💼 Processing Application [{index + 1}/{len(qualified_jobs)}]: {title} at {company}")
            print("─" * 70)
            
            # 1. Dynamically trigger your AI agent to tailor a summary for THIS specific job description
            print("🧠 Requesting custom profile generation from Amazon Nova...")
            tailored_summary = tailor_application_profile(desc)
            
            # 2. Navigate the browser tool to the application portal
            print("🌐 Navigating browser to portal submission form...")
            page.goto(form_url)
            
            # 3. Fill the HTML input elements using CSS selectors matching our form IDs
            print("✍️ Auto-filling application parameters...")
            page.fill("#applicant-name", "Colin Keith")
            page.fill("#applicant-email", "colin.ad.keith@gmail.com")
            page.fill("#target-position", f"{title} ({company})")
            page.fill("#tailored-profile", tailored_summary.strip())
            
            # Take a screenshot of the filled form for audit history logs before submitting
            os.makedirs("data/receipts", exist_ok=True)
            screenshot_path = f"data/receipts/filled_app_{index + 1}.png"
            page.screenshot(path=screenshot_path)
            print(f"📸 Audit log saved: '{screenshot_path}'")
            
            # 4. Click the submit button
            print("⚡ Clicking Submit Button...")
            page.click("#submit-btn")
            
            # Verify success banner display state
            page.wait_for_selector("#success-message", state="visible")
            print("🎉 Form Submission Confirmed by UI Engine!")
            print("-" * 70 + "\n")
            time.sleep(2)  # Short delay between loops
            
        browser.close()
    print("🏁 Automated Application Loop finished execution successfully!")

if __name__ == "__main__":
    execute_automated_applications()