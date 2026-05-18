import os
import sys

# CRITICAL PATH PATCH: Force Python to recognize the workspace root directory.
root_workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if root_workspace not in sys.path:
    sys.path.insert(0, root_workspace)

import json
import array
import oracledb
from dotenv import load_dotenv
from src.utils.bedrock_guardrail import get_embedding

load_dotenv()
oracledb.defaults.fetch_lobs = False

def get_closest_resume_match(job_description_vector):
    """Queries Oracle 23ai to find the single closest resume chunk and its distance score."""
    conn = oracledb.connect(
        user="ADMIN",
        password=os.getenv("DB_PASSWORD"),
        dsn="mcpvectordb_low",
        config_dir="/workspaces/3_cloud_MCP_Project/network/admin",
        wallet_location="/workspaces/3_cloud_MCP_Project/network/admin",
        wallet_password=os.getenv("WALLET_PASSWORD")
    )
    cursor = conn.cursor()
    
    sql = """
        SELECT content, VECTOR_DISTANCE(embedding, :1, COSINE) as dist
        FROM resume_vectors 
        ORDER BY dist
        FETCH FIRST 1 ROWS ONLY
    """
    
    vector_array = array.array('f', job_description_vector)
    cursor.execute(sql, [vector_array])
    row = cursor.fetchone()
    
    cursor.close()
    conn.close()
    return row if row else (None, 2.0)

def load_json_file(file_path, default_value):
    """Safely utility to load JSON files without crashing if they don't exist yet."""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return default_value
    return default_value

def screen_discovered_jobs():
    input_path = "data/discovered_jobs.json"
    output_path = "data/qualified_jobs.json"
    history_path = "data/processed_history.json"
    
    if not os.path.exists(input_path):
        print(f"❌ Error: Missing '{input_path}'. Run discovery first!")
        return
        
    raw_discovered = load_json_file(input_path, [])
    existing_qualified = load_json_file(output_path, [])
    historical_ledger = load_json_file(history_path, [])
    
    processed_ids = set(historical_ledger)
    fresh_unseen_jobs = [j for j in raw_discovered if j.get("job_id") not in processed_ids]
    
    skipped_count = len(raw_discovered) - len(fresh_unseen_jobs)
    print(f"🧠 Persistent Memory: Identified {skipped_count} previously processed jobs. Skipping to prevent API duplication.")
    print(f"🕵️ Screen Agent inspecting {len(fresh_unseen_jobs)} brand-new targets against your vector profile...\n")
    
    if not fresh_unseen_jobs:
        print("📭 No new unique listings to evaluate this cycle.")
        return

    new_qualified_matches = []
    MATCH_THRESHOLD = 0.55
    
    for job in fresh_unseen_jobs:
        title = job.get("title")
        company = job.get("company")
        desc = job.get("description", "")
        job_id = job.get("job_id")
        
        try:
            job_vector = get_embedding(desc[:1000])
            best_chunk, distance_score = get_closest_resume_match(job_vector)
            
            is_match = distance_score <= MATCH_THRESHOLD
            status_icon = "✅ [NEW MATCH]" if is_match else "❌ [NEW SKIP]"
            
            print(f"{status_icon} '{title}' at {company}")
            print(f"   ├─ Semantic Distance: {distance_score:.4f}")
            
            if is_match:
                job["semantic_distance"] = distance_score
                new_qualified_matches.append(job)
                
            historical_ledger.append(job_id)
            print("-" * 70)
            
        except Exception as e:
            print(f"⚠️ Failed to screen '{title}': {e}")
            
    cumulative_qualified = existing_qualified + new_qualified_matches
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cumulative_qualified, f, indent=4, ensure_ascii=False)
        
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(historical_ledger, f, indent=4, ensure_ascii=False)
        
    print(f"\n🎯 Screening complete! Appended {len(new_qualified_matches)} new matches.")
    print(f"📁 Cumulative tracking pipeline now holds {len(cumulative_qualified)} deduplicated records.")

if __name__ == "__main__":
    screen_discovered_jobs()