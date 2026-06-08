from googleapiclient.discovery import build
import pandas as pd
from dotenv import load_dotenv
import os


# -----------------------------
# LOAD API KEY
# -----------------------------

load_dotenv(dotenv_path="../.env")

API_KEY = os.getenv("YOUTUBE_API_KEY")


# -----------------------------
# BUILD YOUTUBE API
# -----------------------------

youtube = build(
    'youtube',
    'v3',
    developerKey=API_KEY
)


# -----------------------------
# CHANNELS TO ANALYZE
# -----------------------------

channels = [

    "MrBeast",

    "TED",

    "SonyMusicIndia"
]


# -----------------------------
# STORE ALL VIDEO DATA
# -----------------------------

all_video_data = []


# -----------------------------
# LOOP THROUGH CHANNELS
# -----------------------------

for channel_name in channels:


    # SEARCH CHANNEL

    search_request = youtube.search().list(

        part="snippet",

        q=channel_name,

        type="channel",

        maxResults=1
    )

    search_response = search_request.execute()


    # GET CHANNEL ID

    channel_id = search_response['items'][0]['snippet']['channelId']


    # GET CHANNEL DETAILS

    channel_request = youtube.channels().list(

        part="snippet,statistics,contentDetails",

        id=channel_id
    )

    channel_response = channel_request.execute()

    channel_item = channel_response['items'][0]


    # CHANNEL INFO

    channel_title = channel_item['snippet']['title']

    subscribers = int(

        channel_item['statistics'].get(
            'subscriberCount',
            0
        )
    )

    total_views = int(

        channel_item['statistics'].get(
            'viewCount',
            0
        )
    )

    total_videos = int(

        channel_item['statistics'].get(
            'videoCount',
            0
        )
    )


    # GET UPLOAD PLAYLIST ID

    uploads_playlist = channel_item[
        'contentDetails'
    ][
        'relatedPlaylists'
    ][
        'uploads'
    ]


    # FETCH VIDEOS FROM PLAYLIST

    playlist_request = youtube.playlistItems().list(

        part="snippet",

        playlistId=uploads_playlist,

        maxResults=15
    )

    playlist_response = playlist_request.execute()


    # STORE VIDEO IDS

    video_ids = []


    for item in playlist_response['items']:

        video_ids.append(

            item['snippet']
            ['resourceId']
            ['videoId']
        )


    # GET VIDEO DETAILS

    video_request = youtube.videos().list(

        part="snippet,statistics,contentDetails",

        id=",".join(video_ids)
    )

    video_response = video_request.execute()


    # PROCESS EACH VIDEO

    for video in video_response['items']:


        # VIDEO TITLE

        title = video[
            'snippet'
        ].get(
            'title',
            'No Title'
        )


        # PUBLISHED DATE

        published_date = video[
            'snippet'
        ].get(
            'publishedAt',
            'Not Available'
        )


        # VIDEO STATISTICS

        views = int(

            video.get(
                'statistics',
                {}
            ).get(
                'viewCount',
                0
            )
        )

        likes = int(

            video.get(
                'statistics',
                {}
            ).get(
                'likeCount',
                0
            )
        )

        comments = int(

            video.get(
                'statistics',
                {}
            ).get(
                'commentCount',
                0
            )
        )


        # VIDEO DURATION

        duration = video.get(

            'contentDetails',
            {}

        ).get(

            'duration',
            'Not Available'
        )


        # ENGAGEMENT RATE

        if views != 0:

            engagement_rate = (

                (likes + comments)
                / views

            ) * 100

        else:

            engagement_rate = 0


        # STORE VIDEO DATA

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

            "Engagement Rate (%)":
            round(
                engagement_rate,
                2
            )
        }


        # APPEND TO LIST

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

df.to_csv(

    "../data/youtube_advanced_data.csv",

    index=False
)


print(
    "Advanced YouTube data saved successfully!"
)