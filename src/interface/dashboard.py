import os
import json
import subprocess
import streamlit as st
from playwright.sync_api import sync_playwright
from src.agents.Tailor_agent import tailor_application_profile

# Set up page configurations
st.set_page_config(
    page_title="Data Guardian - Agent Control Center",
    page_icon="🕵️",
    layout="wide"
)

st.title("🕵️ Cloud MCP Project: Job Agent Control Center")
st.caption("Multi-Cloud Autonomous Discovery, Semantic Screening, and Browser Application Pipeline")
st.markdown("---")

# Helper functions to load dataset states
def load_json_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

discovered_jobs = load_json_data("data/discovered_jobs.json")
qualified_jobs = load_json_data("data/qualified_jobs.json")

# ==========================================
# SIDEBAR: SYSTEM CONTROLS
# ==========================================
st.sidebar.header("⚙️ Pipeline Commands")

if st.sidebar.button("🌐 Execute Job Discovery", use_container_width=True):
    with st.spinner("Searching live APIs and local feeds..."):
        # Run our discovery script as a clean subprocess to maintain environment pathing
        result = subprocess.run(["python", "src/infrastructure/job_discovery.py"], capture_output=True, text=True)
        st.sidebar.success("Discovery complete!")
        st.rerun()

if st.sidebar.button("📡 Execute Semantic Screener", use_container_width=True):
    with st.spinner("Calculating vector distances via Oracle 23ai & AWS Titan..."):
        result = subprocess.run(["python", "src/agents/Screener_agent.py"], capture_output=True, text=True)
        st.sidebar.success("Screening complete!")
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Pipeline Summary")
st.sidebar.metric("Discovered Targets", len(discovered_jobs))
st.sidebar.metric("Qualified Matches", len(qualified_jobs))

# ==========================================
# MAIN LAYOUT: TABS SYSTEMS
# ==========================================
tab1, tab2 = st.tabs(["📋 Discovered Pipeline", "🚀 Application Command Center"])

# ------------------------------------------
# TAB 1: ALL DISCOVERED JOBS LIST
# ------------------------------------------
with tab1:
    st.subheader("All Scraped & Discovered Positions")
    st.write("Below are the raw roles pulled by the discovery layer before or during vector evaluation.")
    
    if not discovered_jobs:
        st.info("No jobs found yet. Use the sidebar command to launch a discovery loop.")
    else:
        for job in discovered_jobs:
            with st.expander(f"💼 {job.get('title')} — {job.get('company')} ({job.get('location')})"):
                st.markdown(f"**Source:** {job.get('source')} | [View Original Posting]({job.get('url')})")
                st.markdown("**Description Preview:**")
                st.write(job.get("description"))

# ------------------------------------------
# TAB 2: QUALIFIED HUMAN-IN-THE-LOOP CONTROL
# ------------------------------------------
with tab2:
    st.subheader("Qualified Targets & Document Tailoring")
    st.write("These jobs successfully cleared the Oracle 23ai vector similarity threshold.")
    
    if not qualified_jobs:
        st.warning("No qualified targets currently in queue. Run the Semantic Screener to populate this list.")
    else:
        # Create a dropdown selector for jobs that cleared the threshold
        job_options = [f"{j.get('title')} at {j.get('company')}" for j in qualified_jobs]
        selected_job_str = st.selectbox("🎯 Select a qualified target to review & process:", job_options)
        
        # Extract the corresponding job dict
        selected_index = job_options.index(selected_job_str)
        job = qualified_jobs[selected_index]
        
        col1, col2 = st.columns([1, 1.2])
        
        with col1:
            st.markdown("### 📋 Job Specifications")
            st.info(f"**Vector Proximity Score:** {job.get('semantic_distance', 0.0):.4f}")
            st.markdown(f"**Company:** {job.get('company')}")
            st.markdown(f"**Location:** {job.get('location')}")
            st.markdown("**Core Requirements:**")
            st.text_area("Job Details", job.get("description"), height=250, disabled=True)
            
        with col2:
            st.markdown("### 📝 Tailored Document Workspace")
            st.write("Review and fine-tune the template cover letter compiled for this position:")
            
            # Use st.cache_data or session state to avoid regenerating documents on random UI clicks
            state_key = f"letter_{job.get('job_id')}"
            if state_key not in st.session_state:
                with st.spinner("Calling Amazon Nova to refine your cover letter..."):
                    st.session_state[state_key] = tailor_application_profile(job.get("description"))
            
            # Provide an interactive text area so you can make manual structural adjustments!
            edited_letter = st.text_area("Cover Letter Text Editor", st.session_state[state_key], height=350)
            
            # 🚀 EXECUTE BROWSER AUTOMATION FOR THIS SINGLE SELECTED JOB
            if st.button(f"⚡ Launch Playwright Applier for {job.get('company')}", type="primary", use_container_width=True):
                with st.spinner("Booting headless Chromium engine to submit application..."):
                    try:
                        local_form_path = os.path.abspath("mock_apply_page.html")
                        form_url = f"file://{local_form_path}"
                        
                        with sync_playwright() as p:
                            browser = p.chromium.launch(headless=True)
                            page = browser.new_page()
                            
                            page.goto(form_url)
                            page.fill("#applicant-name", "Colin Keith")
                            page.fill("#applicant-email", "colin.ad.keith@gmail.com")
                            page.fill("#target-position", f"{job.get('title')} ({job.get('company')})")
                            page.fill("#tailored-profile", edited_letter.strip())
                            
                            # Capture a screenshot live from the Streamlit UI frame
                            os.makedirs("data/receipts", exist_ok=True)
                            receipt_path = f"data/receipts/ui_app_{job.get('job_id')}.png"
                            page.screenshot(path=receipt_path)
                            
                            page.click("#submit-btn")
                            page.wait_for_selector("#success-message", state="visible")
                            browser.close()
                            
                        st.success(f"🎉 Success! Application filed smoothly. Receipt saved to {receipt_path}")
                        st.image(receipt_path, caption="Visual Form Audit Entry Log Captured", use_column_width=True)
                        
                    except Exception as e:
                        st.error(f"Browser Submission Failed: {e}")