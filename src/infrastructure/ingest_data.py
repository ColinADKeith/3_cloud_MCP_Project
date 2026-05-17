import array
import os
import json
import re
import oracledb
from pypdf import PdfReader
from dotenv import load_dotenv
from src.utils.bedrock_guardrail import get_embedding

load_dotenv()

def extract_chunks_from_pdf(pdf_path):
    """Reads a PDF, repairs broken PDF line wraps, and groups text into logical chunks."""
    print(f"📖 Reading document content from: {pdf_path}")
    reader = PdfReader(pdf_path)
    raw_lines = []
    
    # 1. Pull lines and filter out empty spacing
    for page in reader.pages:
        text = page.extract_text()
        if text:
            for line in text.split('\n'):
                cleaned_line = line.strip()
                if cleaned_line:
                    raw_lines.append(cleaned_line)
                    
    chunks = []
    current_chunk = ""
    
    # 2. Process lines intelligently
    for line in raw_lines:
        # If a line starts with a bullet point or looks like a header, close the previous chunk
        if line.startswith('•') or line.startswith('-') or re.match(r'^[A-Z][A-Za-z\s]{3,20}:$', line):
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = line
        else:
            # Otherwise, append it with a space to heal mid-sentence line breaks
            if current_chunk:
                # If the previous word didn't end with a space, add one
                current_chunk += " " + line
            else:
                current_chunk = line
                
        # If the chunk gets reasonably comprehensive, cycle it out
        if len(current_chunk) >= 200 and (current_chunk.endswith('.') or current_chunk.endswith(';')):
            chunks.append(current_chunk.strip())
            current_chunk = ""
            
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    # Filter out any lingering fragments under 30 characters
    return [c for c in chunks if len(c) > 30]

def ingest_professional_data():
    pdf_filename = "resume.pdf"
    
    if not os.path.exists(pdf_filename):
        print(f"❌ Error: Could not find '{pdf_filename}' in your root directory.")
        return

    try:
        # Extract dynamic, context-healed chunks from your uploaded PDF
        resume_chunks = extract_chunks_from_pdf(pdf_filename)
        print(f"🧩 Successfully split resume into {len(resume_chunks)} clean semantic chunks.\n")

        # Open connection to the Data Guardian
        conn = oracledb.connect(
            user="ADMIN",
            password=os.getenv("DB_PASSWORD"),
            dsn="mcpvectordb_low",
            config_dir="/workspaces/3_cloud_MCP_Project/network/admin",
            wallet_location="/workspaces/3_cloud_MCP_Project/network/admin",
            wallet_password=os.getenv("WALLET_PASSWORD")
        )
        cursor = conn.cursor()

        # Clear out previous fragmented data
        print("🧹 Clearing fragmented placeholder data from table...")
        cursor.execute("TRUNCATE TABLE resume_vectors")

        for index, text_chunk in enumerate(resume_chunks):
            print(f"🔏 Vectorizing chunk [{index + 1}/{len(resume_chunks)}]: {text_chunk[:50]}...")
            
            # 1. Generate high-fidelity embedding vector
            vector = get_embedding(text_chunk)
            
            # 2. Cast to array type for driver handling
            vector_array = array.array('f', vector)
            
            # 3. Apply structural metadata tags
            metadata = {"source": "uploaded_pdf", "type": "experience_profile"}
            
            # 4. Commit to Oracle 23ai
            cursor.execute(
                "INSERT INTO resume_vectors (content, metadata, embedding) VALUES (:1, :2, :3)",
                [text_chunk, json.dumps(metadata), vector_array]
            )

        conn.commit()
        print(f"\n🚀 SUCCESS: Your resume has been re-vectorized with complete semantic context!")
        
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Ingestion Failed: {e}")

if __name__ == "__main__":
    ingest_professional_data()