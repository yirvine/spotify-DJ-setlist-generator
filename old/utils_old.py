import requests
import random
import pandas as pd
import time


def get_access_token(client_id, client_secret):
    auth_response = requests.post(
        'https://accounts.spotify.com/api/token',
        {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
        }
    )
    return auth_response.json().get('access_token')

# def get_playlist_tracks(playlist_id, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    tracks = []
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    while url:
        response = requests.get(url, headers=headers)
        json_response = response.json()
        # Debugging: print raw response to check what's being received
        print("API Response:", json_response)

        tracks.extend([{
            'id': item['track']['id'],
            'name': item['track']['name'],
            'artists': item['track']['artists'][0]['name'] if item['track']['artists'] else 'Unknown',
            'danceability': 0,  # Placeholder, actual value fetched later
            'energy': 0,  # Placeholder, actual value fetched later
        } for item in json_response['items'] if 'track' in item])

        url = json_response.get('next')
    
    # Debugging: Print tracks list before fetching additional details
    print("Tracks before fetching additional details:", tracks)

    tracks = fetch_additional_track_details(tracks, access_token)
    # Debugging: Print tracks list after fetching additional details
    print("Tracks after fetching additional details:", tracks)

    return tracks

#use these two functions instead:
def get_track_ids(playlist_id, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    track_ids = []
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    while url:
        response = requests.get(url, headers=headers)
        data = response.json()
        track_ids.extend([item['track']['id'] for item in data['items'] if item['track'] and item['track']['id']])
        url = data.get('next')
    return track_ids


import time

def get_tracks_features(track_ids, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    features = []
    batch_size = 1  # Max size per Spotify's documentation

    for i in range(0, len(track_ids), batch_size):
        batch_ids = track_ids[i:i+batch_size]
        success = False
        while not success:
            url = f"https://api.spotify.com/v1/audio-features?ids={','.join(batch_ids)}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                features.extend([feat for feat in data['audio_features'] if feat])
                success = True
            elif response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 150))  # Default to 10 seconds if header is missing
                print(f"Rate limit exceeded, waiting {retry_after} seconds...")
                time.sleep(retry_after)
            else:
                print("Error fetching features:", response.json().get('error', 'Unknown Error'))
                break

    return features



def fetch_additional_track_details(tracks, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    for track in tracks:
        additional_response = requests.get(f"https://api.spotify.com/v1/tracks/{track['id']}", headers=headers)
        additional_data = additional_response.json()
        if 'error' in additional_data:
            print(f"Error fetching track details for {track['id']}: {additional_data['error']}")
            continue  # Skip this track

        features_response = requests.get(f"https://api.spotify.com/v1/audio-features/{track['id']}", headers=headers)
        features_data = features_response.json()
        if 'error' in features_data:
            print(f"Error fetching features for track {track['id']}: {features_data['error']}")
            continue  # Skip this track

        track.update({
            'name': additional_data.get('name', 'Unknown'),
            'artists': additional_data['artists'][0]['name'] if additional_data.get('artists') else 'Unknown',
            'key': features_data.get('key', -1),
            'mode': features_data.get('mode', -1),
            'tempo': features_data.get('tempo', 0)
        })
    return tracks

def calculate_hype_and_filter(tracks, top_n=30):
    for track in tracks:
        track['hype'] = track['danceability'] + track['energy']  # Calculate 'hype'
    sorted_tracks = sorted(tracks, key=lambda x: x['hype'], reverse=True)
    return sorted_tracks[:top_n]  # Return only the top 'n' tracks based on 'hype'

def generate_sequence(tracks, num_initial_high_hype=8, final_hype_count=20):
    from pandas import DataFrame
    import heapq  # For maintaining a min-heap if needed
    import random

    # Sorting tracks by 'hype'
    sorted_tracks = sorted(tracks, key=lambda x: x['hype'], reverse=True)
    initial_high_hype_tracks = sorted_tracks[:num_initial_high_hype]
    final_high_hype_tracks = sorted_tracks[-final_hype_count:]

    # Start sequence with a random high 'hype' track from the top initial choices
    sequence = [random.choice(initial_high_hype_tracks)]
    used_ids = {sequence[0]['id']}

    # Use a priority queue to manage candidates by their 'hype'
    middle_tracks = [track for track in sorted_tracks[num_initial_high_hype:-final_hype_count] if track not in initial_high_hype_tracks]
    candidates = [(track['hype'], track) for track in middle_tracks if is_tempo_compatible(sequence[-1]['tempo'], track['tempo'])]
    heapq.heapify(candidates)

    # Generate the main sequence
    while len(sequence) < 6:
        if not candidates:
            break
        _, next_track = heapq.heappop(candidates)
        if is_key_compatible(sequence[-1], next_track) and next_track['id'] not in used_ids:
            sequence.append(next_track)
            used_ids.add(next_track['id'])

    # Add closing high-hype tracks, ensuring they are the highest available that align
    for i in range(3):
        compatible_tracks = [track for track in final_high_hype_tracks if track['id'] not in used_ids and is_tempo_compatible(sequence[-1]['tempo'], track['tempo']) and is_key_compatible(sequence[-1], track)]
        if compatible_tracks:
            next_track = max(compatible_tracks, key=lambda x: x['hype'])
            sequence.append(next_track)
            used_ids.add(next_track['id'])

    return DataFrame(sequence)

def is_key_compatible(key1, key2):
    compatible_changes = [0, 5, 7, -5, -7]  # Account for wrap-around
    if key1['mode'] == key2['mode'] or (key1['mode'] != key2['mode'] and ((key1['key'] in [0, 5, 7] and key1['mode'] == 1) or (key2['key'] in [0, 5, 7] and key2['mode'] == 1))):
        for change in compatible_changes:
            if (key1['key'] + change) % 12 == key2['key']:
                return True
    return False

def is_tempo_compatible(tempo1, tempo2, max_difference=4):
    return abs(tempo1 - tempo2) <= max_difference

