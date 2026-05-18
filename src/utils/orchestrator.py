import os
import sys
import subprocess

# Path hardening to guarantee root execution pathing
root_workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if root_workspace not in sys.path:
    sys.path.insert(0, root_workspace)

def run_pipeline_step(script_path, step_name):
    print(f"\n{"="*60}")
    print(f"🚀 EXECUTING: {step_name}")
    print(f"{"="*60}")
    
    # Run the target Python script as a clean subprocess
    result = subprocess.run(["python", script_path], capture_output=False)
    
    if result.returncode != 0:
        print(f"❌ Error: {step_name} failed with exit code {result.returncode}. Terminating pipeline.")
        sys.exit(result.returncode)
    print(f"✅ Success: {step_name} completed cleanly.")

if __name__ == "__main__":
    print("🏁 Starting Full Autonomous End-to-End Career Pipeline...")
    
    # 1. Gather all active listings across multi-boards
    run_pipeline_step("src/infrastructure/job_discovery.py", "Step 1: Multi-Board Discovery Scraper")
    
    # 2. Filter using Oracle 23ai vectors and log to persistent history memory
    run_pipeline_step("src/agents/Screener_agent.py", "Step 2: Oracle 23ai Vector Screen Agent")
    
    # 3. Compile everything down to your styled analytics workbook
    run_pipeline_step("src/utils/export_excel.py", "Step 3: Executive Excel Workbook Exporter")
    
    print("\n🏆 PIPELINE COMPLETE: Your weekly spreadsheet is fully compiled and ready!")