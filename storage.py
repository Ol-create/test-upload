import os
import boto3
from botocore.exceptions import NoCredentialsError

# DO NOT HARDCODE KEYS HERE
# AWS_ACCESS_KEY_ID = "AKIA..." # <--- REMOVE HARDCODED KEYS
# AWS_SECRET_ACCESS_KEY = "xyz/..." # <--- REMOVE HARDCODED KEYS

def get_s3_client():
    """Initializes and returns an S3 client using environment variables."""
    # Boto3 automatically looks for AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY 
    # in the environment (which App Runner provides via IAM Role or its variables).
    # If the variables are not set, it will automatically use the Instance Role.
    return boto3.client(
        's3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
    )

def upload_audio(file_path: str, user_id: str, filename: str) -> str:
    s3_client = get_s3_client()
    bucket_name = os.environ.get('S3_BUCKET_NAME')

    if not bucket_name:
        raise EnvironmentError("S3_BUCKET_NAME environment variable is not set.")

    # Create a path specific to the user
    object_name = f"audio/{user_id}/{filename}"
    
    try:
        s3_client.upload_file(file_path, bucket_name, object_name)
        # Return the public/internal URI for the file
        s3_uri = f"s3://{bucket_name}/{object_name}"
        return s3_uri
    except NoCredentialsError:
        raise Exception("AWS credentials not available or insufficient permissions.")
    except Exception as e:
        raise Exception(f"S3 upload failed: {e}")
