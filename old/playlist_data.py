import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Spotify API credentials
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

# Get token
auth_response = requests.post(
    'https://accounts.spotify.com/api/token',
    {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    }
)
auth_response_data = auth_response.json()
access_token = auth_response_data['access_token']

# Use the token to access the API
headers = {
    'Authorization': f'Bearer {access_token}',
}

# Function to get tracks from a playlist
def get_playlist_tracks(playlist_id):
    tracks = []
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    while url:
        response = requests.get(url, headers=headers)
        json_response = response.json()
        tracks.extend(json_response['items'])
        url = json_response.get('next')  # A new page of tracks, if available
    return tracks

# Your playlist ID
playlist_id = '5jJKoLaJ3YboeBsAuba76K'  # Replace with your playlist ID

# Fetching tracks from the playlist
playlist_tracks = get_playlist_tracks(playlist_id)

# Loop through each track and print details and features
for track in playlist_tracks:
    track_id = track['track']['id']
    track_details_response = requests.get(f'https://api.spotify.com/v1/tracks/{track_id}', headers=headers)
    track_details_data = track_details_response.json()

    # Extract and print song details
    print(f"\nSong Name: {track_details_data['name']}")
    print(f"Artist Name: {track_details_data['artists'][0]['name']}")  # Assuming at least one artist
    print(f"Popularity: {track_details_data['popularity']}")
    print(f"Release Date: {track_details_data['album']['release_date']}")
    print(f"Explicit: {track_details_data['explicit']}")

    # Fetch and print audio features
    features_response = requests.get(f'https://api.spotify.com/v1/audio-features/{track_id}', headers=headers)
    features_data = features_response.json()
    print(f"Energy: {features_data['energy']}")
    print(f"Danceability: {features_data['danceability']}")
    print(f"Key: {features_data['key']}")
    print(f"Loudness: {features_data['loudness']}")
    print(f"Mode: {features_data['mode']}")
    print(f"Speechiness: {features_data['speechiness']}")
    print(f"Instrumentalness: {features_data['instrumentalness']}")
    print(f"Tempo: {features_data['tempo']}")
    print(f"Time Signature: {features_data['time_signature']}")
