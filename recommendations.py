# ### Recommendation system for Immigrant users by Python #

# #### installation of packages

# !pip install sqlalchemy
# !pip install pandas
# !pip install psycopg2
# !pip install flask
# !pip install scikit-learn
# help()


# #### Data reading directly from postgres database server
import os
from flask import Flask, request, jsonify
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import create_engine
import pandas as pd

# Establish a connection to the database
# db_url = os.getenv(
#     'DATABASE_URL', 'postgres://postgres:postgres@localhost:5432/homeheart_database')
# engine = create_engine(
#     db_url)
db_url = 'postgresql://homeheart_database_deployed_user:VF6q9xLI3fdc3etWQKg5H8KyoYPfVeK1@dpg-cj8m7q2vvtos73fsf9lg-a.oregon-postgres.render.com/homeheart_database_deployed'
engine = create_engine(db_url)

print('Connected to database!: ', engine.url)
# Query the database directly and load data into a pandas DataFrame

# professionals.head()


# #### The recommender engine using content based filtering
def get_cosine_sim():
    users = pd.read_sql_table('users', engine)
    professionals = pd.read_sql_table('medical_professionals', engine)

    # Fill NaN values with an empty string
    users["language_preference"] = users["language_preference"].fillna('')
    users["country_of_origin"] = users["country_of_origin"].fillna('')
    professionals["language_proficiency"] = professionals["language_proficiency"].fillna(
        '')
    professionals["country_of_operation"] = professionals["country_of_operation"].fillna(
        '')
    professionals["specialization"] = professionals["specialization"].fillna(
        '')

    users['entity_type'] = 'user'
    professionals['entity_type'] = 'professional'
    users.rename(columns={'user_id': 'entity_id'}, inplace=True)
    professionals.rename(
        columns={'professional_id': 'entity_id'}, inplace=True)

    users["combined_features"] = users["language_preference"] + \
        " " + users["country_of_origin"]
    professionals["combined_features"] = professionals["language_proficiency"] + " " + \
        professionals["country_of_operation"] + \
        " " + professionals["specialization"]

    combined = pd.concat([users, professionals], ignore_index=True)

    count = CountVectorizer()
    count_matrix = count.fit_transform(combined['combined_features'])
    cosine_sim = cosine_similarity(count_matrix, count_matrix)

    return cosine_sim, combined


def get_recommendations(user_id):
    cosine_sim, combined = get_cosine_sim()  # Update model on-demand
    user_idx = combined[(combined['entity_id'] == user_id)
                        & (combined['entity_type'] == 'user')].index

    if len(user_idx) == 0:
        # User not found in the combined DataFrame, return an appropriate message or an empty list
        return {'message': 'User not found'}, 404

    idx = user_idx[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:20]
    user_prof_indices = [i[0] for i in sim_scores]

    # Filter the results to include only professionals
    recommended_professionals = combined.loc[user_prof_indices]
    recommended_professionals = recommended_professionals[
        recommended_professionals['entity_type'] == 'professional']

    return recommended_professionals['entity_id']
