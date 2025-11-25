**pip install boto3[crt]**
**aws configure**

````
import boto3
# Let's use Amazon S3
s3 = boto3.resource('s3')
# Print out bucket names
for bucket in s3.buckets.all():
    print(bucket.name)
````

**Python Script: List All S3 Buckets**
````
import boto3
from botocore.exceptions import ClientError

# --- CREATE S3 CLIENT ---
s3 = boto3.client('s3')

try:
    print("📦 Fetching list of all S3 buckets...")
    response = s3.list_buckets()

    buckets = response.get('Buckets', [])

    if buckets:
        print("✅ Your S3 Buckets:")
        for bucket in buckets:
            print(f" - {bucket['Name']} (Created on: {bucket['CreationDate']})")
    else:
        print("⚠️ No buckets found in your account.")

except ClientError as e:
    print(f"❌ Error: {e}")
````
