# src/spotify_api.py

import requests
import base64

def get_spotify_token(client_id, client_secret):
    auth_url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}"
    }
    data = {
        "grant_type": "client_credentials"
    }
    response = requests.post(auth_url, headers=headers, data=data)
    response_data = response.json()
    return response_data["access_token"]

def get_track_image(track_id, token):
    track_url = f"https://api.spotify.com/v1/tracks/{track_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(track_url, headers=headers)
    response_data = response.json()
    if "album" in response_data and "images" in response_data["album"]:
        return response_data["album"]["images"][0]["url"]  # URL de la imagen de mayor resolución
    return None
