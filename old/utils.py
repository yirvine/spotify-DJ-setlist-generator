import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def get_access_token():
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    auth_response = requests.post(
        'https://accounts.spotify.com/api/token',
        {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
        }
    )
    auth_response_data = auth_response.json()
    return auth_response_data['access_token']

def get_playlist_tracks(playlist_id, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    tracks = []
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    while url:
        response = requests.get(url, headers=headers)
        json_response = response.json()
        tracks.extend(json_response['items'])
        url = json_response.get('next')  # A new page of tracks, if available
    return tracks

def fetch_track_details(track_id, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    track_details_response = requests.get(f'https://api.spotify.com/v1/tracks/{track_id}', headers=headers)
    track_details_data = track_details_response.json()
    features_response = requests.get(f'https://api.spotify.com/v1/audio-features/{track_id}', headers=headers)
    features_data = features_response.json()
    track_data = {
        'name': track_details_data.get('name', 'Unknown'),
        'artists': track_details_data['artists'][0]['name'] if track_details_data.get('artists') else 'Unknown',
        'key': features_data.get('key', -1),
        'mode': features_data.get('mode', -1),
        'danceability': features_data.get('danceability', 0),
        'energy': features_data.get('energy', 0)
    }
    return track_data
