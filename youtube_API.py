import os
import pickle
import re
from googleapiclient.discovery import build

def duration_string_to_seconds(duration_string):
    match = re.match('PT(\d+H)?(\d+M)?(\d+S)?', duration_string)
    hours = int(match.group(1)[:-1]) if match.group(1) else 0
    minutes = int(match.group(2)[:-1]) if match.group(2) else 0
    seconds = int(match.group(3)[:-1]) if match.group(3) else 0
    return hours * 3600 + minutes * 60 + seconds

# Set up the API client
api_key = 'AIzaSyDNYvOgovBehCXZa9aFnc11fT7rarX1HTg'
youtube = build('youtube', 'v3', developerKey=api_key)


# Load the saved videos dictionary from disk, if it exists
if os.path.isfile("videos_to_download.pickle"):
    with open("videos_to_download.pickle", "rb") as f:
        videos = pickle.load(f)
else:
    videos = {}

# Set up the search parameters
channel_id = 'UCQwkEQ6EQc4jM2QnrvubBHg'
max_results = 50
order_by = "viewCount"

# Call the YouTube API to get the most popular short videos for the given channel ID
request = youtube.search().list(
    part="id,snippet",
    channelId=channel_id,
    maxResults=max_results,
    type="video",
    order=order_by
)
response = request.execute()

# Update the videos dictionary with any new videos we found
for item in response['items']:
    video_id = item['id']['videoId']
    video_duration = youtube.videos().list(id=video_id, part='contentDetails').execute()['items'][0]['contentDetails']['duration']
    duration_in_seconds = duration_string_to_seconds(video_duration)
    if duration_in_seconds <= 600:
        video_title = item['snippet']['title']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        if video_url not in videos:
            videos[video_url] = video_title


# Save the updated videos dictionary to disk
with open("videos_to_download.pickle", "wb") as f:
    pickle.dump(videos, f)

# Print out the list of video titles and URLs
for video_url, video_title in videos.items():
    print(f"{video_title}: {video_url}")

