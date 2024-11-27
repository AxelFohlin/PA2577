import os
from flask import Flask, request, jsonify
from db_connection import get_db_connection
import bcrypt
from functools import wraps
import logging

import jwt
import datetime

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

if os.getenv("SECRET_KEY", "no") == "no":
    raise ValueError("No SECRET_KEY set for user-management")

def generate_token(user_id, username):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    token = jwt.encode(
        {"user_id": user_id, "username": username, "exp": expiration},
        os.getenv("SECRET_KEY"),
        algorithm="HS256"
    )
    return token

def verify_token(token):
    app.logger.debug(f"Verifying token: {token}")
    try:
        # Decode the token using the secret key
        decoded_token = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
        return decoded_token  # Return the decoded token (user info)
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Invalid token

@app.route('/verify-token')
def verify():
    token = request.headers.get('Authorization')

    token = token.replace("Bearer ", "")

    # Verify the token
    user = verify_token(token)
    if user:
        return jsonify({"message": "Token is valid"}), 200
    else:
        return jsonify({"error": "Invalid token"}), 401

def token_required(f):
    """Decorator to require a valid JWT token for protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not verify_token(request.headers.get('Authorization').replace("Bearer ", "")):
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    
    return decorated_function


@app.route('/favorite', methods=['POST'])
@token_required
def toggle_favorite():
    data = request.json
    user_id = data.get('user_id')
    movie_id = data.get('movie_id')
    action = data.get('action')

    db = get_db_connection()
    cursor = db.cursor()
    try:
        if action == 'add':
            # Add movie to user's favorites
            cursor.execute(
                "INSERT INTO user_movies (user_id, movie_id) VALUES (%s, %s)",
                (user_id, movie_id)
            )
            db.commit()
            return jsonify({"message": "Movie favorited successfully"}), 200
        elif action == 'remove':
            # Remove movie from user's favorites
            cursor.execute(
                "DELETE FROM user_movies WHERE user_id = %s AND movie_id = %s",
                (user_id, movie_id)
            )
            db.commit()
            return jsonify({"message": "Movie unfavorited successfully"}), 200
        else:
            return jsonify({"error": "Invalid action"}), 400
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        db.close()

@app.route('/favorites/<int:user_id>')
@token_required
def get_user_favorites(user_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT movie_id FROM user_movies WHERE user_id = %s", (user_id,)
        )
        favorite_movies = cursor.fetchall()
    
        favorite_movie_ids = [movie['movie_id'] for movie in favorite_movies]

        return jsonify(favorite_movie_ids), 200
    except Exception as e:
        # Handle errors and return a failure response
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        db.close()

# Endpoint for user registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    email = data['email']

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Insert user into the database
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO user_credentials (username, password, email) VALUES (%s, %s, %s)",
            (username, hashed_password, email)
        )
        db.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        db.close()

# Endpoint for user login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    # Verify user credentials
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM user_credentials WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            token = generate_token(user['user_id'], user['username'])
            # Return the token in the header and a response body with a message
            response = jsonify({"message": "Login successful", "user_id": user['user_id']})
            response.status_code = 200
            response.headers['Authorization'] = f'Bearer {token}'
            return response
        else:
            return jsonify({"error": "Invalid username or password"}), 401
    finally:
        cursor.close()
        db.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
