# importing the required libraries
from fastapi import FastAPI, HTTPException # fastapi library for creating the API
from mysql.connector import connect, Error # mysql.connector library for connecting to the MySQL database
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from pymysql.err import IntegrityError
import pymysql.cursors
from fastapi import BackgroundTasks
from vibescore import update_vibe_scores

class VoteCreate(BaseModel):
    influencer_id: int
    good_vote: int
    bad_vote: int

# Define the Pydantic model for input validation
class VoteUpdate(BaseModel):
    good_vote: int
    bad_vote: int

# Load environment variables
load_dotenv()


app = FastAPI() # create an instance of the FastAPI class which can be used by uvicorn to run tha API in our local machine

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://vibecheck-frontend-57495040685.us-central1.run.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.get("/News") # endpoint to fetch the data from the content table
async def get_content():
    return fetch_all_from_table("News")

@app.get("/Videos") # endpoint to fetch the data from the comments table
async def get_comments():
    return fetch_all_from_table("Videos")

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

# create the API endpoint to update the vote in the votes table
@app.put("/Votes/{influencer_id}") # endpoint to update the vote in the votes table based on the influencer_id
async def update_or_create_vote(influencer_id: int, vote_data: VoteUpdate, background_tasks: BackgroundTasks):
    connection = get_database_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Could not connect to the database")

    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Check if a vote entry exists for the given influencer_id
            cursor.execute("SELECT * FROM Votes WHERE influencer_id = %s", (influencer_id,))
            existing_vote = cursor.fetchone()

            if existing_vote:
                # If vote exists, update the good_vote and bad_vote
                cursor.execute(
                    """
                    UPDATE Votes
                    SET good_vote = good_vote + %s, bad_vote = bad_vote + %s
                    WHERE influencer_id = %s
                    """,
                    (vote_data.good_vote, vote_data.bad_vote, influencer_id)
                )
                connection.commit()
                # Run vibe score update in the background
                background_tasks.add_task(update_vibe_scores)
                return {"message": "Vote updated successfully"}
            else:
                # If vote does not exist, insert a new row
                cursor.execute(
                    """
                    INSERT INTO Votes (influencer_id, good_vote, bad_vote)
                    VALUES (%s, %s, %s)
                    """,
                    (influencer_id, vote_data.good_vote, vote_data.bad_vote)
                )
                connection.commit()
                # Run vibe score update in the background
                background_tasks.add_task(update_vibe_scores)
                return {"message": "Vote created successfully"}
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Error updating or creating vote: {e}")
    finally:
        connection.close()


