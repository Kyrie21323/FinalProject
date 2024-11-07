# import the necessary packages
import creds
from googleapiclient.discovery import build
import pandas as pd
#import seaborn as sns

# set up the YouTube API
# creds.py contains the API key as variable YT_api
# for security reasons, this file is not included in the repository
# structure of the creds.py file:
# YT_api = 'your_api_key'
API_KEY = creds.YT_api
# channel_ids is a list of channel ids for the influencers
channel_ids = ['UCX6OQ3DkcsbYNE6H8uQQuVA',
                'UCxgAuX3XZROujMmGphN_scA',
                'UCqECaJ8Gagnn7YCbPEzWH6g',
                'UCIwFjwMjI0y7PDBVEO9-bkQ']

# setting up the YouTube API service by defining the API service name and version
api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "YOUR_CLIENT_SECRET_FILE.json"
# creating the youtube variable that will be used to access the YouTube API
youtube = build(api_service_name, api_version, developerKey=API_KEY)


# function to get the video statistics

def get_channel_stats(youtube, channel_ids):
    data_list = [] # list to store the data
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=','.join(channel_ids)
    ) # request to get the channel statistics for further processing
    response = request.execute() 
    # loop through the response and store the data in the data_list according to the channel id list
    for i in range(len(response['items'])):
        # store the data in a dictionary
        data = dict(Name = response['items'][i]['snippet']['title'],
                    subscriber_count = response['items'][i]['statistics']['subscriberCount'],
                    view_count = response['items'][i]['statistics']['viewCount'],
                    video_count = response['items'][i]['statistics']['videoCount'],
                    playlist_id = response['items'][i]['contentDetails']['relatedPlaylists']['uploads'])
        data_list.append(data) # append the dictionary data to the data_list
    return data_list

channel_data = get_channel_stats(youtube, channel_ids)
# Function to get the latest video link from a playlist
def get_latest_video_link(youtube, playlist_id): # using the playlist id that we fetched earlier using the get_channel_stats function
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=1
    )
    # getting the video id and title from the response
    response = request.execute()
    video_id = response['items'][0]['snippet']['resourceId']['videoId']
    video_title = response['items'][0]['snippet']['title']
    video_link = f"https://www.youtube.com/watch?v={video_id}" # creating the video link using the video id
    return video_title, video_link


# Add latest video link to each channel's data
for channel in channel_data:
    video_title, latest_video_link = get_latest_video_link(youtube, channel['playlist_id'])
    channel['Title'] = video_title
    channel['URL'] = latest_video_link

# create a pandas DataFrame to store the channel data
stats = pd.DataFrame(channel_data)
#print(stats)    

# change the data types of the certain columns to numeric
stats['subscriber_count'] = pd.to_numeric(stats['subscriber_count'])
stats['view_count'] = pd.to_numeric(stats['view_count'])
stats['video_count'] = pd.to_numeric(stats['video_count'])

# print the data
#print(stats)

# function to get the top comments from the latest video

def get_top_comments(youtube, video_id): # using the video id that we fetched earlier using the get_latest_video_link function
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=10, # we can tweak this number to get more or less comments
        order="relevance" # getting the top comments based on relevance
    )
    response = request.execute()
    comments_data = []
    # loop through the response and store the top comments in the comments_data list
    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
        author = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
        comments_data.append({'author': author, 'comment': comment}) # append the author and comment to the comments_data list
    return comments_data


comments_list = [] # list to store the comments data
for channel in channel_data:
    video_id = channel['URL'].split('=')[-1] # getting the video id from the video link
    comments_data = get_top_comments(youtube, video_id) # getting the top comments for the video
    comments_df = pd.DataFrame(comments_data) # creating a DataFrame from the comments data
    comments_list.append(comments_df) # append the DataFrame to the comments_list

# Save the stats DataFrame to a CSV file
stats.to_csv('channel_stats.csv', index=False)

# Initialize an empty list to hold all comments with channel information
all_comments = []

# Loop through each channel's comments and add channel name
for i, comments_df in enumerate(comments_list):
    # Add the channel name or video title to each comment
    comments_df['Name'] = channel_data[i]['Name']
    comments_df['video_title'] = channel_data[i]['Title']
    all_comments.append(comments_df)

# Concatenate all comments DataFrames into one
all_comments_df = pd.concat(all_comments, ignore_index=True)

# print the comments data
#print(all_comments_df)

# Save the combined comments DataFrame to a CSV file
all_comments_df.to_csv('all_comments.csv', index=False)