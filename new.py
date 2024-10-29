import ytapi
import mysql.connector
import os
from dotenv import load_dotenv
import pandas as pd
from mysql.connector import Error

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

channel_ids = ['UCX6OQ3DkcsbYNE6H8uQQuVA', 'UCxgAuX3XZROujMmGphN_scA', 'UCqECaJ8Gagnn7YCbPEzWH6g', 'UC0WP5P-ufpRfjbNrmOWwLBQ']

def store_data_in_db(channel_data, comments_data):
    connection = create_connection(with_database=True)
    if connection:
        # Add your database insertion logic here using channel_data and comments_data DataFrames
        connection.close()

def main():
    channel_data_df = ytapi.get_channel_stats(channel_ids)

    for index, row in channel_data_df.iterrows():
        video_title, video_id = ytapi.get_latest_video_link(row['playlist_id'])
        channel_data_df.at[index, 'Title'] = video_title
        channel_data_df.at[index, 'VideoID'] = video_id

        comments_df = ytapi.get_top_comments(video_id)
        
        # Store data in database
        store_data_in_db(channel_data_df, comments_df)

if __name__ == "__main__":
    main()