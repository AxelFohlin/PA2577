import os
from flask import Flask, request, jsonify
from db_connection import get_db_connection
import bcrypt

import jwt
import datetime

app = Flask(__name__)

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
