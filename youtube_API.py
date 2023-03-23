import configparser
import json
import os
import config
import pickle
import re
from googleapiclient.discovery import build

class YouTubeVideoSaver:
    def __init__(self, api_key):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=config.youtube_api)
        self.file_path = "videos_to_download.pickle"

        if os.path.isfile("videos_to_download.pickle"):
            with open("videos_to_download.pickle", "rb") as f:
                self.videos = pickle.load(f)
                self.videos = json.loads(self.videos)
        else:
            self.videos = {}

    def duration_string_to_seconds(self, duration_string):
        match = re.match('PT(\d+H)?(\d+M)?(\d+S)?', duration_string)
        hours = int(match.group(1)[:-1]) if match.group(1) else 0
        minutes = int(match.group(2)[:-1]) if match.group(2) else 0
        seconds = int(match.group(3)[:-1]) if match.group(3) else 0
        return hours * 3600 + minutes * 60 + seconds

    def return_channel_metadata(self,channel_id,max_results=50):
        # Call the YouTube API to get the most popular short videos for the given channel ID
        request = self.youtube.search().list(
            part="id,snippet",
            channelId=channel_id,
            maxResults=max_results,
            type="video",
            order="viewCount"
        )
        response = request.execute()

        for item in response['items']:
            video_id = item['id']['videoId']
            video_duration = self.youtube.videos().list(id=video_id, part='contentDetails').execute()['items'][0]['contentDetails']['duration']
            duration_in_seconds = self.duration_string_to_seconds(video_duration)
            if duration_in_seconds <= 600:
                video_title = item['snippet']['title']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                channel_title = item['snippet']['channelTitle']
                is_short = duration_in_seconds <= 60
                video_data = {'title': video_title, 'url': video_url, 'is_short': is_short}
                if channel_title not in self.videos:
                    self.videos[channel_title] = [video_data]
                else:
                    self.videos[channel_title].append(video_data)

    def save_videos_to_file(self):
        # convert the dictionary to JSON
        json_data = json.dumps(self.videos, indent=4)

        # Save the updated videos dictionary to disk
        with open(self.file_path, "wb") as f:
            pickle.dump(json_data, f)

    def process_all_channels(self):
        config = configparser.ConfigParser()
        config.read('channels.ini')

        for section in config.sections():
            for channel_id in config[section].values():
                print(channel_id)
                self.return_channel_metadata(channel_id)
        self.save_videos_to_file()

    def print_video_titles_and_urls(self):
        # Print out the list of video titles and URLs
        for channel_title, videos in self.videos.items():
            for video in videos:
                print(f"{video['title']}: {video['url']}")

l = YouTubeVideoSaver(config.youtube_api)
l.process_all_channels()