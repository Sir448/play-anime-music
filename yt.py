
import yt_dlp
import vlc
from time import sleep

import os
from dotenv import load_dotenv
import googleapiclient.discovery


load_dotenv()

api_service_name = "youtube"
api_version = "v3"
YT_API_KEY=os.getenv("YT_API_KEY")

youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey = YT_API_KEY)


def get_video_id(search):
    request = youtube.search().list(
            part="id",
            maxResults=1,
            q=search + " audio",
            type="video",
            videoCategoryId="10"
        )
    response = request.execute()

    return response["items"][0]["id"]["videoId"]

def get_audio_url(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'nocheckcertificate': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info['url'], info['title']

def format_duration(ms: int) -> str:
    total_seconds = ms // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"

def play_video(video_id, player):
    audio_url, title = get_audio_url(video_id)
    print("Retrieved Audio Url")
    media = vlc.Media(audio_url)
    player.set_media(media)
    player.play()
    while player.get_length() <= 0:
        sleep(0.1)
    print(f"Playing {title} {format_duration(player.get_length())}")
