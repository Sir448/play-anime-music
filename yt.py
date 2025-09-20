import yt_dlp
import vlc
from time import sleep
import os
from dotenv import load_dotenv
from config import get_config

if not get_config("use-yt-dlp"):
    import googleapiclient.discovery

    load_dotenv()

    api_service_name = "youtube"
    api_version = "v3"
    YT_API_KEY = os.getenv("YT_API_KEY")

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=YT_API_KEY
    )


def get_video_id(search):
    request = youtube.search().list(
        part="id",
        maxResults=1,
        q=search + " lyrics",
        type="video",
        videoCategoryId="10",
    )
    response = request.execute()

    return response["items"][0]["id"]["videoId"]


def get_audio_url_ytapi(name):
    video_id = get_video_id(name)
    print(f"Video Id: {video_id}")
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {"format": "bestaudio/best", "quiet": True, "nocheckcertificate": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info["url"], info["title"], url


def get_audio_url_ytdlp(name):
    query = f"ytsearch1:{name} lyrics"
    ydl_opts = {"format": "bestaudio/best", "quiet": True, "nocheckcertificate": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        entries = ydl.extract_info(query, download=False)
        entry = entries["entries"][0]
        url = f"https://www.youtube.com/watch?v={entry['id']}"
        return entry["url"], entry["title"], url


def get_audio_url(name):
    if get_config("use-yt-dlp"):
        return get_audio_url_ytdlp(name)
    return get_audio_url_ytapi(name)


def format_duration(ms: int) -> str:
    total_seconds = ms // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"


def play_video(name, player):
    audio_url, title, video_url = get_audio_url(name)
    print("Retrieved Audio Url")
    media = vlc.Media(audio_url)
    player.set_media(media)
    player.play()
    while player.get_length() <= 0:
        sleep(0.1)
    player.set_time(0)
    print(f"Playing {title} {format_duration(player.get_length())}")
    print(f"YT: {video_url}")
