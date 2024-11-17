import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import pandas as pd

#load variables from the .env file
load_dotenv()

#the function can either connect with or without specifying a database
def create_connection(with_database=True):
    connection = None
    try:
        #print connection details for debugging purposes
        #print(f"Attempting to connect to:")
        #print(f"Host: {os.getenv('DB_HOST')}")
        #print(f"User: {os.getenv('DB_USER')}")
        # if with_database:
        #     print(f"Database: {os.getenv('DB_NAME')}")

        #establish connection to the database
        if with_database:
            #if the database is already created, connect with it
            connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASS'),
                database=os.getenv('DB_NAME')
            )
        else:
            #when creating the database - without specifying
            connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASS')
            )
        #debug message
        # print("Successfully connected to the database")
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    return connection

#create the database if it doesn't already exist
def create_database(connection):
    print("Creating database...")
    create_db_query = f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME')};"
    try:
        #create database with SQL query
        with connection.cursor() as cursor:
            cursor.execute(create_db_query)
            print(f"Database '{os.getenv('DB_NAME')}' created or already exists.")
    except Error as e:
        print(f"Error creating database: {e}")

#create influencers table
def create_influencers_table(connection):
    print("Creating influencers table...")
    create_table_query = """
    CREATE TABLE IF NOT EXISTS Influencers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        vibe_score DECIMAL(5, 2) DEFAULT 0.00,
        image_url TEXT NOT NULL
    );
    """
    try:
        #execute query to create table
        with connection.cursor() as cursor:
            cursor.execute(create_table_query)
            connection.commit()  #changes committed to the database
    except Error as e:
        print(f"Error creating influencers table: {e}")

#create content table / logic is same as influencer table
def create_news_table(connection):
    print("Creating news table...")
    create_table_query = """
    CREATE TABLE IF NOT EXISTS News (
        id INT AUTO_INCREMENT PRIMARY KEY,
        influencer_id INT NOT NULL,
        url TEXT NOT NULL,
        title VARCHAR(255),
        article TEXT NOT NULL,
        sentiment_score INT,
        FOREIGN KEY (Influencer_id) REFERENCES Influencers(id) ON DELETE CASCADE
    );
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(create_table_query)
            connection.commit()
    except Error as e:
        print(f"Error creating news table: {e}")

#create comments table / logic is same as influencer table
def create_videos_table(connection):
    print("Creating videos table...")
    create_table_query = """
    CREATE TABLE IF NOT EXISTS Videos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        influencer_id INT NOT NULL,
        url TEXT NOT NULL,
        title VARCHAR(255),
        comment TEXT NOT NULL,
        sentiment_score INT,
        FOREIGN KEY (Influencer_id) REFERENCES Influencers(id) ON DELETE CASCADE
    );
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(create_table_query)
            connection.commit()
    except Error as e:
        print(f"Error creating comments table: {e}")

#create votes table / logic is same as influencer table
def create_votes_table(connection): 
    print("Creating votes table...")
    create_table_query = """
    CREATE TABLE IF NOT EXISTS Votes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        influencer_id INT NOT NULL,
        good_vote INT DEFAULT 0,
        bad_vote INT DEFAULT 0,
        FOREIGN KEY (Influencer_id) REFERENCES Influencers(id) ON DELETE CASCADE
    );
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(create_table_query)
            connection.commit()
    except Error as e:
        print(f"Error creating votes table: {e}")

#add influencers into the Influencers table
def add_influencers(connection, influencers_data):
    insert_influencer_query = """
    INSERT INTO Influencers (name, image_url)
    VALUES (%s, %s)
    """
    check_influencer_query = "SELECT id FROM Influencers WHERE name = %s"

    try:
        with connection.cursor() as cursor:
            for _, row in influencers_data.iterrows():
                #check if influencer already exists
                cursor.execute(check_influencer_query, (row['Name'],))
                result = cursor.fetchone()
                if result is None:
                    #insert the new influencer
                    cursor.execute(insert_influencer_query, (row['Name'], row['Image_URL']))
                    connection.commit()
                    print(f"Influencer '{row['Name']}' added.")
                else:
                    print(f"Influencer '{row['Name']}' already exists.")
    except Error as e:
        print(f"Error inserting influencers: {e}")

#process influencers.csv file
def process_influencers_csv(connection, file_path):
    print(f"Processing influencers data from: {file_path}")
    data = pd.read_csv(file_path, names=['Name', 'Image_URL'], header=0)                #use cleaned column names
    
    #ensure required columns are present
    required_columns = {'Name', 'Image_URL'}
    if required_columns.issubset(data.columns):
        add_influencers(connection, data)
    else:
        print(f"Missing required columns in file: {file_path}")








#main function that creates the database and tables
def main():
    #connect without specifying the database first to see if it doesn't exist
    connection = create_connection(with_database=False)
    if connection:
        create_database(connection)                         #create if it doesn't exist
        connection.close()

    #connect to the created database and create the tables
    connection = create_connection(with_database=True)
    if connection:
        create_influencers_table(connection)                #create influencers table 
        create_news_table(connection)                       #create content table
        create_videos_table(connection)                     #create comments table
        create_votes_table(connection)                      #create votes table

        #process the influencers.csv file and add it
        process_influencers_csv(connection, "scraping/influencers.csv")

        #save the CSV data
        #merged_data = clean_data()

        #insert cleaned data into MySQL
        #add_influencer(connection, merged_data)
        #add_content(connection, merged_data)
        #add_comment(connection, merged_data)
        
        connection.close()

#check if the script is run directly
if __name__ == "__main__":
    main()

