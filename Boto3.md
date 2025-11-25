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

**List All S3 Buckets**
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
**Create EC2 Instance with boto3**
````
import boto3
from botocore.exceptions import ClientError

# --- CONFIGURE YOUR DETAILS ---
REGION = "us-east-1"  # e.g. us-east-1
AMI_ID = "ami-0c02fb55956c7d316"  # Amazon Linux 2 AMI (example)
INSTANCE_TYPE = "t2.micro"  # Free-tier eligible
KEY_NAME = "my-keypair"  # Make sure this key pair already exists
SECURITY_GROUP_ID = "sg-0123456789abcdef0"  # Replace with your security group
SUBNET_ID = "subnet-0123456789abcdef0"  # Optional: specify a subnet

# --- CREATE EC2 CLIENT ---
ec2 = boto3.client("ec2", region_name=REGION)

try:
    print("🚀 Launching EC2 instance...")
    response = ec2.run_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        SecurityGroupIds=[SECURITY_GROUP_ID],
        SubnetId=SUBNET_ID,              # Optional — remove if not needed
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'Name', 'Value': 'MyBoto3Instance'}
                ]
            }
        ]
    )

    instance_id = response["Instances"][0]["InstanceId"]
    print(f"✅ EC2 Instance launched successfully: {instance_id}")

    # --- OPTIONAL: Wait until instance is running ---
    print("⏳ Waiting for the instance to run...")
    waiter = ec2.get_waiter("instance_running")
    waiter.wait(InstanceIds=[instance_id])
    print(f"🟢 Instance {instance_id} is now running.")

except ClientError as e:
    print(f"❌ Error: {e}")
````
