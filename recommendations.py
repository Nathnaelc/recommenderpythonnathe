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
db_url = os.getenv(
    'DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/homeheart_database')
# db_url = 'postgresql://postgres:postgres@localhost:5432/homeheart_database'
engine = create_engine(
    db_url)

# Query the database directly and load data into a pandas DataFrame
users = pd.read_sql_table('users', engine)
professionals = pd.read_sql_table('medical_professionals', engine)
# professionals.head()
professionals.columns.tolist()
users.columns.tolist()


# #### The recommender engine using content based filtering

# In[36]:


def get_cosine_sim():
    # For both users and professionals, combine the necessary features into a single string
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


cosine_sim, combined = get_cosine_sim()


def get_recommendations(user_id):
    # For both users and professionals, combine the necessary features into a single string
    users["combined_features"] = users["language_preference"] + \
        " " + users["country_of_origin"]
    professionals["combined_features"] = professionals["language_proficiency"] + " " + \
        professionals["country_of_operation"] + \
        " " + professionals["specialization"]

    # Combine the two dataframes
    combined = pd.concat([users, professionals])

    # Initialize a CountVectorizer (this converts the text to a matrix of token counts)
    count = CountVectorizer()

    # Fit and transform the 'combined_features' of our combined dataframe
    # This step will generate a matrix where each row represents a user/professional
    # and each column represents a word in 'combined_features', the value is the count of that word
    count_matrix = count.fit_transform(combined['combined_features'])

    # Compute the Cosine Similarity matrix based on the count_matrix.
    # Cosine similarity is a measure of similarity between two non-zero vectors of an inner product space
    # that measures the cosine of the angle between them.
    cosine_sim = cosine_similarity(count_matrix, count_matrix)

    # Save your trained model
    with open('model.pkl', 'wb') as file:
        pickle.dump(cosine_sim, file)

    # Get the index of the user who needs recommendations
    idx = combined[combined['user_id'] == user_id].index[0]

    # Get a list of cosine similarity scores for that user with all others
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the list of similarity scores in descending order
    # Each item in sim_scores is a tuple where the first element is an index,
    # and the second is a similarity score
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores for the 10 most similar users/professionals
    # We are excluding the first item because it's the user itself
    sim_scores = sim_scores[1:11]

    # Extract the user/professional indices of these similar users/professionals
    user_prof_indices = [i[0] for i in sim_scores]

    # Return the top 10 most similar users/professionals
    return combined['professional_id'].iloc[user_prof_indices]
