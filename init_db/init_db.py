import pymysql
import os

# Fetch environment variables
host = os.getenv("MYSQL_HOST", "localhost")
user = os.getenv("MYSQL_USER", "root")
password = os.getenv("MYSQL_ROOT_PASSWORD", "")
database = os.getenv("MYSQL_DATABASE", "my_database")

# Initialization SQL statements
schema = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
seed_data = """
INSERT INTO users (name, email)
VALUES ('John Doe', 'john.doe@example.com');
"""

try:
    # Connect to the database
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = connection.cursor()

    # Execute the schema creation
    cursor.execute(schema)
    print("Schema created successfully!")

    # Seed the data
    cursor.execute(seed_data)
    connection.commit()
    print("Data seeded successfully!")

finally:
    connection.close()
