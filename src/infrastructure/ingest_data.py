import array  # <-- CRITICAL: Needed for Oracle Vector mapping
import oracledb
import os
import json
from dotenv import load_dotenv
from src.utils.bedrock_guardrail import get_embedding

load_dotenv()

# Placeholder data
MY_HISTORY = [
    {"text": "IT Student at NBCC specializing in Cloud Infrastructure.", "type": "education"},
    {"text": "Experienced in SQL and multi-cloud management (AWS, Azure, OCI).", "type": "skill"},
    {"text": "Developed an autonomous agent for automated job applications.", "type": "project"}
]

def ingest_professional_data():
    try:
        # Using your established Wallet connection
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
            print(f"🔏 Vectorizing: {item['text'][:30]}...")
            # 1. Ask AWS for the math
            vector = get_embedding(item['text'])
            
            # 2. Convert to a Python float array so python-oracledb treats it as a VECTOR
            vector_array = array.array('f', vector) # 'f' stands for 32-bit floating point
            
            # 3. Save it to Oracle 23ai
            cursor.execute(
                "INSERT INTO resume_vectors (content, metadata, embedding) VALUES (:1, :2, :3)",
                [item['text'], json.dumps({"type": item['type']}), vector_array]
            )

        conn.commit()
        print(f"\n🚀 SUCCESS: {len(MY_HISTORY)} items stored in the Data Guardian.")
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Ingestion Failed: {e}")

if __name__ == "__main__":
    ingest_professional_data()