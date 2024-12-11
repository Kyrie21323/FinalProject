# VibeCHECK Project

## Project Overview

VibeCHECK is a web-based application that allows users to analyze influencer behavior and public sentiment. Users can view content related to influencers, from YouTube videos & comments and TMZ news articles, and vote whether the influencer's vibe is 'good' or 'bad.' The system analyzes scraped data from YouTube and TMZ and stores it in a MySQL database. Users will be able to vote on influencer behavior based on publicly available content and comments. Our algorithm then returns a score that gauges the "vibe" of an influencer.

## Project Structure
The project consists of the following key components:
### FastAPI Application (main.py)
- Provides API endpoints for interacting with the database.
- Includes background tasks for vibe score updates and sentiment analysis.
### Vibe Score Calculation (vibescore.py)
- Calculates vibe scores based on sentiment and vote data.
- Updates the Influencers table with the calculated scores.
### Sentiment Analysis (sentimentanalysis.py)
- Performs sentiment analysis on news articles and video comments using TextBlob.
- Updates the News and Videos tables with sentiment scores.
### Database Integration
- Uses SQLAlchemy for ORM (Object Relational Mapping) to interact with MySQL tables.
- Reflects existing database tables dynamically.
## Data Model

The project follows a structured relational database schema using **MySQL**. The data is organized into five key tables:

### 1. **Influencers**

- **id**: INT, Primary Key
- **name**: VARCHAR, Influencer's name
- **vibe_score**: DECIMAL, Calculated score based on votes
- **image_url**: TEXT, URL for the influencer's profile image
- **bio**: TEXT, basic information of the influencer
- **instagram**: TEXT, url to the influencer's instagram account
- **youtube**: TEXT, url to the influencer's youtube account

### 2. **Videos**

- **id**: INT, Primary Key
- **influencer_id**: INT, Foreign Key references `influencers`
- **url**: TEXT, Link to the video
- **title**: VARCHAR, Title of the video
- **comment**: TEXT, User comment on the video
- **sentiment_score**: INT, Sentiment analysis score (to be implemented)

### 3. **News**

- **id**: INT, Primary Key
- **influencer_id**: INT, Foreign Key references `influencers`
- **url**: TEXT, Link to the news article
- **title**: VARCHAR, Title of the article
- **article**: TEXT, Body content of the article
- **sentiment_score**: INT, Sentiment analysis score (to be implemented)

### 4. **Votes**

- **id**: INT, Primary Key
- **influencer_id**: INT, Foreign Key references `influencers`
- **good_vote**: INT, Count of 'good' votes
- **bad_vote**: INT, Count of 'bad' votes

### 5. **VibeScoreHistory**

- **id**: INT, Primary Key
- **influencer_id**: INT, Foreign Key references `influencers`
- **vibe_score**: INT, vibescore of the influencer
- **recorded_at**: DATETIME, the date time the vibescore was recorded

### ER Diagram

![ER Diagram](resources/ER_Diagram(2).png)

### SQL Database:

We chose SQL (MySQL) for the following reasons:

- **Relational Data**: SQL is ideal because the relationships between influencers, content, and comments are clear and structured.
- **Data Integrity**: MySQL enforces strict data integrity with foreign keys to maintain consistency.
- **Efficiency**: SQL allows for efficient querying of structured data, which fits our needs as the data we're working with (influencers, content, votes) follows a well-defined structure.

While MongoDB offers flexibility in schema design, our need for structured data and complex relationships makes SQL a better choice for this project.

## Setup Instructions

### Prerequisites

- **Python 3.8 or higher**
- **MySQL Server** (installed and running)
- **pip** (Python package manager)

### Installation Steps

1. **Clone the Repository**
   ```
   git clone
   ```
2. **Navigate to the project directory**
   ```
   cd path/to/finalproject
   ```
3. **Set Up Virtual Environment**
   ```
   python -m venv .venv
   #On Windows:
   .venv\Scripts\activate
   #On macOS/Linux:
   source .venv/bin/activate
   ```
4. **Install Required Packages - requirements.txt file**
   ```
   pip install -r requirements.txt
   ```
5. **Set up your .env file**

- Create a new file in the project root directory and name it .env
- Open the .env file in a text editor
- Add your MySQL connection details in the following format:

```
DB_HOST=your_mysql_host
DB_USER=your_mysql_username
DB_PASS=your_mysql_password
DB_NAME=your_database_name
YT_api =your_youtubeapikey
```

- Replace the placeholders with your actual MySQL connection details
- Save and close the .env file

6. **Run the Scrapers and Database Setup**

```
python main.py
```

## Ethics Considerations

1. **YouTube**

   - **Adhere to API Policies**: Use YouTube’s official API for data collection, following its terms of service and API usage limits. Avoid scraping the website directly as it may violate YouTube’s guidelines.
   - **Respect Content Ownership**: Videos and comments are user-generated and protected by copyright. Ensure that any collected data is used for non-commercial, educational, or research purposes and appropriately credits creators.
   - **Minimize Impact and Privacy**: Avoid scraping or collecting personal data like user profiles or private information. Be transparent about how data is used, especially when it involves public comments or video metadata.

2. **TMZ**
   - This project involves the use of web scraping techniques to extract celebrity headlines from TMZ's public website. Web scraping, while a valuable tool for data collection, must be performed responsibly and ethically. The below outlines the ethical considerations for this project.
   - **Respect Terms of Service and Ownership**: Adhere to TMZ's terms of service, respect intellectual property, and use the scraped data only for non-commercial purposes.
   - **Minimize Website Impact**: Limit scraping frequency to avoid server overload and ensure responsible data collection.
   - **Ensure Transparency**: Attribute TMZ as the data source and avoid sharing personally identifiable information.

## Data Integration

### Youtube Data

- The project utilizes the YouTube Data API v3 to extract data from YouTube channels. This includes channel statistics, video details, and top comments. The following steps outline the process:
- What it Does: Scrapes data from a list of YouTube channels, including video titles, URLs, and top comments.
- Process:
  - Fetches channel details using the YouTube Data API.
  - Extracts the latest video and top comments.
  - Stores the data in the Videos table in the database.

### TMZ Data

- What it Does: Scrapes articles related to influencers from TMZ.
- Process:
  - Searches TMZ for a predefined list of influencers.
  - Extracts article titles, URLs, and content.
  - Stores the data in the News table in the database.

### API Setup:

- Obtain an API key from the Google Developer Console.
- Use the googleapiclient.discovery library in Python to create a service object for interacting with the YouTube API.

### Fetching Channel Statistics:

- Use the channels().list method to retrieve channel details such as subscriber count, view count, and video count.
- Store this data in a structured format for analysis.

### Extracting Video Information:

- Retrieve the latest video link from a channel's upload playlist using `playlistItems().list`.
- Gather video statistics and metadata for further sentiment analysis.

### Sentiment Analysis:

- Perform sentiment analysis on comments retrieved from videos using natural language processing (NLP) techniques.
- Use this data to determine the general sentiment of viewers towards specific content or influencers.

### Data Storage and Visualization:

- Store collected data in pandas DataFrames for easy manipulation and analysis.
- For now we are exporting data to CSV files for reporting purposes, we have our database outlined and in future we'll store the data to the database according to the format outlined above.

### Future Enhancements

- Integrate additional social media platforms for more comprehensive influencer monitoring.
- Implement machine learning algorithms to predict future trends in influencer popularity.
- Enhance user engagement features by allowing discussions or sharing of opinions within the app.

# FastAPI Application for Database Access

This FastAPI application provides RESTful API endpoints to access data from four tables in a MySQL database: `influencers`, `content`, `comments`, and `votes`.

## Features
- Fetch data from multiple database tables (Influencers, Votes, VibeScoreHistory, News, Videos).
- Insert new votes into the Votes table.
- Update or create votes dynamically while recalculating vibe scores in the background.
- Perform sentiment analysis on news and videos in the background.

## Prerequisites

- Python 3.7+
- MySQL Server
- Necessary Python packages listed in `requirements.txt`


## Installation

1. **Clone the Repository**

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

`pip install fastapi uvicorn mysql-connector-python python-dotenv pandas`
or
`pip install -r requirements.txt`

## Environment Variables
The application uses environment variables to connect to the MySQL database. Create a .env file in the project directory with the following keys:

`DB_HOST=<your-database-host>`
`DB_USER=<your-database-user>`
`DB_PASS=<your-database-password>`
`DB_NAME=<your-database-name>`
`YT_api =<your-YouTube-API-Key>`

## Running the Application

Start the FastAPI Server

- Use Uvicorn to run the FastAPI application:
  `uvicorn database_api:app --reload`

this will give us localhost link for the API access:

### Access API Endpoints

- The following endpoints are available:\
   GET /Influencers: Retrieve all records from the influencers table.\
   GET /votes/{influencer_id}: Retrieve all votes for the specific influencer from the vote table.\
   GET /News: Retrieve all records from the comments table.\
   GET /Votes: Retrieve all records from the votes table.\
   GET /Videos: Retrieve all records from the videos table.\
   GET /Votes: Retrieve all records from the votes table.\
   POST /Votes: Add a new vote to the votes table.\
   PUT /Votes/{influencer_id}: Add a new vote to the votes table for a specific influencer.\


1. Vibe Score History
Fetch all records from the VibeScoreHistory table.
- URL: /VibeScoreHistory
- Method: GET
- Response: List of vibe score history records.
2. Influencers
Fetch all records from the Influencers table.
- URL: /Influencers
- Method: GET
- Response: List of influencer records.
3. Votes
- a. Fetch Votes by Influencer ID
   Fetch vote details for a specific influencer.
   - URL: /Votes/{influencer_id}
   - Method: GET
   - Path Parameter:
      - influencer_id (int): ID of the influencer.
   - Response: Vote record for the specified influencer.
- b. Fetch All Votes
   Fetch all records from the Votes table.
   - URL: /Votes
   - Method: GET
   - Response: List of all vote records.
- c. Add a New Vote
   Insert a new vote into the database.
   - URL: /Votes
   - Method: POST
   - Request Body:
   {
  "influencer_id": <int>,
  "good_vote": <int>,
  "bad_vote": <int>
   }
   - Response:
   { "message": "Vote added successfully" }
- d. Update or Create Vote
   Update an existing vote or create a new one for an influencer.
   - URL: /Votes/{influencer_id}
   - Method: PUT
   - Path Parameter:
      - influencer_id (int): ID of the influencer.
   - Request Body:
   {
  "good_vote": <int>,
  "bad_vote": <int>
   }
4. News
Fetch all records from the News table and trigger sentiment analysis in the background.
- URL: /News
- Method: GET
- Response: List of news records.
5. Videos
Fetch all records from the Videos table and trigger sentiment analysis in the background.
- URL: /Videos
- Method: GET
- Response: List of video records.

## Background Tasks
The API uses FastAPI's BackgroundTasks feature to perform certain operations asynchronously:
1. Sentiment analysis for news and videos is triggered when fetching data from `/News` and `/Videos`.
2. Vibe score updates are triggered when votes are updated or created via `/Votes/{influencer_id}`.

## Key Functionalities
### Sentiment Analysis
Sentiment analysis is performed on text data (news articles and video comments) using TextBlob's polarity scoring.

#### Process:
- Fetch data from News or Videos table.
- Calculate polarity using TextBlob.
- Assign a scaled sentiment score (1–10) based on polarity.
- Update the database with calculated sentiment scores.
#### Functions:
- `perform_sentiment_analysis(dataframe, text_column)`
   - Performs TextBlob-based polarity scoring and assigns sentiment scores.
- `update_sentiment_scores(table_name, dataframe)`
   - Updates the database table with calculated sentiment scores.

### Vibe Score Calculation
Vibe scores are calculated as a weighted average of normalized news sentiment, video sentiment, and vote scores.

#### Process:
- Fetch data from `News`, `Videos`, and `Votes` tables.
- Calculate normalized sentiment scores (0–1 scale).
- Compute vote score as good votes/(good votes+bad votes).
- Combine these metrics into a final vibe score:
   Vibe Score = 0.25 × News Sentiment + 0.25 × Video Sentiment + 0.5×Vote Score
- Update the Influencers table with calculated vibe scores.

Functions:
- `calculate_vibe_score(news_sentiment, video_sentiment, vote_score)`
   Combines metrics into a final vibe score.
- `update_vibe_scores()`
   Updates vibe scores for all influencers in the database.

## Error Handling
The API includes robust error handling using FastAPI's HTTPException class. Common error scenarios include:
- Database connection failures (500 Internal Server Error).
- Missing data (404 Not Found).
- SQL execution errors (500 Internal Server Error).

## Dependencies
The following Python libraries are used in this project:
- FastAPI - For building APIs.
- mysql.connector - For connecting to MySQL databases.
- Pydantic - For request validation.
- dotenv - For managing environment variables.
- pymysql - For advanced MySQL operations.
- SQLAlchemy – For ORM-based database interaction.
- TextBlob – For performing sentiment analysis.
- Pandas – For data manipulation.

