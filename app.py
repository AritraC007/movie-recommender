import streamlit as st
import pickle
import pandas as pd
import requests
import gdown
import os

# Download similarity.pkl from Google Drive if not present
SIMILARITY_FILE = "similarity.pkl"
DRIVE_URL = "https://drive.google.com/uc?id=1GTTYQ3spHQPYXY6LqDXN7fJohg6m9bKI"

if not os.path.exists(SIMILARITY_FILE):
    with st.spinner("Downloading similarity matrix..."):
        gdown.download(DRIVE_URL, SIMILARITY_FILE, quiet=False)

# Load data
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

@st.cache_data
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    try:
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    except:
        pass
    return "https://via.placeholder.com/500x750?text=No+Poster"

def find_index(movie):
    for index, m in movies.iterrows():
        if m['title'] == movie:
            return index
    return -1

def recommend(movie_name):
    index = find_index(movie_name)
    dist = list(enumerate(similarity[index]))
    suggested_movies = sorted(dist, reverse=True, key=lambda x: x[1])[1:6]

    recommended_list = []
    recommended_movie_posters = []

    for m in suggested_movies:
        movie_data = movies.iloc[m[0]]
        recommended_list.append(movie_data.title)
        recommended_movie_posters.append(fetch_poster(movie_data.id))

    return recommended_list, recommended_movie_posters

st.title('🎬Movie Recommendation System')

movie_name = st.selectbox(
    "Select a movie you liked:",
    movies['title'].values
)

if st.button("Recommend", type="primary"):
    recommended_list, posters = recommend(movie_name)

    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.text(recommended_list[i])
            st.image(posters[i])
