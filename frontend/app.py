import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
import requests
from functools import wraps
import logging

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
app.secret_key = os.getenv("SECRET_KEY", "secret")

# Base URL for the User Management Microservice
USER_SERVICE_URL = "http://user-management-service:5000"


def validate_token() -> bool:
    """Validate JWT token by calling the user-management-service."""
    token = session.get('token')  # Get token from session

    if not token:
        return False

    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{USER_SERVICE_URL}/verify-token", headers=headers)

        if response.status_code == 200:
            return True  # Token is valid
        else:
            return False  # Invalid token
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to user-management-service: {e}")
        return False


def token_required(f):
    """Decorator to require a valid JWT token for protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not validate_token():
            return redirect(url_for('login'))

        return f(*args, **kwargs)
    
    return decorated_function






# Helper function to fetch movies from OMDb API
def fetch_movies(query='Marvel'):
    url = f'http://www.omdbapi.com/?s={query}&apikey={os.getenv("API_KEY")}'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('Search', [])
    return []

def fetch_movie_by_id(imdb_id):
    url = f'http://www.omdbapi.com/?i={imdb_id}&apikey={os.getenv("API_KEY")}'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data
    return None

@app.route('/movie/<movie_id>')
def movie(movie_id):
    # Fetch movie details using the movie_id (imdbID)
    response = requests.get(f'http://www.omdbapi.com/?i={movie_id}&apikey={os.getenv("API_KEY")}')
    movie_data = response.json()

    if movie_data.get('Response') == 'True':
        return render_template('movie_detail.html', movie=movie_data)
    else:
        return f"Movie not found.", 404


@app.route('/favorite', methods=['POST'])
@token_required
def favorite_movie():
    data = request.json
    user_id = data.get('user_id')
    movie_id = data.get('movie_id')
    action = data.get('action')

    if not user_id or not movie_id or not action:
        return jsonify({"message": "Missing required fields"}), 400

    headers = {"Authorization": f"Bearer {session.get('token')}"}
    response = requests.post(f"{USER_SERVICE_URL}/favorite", json={
        "user_id": user_id,
        "movie_id": movie_id,
        "action": action
    }, headers=headers)
    app.logger.debug(f"Response from user-management-service: {response.json()}, {response.status_code}")
    if response.status_code != 200:
        return jsonify({"message": "Failed to add movie to favorites"}), 500

    return jsonify({"message": "Movie added to favorites!"}), 200

@app.route('/favorites')
@token_required
def favorites():
    user_id = session.get('user_id')
    headers = {"Authorization": f"Bearer {session.get('token')}"}
    response = requests.get(f"{USER_SERVICE_URL}/favorites/{user_id}", headers=headers)

    if response.status_code == 200:
        movie_ids = response.json()

        movies = []
        for imdb_id in movie_ids:
            movie = fetch_movie_by_id(imdb_id)
            if movie:
                movies.append(movie)

        return render_template('favorites.html', movies=movies, user_id=user_id, favorite_movies=movie_ids)
    else:
        return jsonify({"message": "Failed to fetch favorites"}), 500

# Home page with registration and login forms
@app.route('/')
@token_required
def index():
    user_id = session.get('user_id')
    query = request.args.get('query', 'Marvel')  # Default query
    movies = fetch_movies(query)
    headers = {"Authorization": f"Bearer {session.get('token')}"}
    response = requests.get(f"{USER_SERVICE_URL}/favorites/{user_id}", headers=headers)
    favorite_movies = response.json() if response.status_code == 200 else []

    app.logger.debug(f"Favorite movies: {favorite_movies}")

    return render_template('index.html', movies=movies, query=query, user_id=user_id, favorite_movies=favorite_movies)

# Route to serve the login page
@app.route('/login')
def serve_login():
    return render_template('login.html')

# Route to serve the register page
@app.route('/register')
def serve_register():
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('token', None)
    return redirect(url_for('login'))

# Handle registration form submission
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']

    # Send registration data to the User Management Microservice
    response = requests.post(f"{USER_SERVICE_URL}/register", json={
        "username": username,
        "password": password,
        "email": email
    })

    if response.status_code == 201:
        return redirect(url_for('index'))
    else:
        error = response.json().get("error", "Unknown error occurred")
        return render_template('register.html', error=f"Registration failed: {error}")

# Handle login form submission
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Send login data to the User Management Microservice
    response = requests.post(f"{USER_SERVICE_URL}/login", json={
        "username": username,
        "password": password
    })

    if response.status_code == 200:
        token = response.headers.get('Authorization')

        session['token'] = token
        session['user_id'] = response.json().get('user_id')

        return redirect(url_for('index'))
    else:
        error = response.json().get("error", "Invalid username or password")
        return render_template('login.html', error=f"Login failed: {error}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
