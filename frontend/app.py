from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests

app = Flask(__name__)

# Base URL for the User Management Microservice
USER_SERVICE_URL = "http://user-management-service:5000"

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
        user_id = response.json().get("user_id")
        return render_template('success.html', message=f"Login successful! User ID: {user_id}")
    else:
        error = response.json().get("error", "Invalid username or password")
        return render_template('index.html', error=f"Login failed: {error}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
