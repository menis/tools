# @author Sergey Menis w/ a starting template from ChatGPT
# Sample code to update Amazon S3 Lifecycle configuration 
# without overwriting existing rules.
# Example uses put-bucket-lifecycle-configuration.

import sys
import boto3
import json
from botocore.exceptions import ClientError

# Initialize S3 client
s3_client = boto3.client('s3')

def get_lifecycle_policy(bucket_name):
    try:
        # Get the lifecycle configuration of the bucket
        response = s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
        return response['Rules']
    except ClientError as e:
        print(f"Error fetching lifecycle policy: {e}")
        return None

def add_lifecycle_rule(existing_rules, new_rule):
    """Add a new rule to the existing lifecycle configuration"""
    existing_rules.append(new_rule)
    print("Added new rules. Lifecycle policy updated to: ")
    print(existing_rules)
    return existing_rules

def upload_lifecycle_policy(bucket_name, rules):
    try:
        # Create the lifecycle configuration object
        lifecycle_configuration = {
            'Rules': rules
        }
        
        # Set the lifecycle configuration for the bucket
        s3_client.put_bucket_lifecycle_configuration(
            Bucket=bucket_name,
            LifecycleConfiguration=lifecycle_configuration
        )
        print(f"Lifecycle policy successfully updated for bucket {bucket_name}.")
    except ClientError as e:
        print(f"Error uploading lifecycle policy: {e}")

def main():
    if len(sys.argv) < 2:
        print("Please specify a bucket name!")
        sys.exit()
	 	
    bucket_name = sys.argv[1]  # Replace with your bucket name
    print("Fetching lifecycle policy for bucket - "+bucket_name)

    # Step 1: Fetch the current lifecycle rules for the bucket
    existing_rules = get_lifecycle_policy(bucket_name)
    if existing_rules is None:
        print("No existing lifecycle policy found.")
        existing_rules = []
    else:
        print("Existing rules found: ")
        print(existing_rules)

    # Step 2: Define the new lifecycle rule you want to add
    new_rule = {
        "ID": "MoveToIntelligentTieringImmediately",
        "Filter": {
        "Prefix": ""
        },
        "Status": "Enabled",
        "Transitions": [
        {
            "Days": 0,
            "StorageClass": "INTELLIGENT_TIERING"
        }
        ],
        "AbortIncompleteMultipartUpload": {
        "DaysAfterInitiation": 7
        }
    }

    # Step 3: Add the new rule to the existing lifecycle rules
    updated_rules = add_lifecycle_rule(existing_rules, new_rule)

    # Step 4: Upload the updated lifecycle policy to the bucket
    upload_lifecycle_policy(bucket_name, updated_rules)

if __name__ == "__main__":
    main()
 
