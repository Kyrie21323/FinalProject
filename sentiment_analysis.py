# sentiment analysis using TextBlob

# import the required libraries
from textblob import TextBlob
import os
import pandas as pd
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import update, MetaData, Table
load_dotenv()

# first we going to get the data from our database using the sqlalchemy.
# creating a connection to the database.
engine = sqlalchemy.create_engine(f'mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}@{os.getenv("DB_HOST")}/{os.getenv("DB_NAME")}')

News = pd.read_sql_table('News', engine)

# we are going to use the TextBlob library to perform sentiment analysis on the news articles.
# we are going to create a function that will take the news article as input and return the sentiment of the article.
# Define a function to assign sentiment scores based on polarity
def assign_score(polarity):
    if polarity > 0:
        return round(5 + (5 * polarity))  # Scale from 6 to 10 for positive sentiments
    elif polarity < 0:
        return round(5 * polarity) + 5    # Scale from 1 to 4 for negative sentiments
    else:
        return 5  

News['polarity'] = News['article'].apply(lambda x: TextBlob(x).sentiment.polarity) # we are going to use the apply function to apply the TextBlob function to each article in the News dataframe.
News['sentiment_score'] = News['polarity'].apply(assign_score) # we are going to use the apply function to apply the assign_score function to each polarity value in the News dataframe.

# now we going to drop the polarity column from the News dataframe.
News.drop(columns=['polarity'], inplace=True)

# now we going to update the News table in the database with the sentiment scores.
metadata = MetaData()  
metadata.reflect(engine) 
# Get reference to the 'Articles' table (replace 'Articles' with your actual table name)
news_table = Table('News', metadata, autoload_with=engine)

with engine.begin() as conn:  # Using `begin()` ensures that transaction is automatically committed or rolled back if an error occurs.
    for index, row in News.iterrows():
        # Debugging: Print out which row is being updated.
        print(f"Updating id {row['id']} with sentiment_score {row['sentiment_score']}")

        # Create an update statement for each row based on its 'id'
        stmt = (
            update(news_table)
            .where(news_table.c.id == row['id'])  # Match by 'id'
            .values(sentiment_score=row['sentiment_score'])  # Update only 'sentiment_score'
        )
        # Execute the update statement
        conn.execute(stmt)

print("Sentiment analysis for news article is complete and sentiment scores updated in the database.")

# sentiment analysis for the Youtube comments

# first we going to get the data from our database using the sqlalchemy.
Videos = pd.read_sql_table('Videos', engine)

# we are going to use the TextBlob library to perform sentiment analysis on the youtube comments.
# Define a function to assign sentiment scores based on polarity
def assign_score(polarity):
    if polarity > 0:
        return round(5 + (5 * polarity))  # Scale from 6 to 10 for positive sentiments
    elif polarity < 0:
        return round(5 * polarity) + 5    # Scale from 1 to 4 for negative sentiments
    else:
        return 5                          # Neutral sentiment is scored as 5

# Apply sentiment analysis and assign scores
Videos['polarity'] = Videos['comment'].apply(lambda x: TextBlob(x).sentiment.polarity)
Videos['sentiment_score'] = Videos['polarity'].apply(assign_score)

# Drop the 'polarity' column as it's no longer needed
Videos.drop('polarity', axis=1, inplace=True)

metadata = MetaData()
metadata.reflect(engine)  # Reflect the existing database schema

# Get reference to the 'Videos' table
videos_table = Table('Videos', metadata, autoload_with=engine)

# Establish a connection to execute updates
with engine.begin() as conn:  # Using `begin()` ensures that transaction is automatically committed or rolled back if an error occurs.
    for index, row in Videos.iterrows():
        # Debugging: Print out which row is being updated.
        print(f"Updating id {row['id']} with sentiment_score {row['sentiment_score']}")

        # Create an update statement for each row based on its 'id'
        stmt = (
            update(videos_table)
            .where(videos_table.c.id == row['id'])  # Match by 'id'
            .values(sentiment_score=row['sentiment_score'])  # Update only 'sentiment_score'
        )
        # Execute the update statement
        conn.execute(stmt)

print("Sentiment analysis for You-Tube comments is complete and sentiment scores updated in the database.")
