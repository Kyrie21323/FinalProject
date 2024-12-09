# import the necessary libraries
import os
import pandas as pd
import math
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import update, MetaData, Table
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func
load_dotenv()

# create a connection to the database
engine = sqlalchemy.create_engine(f'mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}@{os.getenv("DB_HOST")}/{os.getenv("DB_NAME")}')
SessionLocal = sessionmaker(bind=engine) # create a sessionmaker object so that we can create a session to interact with the database.
session = SessionLocal() # sessionLocal object to create a session and we can interact with the database locally.

# Reflect existing database tables
metadata = MetaData()
metadata.reflect(bind=engine)

# Define references to tables
news_table = Table('News', metadata, autoload_with=engine)
videos_table = Table('Videos', metadata, autoload_with=engine)
votes_table = Table('Votes', metadata, autoload_with=engine)
influencers_table = Table('Influencers', metadata, autoload_with=engine)

# Query data from News, Videos, and Votes tables
news_query = session.query(news_table).all()
videos_query = session.query(videos_table).all()
votes_query = session.query(votes_table).all()

# Initializing the dataframes for News, Videos, Votes, and Influencers
Influencer = pd.read_sql_table('Influencers', engine)
News = pd.read_sql_table('News', engine)
Videos = pd.read_sql_table('Videos', engine)
Votes = pd.read_sql_table('Votes', engine)

# Define the base for your models
Base = declarative_base()

# Influencer Table
class Influencers(Base):
    __tablename__ = 'Influencers'
    id = Column(Integer, primary_key=True)
    influencer_id = Column(Integer)
    good_vote = Column(Integer)
    bad_vote = Column(Integer)

# News Table
class News(Base):
    __tablename__ = 'News'
    id = Column(Integer, primary_key=True)
    influencer_id = Column(Integer, ForeignKey('influencers.influencer_id'))
    url = Column(String)
    title = Column(String)
    article = Column(String)
    sentiment_score = Column(Float)

# Video Table
class Video(Base):
    __tablename__ = 'Videos'
    id = Column(Integer, primary_key=True)
    influencer_id = Column(Integer, ForeignKey('influencers.influencer_id'))
    url = Column(String)
    title = Column(String)
    comment = Column(String)
    sentiment_score = Column(Float)

# Votes Table
class Vote(Base):
    __tablename__ = 'Votes'
    id = Column(Integer, primary_key=True)
    influencer_id = Column(Integer)
    good_vote = Column(Integer)
    bad_vote = Column(Integer)


# convert the query results into pandas dataframes
News = pd.DataFrame([row._asdict() for row in news_query])
Videos = pd.DataFrame([row._asdict() for row in videos_query])
Votes = pd.DataFrame([row._asdict() for row in votes_query])

# Define a function to calculate vote_score
def calculate_vote_score(good_vote, bad_vote):
    return (good_vote - bad_vote) / (good_vote + bad_vote + 1)

# Define a function to calculate normalized sentiment score (assuming sentiment_score is between 0-10)
def normalize_sentiment(sentiment_score):
    return sentiment_score / 10

# Define a function to calculate vibe score based on sentiment and vote scores
def calculate_vibe_score(news_sentiment, video_sentiment, vote_score):
    return round(0.25 * news_sentiment + 0.25 * video_sentiment + 0.5 * vote_score, 2)

def get_data_as_dataframe(table_name):
    """
    Fetch data from a table and return it as a Pandas DataFrame.
    """
    return pd.read_sql_table(table_name, engine)

def update_vibe_scores():
    """
    Calculate and update vibe scores for all influencers in the database.
    """
    # Load data from the database into Pandas DataFrames
    News = get_data_as_dataframe('News')
    Videos = get_data_as_dataframe('Videos')
    Votes = get_data_as_dataframe('Votes')

    # Create a dictionary to store vibe scores for each influencer_id
    vibe_scores = {}

    # Iterate over each influencer in the Votes table
    for index, vote_row in Votes.iterrows():
        influencer_id = vote_row['influencer_id']

        # Fetch average sentiment scores for news articles related to this influencer
        filtered_scores = News[News['influencer_id'] == influencer_id]['sentiment_score']
        if filtered_scores.empty or filtered_scores.isna().all():
            avg_news_sentiment = 0.0  # Default to 0 if no valid scores exist
        else:
            avg_news_sentiment = filtered_scores.mean()
        
        avg_video_sentiment = Videos[Videos['influencer_id'] == influencer_id]['sentiment_score'].mean() or 0

        # Normalize sentiment scores
        normalized_news_sentiment = normalize_sentiment(avg_news_sentiment)
        normalized_video_sentiment = normalize_sentiment(avg_video_sentiment)

        # Calculate vote score based on good and bad votes
        vote_score = calculate_vote_score(vote_row['good_vote'], vote_row['bad_vote'])

        # Calculate final vibe score
        vibe_score = calculate_vibe_score(normalized_news_sentiment, normalized_video_sentiment, vote_score)

        # Store the result in the dictionary with influencer_id as key and vibe score as value
        vibe_scores[influencer_id] = vibe_score

    # Update the Vibe Score in the Influencers table for each influencer_id
    with engine.begin() as conn:
        for influencer_id, vibe_score in vibe_scores.items():
            if math.isnan(vibe_score):
                print(f"Vibe score for influencer {influencer_id} is NaN. Defaulting to 0.0.")
                vibe_score = 0.0
            print(f"Updating influencer {influencer_id} with vibe score {vibe_score}")
            stmt = (
                update(influencers_table)
                .where(influencers_table.c.id == influencer_id)  # Match by 'influencer_id'
                .values(vibe_score=vibe_score)                 # Update 'vibe_score'
            )
            conn.execute(stmt)

    print("Vibe scores updated successfully.")



# # Create a dictionary to store vibe scores for each influencer_id
# vibe_scores = {}

# # Iterate over each influencer in the Votes table
# for index, vote_row in Votes.iterrows():
#     influencer_id = vote_row['influencer_id']

#     # Filter sentiment scores for the specific influencer
#     filtered_scores = News[News['influencer_id'] == influencer_id]['sentiment_score']
#     # Check if the filtered DataFrame is empty or if all values are NaN
#     if filtered_scores.empty or filtered_scores.isna().all():
#         avg_news_sentiment = 0.0  # Default to 0 if no valid scores exist
#     else:
#         avg_news_sentiment = filtered_scores.mean()  # Calculate the mean
    
#     # # Fetch average sentiment scores for news articles related to this influencer
#     # avg_news_sentiment = News[News['influencer_id'] == influencer_id]['sentiment_score'].mean() or 0
    
#     # Fetch average sentiment scores for videos related to this influencer
#     avg_video_sentiment = Videos[Videos['influencer_id'] == influencer_id]['sentiment_score'].mean() or 0
    
#     # Normalize sentiment scores
#     normalized_news_sentiment = normalize_sentiment(avg_news_sentiment)
#     normalized_video_sentiment = normalize_sentiment(avg_video_sentiment)
    
#     # Calculate vote score based on good and bad votes
#     vote_score = calculate_vote_score(vote_row['good_vote'], vote_row['bad_vote'])
    
#     # Calculate final vibe score
#     vibe_score = calculate_vibe_score(normalized_news_sentiment, normalized_video_sentiment, vote_score)
    
#     # Store the result in the dictionary with influencer_id as key and vibe score as value
#     vibe_scores[influencer_id] = vibe_score

# # Now update the Vibe Score in the Influencers table for each influencer_id
# with engine.begin() as conn:
#     for influencer_id, vibe_score in vibe_scores.items():
#         print(f"Updating influencer {influencer_id} with vibe score {vibe_score}")
        
#         # Create an update statement for each row based on its 'influencer_id'
#         stmt = (
#             update(influencers_table)
#             .where(influencers_table.c.id == influencer_id)  # Match by 'influencer_id'
#             .values(vibe_score=vibe_score)                             # Update 'vibe_score'
#         )
#         # Execute the update statement
#         conn.execute(stmt)

# print("Vibe scores updated successfully.")
