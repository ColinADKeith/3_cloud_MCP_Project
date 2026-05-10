import boto3
import json
import os

# Config: Stay under $5.00/month or 100k tokens
TOKEN_LIMIT = 100000 
LOG_FILE = "usage_log.json"

def check_budget():
    if not os.path.exists(LOG_FILE):
        return 0
    with open(LOG_FILE, "r") as f:
        data = json.load(f)
        return data.get("total_tokens", 0)

def call_bedrock_with_guardrail(prompt):
    current_usage = check_budget()
    if current_usage > TOKEN_LIMIT:
        print("🚨 Budget Alert: Bedrock calls suspended to keep you on the Free Tier.")
        return None

    client = boto3.client("bedrock-runtime", region_name="us-east-1")
    response = client.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0", # Check latest free models
        body=json.dumps({"prompt": prompt, "max_tokens": 500})
    )
    
    # Update log (In a real app, send this to your OCI DB!)
    usage = response['ResponseMetadata']['HTTPHeaders'].get('x-amzn-bedrock-tokens', 500)
    with open(LOG_FILE, "w") as f:
        json.dump({"total_tokens": current_usage + int(usage)}, f)
        
    return response

def get_embedding(text):
    """
    Converts text into a 1536-dimension vector using AWS Titan.
    """
    # Uses the AWS credentials from your environment/CLI
    client = boto3.client("bedrock-runtime", region_name="us-east-1")
    
    body = json.dumps({
        "inputText": text
    })
    
    response = client.invoke_model(
        modelId="amazon.titan-embed-text-v1", # The 'Titan' model creates 1536-dim vectors
        body=body
    )
    
    response_body = json.loads(response.get("body").read())
    return response_body.get("embedding")