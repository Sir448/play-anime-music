from time import sleep
import threading
from random import choice
import vlc
from config import get_config, set_config, save_config, update_config
from args import parse_args
from queue import Queue


instance = vlc.Instance('--no-video')
player = instance.media_player_new()
volume = get_config("volume", 20)
player.audio_set_volume(volume)

song_queue = Queue()

args = parse_args()
kwargs = {k: v for k, v in vars(args).items() if v is not None}
if kwargs:
    update_config(**kwargs)

INCLUDE_OPS = get_config("include_ops", True)
INCLUDE_EDS = get_config("include_eds", True)
SEARCH_PAGE_LIMIT = get_config("search_page_limit", 5)


from mal import refresh_token, gen_song, get_animes, search_animes, format_songs
from yt import play_video


def player_thread():
    print(f"Playing music at {volume}% volume")
    currentAnime, currentQueueCount = None, 1
    while True:
        try:
            if song_queue.empty():
                if currentAnime:
                    print("\nResuming random songs")
                currentAnime, currentQueueCount, originalQueueLength = None, 1, 1
                name, anime, url = gen_song(
                    access_token, choice(anime_ids), INCLUDE_OPS, INCLUDE_EDS
                )
                    
                    
                print("\n\n")
                print(f"🎵 Song:      {name}")
                print(f"📺 Anime:     {anime}")
                print(f"🔗 MAL:       {url}")
            else:
                name, anime, url, label = song_queue.get_nowait()
                if not currentAnime or currentAnime != anime:
                    print("\n\n")
                    print(f"📺 Anime:     {anime}")
                    print(f"🔗 MAL:       {url}")
                    currentAnime, currentQueueCount, originalQueueLength = anime, 1, song_queue.qsize() + 1
                    
                spaces = max(10 - len(label), 1)
                print(f"\n🎵 {label}:{" "*spaces}{name} [{currentQueueCount}/{originalQueueLength}]")
                currentQueueCount += 1
    
            play_video(name, player, instance)
            while player.get_state() != vlc.State.Playing:
                sleep(0.1)

            while player.get_state() in {vlc.State.Playing, vlc.State.Paused}:
                sleep(0.5)
        except Exception as e:
            print("Error Occurred, Skipping to next song")
            print(e)


def command_loop():
    while True:
        while player.get_state() not in {vlc.State.Playing, vlc.State.Paused}:
            sleep(0.5)
        cmd = input("Enter Command: ").strip().lower()
        state = player.get_state()
        if cmd == "p" and state == vlc.State.Paused or cmd == "play" or cmd == "resume":
            player.play()
            print("Playing")
        elif cmd == "p" or cmd == "pause":
            player.pause()
            print("Paused")
        elif cmd == "next" or cmd == "n":
            player.stop()
            print("Next Song")
        elif cmd == "restart" or cmd == "r":
            player.set_time(0)
            print("Restarted Song")
        elif cmd.startswith("v"):
            try:
                vol = int(cmd.split()[1])
                vol = max(0, min(100, vol))
                player.audio_set_volume(vol)
                set_config("volume", vol)
                print(f"Volume set to {vol}%")
            except:
                print("Usage: volume <0-100>")
        elif cmd.startswith("s"):
            try:
                # Get search term
                terms = cmd.split()
                if len(terms) < 2:
                    print("Usage: search <search term>")
                    continue
                search = " ".join(terms[1:])
                
                # Initial search results
                current_offset = 0
                results = search_animes(access_token, search, current_offset)
                print("Search Results:")
                for i, result in enumerate(results):
                    print(f"{i+1}) {result[1]}")
                
                # Command for what anime to play songs from
                while True:
                    cmd = input("Enter the number of the song to play, 'n' for next page, or 'q' to quit search: ")
                    # If anime is chosen
                    if cmd.isdigit():
                        index = int(cmd) - 1
                        if index >= len(results):
                            print("Song Number Invalid")
                            continue
                        # Get songs before removing old songs in case there's an error
                        songs = format_songs(access_token, results[index][0])
                        # Remove old songs
                        while not song_queue.empty():
                            song_queue.get_nowait()
                        # Add new songs
                        for song in songs:
                            song_queue.put(song)
                        player.stop()
                        break    
                    elif cmd.startswith('n'):
                        current_offset += SEARCH_PAGE_LIMIT
                        new_results = search_animes(access_token, search, current_offset)
                        results.extend(new_results)
                        for i, result in enumerate(new_results):
                            print(f"{i+current_offset+1}) {result[1]}")
                    elif cmd.startswith('q'):
                        break
                    else:
                        print("Invalid Command")
            except Exception as e:
                print("Error Occurred, Continuing current song")
                print(e)
        elif cmd == "quit" or cmd == "q":
            player.stop()
            break
        elif cmd == "help":
            print(
                """
Available commands:

  play             - Resume playback if paused
  pause            - Pause the current song
  next             - Skip to the next song in the playlist
  restart            - Return to the beginning of the song
  volume <0-100>   - Set playback volume (0 = mute, 100 = max)
  help             - Show this help message
  quit             - Stop playback and exit the player
"""
            )
        else:
            print("Unknown command. Type Help to get list of commands")


if __name__ == "__main__":
    access_token = refresh_token()

    anime_ids = get_animes(access_token)

    thread = threading.Thread(target=player_thread, daemon=True)
    thread.start()

    command_loop()
    save_config()
