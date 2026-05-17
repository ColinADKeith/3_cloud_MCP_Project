import os
import json
import array
import oracledb
from dotenv import load_dotenv
from src.utils.bedrock_guardrail import get_embedding

load_dotenv()

# Ensure Oracle fetches CLOBs/JSON text immediately as standard strings
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
    
    # Select content and calculate the exact Cosine distance
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

def screen_discovered_jobs():
    input_path = "data/discovered_jobs.json"
    output_path = "data/qualified_jobs.json"
    
    if not os.path.exists(input_path):
        print(f"❌ Error: Missing '{input_path}'. Run discovery first!")
        return
        
    with open(input_path, "r", encoding="utf-8") as f:
        jobs = json.load(f)
        
    print(f"🕵️ Automated Screener inspecting {len(jobs)} targets against your Oracle vector profile...\n")
    
    qualified_pipeline = []
    
    # Semantic Threshold: Cosine distance ranges from 0 (identical) to 2 (opposite).
    # A distance under 0.55 indicates a strong conceptual overlap with your skills.
    MATCH_THRESHOLD = 0.55
    
    for job in jobs:
        title = job.get("title")
        company = job.get("company")
        desc = job.get("description", "")
        
        # 1. Vectorize the job requirements using AWS Bedrock Titan
        try:
            # We look at the first 1000 characters of the description to grab core requirements
            job_vector = get_embedding(desc[:1000])
            
            # 2. Measure the distance against your resume in Oracle 23ai
            best_chunk, distance_score = get_closest_resume_match(job_vector)
            
            # 3. Evaluate matching criteria
            is_match = distance_score <= MATCH_THRESHOLD
            status_icon = "✅ [MATCH]" if is_match else "❌ [SKIP]"
            
            print(f"{status_icon} '{title}' at {company}")
            print(f"   ├─ Semantic Distance: {distance_score:.4f}")
            if is_match:
                print(f"   └─ Closest Match: {best_chunk[:75]}...")
                # Append matching score to tracking data
                job["semantic_distance"] = distance_score
                qualified_pipeline.append(job)
            print("-" * 70)
            
        except Exception as e:
            print(f"⚠️ Failed to screen '{title}': {e}")
            
    # 4. Save the qualified pipeline target manifest
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(qualified_pipeline, f, indent=4, ensure_ascii=False)
        
    print(f"\n🎯 Screening complete! Saved {len(qualified_pipeline)} qualified targets to '{output_path}'.")

if __name__ == "__main__":
    screen_discovered_jobs()