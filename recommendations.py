# ### Recommendation system for Immigrant users by Python #

# #### installation of packages

# !pip install sqlalchemy
# !pip install pandas
# !pip install psycopg2
# !pip install flask
# !pip install scikit-learn
# help()


# #### Data reading directly from postgres database server
# ### Recommendation system for Immigrant users by Python ###

from apscheduler.schedulers.background import BackgroundScheduler
import os
from sqlalchemy import create_engine
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
# Database connection URL
db_url = 'postgresql://homeheart_database_deployed_user:VF6q9xLI3fdc3etWQKg5H8KyoYPfVeK1@dpg-cj8m7q2vvtos73fsf9lg-a.oregon-postgres.render.com/homeheart_database_deployed'
engine = create_engine(db_url)

# Global variables
cosine_sim = None
combined = None


def update_data():
    global cosine_sim, combined, users, professionals
    # Query the database directly and load data into a pandas DataFrame
    users = pd.read_sql_table('users', engine)
    professionals = pd.read_sql_table('medical_professionals', engine)
    cosine_sim, combined = get_cosine_sim(users, professionals)


def get_cosine_sim(users, professionals):
    # Fill NaN values with an empty string
    users["language_preference"] = users["language_preference"].fillna('')
    users["country_of_origin"] = users["country_of_origin"].fillna('')
    professionals["language_proficiency"] = professionals["language_proficiency"].fillna(
        '')
    professionals["country_of_operation"] = professionals["country_of_operation"].fillna(
        '')
    professionals["specialization"] = professionals["specialization"].fillna(
        '')

    users["combined_features"] = users["language_preference"] + \
        " " + users["country_of_origin"]
    professionals["combined_features"] = professionals["language_proficiency"] + " " + \
        professionals["country_of_operation"] + \
        " " + professionals["specialization"]

    # Combine the two dataframes
    combined = pd.concat([users, professionals], ignore_index=True)

    # Initialize a CountVectorizer (this converts the text to a matrix of token counts)
    count = CountVectorizer()

    # Fit and transform the 'combined_features' of our combined dataframe
    count_matrix = count.fit_transform(combined['combined_features'])

    # Compute the Cosine Similarity matrix based on the count_matrix.
    cosine_sim = cosine_similarity(count_matrix, count_matrix)

    # Save your trained model
    with open('model.pkl', 'wb') as file:
        pickle.dump(cosine_sim, file)

    return cosine_sim, combined


def get_recommendations(user_id):
    global cosine_sim, combined

    # Combining features
    users["combined_features"] = users["language_preference"] + \
        " " + users["country_of_origin"]
    professionals["combined_features"] = professionals["language_proficiency"] + " " + \
        professionals["country_of_operation"] + \
        " " + professionals["specialization"]

    # Combining dataframes
    combined = pd.concat([users, professionals])

    # Initializing CountVectorizer
    count = CountVectorizer()

    # Fitting and transforming combined features
    count_matrix = count.fit_transform(combined['combined_features'])

    # Computing Cosine Similarity matrix
    cosine_sim = cosine_similarity(count_matrix, count_matrix)

    # Getting the index of the user
    idx = combined[combined['user_id'] == user_id].index[0]

    # Getting similarity scores
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]

    # Extracting indices
    user_prof_indices = [i[0] for i in sim_scores]

    # Returning professional IDs
    return combined['professional_id'].iloc[user_prof_indices]


# Initial update
update_data()

# Scheduling the update_data function to be called every second
scheduler = BackgroundScheduler()
scheduler.add_job(update_data, 'interval', seconds=1)
scheduler.start()
