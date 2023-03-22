from moviepy.editor import *


class VideoEditor:
    """
    A class that represents a video editor.
    """

    def __init__(self, file_path: str) -> None:
        """
        Constructs all the necessary attributes for the VideoEditor object.

        Parameters:
        file_path (str): The path of the video file.
        """

        self.video = VideoFileClip(file_path, target_resolution=(1920,1080))
        self.length = self.video.duration
        self.file_name = self.video.filename
        self.width, _ = self.video.size

    def create_subclip_with_text(self, start: float, end: float, text: str) -> CompositeVideoClip:
        """
        Creates a subclip with text.

        Parameters:
        start (float): The start time of the subclip.
        end (float): The end time of the subclip.
        text (str): The text to be displayed on the subclip.

        Returns:
        CompositeVideoClip: A composite video clip with the subclip and the text.
        """

        subclip = self.video.subclip(start, end)
        text_clip_size = 200
        x_pos = self.width // 2 - text_clip_size // 2
        y_pos = 250

        text_clip = (
            TextClip(text, fontsize=150, color='white', bg_color='gray35', size=(text_clip_size, 0), font='Lane')
            .set_opacity(0.5)
            .set_duration(4)
            .crossfadein(0.5)
            .crossfadeout(0.5)
            .set_position((x_pos, y_pos))
        )


        composite_clip = CompositeVideoClip([subclip, text_clip])
        return composite_clip

    def save_clips_with_text_by_duration(self, num_clips: int, clip_duration: float, file_name: str) -> None:
        """
        Saves multiple clips with text based on the duration of each clip.

        Parameters:
        num_clips (int): The number of clips to be created.
        clip_duration (float): The duration of each clip.
        file_name (str): The name of the output file.
        """

        for i in range(num_clips):
            start = i * clip_duration
            end = start + clip_duration
            subclip = self.create_subclip_with_text(start, end,f" Part {i+1}/{num_clips}")
            subclip_file_name = f"{file_name}_Part{i+1}.mp4"
            subclip.write_videofile(subclip_file_name)

    def save_clips_with_text(self, num_clips: int) -> None:
        """
        Saves multiple clips with text.

        Parameters:
        num_clips (int): The number of clips to be created.
        """

        # Create clips directory if it does not exist
        if not os.path.exists("clips"):
            os.makedirs("clips")

        # Create self.file_name directory if it does not exist
        file_name_no_ext = os.path.splitext(self.file_name)[0]
        file_directory = os.path.join("clips", file_name_no_ext)
        if not os.path.exists(file_directory):
            os.makedirs(file_directory)

        clip_duration = self.length / num_clips
        for i in range(num_clips):
            start = i * clip_duration
            end = min(start + clip_duration, self.length)
            subclip = self.create_subclip_with_text(start, end, f" Part {i + 1}/{num_clips}")
            subclip_file_name = f"{self.file_name}_Part{i + 1}.mp4"
            subclip_path = os.path.join(file_directory, subclip_file_name)
            subclip.write_videofile(subclip_path)

l = VideoEditor('Adnan Confronts A Group Of Hindutva! Adnan and Visitor Speakers Corner.mp4')
l.save_clips_with_text(3)