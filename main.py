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

#read and clean CSV data - only youtube for now
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

#add influencers into database
def add_influencer(connection, influencer_data):
    #check if an influencer exists
    check_influencer_query = "SELECT id FROM influencers WHERE name = %s"

    #insert the new influencer
    insert_influencer_query = """
    INSERT INTO influencers (name)
    VALUES (%s)
    """

    try:
        with connection.cursor() as cursor:
            for _, row in influencer_data.iterrows():
                # Check if already exists
                cursor.execute(check_influencer_query, (row['Name'],))
                result = cursor.fetchone()

                if result is None:
                    #if it doesn't, insert
                    cursor.execute(insert_influencer_query, (row['Name'],))
                    connection.commit()
                    print(f"Influencer '{row['Name']}' added.")
                else:
                    #if it does, print message
                    print(f"Influencer '{row['Name']}' already exists with ID: {result[0]}")

    except Error as e:
        print(f"Error inserting influencers: {e}")

#add content into database / checking for existing logic is same as add_influencer
def add_content(connection, content_data):
    #check if the content exists
    check_content_query = "SELECT id FROM content WHERE url = %s"

    #insert new content
    insert_content_query = """
    INSERT INTO content (influencer_id, platform, url, title) 
    VALUES (%s, %s, %s, %s)
    """
    try:
        with connection.cursor() as cursor:
            for _, row in content_data.iterrows():
                #check if content exists
                cursor.execute(check_content_query, (row['URL'],))
                result = cursor.fetchone()
                if result is None:
                    influencer_id_query = "SELECT id FROM influencers WHERE name = %s"
                    cursor.execute(influencer_id_query, (row['Name'],))
                    influencer_id = cursor.fetchone()
                    if influencer_id:
                        cursor.execute(insert_content_query, (influencer_id[0], "YouTube", row['URL'], row['Title']))
                        connection.commit()
                        print(f"Content '{row['Title']}' added for influencer '{row['Name']}'.")
                    else:
                        print(f"Influencer '{row['Name']}' not found for content '{row['Title']}'.")
                else:
                    print(f"Content '{row['Title']}' already exists with ID: {result[0]}")

    except Error as e:
        print(f"Error inserting content: {e}")

#add comments into database / checking for existing logic is same as add_influencer
def add_comment(connection, comment_data):
    check_comment_query = "SELECT id FROM comments WHERE comment_text = %s AND content_id = %s"

    insert_comment_query = """
    INSERT INTO comments (content_id, comment_text)
    VALUES (%s, %s)
    """

    try:
        with connection.cursor() as cursor:
            for _, row in comment_data.iterrows():
                content_id_query = "SELECT id FROM content WHERE title = %s"
                cursor.execute(content_id_query, (row['video_title'],))
                content_id = cursor.fetchone()
                if content_id:
                    cursor.execute(check_comment_query, (row['comment'], content_id[0]))
                    result = cursor.fetchone()
                    if result is None:
                        cursor.execute(insert_comment_query, (content_id[0], row['comment']))
                        connection.commit()
                        print(f"Comment added for content ID {content_id[0]}.")
                    else:
                        print(f"Comment already exists for content ID {content_id[0]}.")
                else:
                    print(f"Content '{row['video_title']}' not found for comment '{row['comment']}'.")

    except Error as e:
        print(f"Error inserting comments: {e}")

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
        add_influencer(connection, yt_channel_stats_cleaned)
        add_content(connection, yt_channel_stats_cleaned)
        add_comment(connection, yt_comments_cleaned)
        
        connection.close()

#check if the script is run directly
if __name__ == "__main__":
    main()

