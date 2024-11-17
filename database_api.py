# importing the required libraries
from fastapi import FastAPI, HTTPException # fastapi library for creating the API
from mysql.connector import connect, Error # mysql.connector library for connecting to the MySQL database
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from pymysql.err import IntegrityError
import pymysql.cursors

class VoteCreate(BaseModel):
    influencer_id: int
    good_vote: int
    bad_vote: int

class VoteUpdate(BaseModel):
    good_vote: int
    bad_vote: int

# Load environment variables
load_dotenv()


app = FastAPI() # create an instance of the FastAPI class which can be used by uvicorn to run tha API in our local machine

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# function to connect to the mysql database
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

# function to fetch all the tables that we already created in the database.
def fetch_all_from_table(table_name):
    connection = get_database_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Could not connect to the database error 500") # raise an exception if the connection is not established

    try:
        with connection.cursor(dictionary=True) as cursor: # using the cursor to execute the SQL query
            cursor.execute(f"SELECT * FROM {table_name}") # SQL query to fetch all the data from the table
            result = cursor.fetchall() # fetch all the data from the table
            return result # return the result
    # raise an exception if there is an error while fetching the data
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data from {table_name}: {e}")
    finally:
        connection.close()

# create the API endpoints to fetch the data from the tables
@app.get("/Influencers") # endpoint to fetch the data from the influencers table
async def get_influencers(): # async function to fetch the data, async is used to make the function asynchronous which is useful when we are fetching data from the database or making API requests
    return fetch_all_from_table("Influencers") # async function was recommended by the LLM to make our API better as previously I was incountring some errors

# this endpoint is used to fetch the data from th votes table based on the influencer_id and content_id
# this function is useful when we want to fetch the data based on the influencer_id and content_id and based on that we want to update the votecount.

@app.get("/Votes/{influencer_id}")
async def get_vote(influencer_id: int):
    connection = get_database_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Could not connect to the database")

    try:
        # Use DictCursor to return results as dictionaries
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Pass influencer_id as a tuple (influencer_id,)
            cursor.execute(
                "SELECT * FROM Votes WHERE influencer_id = %s",
                (influencer_id,)  # Pass as a tuple
            )
            vote = cursor.fetchone()
            if vote is None:
                # Return a 404 error if no vote is found
                raise HTTPException(status_code=404, detail="Vote not found")
            return vote
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Error fetching vote: {e}")
    finally:
        connection.close()


# @app.get("/Votes/{influencer_id}")
# async def get_vote(influencer_id: int):
#     connection = get_database_connection()
#     if connection is None:
#         raise HTTPException(status_code=500, detail="Could not connect to the database")

#     try:
#         with connection.cursor(dictionary=True) as cursor:
#             cursor.execute(
#                 "SELECT * FROM Votes WHERE influencer_id = %s",
#                 (influencer_id)
#             )
#             vote = cursor.fetchone()
#             if vote is None:
#                 # Return a 404 error if no vote is found
#                 raise HTTPException(status_code=404, detail="Vote not found")
#             return vote
#     except Error as e:
#         raise HTTPException(status_code=500, detail=f"Error fetching vote: {e}")
#     finally:
#         connection.close()


@app.get("/content") # endpoint to fetch the data from the content table
async def get_content():
    return fetch_all_from_table("content")

@app.get("/comments") # endpoint to fetch the data from the comments table
async def get_comments():
    return fetch_all_from_table("comments")

@app.get("/Votes") # endpoint to fetch the data from the votes table
async def get_votes():
    return fetch_all_from_table("Votes")


# create the API endpoint to add a new vote to the votes table
@app.post("/Votes", status_code=201)  # Status code 201 indicates resource creation
async def create_vote(vote: VoteCreate):
    connection = get_database_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Could not connect to the database")

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Votes (influencer_id, good_vote, bad_vote) VALUES (%s, %s, %s)", # SQL query to insert the vote into the votes table
                (vote.influencer_id, vote.good_vote, vote.bad_vote) # values to be inserted into the table
            )
            connection.commit()
            return {"message": "Vote added successfully"}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error inserting vote: {e}")
    finally:
        connection.close()

# @app.put to update the item in the table
@app.put("/Votes", status_code=200)
async def upsert_vote(vote: VoteCreate):
    connection = get_database_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Could not connect to the database")

    try:
        with connection.cursor() as cursor:
            # Upsert query: Insert new vote or update existing vote
            cursor.execute(
                """
                INSERT INTO Votes (influencer_id, good_vote, bad_vote)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    good_vote = good_vote + VALUES(good_vote),
                    bad_vote = bad_vote + VALUES(bad_vote);
                """,
                (vote.influencer_id, vote.good_vote, vote.bad_vote)
            )
            connection.commit()
            return {"message": "Vote updated or added successfully"}
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Database integrity error")
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error processing vote: {e}")
    finally:
        connection.close()




# @app.put("/Votes")
# async def update_or_create_vote(vote: VoteCreate):
#     connection = get_database_connection()
#     if connection is None:
#         raise HTTPException(status_code=500, detail="Could not connect to the database")

#     try:
#         with connection.cursor() as cursor:
#             # Check if the vote already exists
#             cursor.execute(
#                 "SELECT * FROM Votes WHERE influencer_id = %s", # SQL query to check if the vote already exists
#                 (vote.influencer_id) # values to be checked
#             )
#             existing_vote = cursor.fetchone() # fetch the vote if it already exists

#             if existing_vote is None:
#                 # If no existing record found, insert a new one
#                 cursor.execute(
#                     "INSERT INTO Votes (influencer_id, good_vote, bad_vote) VALUES (%s, %s, %s)", # based on the parametets passed we insert the new vote
#                     (vote.influencer_id, vote.good_vote, vote.bad_vote)
#                 )
#                 message = "Vote created successfully"
#             else:
#                 # Otherwise update the existing record
#                 cursor.execute(
#                     "UPDATE Votes SET good_vote = %s, bad_vote = %s WHERE influencer_id = %s",
#                     (vote.good_vote, vote.bad_vote, vote.influencer_id)
#                 )
#                 message = "Vote updated successfully"

#             connection.commit()
#             return {"message": message}
    
#     except Error as e:
#         raise HTTPException(status_code=500, detail=f"Error processing vote: {e}")
    
#     finally:
#         connection.close()


# @app.put("/votes/update")
# async def update_vote(influencer_id: int, content_id: int, new_vote: str):
#     connection = get_database_connection()
#     if connection is None:
#         raise HTTPException(status_code=500, detail="Could not connect to the database")

#     try:
#         with connection.cursor() as cursor:
#             # Check if the vote exists first
#             cursor.execute(
#                 "SELECT * FROM votes WHERE influencer_id = %s AND content_id = %s", 
#                 (influencer_id, content_id)
#             )
#             vote_record = cursor.fetchone()

#             if not vote_record:
#                 raise HTTPException(status_code=404, detail="Vote record not found")

#             # Update the vote value
#             cursor.execute(
#                 "UPDATE votes SET vote = %s WHERE influencer_id = %s AND content_id = %s", 
#                 (new_vote, influencer_id, content_id)
#             )
#             connection.commit()  # Commit changes to the database

#             return {"message": "Vote updated successfully"}
    
#     except Error as e:
#         raise HTTPException(status_code=500, detail=f"Error updating vote: {e}")
    
#     finally:
#         connection.close()

# to change the acutual database schema so that we can update the vote easily
# def create_votes_table(connection):
#     print("Creating votes table...")
#     create_table_query = """
#     CREATE TABLE IF NOT EXISTS votes (
#         id INT AUTO_INCREMENT PRIMARY KEY,
#         influencer_id INT,
#         content_id INT,
#         vote ENUM('upvote', 'downvote') NOT NULL,
#         FOREIGN KEY (influencer_id) REFERENCES influencer(id) ON DELETE CASCADE,
#         FOREIGN KEY (content_id) REFERENCES content(id) ON DELETE CASCADE
#     );
#     """
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute(create_table_query)
#             connection.commit()
#             print("Table 'votes' created successfully.")
#     except Error as e:
#         print(f"Error creating votes table: {e}")

# how to use the put request using API call in python:
# I've implitmented that in another file called test_api.py we can later delete that.