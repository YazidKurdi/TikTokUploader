from pytube import YouTube

yt = YouTube('https://www.youtube.com/watch?v=wmpSwtWFc20ab_channel=SamDawah').streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download()

