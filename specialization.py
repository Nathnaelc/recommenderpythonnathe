import random
import psycopg2
qualifications = [
    "PhD in Clinical Psychology",
    "Master's in Counseling",
    "PsyD in School Psychology",
    "Master's in Social Work",
    "PhD in Psychiatry",
    "MD specializing in Psychiatry",
    "Certificate in Addiction Counseling",
    "Master's in Marriage and Family Therapy",
]


# Connect to your postgres DB
conn = psycopg2.connect(
    dbname='homeheart_database',
    user='postgres',
    password='postgres',
    host='localhost'
)

# Open a cursor to perform database operations
cur = conn.cursor()

# Fetch all rows from the medical_professionals table
cur.execute("SELECT * FROM medical_professionals")

rows = cur.fetchall()
for row in rows:
    # Randomly choose a qualification
    qualification = random.choice(qualifications)

    # Update the qualification field
    cur.execute(
        "UPDATE medical_professionals SET qualification = %s WHERE professional_id = %s",
        # replace 0 with the correct index of 'professional_id' in your table
        (qualification, row[0])
    )


# Make the changes to the database persistent
conn.commit()

# Close communication with the database
cur.close()
conn.close()
print("Done!")
