# Use the official MySQL image
FROM mysql:8.0

# Copy the initialization script into the container
COPY init.sql /docker-entrypoint-initdb.d/

# Expose the MySQL default port
EXPOSE 3306
