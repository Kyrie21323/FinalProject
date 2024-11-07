from fastapi import FastAPI, HTTPException
from mysql.connector import connect, Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

def get_database_connection():
    try:
        connection = connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            database=os.getenv('DB_NAME')
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def fetch_all_from_table(table_name):
    connection = get_database_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Could not connect to the database")

    try:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(f"SELECT * FROM {table_name}")
            result = cursor.fetchall()
            return result
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data from {table_name}: {e}")
    finally:
        connection.close()
        

@app.get("/influencers")
async def get_influencers():
    return fetch_all_from_table("influencers")

@app.get("/content")
async def get_content():
    return fetch_all_from_table("content")

@app.get("/comments")
async def get_comments():
    return fetch_all_from_table("comments")

@app.get("/votes")
async def get_votes():
    return fetch_all_from_table("votes")

# from fastapi import FastAPI, HTTPException, Depends, status
# from pydantic import BaseModel
# from typing import Annotated
# import main
# from sqlalchemy.orm import Session

# app = FastAPI()

# class influencersBase(BaseModel):
#     name: str
#     followers: int
#     vibe_score: float

# class contentBase(BaseModel):
#     influencer_id: int
#     platform: str
#     url: str
#     title: str

# class commentBase(BaseModel):
#     content_id: int
#     comment_text: str
#     sentiment_score: float

# class voteBase(BaseModel):
#     influencer_id: int
#     content_id: int
#     vote: int

# def get_db():
#     db = main.Sessionlocal()
#     try:
#         yield db
#     finally:
#         db.close()