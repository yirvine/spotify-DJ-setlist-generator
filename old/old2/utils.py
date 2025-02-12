# # utils.py

# import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials
# import pandas as pd
# import os
# from dotenv import load_dotenv

# def get_spotify_client():
#     load_dotenv()
#     client_id = os.getenv('SPOTIFY_CLIENT_ID')
#     client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
#     # Debugging: Print the environment variables
#     print("Client ID:", client_id)
#     print("Client Secret:", client_secret)
    
#     if not client_id or not client_secret:
#         raise ValueError("Missing Spotify client ID or client secret.")
    
#     auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
#     sp = spotipy.Spotify(auth_manager=auth_manager)
#     return sp

# def get_playlist_tracks(sp, playlist_id):
#     results = sp.playlist_tracks(playlist_id)
#     tracks = results['items']
#     while results['next']:
#         results = sp.next(results)
#         tracks.extend(results['items'])
#     return tracks

# def extract_features_from_playlist(sp, playlist_id):
#     tracks = get_playlist_tracks(sp, playlist_id)
#     track_features = []
#     for item in tracks:
#         track = item['track']
#         features = sp.audio_features(track['id'])[0]
#         track_features.append({
#             'name': track['name'],
#             'artist': track['artists'][0]['name'],
#             'key': features['key'],
#             'mode': features['mode'],
#             'tempo': features['tempo'],
#             'danceability': features['danceability'],
#             'energy': features['energy']
#         })
#     return pd.DataFrame(track_features)

# utils.py

# utils.py
# utils.py

import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
import pandas as pd

def get_spotify_client():
    load_dotenv()
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        raise ValueError("Missing Spotify client ID or client secret.")
    
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    return sp

def get_playlist_tracks(sp, playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

def extract_features_from_playlist(sp, playlist_id):
    tracks = get_playlist_tracks(sp, playlist_id)
    track_ids = [track['track']['id'] for track in tracks]

    track_features = []
    batch_size = 20

    for i in range(0, len(track_ids), batch_size):
        batch_ids = track_ids[i:i+batch_size]
        features = None

        # Retry mechanism with exponential backoff
        for retry in range(10):
            try:
                features = sp.audio_features(batch_ids)
                break  # Exit retry loop if request is successful
            except spotipy.exceptions.SpotifyException as e:
                if e.http_status == 429:
                    retry_after = int(e.headers.get('Retry-After', 1))
                    print(f"Rate limited. Retrying in {retry_after} seconds...")
                    time.sleep(retry_after)
                else:
                    raise e
            except Exception as e:
                raise e
            time.sleep(2 ** retry)  # Exponential backoff

        if features:
            for j, feature in enumerate(features):
                if feature is not None:
                    track = tracks[i + j]['track']
                    track_features.append({
                        'name': track['name'],
                        'artist': track['artists'][0]['name'],
                        'key': feature['key'],
                        'mode': feature['mode'],
                        'tempo': feature['tempo'],
                        'danceability': feature['danceability'],
                        'energy': feature['energy']
                    })

    return pd.DataFrame(track_features)
