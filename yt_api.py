import creds
from googleapiclient.discovery import build
import pandas as pd

API_KEY = creds.YT_api
api_service_name = "youtube"
api_version = "v3"
youtube = build(api_service_name, api_version, developerKey=API_KEY)

def get_channel_stats(channel_ids):
    data_list = []
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=','.join(channel_ids)
    )
    response = request.execute()
    for item in response['items']:
        data = {
            'Name': item['snippet']['title'],
            'subscriber_count': int(item['statistics']['subscriberCount']),
            'view_count': int(item['statistics']['viewCount']),
            'video_count': int(item['statistics']['videoCount']),
            'playlist_id': item['contentDetails']['relatedPlaylists']['uploads']
        }
        data_list.append(data)
    return pd.DataFrame(data_list)

def get_latest_video_link(playlist_id):
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=1
    )
    response = request.execute()
    video_id = response['items'][0]['snippet']['resourceId']['videoId']
    video_title = response['items'][0]['snippet']['title']
    return video_title, video_id

def get_top_comments(video_id):
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=10,
        order="relevance"
    )
    response = request.execute()
    comments_data = [
        {
            'author': item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
            'comment': item['snippet']['topLevelComment']['snippet']['textDisplay']
        }
        for item in response['items']
    ]
    return pd.DataFrame(comments_data)