from utils import get_access_token, get_playlist_tracks, fetch_track_details
import pandas as pd
import datetime
import random

def main():
    access_token = get_access_token()
    playlist_id = '3PvHlYKI4XCKZcmzY8VjVe'  # Replace with your playlist ID
    playlist_tracks = get_playlist_tracks(playlist_id, access_token)
    
    track_data_list = []
    for track in playlist_tracks:
        track_id = track['track']['id']
        track_data = fetch_track_details(track_id, access_token)
        track_data_list.append(track_data)
    
    # Create DataFrame
    df = pd.DataFrame(track_data_list)
    
    # Pick a random first song
    first_song = random.choice(df.to_dict('records'))
    sequence = [first_song]
    
    print("Track sequence:")
    for track in sequence:
        print(f"Song: {track['name']}, Artist: {track['artists']}, Key: {track['key']}, Mode: {track['mode']}, Danceability: {track['danceability']}, Energy: {track['energy']}")
    
    # Save to CSV
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f'song_sequence_{current_time}.csv'
    df.to_csv(filename, index=False)
    print(f"Sequence generated and saved to {filename}.")

if __name__ == "__main__":
    main()
