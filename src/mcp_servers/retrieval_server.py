import array
import os
import json
from mcp.server.fastmcp import FastMCP
import oracledb
from dotenv import load_dotenv
from src.utils.bedrock_guardrail import get_embedding

load_dotenv()

# CRITICAL: Tell Oracle to fetch large text objects (CLOBs) as immediate strings 
# instead of pointers. This prevents DPY-1001 when connections close early.
oracledb.defaults.fetch_lobs = False

# Initialize FastMCP framework
mcp = FastMCP("Resume Retrieval Server")

def query_vector_database(search_vector, limit=3):
    """Queries Oracle 23ai for the closest semantic matches."""
    conn = oracledb.connect(
        user="ADMIN",
        password=os.getenv("DB_PASSWORD"),
        dsn="mcpvectordb_low",
        config_dir="/workspaces/3_cloud_MCP_Project/network/admin",
        wallet_location="/workspaces/3_cloud_MCP_Project/network/admin",
        wallet_password=os.getenv("WALLET_PASSWORD")
    )
    cursor = conn.cursor()
    
    # Oracle 23ai native vector distance calculation using Cosine similarity
    sql = """
        SELECT content, metadata 
        FROM resume_vectors 
        ORDER BY VECTOR_DISTANCE(embedding, :1, COSINE)
        FETCH FIRST :2 ROWS ONLY
    """
    
    # Cast the list into an explicit float array mapping to the database VECTOR data type
    vector_array = array.array('f', search_vector)
    
    cursor.execute(sql, [vector_array, limit])
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return results

@mcp.tool()
def search_resume(query: str) -> str:
    """
    Searches the candidate's professional resume history using AI semantic search.
    Use this tool when a job description requires matching skills or education.
    """
    try:
        # 1. Generate search embedding vector
        search_vector = get_embedding(query)
        
        # 2. Query the vector engine database
        matched_rows = query_vector_database(search_vector, limit=2)
        
        # 3. Format structural output with defensive dict checking
        formatted_results = []
        for row in matched_rows:
            content, meta_json = row
            
            if isinstance(meta_json, dict):
                meta = meta_json
            else:
                meta = json.loads(meta_json.read() if hasattr(meta_json, 'read') else meta_json)
                
            formatted_results.append(f"[{meta.get('type', 'UNKNOWN').upper()}]: {content}")
            
        return "\n\n".join(formatted_results) if formatted_results else "No matching background found."
        
    except Exception as e:
        return f"Error during semantic search: {str(e)}"

if __name__ == "__main__":
    # Serve transport over standard I/O streams for the MCP client handshake
    mcp.run(transport='stdio')