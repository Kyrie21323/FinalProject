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

def get_data_from_table(table_name):
    # Fetch data from the given table using SQLAlchemy.
    return pd.read_sql_table(table_name, engine)

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

def perform_sentiment_analysis(dataframe, text_column):
    dataframe['polarity'] = dataframe[text_column].apply(lambda x: TextBlob(x).sentiment.polarity) # we are going to use the apply function to apply the TextBlob function to each article in the News dataframe.
    dataframe['sentiment_score'] = dataframe['polarity'].apply(assign_score) # we are going to use the apply function to apply the assign_score function to each polarity value in the News dataframe.
    dataframe.drop(columns=['polarity'], inplace=True)  # Drop polarity column after use
    return dataframe

def update_sentiment_scores(table_name, dataframe):
    # now we going to update the News table in the database with the sentiment scores.
    metadata = MetaData()
    metadata.reflect(engine)
    
    # Get reference to the target table
    target_table = Table(table_name, metadata, autoload_with=engine)

    with engine.begin() as conn:
        for index, row in dataframe.iterrows():
            print(f"Updating id {row['id']} with sentiment_score {row['sentiment_score']}")
            # Create an update statement for each row based on its 'id'
            stmt = (
                update(target_table)
                .where(target_table.c.id == row['id'])  # Match by 'id'
                .values(sentiment_score=row['sentiment_score'])  # Update only 'sentiment_score'
            )
            conn.execute(stmt)

def analyze_and_update_news():
    # Perform sentiment analysis on the 'News' table and update the database.
    news_data = get_data_from_table('News')
    analyzed_news = perform_sentiment_analysis(news_data, 'article')
    update_sentiment_scores('News', analyzed_news)
    print("Sentiment analysis for news articles is complete and scores updated.")

def analyze_and_update_videos():
    # Perform sentiment analysis on the 'Videos' table and update the database.
    video_data = get_data_from_table('Videos')
    analyzed_videos = perform_sentiment_analysis(video_data, 'comment')
    update_sentiment_scores('Videos', analyzed_videos)
    print("Sentiment analysis for YouTube comments is complete and scores updated.")

