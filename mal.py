import json
import requests
import time
import re

import os
from dotenv import load_dotenv
from random import randint
from auth import get_new_token
from config import get_config

load_dotenv()

MAL_CLIENT_ID = os.getenv("MAL_CLIENT_ID")
MAL_CLIENT_SECRET = os.getenv("MAL_CLIENT_SECRET")


def refresh_token():
    """
    Refreshes the MAL access token stored in token.json if expired.
    Uses MAL_CLIENT_ID and MAL_CLIENT_SECRET from environment variables.
    """
    if not os.path.exists("token.json"):
        return get_new_token()

    # Load existing token
    with open("token.json", "r", encoding="utf-8") as f:
        token_data = json.load(f)

    # Track when the token was obtained
    if "obtained_at" not in token_data:
        token_data["obtained_at"] = int(time.time())

    # Check if expired
    current_time = int(time.time())
    expiry_time = token_data["obtained_at"] + token_data["expires_in"]
    if current_time < expiry_time - 10:  # refresh a bit early
        return token_data["access_token"]  # still valid

    # Refresh token
    refresh_url = "https://myanimelist.net/v1/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": token_data["refresh_token"],
        "client_id": MAL_CLIENT_ID,
        "client_secret": MAL_CLIENT_SECRET,
    }

    resp = requests.post(refresh_url, data=data)
    if resp.status_code != 200:
        raise Exception(f"Failed to refresh token: {resp.text}")

    new_token = resp.json()
    new_token["obtained_at"] = int(time.time())

    # Save updated token
    with open("token.json", "w", encoding="utf-8") as f:
        json.dump(new_token, f, indent=4)

    print("Token refreshed successfully.")
    return new_token["access_token"]




def process_name_for_youtube(raw_name: str) -> str:
    # # Remove leading number with optional '#' and colon
    # cleaned = re.sub(r"^#?\d+:\s*", "", raw_name.strip())

    # Keep only from the first quote onward
    if '"' in raw_name:
        cleaned = raw_name[raw_name.index('"'):]
    else:
        cleaned = raw_name.strip()

    # Iteratively remove () and [] groups (non-nested only each pass)
    pattern = re.compile(r"\s*(\([^()]*\)|\[[^\[\]]*\])")
    while pattern.search(cleaned):
        cleaned = pattern.sub("", cleaned).strip()

    # Replace multiple spaces with a single space
    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned

# https://api.myanimelist.net/v2/users/@me/animelist?fields=anime_title&status=watching
# https://api.myanimelist.net/v2/users/@me/animelist?fields=anime_title&status=completed


# get list of anime ids for both completed and watching
def get_animes(access_token: str):
    completed, watching = get_stats(access_token)
    url = f"https://api.myanimelist.net/v2/users/@me/animelist?sort=anime_start_date&status=completed&limit={completed}"

    response = requests.get(url, headers={"Authorization": f"Bearer {access_token}"})
    data = response.json()

    completedIds = [x["node"]["id"] for x in data["data"]]

    url = f"https://api.myanimelist.net/v2/users/@me/animelist?sort=anime_start_date&status=watching&limit={watching}"

    response = requests.get(url, headers={"Authorization": f"Bearer {access_token}"})
    data = response.json()

    watchingIds = [x["node"]["id"] for x in data["data"]]

    return completedIds + watchingIds


# get number of animes completed and currently watching
def get_stats(access_token: str):
    url = f"https://api.myanimelist.net/v2/users/@me?fields=anime_statistics"

    response = requests.get(url, headers={"Authorization": f"Bearer {access_token}"})
    data = response.json()
    print(f"Playing from {data['name']}'s list")
    return (
        data["anime_statistics"]["num_items_completed"],
        data["anime_statistics"]["num_items_watching"],
    )


class NoSongsFound(Exception):
    """Raised when an anime has no opening or ending themes."""
    pass


def gen_song(access_token: str, anime_id: int, include_ops=True, include_eds=True):
    url = f"https://api.myanimelist.net/v2/anime/{anime_id}?fields=id,title,opening_themes,ending_themes"
    response = requests.get(url, headers={"Authorization": f"Bearer {access_token}"})
    data = response.json()

    opening_themes = data.get("opening_themes", []) if include_ops else []
    ending_themes = data.get("ending_themes", []) if include_eds else []

    if opening_themes or ending_themes:
        combined = opening_themes + ending_themes
        idx = randint(0, len(combined) - 1)
        theme = combined[idx]["text"]

        # Determine if it's an OP or ED
        if idx < len(opening_themes):
            label = f"OP #{idx + 1}"
        else:
            label = f"ED #{idx - len(opening_themes) + 1}"

        return (
            process_name_for_youtube(theme),
            f"{data.get('title', 'Unknown')} ({label})",
            f"https://myanimelist.net/anime/{anime_id}/",
        )
    else:
        raise NoSongsFound(f"{data['title']} has no OPs or EDs.\nhttps://myanimelist.net/anime/{anime_id}/")

