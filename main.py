import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Load environment variables from .env file
load_dotenv()

def create_connection(with_database=True):
    connection = None
    try:
        # Print connection details
        print(f"Attempting to connect to:")
        print(f"Host: {os.getenv('DB_HOST')}")
        print(f"User: {os.getenv('DB_USER')}")
        if with_database:
            print(f"Database: {os.getenv('DB_NAME')}")

        # Connect with or without specifying the database
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

        print("Successfully connected to the database")
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        print(f"Error Code: {e.errno}")
        print(f"SQL State: {e.sqlstate}")
        print(f"Error Message: {e.msg}")
    return connection

def create_database(connection):
    print("Creating database...")
    create_db_query = f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME')};"
    try:
        with connection.cursor() as cursor:
            cursor.execute(create_db_query)
            print(f"Database '{os.getenv('DB_NAME')}' created or already exists.")
    except Error as e:
        print(f"Error creating database: {e}")

def create_influencers_table(connection):
    print("Creating influencers table...")
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
    print("Creating content table...")
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
    print("Creating votes table...")
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

def add_influencer(connection):
    name = input("Enter influencer name: ")
    vibe_score = float(input("Enter influencer vibe score: "))

    query = """
    INSERT INTO influencers (name, vibe_score)
    VALUES (%s, %s)
    """
    values = (name, vibe_score)

    try:
        with connection.cursor() as cursor:
            print("Inserting influencer into database...")  # Debugging line
            cursor.execute(query, values)
            connection.commit()
            print(f"Influencer added with ID: {cursor.lastrowid}")
    except Error as e:
        print(f"Error adding influencer: {e}")


def main():
    # Connect without specifying the database first to create it
    connection = create_connection(with_database=False)
    if connection:
        create_database(connection)
        connection.close()

    # Connect with the database specified and create tables
    connection = create_connection(with_database=True)
    if connection:
        create_influencers_table(connection)
        create_content_table(connection)
        create_votes_table(connection)
        
        # Option to manually add sample influencers
        add_influencer(connection)

        connection.close()

if __name__ == "__main__":
    main()