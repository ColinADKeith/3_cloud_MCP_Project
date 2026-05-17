import os
import json
from dotenv import load_dotenv
from src.mcp_servers.retrieval_server import query_vector_database
from src.utils.bedrock_guardrail import get_embedding

# Load environment variables
load_dotenv()

def run_local_semantic_test(query_string):
    print(f"🧠 Sending query to AWS Bedrock: '{query_string}'")
    try:
        # 1. Convert our search phrase into a 1536-dimension vector
        search_vector = get_embedding(query_string)
        print("✅ Received search vector from AWS Titan.")
        
        # 2. Query Oracle 23ai using Vector Distance math
        print("📡 Querying Oracle 23ai Data Guardian...")
        matched_rows = query_vector_database(search_vector, limit=2)
        
        print("\n🎯 TOP SEMANTIC MATCHES RETRIEVED:")
        print("=" * 60)
        for row in matched_rows:
            content, meta_json = row
            
            # Defensive check: if python-oracledb already parsed the JSON to a dict, use it.
            if isinstance(meta_json, dict):
                meta = meta_json
            else:
                meta = json.loads(meta_json.read() if hasattr(meta_json, 'read') else meta_json)
                
            print(f"Type: {meta.get('type', 'UNKNOWN').upper()}")
            print(f"Content: {content}")
            print("-" * 60)
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    # Test phrase that matches the conceptual context of your stored rows
    run_local_semantic_test("cloud infrastructure experience")