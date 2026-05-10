import oracledb
import os
import json
from dotenv import load_dotenv
from src.utils.bedrock_guardrail import get_embedding

load_dotenv()

# Example Data - We'll refine this with your actual resume later!
MY_HISTORY = [
    {"text": "IT Student at NBCC specializing in Cloud Infrastructure and AI orchestration.", "type": "education"},
    {"text": "Proficient in Python, SQL, and multi-cloud environment management (AWS, Azure, OCI).", "type": "skill"},
    {"text": "Developed an autonomous agent for automated job application tailoring.", "type": "project"}
]

def ingest_professional_data():
    try:
        # Use your established Wallet connection logic
        conn = oracledb.connect(
            user="ADMIN",
            password=os.getenv("DB_PASSWORD"),
            dsn="mcpvectordb_low",
            config_dir="/workspaces/3_cloud_MCP_Project/network/admin",
            wallet_location="/workspaces/3_cloud_MCP_Project/network/admin",
            wallet_password=os.getenv("WALLET_PASSWORD")
        )
        cursor = conn.cursor()

        for item in MY_HISTORY:
            print(f"🔏 Vectorizing: {item['text'][:40]}...")
            
            # 1. Ask AWS for the math (embedding)
            vector = get_embedding(item['text'])
            
            # 2. Save it to Oracle (sending the vector as a JSON-style list)
            cursor.execute(
                "INSERT INTO resume_vectors (content, metadata, embedding) VALUES (:1, :2, :3)",
                [item['text'], json.dumps({"type": item['type']}), vector]
            )

        conn.commit()
        print(f"\n🚀 SUCCESS: {len(MY_HISTORY)} items are now stored in the Data Guardian.")
        
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Ingestion Failed: {e}")

if __name__ == "__main__":
    ingest_professional_data()