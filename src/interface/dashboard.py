import os
import sys

# CRITICAL PATH PATCH: Force Python to recognize the workspace root directory.
# This prevents ModuleNotFoundError when running via the Streamlit CLI environment.
root_workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if root_workspace not in sys.path:
    sys.path.insert(0, root_workspace)

import json
import subprocess
import streamlit as st
from playwright.sync_api import sync_playwright
from src.agents.Tailor_agent import tailor_application_profile

st.set_page_config(
    page_title="Data Guardian - Live Agent Flight Deck",
    page_icon="🕵️",
    layout="wide"
)

st.title("🕵️ Cloud MCP Project: Live Application Flight Deck")
st.caption("Autonomous Web Automation & Semantic Optimization")
st.markdown("---")

def load_json_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

discovered_jobs = load_json_data("data/discovered_jobs.json")
qualified_jobs = load_json_data("data/qualified_jobs.json")

# ==========================================
# SIDEBAR SYSTEM CONTROLS
# ==========================================
st.sidebar.header("⚙️ Pipeline Commands")

if st.sidebar.button("🌐 Execute Job Discovery", use_container_width=True):
    with st.spinner("Searching live APIs..."):
        subprocess.run(["python", "src/infrastructure/job_discovery.py"], capture_output=True, text=True)
        st.sidebar.success("Discovery complete!")
        st.rerun()

if st.sidebar.button("📡 Execute Semantic Screener", use_container_width=True):
    with st.spinner("Calculating vector distances via Oracle 23ai..."):
        subprocess.run(["python", "src/agents/Screener_agent.py"], capture_output=True, text=True)
        st.sidebar.success("Screening complete!")
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.metric("Discovered Targets", len(discovered_jobs))
st.sidebar.metric("Qualified Matches", len(qualified_jobs))

# ==========================================
# MAIN INTERACTIVE LAYOUT
# ==========================================
tab1, tab2 = st.tabs(["📋 Discovered Pipeline", "🚀 Live Application Portal"])

with tab1:
    st.subheader("All Discovered Positions")
    if not discovered_jobs:
        st.info("No jobs found yet.")
    else:
        for job in discovered_jobs:
            with st.expander(f"💼 {job.get('title')} — {job.get('company')}"):
                st.markdown(f"**Source:** {job.get('source')} | [Portal Link]({job.get('url')})")
                st.write(job.get("description"))

with tab2:
    st.subheader("Production Form Automation (Greenhouse / Lever Focus)")
    
    if not qualified_jobs:
        st.warning("No qualified targets currently in queue.")
    else:
        job_options = [f"{j.get('title')} at {j.get('company')}" for j in qualified_jobs]
        selected_job_str = st.selectbox("🎯 Target Position Context:", job_options)
        
        selected_index = job_options.index(selected_job_str)
        job = qualified_jobs[selected_index]
        
        # User adds the specific target URL if working outside the sandbox mock link
        live_target_url = st.text_input("🔗 Live Application URL (Paste the job's Greenhouse/Lever apply link here):", value=job.get('url'))
        
        col1, col2 = st.columns([1, 1.2])
        
        with col1:
            st.markdown("### 📋 Job Metrics")
            st.info(f"**Oracle Proximity Vector:** {job.get('semantic_distance', 0.0):.4f}")
            st.text_area("Requirements Framework", job.get("description"), height=250, disabled=True)
            
        with col2:
            st.markdown("### 📝 Live Cover Letter Adjustments")
            
            state_key = f"letter_{job.get('job_id')}"
            if state_key not in st.session_state:
                with st.spinner("Compiling cover letter text via Amazon Nova..."):
                    st.session_state[state_key] = tailor_application_profile(job.get("description"))
            
            edited_letter = st.text_area("Live Editor Workspace", st.session_state[state_key], height=350)
            
            # 🚀 LIVE DEPLOYMENT BUTTON
            if st.button(f"⚡ Execute Real Application to {job.get('company')}", type="primary", use_container_width=True):
                if "mock-local-careers" in live_target_url:
                    st.error("Please paste a valid live application URL link before executing a production web deployment.")
                elif not os.path.exists("resume.pdf"):
                    st.error("Missing source file 'resume.pdf' in root workspace folder. Cannot satisfy form attachment protocols.")
                else:
                    with st.spinner("Launching production browser context..."):
                        try:
                            resume_absolute_path = os.path.abspath("resume.pdf")
                            
                            with sync_playwright() as p:
                                browser = p.chromium.launch(headless=True)
                                page = browser.new_page()
                                
                                print(f"📡 Browsing live portal path: {live_target_url}")
                                page.goto(live_target_url, timeout=45000)
                                page.wait_for_load_state("networkidle")
                                
                                # Hardened Smart Parsing Interaction Steps:
                                print("✍️ Injecting user identifying telemetry data...")
                                
                                # 1. Name Input Logic
                                if page.locator("input[name*='name']").first.is_visible():
                                    page.locator("input[name*='name']").first.fill("Colin Keith")
                                elif page.locator("input[id*='name']").first.is_visible():
                                    page.locator("input[id*='name']").first.fill("Colin Keith")
                                    
                                # 2. Email Input Logic
                                if page.locator("input[name*='email']").first.is_visible():
                                    page.locator("input[name*='email']").first.fill("colin.ad.keith@gmail.com")
                                    
                                # 3. Dynamic Cover Letter Attachment
                                if page.locator("textarea[name*='cover']").first.is_visible():
                                    page.locator("textarea[name*='cover']").first.fill(edited_letter.strip())
                                elif page.locator("textarea[id*='cover']").first.is_visible():
                                    page.locator("textarea[id*='cover']").first.fill(edited_letter.strip())
                                    
                                # 4. FILE UPLOAD PROMPT HANDLING
                                print("📁 Locating file upload gates for resume attachment...")
                                file_input_selector = "input