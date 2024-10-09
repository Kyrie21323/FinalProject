import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Load the environment variables from .env file
load_dotenv()

def create_connection(with_database=True):
    connection = None
    try:
        if with_database:
            connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASS'),
                database=os.getenv('DB_NAME')
            )
        else:
            connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASS')
            )
        if connection.is_connected():
            print("Connection successful!")
    except Error as e:
        print(f"Error: {e}")
    return connection

def create_database(connection):
    create_db_query = f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME')};"
    try:
        with connection.cursor() as cursor:
            cursor.execute(create_db_query)
            print(f"Database '{os.getenv('DB_NAME')}' created or already exists.")
    except Error as e:
        print(f"Error creating database: {e}")

def create_influencers_table(connection):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS influencers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        vibe_score DECIMAL(5, 2) DEFAULT 0.00
    );
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(create_table_query)
            connection.commit()
            print("Table 'influencers' created successfully.")
    except Error as e:
        print(f"Error creating influencers table: {e}")

def create_content_table(connection):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS content (
        id INT AUTO_INCREMENT PRIMARY KEY,
        influencer_id INT,
        platform VARCHAR(50),
        url TEXT NOT NULL,
        title VARCHAR(255),
        FOREIGN KEY (influencer_id) REFERENCES influencers(id) ON DELETE CASCADE
    );
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(create_table_query)
            connection.commit()
            print("Table 'content' created successfully.")
    except Error as e:
        print(f"Error creating content table: {e}")

def create_votes_table(connection):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS votes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        influencer_id INT,
        content_id INT,
        vote ENUM('good', 'bad') NOT NULL,
        FOREIGN KEY (influencer_id) REFERENCES influencers(id) ON DELETE CASCADE,
        FOREIGN KEY (content_id) REFERENCES content(id) ON DELETE CASCADE
    );
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(create_table_query)
            connection.commit()
            print("Table 'votes' created successfully.")
    except Error as e:
        print(f"Error creating votes table: {e}")

def add_sample_data(connection):
    sample_influencers = [
        ("John Doe", 4.5),
        ("Jane Smith", 3.8)
    ]
    influencer_query = "INSERT INTO influencers (name, vibe_score) VALUES (%s, %s)"
    
    try:
        with connection.cursor() as cursor:
            cursor.executemany(influencer_query, sample_influencers)
            connection.commit()
            print(f"Inserted {cursor.rowcount} sample influencers.")
    except Error as e:
        print(f"Error inserting influencers: {e}")

    sample_content = [
        (1, "YouTube", "https://youtube.com/video1", "John Doe's Video 1"),
        (2, "Instagram", "https://instagram.com/post1", "Jane Smith's Post 1")
    ]
    content_query = "INSERT INTO content (influencer_id, platform, url, title) VALUES (%s, %s, %s, %s)"
    
    try:
        with connection.cursor() as cursor:
            cursor.executemany(content_query, sample_content)
            connection.commit()
            print(f"Inserted {cursor.rowcount} sample content entries.")
    except Error as e:
        print(f"Error inserting content: {e}")

    sample_votes = [
        (1, 1, "good"),
        (2, 2, "bad")
    ]
    votes_query = "INSERT INTO votes (influencer_id, content_id, vote) VALUES (%s, %s, %s)"
    
    try:
        with connection.cursor() as cursor:
            cursor.executemany(votes_query, sample_votes)
            connection.commit()
            print(f"Inserted {cursor.rowcount} sample votes.")
    except Error as e:
        print(f"Error inserting votes: {e}")

def main():
    connection = create_connection(with_database=False)  # First, connect without a database
    if connection:
        create_database(connection)  # Create the database if it doesn't exist
        connection.close()

    # Connect to the newly created database
    connection = create_connection(with_database=True)
    if connection:
        create_influencers_table(connection)
        create_content_table(connection)
        create_votes_table(connection)
        add_sample_data(connection)
        connection.close()

if __name__ == "__main__":
    main()
