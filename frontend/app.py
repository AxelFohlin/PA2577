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

# Home page with registration and login forms
@app.route('/')
@token_required
def index():
    user_data = session.get('user_id')
    query = request.args.get('query', 'Marvel')  # Default query
    movies = fetch_movies(query)

    return render_template('index.html', movies=movies, query=query, user_id=user_data)

# Route to serve the login page
@app.route('/login')
def serve_login():
    return send_from_directory('static', 'login.html')

# Route to serve the register page
@app.route('/register')
def serve_register():
    return send_from_directory('static', 'register.html')

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
        return render_template('index.html', error=f"Registration failed: {error}")

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
        return render_template('index.html', error=f"Login failed: {error}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
