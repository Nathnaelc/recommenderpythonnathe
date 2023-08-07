import boto3

# Create a session using your AWS credentials
session = boto3.Session(
    aws_access_key_id='AKIAXFOQCIPP6CAVTLNO',
    aws_secret_access_key='l2TWd46tK3q4TNtj2W6AbcCiYD+s4MwmEDaWsYiV',
    # change this to 'us-west-2' if your bucket is in US West (Oregon)
    region_name='us-west-1'
)

# Create an S3 resource object using the session
s3 = session.resource('s3')

# Replace 'your-bucket-name' with the name of your bucket
bucket_name = 'homeheart-images'
bucket = s3.Bucket(bucket_name)
# change this to 'us-west-2' if your bucket is in US West (Oregon)
region = 'us-west-1'

# Get the list of objects in the bucket
objects = bucket.objects.all()

# Create a list to store the URLs
urls = []

# Loop over the objects in the bucket
for object in objects:
    # Construct the object URL and append it to the list
    url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{object.key}"
    urls.append(url)

# Now 'urls' is a list of all object URLs in the bucket
print(urls)
