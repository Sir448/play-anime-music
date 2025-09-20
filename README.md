# Anime Music Player

This Python script plays songs from your MyAnimeList (MAL) anime list. It automatically fetches opening and ending themes from your completed and currently watching anime and streams them from YouTube.

### Features:

- Optionally include openings (--include-ops) and/or endings (--include-eds).
- Plays songs, allowing pause, resume, and skip commands.
- Command-line interface for easy control while music is playing.

### Setup:

1. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2. Install [VLC](https://www.videolan.org/vlc/)

3. Create a client in the [MAL API](https://myanimelist.net/apiconfig)

4. Add your **Client ID** and **Client Secret** to a `.env` file:
    ```text
    MAL_CLIENT_ID=your_client_id
    MAL_CLIENT_SECRET=your_client_secret
    ```

5. (Optional) Get a [YouTube API key](https://developers.google.com/youtube/v3/getting-started) and add it to `.env`:
    ```text
    YT_API_KEY=your_api_key
    ```
    > Only needed if you want to search with YouTube API instead of YT-DLP.

6. Run the script:
    ```bash
    python playAnimusic.py
    ```

### TODO

- Seeking
- Skip around song
- UI
    - Anime Thumbnails



