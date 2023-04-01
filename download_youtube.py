import json
import os
import pickle
from pytube import YouTube


class VideoDownloader:
    def __init__(self):
        self.to_download_path = "to_download/DAWAH/videos_to_download_DAWAH.pickle"
        self.directory_path = "downloaded_videos"
        self.downloaded_videos_path = os.path.join(self.directory_path, "downloaded_videos.pickle")
        self.downloaded_videos_set = self.load_downloaded_videos_set()

        try:
            # Check if the directory exists
            if not os.path.exists(self.directory_path):
                # Create the directory
                os.makedirs(self.directory_path)
        except OSError as error:
            print(f"Failed to create directory: {error}")

    def load_downloaded_videos_set(self):
        # Load the set of downloaded videos from a file, or create a new set
        if os.path.isfile(self.downloaded_videos_path) and os.path.getsize(self.downloaded_videos_path) > 0:
            with open(self.downloaded_videos_path, "rb") as f:
                return pickle.load(f)
        else:
            return set()

    def download_videos(self):
        # Load the JSON object
        with open(self.to_download_path, "rb") as f:
            data = pickle.load(f)

        # Loop over each channel and video, downloading videos that haven't been downloaded yet
        for channel, videos in data.items():

            channel_path = os.path.join(self.directory_path, channel)
            # Create a directory for the channel if it doesn't exist
            try:
                if not os.path.exists(channel_path):
                    os.makedirs(channel_path)
            except OSError as error:
                print(f"Failed to create directory for channel {channel}: {error}")
                continue

            print(f"Channel: {channel}")
            for video_id, video_data in videos.items():
                print(f"Title: {video_data['title']}")
                url = video_data['url']
                if video_id not in self.downloaded_videos_set:
                    yt = YouTube(url)
                    print(f"Downloading video {video_id}...")
                    try:
                        video_path = os.path.join(channel_path, f"{video_id}.mp4")
                        # Download the video to the channel directory
                        yt.streams.filter(progressive=True, file_extension='mp4').order_by(
                            'resolution').desc().first().download(output_path=channel_path)
                        # Add the downloaded video to the set and save the set to a file
                        self.downloaded_videos_set.add(video_id)
                        with open(self.downloaded_videos_path, "wb") as f:
                            pickle.dump(self.downloaded_videos_set, f)
                    except FileNotFoundError as error:
                        print(f"Failed to download video {video_id}: {error}")
                    else:
                        print(f"Video {video_id} downloaded successfully.")
                else:
                    print(f"Video {video_id} has already been downloaded.")

if __name__ == "__main__":
    downloader = VideoDownloader()
    downloader.download_videos()