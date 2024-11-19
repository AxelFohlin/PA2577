import mysql.connector
import os

def get_db_connection():
    """Establish and return a database connection."""
    try:
        # Read database credentials from environment variables
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "rootpassword"),
            database=os.getenv("DB_NAME", "movie_app")
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
