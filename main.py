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
        print(f"Error Code: {e.errno}")
        print(f"SQL State: {e.sqlstate}")
        print(f"Error Message: {e.msg}")
    
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
    CREATE TABLE IF NOT EXISTS influencers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        vibe_score DECIMAL(5, 2) DEFAULT 0.00
    );
    """
    try:
        #execute query to create table
        with connection.cursor() as cursor:
            cursor.execute(create_table_query)
            connection.commit()  #changes committed to the database
            print("Table 'influencers' created successfully.")
    except Error as e:
        print(f"Error creating influencers table: {e}")

#create content table / logic is same as influencer table
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

#create comments table / logic is same as influencer table
def create_comments_table(connection):
    print("Creating comments table...")
    create_table_query = """
    CREATE TABLE IF NOT EXISTS comments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        content_id INT,
        comment_text TEXT NOT NULL,
        sentiment_score DECIMAL(5, 2),
        FOREIGN KEY (content_id) REFERENCES content(id) ON DELETE CASCADE
    );
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(create_table_query)
            connection.commit()
            print("Table 'comments' created successfully.")
    except Error as e:
        print(f"Error creating comments table: {e}")

#create votes table / logic is same as influencer table
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

#read and clean the CSV data - only youtube for now
def clean_data():
    #file paths for the CSV files
    yt_channel_stats_file = 'yt_channel_stats.csv'
    yt_comments_file = 'yt_comments.csv'

    #load CSV files into data frames
    yt_channel_stats_df = pd.read_csv(yt_channel_stats_file)
    yt_comments_df = pd.read_csv(yt_comments_file)

    #clean data - select the needed columns from 'yt_channel_stats.csv'
    yt_channel_stats_cleaned = yt_channel_stats_df[['Name', 'Title', 'URL']].dropna()

    #clean data for comments
    yt_comments_cleaned = yt_comments_df[['comment', 'video_title']].dropna()

    return yt_channel_stats_cleaned, yt_comments_cleaned

#insert influencers into the database / same logic
def insert_influencers(connection, influencers_data):
    insert_query = """
    INSERT INTO influencers (name) 
    VALUES (%s)
    """
    try:
        with connection.cursor() as cursor:
            for _, row in influencers_data.iterrows():
                cursor.execute(insert_query, (row['Name'],))                #only insert the 'Name' field
            connection.commit()
            print("Influencers inserted successfully.")
    except Error as e:
        print(f"Error inserting influencers: {e}")

#insert content into the database
def insert_content(connection, content_data):
    insert_query = """
    INSERT INTO content (influencer_id, platform, url, title) 
    VALUES (%s, %s, %s, %s)
    """
    try:
        with connection.cursor() as cursor:
            for _, row in content_data.iterrows():                                                          #loop through each row in the content data DataFrame
                influencer_id_query = "SELECT id FROM influencers WHERE name = %s"                          #find id according to influencer name
                cursor.execute(influencer_id_query, (row['Name'],))                                         #execute query for current row's 'Name' column and find corresponding influencer ID
                influencer_id = cursor.fetchone()[0]                                                        #fetch first result from the query - the ID of the influencer
                cursor.execute(insert_query, (influencer_id, 'YouTube', row['URL'], row['Title']))          #insert relevant content data to the correct influencer
            connection.commit()
            print("Content inserted successfully.")
    except Error as e:
        print(f"Error inserting content: {e}")


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
        create_content_table(connection)                    #create content table
        create_comments_table(connection)                   #create comments table
        create_votes_table(connection)                      #create votes table

        #clean and save the CSV data to new files
        yt_channel_stats_cleaned, yt_comments_cleaned = clean_data()        #keep the cleaned data alive so that I dont have to read the files again

        #insert cleaned data into MySQL
        insert_influencers(connection, yt_channel_stats_cleaned)
        insert_content(connection, yt_channel_stats_cleaned)

        connection.close()

#check if the script is run directly
if __name__ == "__main__":
    main()
