from googleapiclient.discovery import build
import pandas as pd
from dotenv import load_dotenv
import os 

# -----------------------------
# API KEY
# -----------------------------
load_dotenv(dotenv_path="../.env")

API_KEY = os.getenv("YOUTUBE_API_KEY")

youtube = build('youtube', 'v3', developerKey=API_KEY)

# -----------------------------
# CHANNELS TO ANALYZE
# -----------------------------
channels = [
    "MrBeast",
    "TED",
    "SonyMusicIndia"
]

all_video_data = []

# -----------------------------
# LOOP THROUGH CHANNELS
# -----------------------------
for channel_name in channels:

    # Search channel
    search_request = youtube.search().list(
        part="snippet",
        q=channel_name,
        type="channel",
        maxResults=1
    )

    search_response = search_request.execute()

    channel_id = search_response['items'][0]['snippet']['channelId']

    # Get channel statistics
    channel_request = youtube.channels().list(
        part="snippet,statistics,contentDetails",
        id=channel_id
    )

    channel_response = channel_request.execute()

    channel_item = channel_response['items'][0]

    channel_title = channel_item['snippet']['title']
    subscribers = int(channel_item['statistics'].get('subscriberCount', 0))
    total_views = int(channel_item['statistics'].get('viewCount', 0))
    total_videos = int(channel_item['statistics'].get('videoCount', 0))

    # Upload playlist ID
    uploads_playlist = channel_item['contentDetails']['relatedPlaylists']['uploads']

    # Fetch videos from uploads playlist
    playlist_request = youtube.playlistItems().list(
        part="snippet",
        playlistId=uploads_playlist,
        maxResults=10
    )

    playlist_response = playlist_request.execute()

    video_ids = []

    for item in playlist_response['items']:
        video_ids.append(item['snippet']['resourceId']['videoId'])

    # Get detailed video statistics
    video_request = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        id=",".join(video_ids)
    )

    video_response = video_request.execute()

    # Process each video
    for video in video_response['items']:

        title = video['snippet']['title']

        published_date = video['snippet']['publishedAt']

        views = int(video['statistics'].get('viewCount', 0))
        likes = int(video['statistics'].get('likeCount', 0))
        comments = int(video['statistics'].get('commentCount', 0))

        duration = video['contentDetails']['duration']

        # Engagement Rate
        if views != 0:
            engagement_rate = ((likes + comments) / views) * 100
        else:
            engagement_rate = 0

        video_data = {
            "Channel Name": channel_title,
            "Subscribers": subscribers,
            "Channel Total Views": total_views,
            "Channel Total Videos": total_videos,
            "Video Title": title,
            "Published Date": published_date,
            "Views": views,
            "Likes": likes,
            "Comments": comments,
            "Duration": duration,
            "Engagement Rate (%)": round(engagement_rate, 2)
        }

        all_video_data.append(video_data)

# -----------------------------
# CREATE DATAFRAME
# -----------------------------
df = pd.DataFrame(all_video_data)

# -----------------------------
# DISPLAY DATA
# -----------------------------
print(df)

# -----------------------------
# SAVE CSV
# -----------------------------
df.to_csv("../data/youtube_advanced_data.csv", index=False)

print("Advanced YouTube data saved successfully!")