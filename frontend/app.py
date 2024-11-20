import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import requests
from functools import wraps
import logging

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
app.secret_key = os.getenv("SECRET_KEY", "secret")

# Base URL for the User Management Microservice
USER_SERVICE_URL = "http://user-management-service:5000"

print(os.getenv("API_KEY", "no"))


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
            return jsonify({"error": "Invalid or expired token!"}), 401

        return f(*args, **kwargs)
    
    return decorated_function


# Home page with registration and login forms
@app.route('/')
def index():
    return render_template('index.html')

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
        return render_template('success.html', message="Registration successful!")
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

        return redirect(url_for('dashboard'))
    else:
        error = response.json().get("error", "Invalid username or password")
        return render_template('index.html', error=f"Login failed: {error}")


@app.route('/dashboard')
@token_required
def dashboard():
    user_data = session.get('user_id')
    return jsonify({"message": "Welcome to the dashboard!", "user_id": user_data})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
