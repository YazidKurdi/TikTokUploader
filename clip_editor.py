from moviepy.editor import *
import os


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

        self.video = VideoFileClip(file_path)
        self.length = self.video.duration
        self.file_name = os.path.splitext(os.path.basename(self.video.filename))[0]

        self.crop_video(self.width, self.height)
        self.resize_video(1080, 1920)

    @property
    def width(self):
        return self.video.size[0]

    @property
    def height(self):
        return self.video.size[1]
    def crop_video(self, width, height):
        crop_width = width * 1920 / 1080
        x1, x2 = (width - crop_width) // 2, (width + crop_width) // 2
        y1, y2 = 0, height
        self.video = vfx.crop(self.video, x1=x1, y1=y1, x2=x2, y2=y2)

    def resize_video(self, width, height):
        self.video = self.video.resize((width, height))

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
        margin = 50  # Margin from the edges of the frame

        # Calculate the position of the title text
        title_text_clip_size = 450
        title_text_clip = TextClip(
            self.file_name,
            color="#fce303",
            size=(title_text_clip_size, None),
            fontsize=50,
            font="Amiri-bold",
            align="center",
            method="caption",
        )
        title_text_clip = title_text_clip.set_opacity(0.7).set_duration(7)
        title_text_clip = (
            title_text_clip.crossfadein(0.5)
            .crossfadeout(0.5)
            .set_position((self.width // 2 - title_text_clip.w // 2, margin + title_text_clip.h // 2))
        )

        # Calculate the position of the order text
        padding = 150
        order_text_clip_size = 300
        order_text_clip = TextClip(
            text,
            color="#fce303",
            size=(title_text_clip_size, None),
            fontsize=50,
            font="Amiri-bold",
            align="center",
            method="caption",
        )
        order_text_clip = order_text_clip.set_opacity(0.7).set_duration(7)
        order_text_clip = (
            order_text_clip.crossfadein(0.5)
            .crossfadeout(0.5)
            .set_position((self.width // 2 - order_text_clip.w // 2,title_text_clip.h + margin + padding))
        )



        composite_clip = CompositeVideoClip([subclip, order_text_clip,title_text_clip])
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
            subclip.write_videofile(subclip_path,bitrate='2000k')

l = VideoEditor('Adnan Confronts A Group Of Hindutva! Adnan and Visitor Speakers Corner.mp4')
l.save_clips_with_text(40)