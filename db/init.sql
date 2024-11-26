-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS movie_app;

-- Use the database
USE movie_app;

-- Create the user_credentials table
CREATE TABLE IF NOT EXISTS user_credentials (
    user_id INT AUTO_INCREMENT PRIMARY KEY, -- Unique ID for each user
    username VARCHAR(50) NOT NULL UNIQUE,   -- Unique username
    password VARCHAR(255) NOT NULL,         -- Hashed password
    email VARCHAR(100) NOT NULL UNIQUE      -- Unique email
);

-- Create the user_movies table
CREATE TABLE IF NOT EXISTS user_movies (
    user_id INT,                            -- Foreign key to user_credentials
    movie_id VARCHAR(50),                         -- IMDb IDs of favorite movie
    PRIMARY KEY (user_id, movie_id),
    FOREIGN KEY (user_id) REFERENCES user_credentials(user_id)
);

-- Insert sample data into user_credentials
INSERT INTO user_credentials (username, password, email) VALUES
('john_doe', 'hashed_password1', 'john@example.com'),
('jane_smith', 'hashed_password2', 'jane@example.com');

-- Insert sample data into user_movies
-- INSERT INTO user_movies (user_id, favorites) VALUES
-- (1, 'The Matrix,Inception'),
-- (2, 'Titanic,The Notebook');
