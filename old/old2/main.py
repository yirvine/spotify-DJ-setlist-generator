# main.py

import pandas as pd
from utils import get_spotify_client, extract_features_from_playlist
from datetime import datetime

def main():
    sp = get_spotify_client()
    playlist_id = '5jJKoLaJ3YboeBsAuba76K'  # Your playlist ID
    df = extract_features_from_playlist(sp, playlist_id)

    # Get the current date and time
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")

    # Save the CSV with a unique name
    filename = f'playlist_features_{timestamp}.csv'
    df.to_csv(filename, index=False)
    print(f"Playlist features have been saved to {filename}")

if __name__ == '__main__':
    main()
