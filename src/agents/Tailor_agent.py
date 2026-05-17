import os
import json
import boto3
from dotenv import load_dotenv
from src.mcp_servers.retrieval_server import search_resume

load_dotenv()

def call_bedrock_llm(prompt):
    """Calls AWS Bedrock Converse API with Amazon Nova Lite to generate responses."""
    client = boto3.client("bedrock-runtime", region_name="us-east-1")
    
    # Using the standardized Converse API instead of raw invoke_model payloads
    response = client.converse(
        modelId="amazon.nova-lite-v1:0",
        messages=[
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ],
        inferenceConfig={
            "maxTokens": 512,
            "temperature": 0.3,
            "topP": 0.9
        }
    )
    
    # Extract the clean generated text from the Converse structured response
    return response["output"]["message"]["content"][0]["text"]

def tailor_application_profile(job_description):
    print("🎯 Step 1: Analyzing the job description requirements...")
    
    # Target themes matching your professional data
    search_query = "Python SQL data pipelines cloud predictive models"
    
    print("📡 Step 2: Fetching matching semantic context from Oracle 23ai...")
    retrieved_context = search_resume(search_query)
    
    print("🧠 Step 3: Orchestrating layout via AWS Bedrock...")
    orchestration_prompt = f"""
    You are an expert career agent. You are helping a candidate tailor their professional profile summary for a specific job application.
    
    TARGET JOB DESCRIPTION:
    {job_description}
    
    CANDIDATE'S SEMANTICALLY MATCHED EXPERIENCE ROWS FROM DATABASE:
    {retrieved_context}
    
    INSTRUCTION:
    Write a high-impact, 3-4 sentence professional profile summary tailored specifically to the job description above. 
    Only use facts present in the candidate's matched experience rows. Make it compelling, professional, and concise.
    """
    
    tailored_summary = call_bedrock_llm(orchestration_prompt)
    return tailored_summary

if __name__ == "__main__":
    # Sample target job description matching your profile metrics
    SAMPLE_JOB = """
    We are seeking an Analyst who can manage massive datasets and construct automated pipelines. 
    The ideal candidate has exceptional skills in Python and SQL database environments, with an interest in deploying data models.
    """
    
    print("🚀 Launching Autonomous Tailoring Agent Loop...\n")
    result = tailor_application_profile(SAMPLE_JOB)
    
    print("\n📝 GENERATED PROFESSIONAL SUMMARY FOR APPLICATION:")
    print("=" * 60)
    print(result.strip())
    print("=" * 60)