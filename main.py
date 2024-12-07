import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import pandas as pd
import time

#import the scraper modules
from scraping.tmz_scraper import main as tmz_scraper_main
from scraping.youtube_scraper import main as youtube_scraper_main

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
        image_url TEXT NOT NULL,
        bio TEXT NOT NULL,
        instagram TEXT NOT NULL,
        youtube TEXT NOT NULL
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

#create history table / logic is same as influencer table
def create_vibe_score_history_table(connection):
    print("Creating VibeScoreHistory table...")
    create_table_query = """
    CREATE TABLE IF NOT EXISTS VibeScoreHistory (
        id INT AUTO_INCREMENT PRIMARY KEY,
        influencer_id INT NOT NULL,
        vibe_score DECIMAL(5, 2) NOT NULL,
        recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (influencer_id) REFERENCES Influencers(id) ON DELETE CASCADE
    );
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(create_table_query)
            connection.commit()
    except Error as e:
        print(f"Error creating VibeScoreHistory table: {e}")

#add influencers into the Influencers table
def add_influencers(connection, influencers_data):
    insert_influencer_query = """
    INSERT INTO Influencers (name, image_url, bio, instagram, youtube)
    VALUES (%s, %s, %s, %s, %s)
    """
    check_influencer_query = "SELECT id FROM Influencers WHERE name = %s"

    try:
        with connection.cursor() as cursor:
            for _, row in influencers_data.iterrows():
                #check if influencer already exists
                cursor.execute(check_influencer_query, (row['Name'],))
                result = cursor.fetchone()
                if result is None:
                    #insert the new influencer with all fields
                    cursor.execute(insert_influencer_query, (
                        row['Name'],
                        row['Image_URL'],
                        row['Bio'],
                        row['Instagram'],
                        row['YouTube']
                    ))
                    connection.commit()
                    print(f"Influencer '{row['Name']}' added.")
                else:
                    print(f"Influencer '{row['Name']}' already exists in the database.")
    except Error as e:
        print(f"Error inserting influencers: {e}")

#process influencers.csv file
def process_influencers_csv(connection, file_path):
    print(f"Processing influencers data from: {file_path}")
    data = pd.read_csv(file_path, header=0)                #use cleaned column names
    
    #ensure required columns are present
    required_columns = {'Name', 'Image_URL', 'Bio', 'Instagram', 'YouTube'}
    if required_columns.issubset(data.columns):
        add_influencers(connection, data)
    else:
        print(f"Missing required columns in file: {file_path}")

#some names in youtube channels are different from our database
def add_videos_with_name_mapping(connection, yt_data):
    #define name mapping
    name_mapping = {
        'Diddy': 'P Diddy',
        'The Rock': 'Dwayne Johnson',
        'CaseyNeistat': 'Casey Neistat',
        'PowerfulJRE': 'Joe Rogan',
        'Kai Cenat Live': 'Kai Cenat'
    }
    #apply the name mapping
    yt_data['Name'] = yt_data['Name'].replace(name_mapping)
    insert_videos_query = """
    INSERT INTO Videos (influencer_id, url, title, comment, sentiment_score)
    VALUES (%s, %s, %s, %s, %s)
    """
    check_video_query = """
    SELECT id FROM Videos WHERE url = %s AND comment = %s
    """
    check_influencer_query = "SELECT id FROM Influencers WHERE name = %s"

    try:
        with connection.cursor() as cursor:
            for _, row in yt_data.iterrows():
                #find influencer_id using the mapped name
                cursor.execute(check_influencer_query, (row['Name'],))
                influencer_id = cursor.fetchone()
                if influencer_id:
                    #check if the video and comment already exist
                    cursor.execute(check_video_query, (row['URL'], row['comment']))
                    video_exists = cursor.fetchone()
                    if not video_exists:
                        #insert the new video and comment
                        cursor.execute(insert_videos_query, (
                            influencer_id[0],                                   #ID from the Influencers table
                            row['URL'],
                            row['Title'],
                            row['comment'],
                            None                                                #no sentiment score available yet in this stage
                        ))
                        connection.commit()
                        print(f"Video '{row['Title']}' added for influencer '{row['Name']}'.")
                else:
                    print(f"Influencer '{row['Name']}' not found in the database.")
    except Error as e:
        print(f"Error inserting into Videos table: {e}")

#process the YouTube data CSV, same logic
def process_yt_videos_csv(connection, file_path):
    print(f"Processing YouTube data from: {file_path}")
    data = pd.read_csv(file_path)
    required_columns = {'Name', 'URL', 'Title', 'comment'}
    if required_columns.issubset(data.columns):
        add_videos_with_name_mapping(connection, data)
    else:
        print(f"Missing required columns in file: {file_path}")

#add articles into the News table
def add_news(connection, news_data):
    insert_news_query = """
    INSERT INTO News (influencer_id, url, title, article, sentiment_score)
    VALUES (%s, %s, %s, %s, %s)
    """
    check_influencer_query = "SELECT id FROM Influencers WHERE name = %s"
    check_news_query = "SELECT id FROM News WHERE url = %s"
    try:
        with connection.cursor() as cursor:
            for _, row in news_data.iterrows():
                #find influencer_id using the celebrity name
                cursor.execute(check_influencer_query, (row['Celebrity'],))
                influencer_id = cursor.fetchone()
                
                if influencer_id:
                    #check if the news article already exists
                    cursor.execute(check_news_query, (row['URL'],))
                    news_exists = cursor.fetchone()
                    if not news_exists:
                        #insert the new news article
                        cursor.execute(insert_news_query, (
                            influencer_id[0],                                       #ID from the Influencers table
                            row['URL'],
                            row['Title'],
                            row['Content'],
                            None                                                    #no sentiment score available yet
                        ))
                        connection.commit()
                        print(f"News '{row['Title']}' added for celebrity '{row['Celebrity']}'.")
                else:
                    print(f"Celebrity '{row['Celebrity']}' not found in the database.")
    except Error as e:
        print(f"Error inserting into News table: {e}")

#process the TMZ data CSV, same logic
def process_tmz_news_csv(connection, file_path):
    print(f"Processing TMZ data from: {file_path}")
    data = pd.read_csv(file_path, names=['Celebrity', 'Title', 'URL', 'Content'], header=0)
    required_columns = {'Celebrity', 'Title', 'URL', 'Content'}
    if required_columns.issubset(data.columns):
        add_news(connection, data)
    else:
        print(f"Missing required columns in file: {file_path}")

#populate the Votes table with default values
def populate_votes_table(connection):
    print("Populating Votes table...")
    insert_votes_query = """
    INSERT INTO Votes (influencer_id, good_vote, bad_vote)
    VALUES (%s, %s, %s)
    """
    check_votes_query = """
    SELECT id FROM Votes WHERE influencer_id = %s
    """
    get_influencers_query = """
    SELECT id FROM Influencers
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(get_influencers_query)
            influencers = cursor.fetchall()
            for influencer in influencers:
                influencer_id = influencer[0]
                #check if a row already exists for this influencer
                cursor.execute(check_votes_query, (influencer_id,))
                vote_exists = cursor.fetchone()
                if not vote_exists:
                    #insert a new row with default values for good_vote and bad_vote
                    cursor.execute(insert_votes_query, (influencer_id, 0, 0))
                    connection.commit()
                    print(f"Votes entry created for influencer ID {influencer_id}.")
    except Error as e:
        print(f"Error populating Votes table: {e}")

def update_vibe_score_history(connection):
    try:
        #query to fetch current vibe scores
        fetch_query = "SELECT id, vibe_score FROM Influencers"
        insert_query = """
        INSERT INTO VibeScoreHistory (influencer_id, vibe_score)
        VALUES (%s, %s)
        """

        with connection.cursor() as cursor:
            cursor.execute(fetch_query)
            influencers = cursor.fetchall()

            for influencer in influencers:
                influencer_id, vibe_score = influencer
                cursor.execute(insert_query, (influencer_id, vibe_score))
            
            connection.commit()
            print("Vibe scores updated successfully.")
    
    except Error as e:
        print(f"Error updating vibe score history: {e}")


#main function that runs the scraping files and creates the database and tables
def main():
    #run TMZ scraper
    print("Running TMZ scraper...")
    #tmz_scraper_main()
    #run YouTube scraper
    print("Running YouTube scraper...")
    #youtube_scraper_main()

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
        create_vibe_score_history_table(connection)         #create history table

        #process influencers.csv file and add it to the Influencers table
        process_influencers_csv(connection, "scraping/influencers.csv")
        #populate the Votes table
        populate_votes_table(connection)
        #process youtube .csv file and add it to Videos table
        process_yt_videos_csv(connection, "scraping/yt_scraped.csv")
        #process TMZ data and add it to the News table
        process_tmz_news_csv(connection, "scraping/tmz_scraped.csv")
        update_vibe_score_history(connection)
        
        connection.close()

#check if the script is run directly
if __name__ == "__main__":
    main()