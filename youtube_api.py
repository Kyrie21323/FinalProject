import creds
from googleapiclient.discovery import build
import pandas as pd
import seaborn as sns

API_KEY = creds.YT_api
channel_ids = ['UCX6OQ3DkcsbYNE6H8uQQuVA',
               'UCxgAuX3XZROujMmGphN_scA',
               'UCqECaJ8Gagnn7YCbPEzWH6g',
               'UC0WP5P-ufpRfjbNrmOWwLBQ']

api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "YOUR_CLIENT_SECRET_FILE.json"
youtube = build(api_service_name, api_version, developerKey=API_KEY)

# Function to get the channel statistics and playlist ID
def get_channel_stats(youtube, channel_ids):
    data_list = []
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=','.join(channel_ids)
    )
    response = request.execute()
    for i in range(len(response['items'])):
        data = dict(channel_name = response['items'][i]['snippet']['title'],
                    subscriber_count = response['items'][i]['statistics']['subscriberCount'],
                    view_count = response['items'][i]['statistics']['viewCount'],
                    video_count = response['items'][i]['statistics']['videoCount'],
                    playlist_id = response['items'][i]['contentDetails']['relatedPlaylists']['uploads'])
        data_list.append(data)
    return data_list

channel_data = get_channel_stats(youtube, channel_ids)
# Function to get the latest video link from a playlist
def get_latest_video_link(youtube, playlist_id):
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=1
    )
    response = request.execute()
    video_id = response['items'][0]['snippet']['resourceId']['videoId']
    video_link = f"https://www.youtube.com/watch?v={video_id}"
    return video_link
# Add latest video link to each channel's data
for channel in channel_data:
    latest_video_link = get_latest_video_link(youtube, channel['playlist_id'])
    channel['latest_video_link'] = latest_video_link

# Convert the data to a DataFrame
stats = pd.DataFrame(channel_data)
print(stats)