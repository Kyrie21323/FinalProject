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
               'UC0WP5P-ufpRfjbNrmOWwLBQ']
#influencer = 'Mark Tilbury'

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
                    playlist_id = response['items'][i]['contentDetails']['relatedPlaylists']['uploads'])
        data_list.append(data) # append the dictionary data to the data_list
    return data_list

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
        comments_data.append(comment) # append the comment only to the comments_data list
    return comments_data

#main code to fetch data and merge into a single csv file
channel_data = get_channel_stats(youtube, channel_ids)
final_data = []

for channel in channel_data:
    video_title, latest_video_link = get_latest_video_link(youtube, channel['playlist_id'])
    top_comments = get_top_comments(youtube, latest_video_link.split('=')[-1])
    
    #add each comment with channel info to final data
    for comment in top_comments:
        final_data.append({
            'Name': channel['Name'],
            'Title': video_title,
            'URL': latest_video_link,
            'comment': comment
        })

# Convert the final data to a DataFrame and save to CSV
final_df = pd.DataFrame(final_data)
final_df.to_csv('yt_channel_stats.csv', index=False)