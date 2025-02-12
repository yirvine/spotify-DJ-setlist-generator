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

# Replace 'spotify_song_id' with the Spotify ID of the song you want to get data for
song_id = '0RXspLL7GwiGm9KIDdT0ma'
song_response = requests.get(f'https://api.spotify.com/v1/tracks/{song_id}', headers=headers)
song_data = song_response.json()


# Extract specific song details
song_name = song_data['name']
artist_name = song_data['artists'][0]['name']  # Assuming there is at least one artist
popularity = song_data['popularity']
release_date = song_data['album']['release_date']
explicit = song_data['explicit']

# Display song details
print(f"Song Name: {song_name}")
print(f"Artist Name: {artist_name}")
print(f"Popularity: {popularity}")
print(f"Release Date: {release_date}")
print(f"Explicit: {explicit}")

# Fetching audio features for the track
features_response = requests.get(f'https://api.spotify.com/v1/audio-features/{song_id}', headers=headers)
features_data = features_response.json()

# Extract specific features
energy = features_data['energy']
danceability = features_data['danceability']
key = features_data['key']
loudness = features_data['loudness']
mode = features_data['mode']
speechiness = features_data['speechiness']
instrumentalness = features_data['instrumentalness']
tempo = features_data['tempo']
time_signature = features_data['time_signature']

# Display audio features
print(f"Energy: {energy}")
print(f"Danceability: {danceability}")
print(f"Key: {key}")
print(f"Loudness: {loudness}")
print(f"Mode: {mode}")
print(f"Speechiness: {speechiness}")
print(f"Instrumentalness: {instrumentalness}")
print(f"Tempo: {tempo}")
print(f"Time Signature: {time_signature}")