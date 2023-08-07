# loading the images url to the database
import psycopg2
import json
from BucketUrl import urls

# Load the data
with open('../homeheart-api/medical_professionals_with_bios.json', 'r') as f:
    data = json.load(f)

# Establish connection
conn = psycopg2.connect(
    dbname='homeheart_database',
    user='postgres',
    password='postgres',
    host='localhost'
)
# Create a new cursor
cur = conn.cursor()

# Iterate over professionals and URLs
for i, professional in enumerate(data):
    # Get corresponding URL (cycle through the list of URLs)
    url = urls[i % len(urls)]
    # Update the professional record with the URL
    cur.execute("UPDATE medical_professionals SET image = %s WHERE professional_id = %s",
                (url, professional['professional_id']))

# Commit changes
conn.commit()

# Close cursor and connection
cur.close()
conn.close()
