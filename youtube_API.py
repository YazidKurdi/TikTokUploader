import configparser
import json
import os
import config
import pickle
import re
from googleapiclient.discovery import build

class YouTubeVideoSaver:
    def __init__(self, api_key: str):
        """Initializes a new instance of the YouTubeVideoSaver class.

        Args:
            api_key (str): The API key to be used to access the YouTube API.

        Returns:
            None
        """
        self.api_key = api_key

        # Create a new instance of the YouTube API client
        self.youtube = build('youtube', 'v3', developerKey=config.youtube_api)

        # Set the file path to the file where videos metadata will be saved
        self.file_path = "to_download/videos_to_download.pickle" # Currently, not doing anything

        # Set the directory path where video metadata will be saved
        directory_path = "./to_download" # Currently, not doing anything


        # Load videos metadata from file
        self.videos = self.load_videos()

    def load_videos(self) -> dict:
        """
        Loads the video data from the pickled file and returns it as a dictionary.

        Returns:
        videos (dict): A dictionary containing the video data.
        """
        # Check if the pickled file exists
        if os.path.isfile(self.file_path): # Currently, not doing anything
            with open(self.file_path, "rb") as f:
                # Load the pickled file and return its content as a dictionary
                videos = pickle.load(f)
                return json.loads(videos)
        else:
            # If the pickled file does not exist, return an empty dictionary
            return dict()

    def duration_string_to_seconds(self, duration_string: str) -> int:
        """
        Converts a duration string of the form 'PT#H#M#S' to the number of seconds.

        Args:
        duration_string (str): The duration string to convert.

        Returns:
        int: The duration in seconds.
        """
        # Parse the duration string using a regular expression
        match = re.match('PT(\d+H)?(\d+M)?(\d+S)?', duration_string)

        # Extract the hours, minutes, and seconds from the match groups, and convert them to integers
        hours = int(match.group(1)[:-1]) if match.group(1) else 0
        minutes = int(match.group(2)[:-1]) if match.group(2) else 0
        seconds = int(match.group(3)[:-1]) if match.group(3) else 0

        # Calculate the total duration in seconds and return it
        return hours * 3600 + minutes * 60 + seconds

    def return_channel_metadata(self, channel_id: str, max_results: int = 50) -> None:
        """
        Retrieves metadata of the most popular short videos for a given channel ID
        and adds the video data to the self.videos dictionary.

        Args:
            channel_id (str): The ID of the channel to retrieve video metadata for.
            max_results (int): The maximum number of videos to retrieve (default 50).

        Returns:
            None
        """
        # Call the YouTube API to get the most popular short videos for the given channel ID
        request = self.youtube.search().list(
            part="id,snippet",
            channelId=channel_id,
            maxResults=max_results,
            type="video",
            order="viewCount"
        )
        response = request.execute()

        # Iterate through each video in the response
        for item in response['items']:
            video_id = item['id']['videoId']

            # Get the duration of the video
            video_duration = \
            self.youtube.videos().list(id=video_id, part='contentDetails').execute()['items'][0]['contentDetails'][
                'duration']

            # Convert the duration from ISO 8601 format to seconds
            duration_in_seconds = self.duration_string_to_seconds(video_duration)

            # Check if the video is short (10 minutes or less)
            if duration_in_seconds <= 600:
                video_title = item['snippet']['title']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                channel_title = item['snippet']['channelTitle']
                is_short = duration_in_seconds <= 60

                # Create a dictionary of the video data
                video_data = {'title': video_title, 'url': video_url, 'is_short': is_short}

                # Add the video data to the self.videos dictionary
                if channel_title not in self.videos:
                    self.videos[channel_title] = {}
                if video_id not in self.videos[channel_title]:
                    self.videos[channel_title][video_id] = video_data

    def save_videos_to_file(self, file_path: str) -> None:
        """
        Save the updated videos dictionary to a file.

        Args:
            file_path (str): The path of the file where to save the videos dictionary.

        Returns:
            None

        """
        # convert the dictionary to JSON
        json_data = json.dumps(self.videos, indent=4)

        # Save the updated videos dictionary to disk
        with open(file_path, "wb") as f:
            pickle.dump(json_data, f)

    def process_all_channels(self):
        """
        Processes all the channels in the channels.ini file.

        Reads the channels.ini configuration file to get a list of channels to process.
        For each channel, it creates a directory to store the videos to download.
        Then, it retrieves metadata about the channel and saves it to a pickle file.
        The name of the pickle file includes the name of the channel.

        Args:
            None

        Returns:
            None
        """
        config = configparser.ConfigParser()
        config.read('channels.ini')

        # Loop over all the sections in the channels.ini file
        for section in config.sections():
            try:
                # Create the directory to store the videos to download
                if not os.path.exists(f"to_download/{section}"):
                    os.makedirs(f"to_download/{section}")
            except OSError as error:
                print(f"Failed to create directory: {error}")

            # Loop over all the channel IDs in the section
            for channel_id in config[section].values():
                # Retrieve the channel metadata and save it to a file
                self.return_channel_metadata(channel_id,50)
                self.save_videos_to_file(f"to_download/{section}/videos_to_download_{section}.pickle")


    def print_video_titles_and_urls(self):
        # Print out the list of video titles and URLs
        for channel_title, videos in self.videos.items():
            for video in videos:
                print(f"{video['title']}: {video['url']}")

l = YouTubeVideoSaver(config.youtube_api)
l.process_all_channels()