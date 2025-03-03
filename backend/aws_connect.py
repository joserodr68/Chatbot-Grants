import os
import json
from typing import Dict, Optional, List
from dotenv import load_dotenv
import boto3
from datetime import datetime, timedelta
import traceback
from boto3.dynamodb.conditions import Key, Attr

# Load environment variables
load_dotenv()

def get_temporary_credentials(duration: int = 3600):
    """Get temporary AWS credentials."""
    try:
        sts_client = boto3.client("sts")
        response = sts_client.get_session_token(DurationSeconds=duration)
        creds = response["Credentials"]
        return {
            "aws_access_key_id": creds["AccessKeyId"],
            "aws_secret_access_key": creds["SecretAccessKey"],
            "aws_session_token": creds["SessionToken"]
        }
    except Exception as e:
        print(f"Error getting temporary credentials: {e}")
        raise

def get_aws_session():
    """Create and return an AWS session with temporary credentials."""
    temp_creds = get_temporary_credentials()
    return boto3.Session(
        aws_access_key_id=temp_creds["aws_access_key_id"],
        aws_secret_access_key=temp_creds["aws_secret_access_key"],
        aws_session_token=temp_creds["aws_session_token"],
        region_name=os.getenv('AWS_REGION', 'eu-south-2')
    )



def get_bedrock_response(prompt: str):
    """Get response from Bedrock."""
    session = get_aws_session()
    
    bedrock = session.client(
        service_name='bedrock-runtime',
        region_name=os.getenv('AWS_REGION')
    )
    
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 1000,
        "temperature": 0.1
    }
    
    try:
        response = bedrock.invoke_model(
            modelId='eu.anthropic.claude-3-5-sonnet-20240620-v1:0',
            accept='application/json',
            contentType='application/json',
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        return response_body
        
    except Exception as e:
        print(f"Error: {e}")
        return None
    
