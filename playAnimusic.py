import json
import time
import threading

from random import choice

import vlc

from mal import refresh_token, gen_song, get_animes
from yt import get_video_id, play_video


INCLUDE_OPS = True
INCLUDE_EDS = True


player = vlc.MediaPlayer()
player.audio_set_volume(20)

def player_thread():
    while True:    
        try:
            name, anime, url = gen_song(access_token, choice(anime_ids))
            print(f"\n\nPlaying: {name}\n{anime}\nMAL: {url}")
            video_id = get_video_id(name)
            print(f"Video Id: {video_id}")
            play_video(video_id, player)
            while player.get_state() != vlc.State.Playing:
                time.sleep(0.1)

            while player.is_playing():
                time.sleep(0.5)
        except Exception as e:
            print("Error Occurred, Skipping to next song")



def command_loop():
    while True:
        while not player.is_playing():
            time.sleep(0.5)
        cmd = input("Enter Command:").strip().lower()
        state = player.get_state()
        if cmd == 'p' and state == vlc.State.Paused or cmd == 'play' or cmd == 'resume':
            player.play()
            print("Playing")
        elif cmd == 'p' or cmd == 'pause':
            player.pause()
            print("Paused")
        elif cmd == 'skip':
            player.stop()
            print("Skipped")
        elif cmd.startswith('v'):
            try:
                vol = int(cmd.split()[1])
                player.audio_set_volume(max(0, min(100, vol)))
                print(f"Volume set to {vol}%")
            except:
                print("Usage: volume <0-100>")
        elif cmd == 'quit' or cmd == 'q':
            player.stop()
            break
        elif cmd == 'help':
            print("""
Available commands:

  play             - Resume playback if paused
  pause            - Pause the current song
  skip             - Skip to the next song in the playlist
  volume <0-100>   - Set playback volume (0 = mute, 100 = max)
  help             - Show this help message
  quit             - Stop playback and exit the player
""")
        else:
            print("Unknown command. Type Help to get list of commands")

if __name__ == '__main__':
    # with open("token.json", 'r') as f:
    #     token = json.load(f)
        
    # access_token = token['access_token']
    # if token["expires_in"] < time.time():
    access_token = refresh_token()

    anime_ids = get_animes(access_token)

    thread = threading.Thread(target=player_thread, daemon=True)
    thread.start()
        
    command_loop()
    