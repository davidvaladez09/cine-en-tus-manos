# tmdb.py
import requests

API_KEY = '828eade795ef83f55d702745da5ae70e'
BASE_URL = 'https://api.themoviedb.org/3'

def search_movie(movie_name):
    url = f"{BASE_URL}/search/movie"
    params = {
        'api_key': API_KEY,
        'query': movie_name
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data['results']
    return []

def get_movie_details(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {
        'api_key': API_KEY,
        'append_to_response': 'credits'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        movie_details = {
            'nombre': data.get('title'),
            'sipnosis': data.get('overview'),
            'director': ', '.join([crew['name'] for crew in data['credits']['crew'] if crew['job'] == 'Director']),
            'escritor': ', '.join([crew['name'] for crew in data['credits']['crew'] if crew['job'] in ['Writer', 'Screenplay']]),
            'reparto': ', '.join([cast['name'] for cast in data['credits']['cast'][:5]]),
            'ano': data.get('release_date', '').split('-')[0],
            'pais': ', '.join([country['name'] for country in data.get('production_countries', [])]),
            'categoria_genero': ', '.join([genre['name'] for genre in data.get('genres', [])])
        }
        return movie_details
    return {}
