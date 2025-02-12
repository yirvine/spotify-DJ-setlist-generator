# from utils import get_access_token, get_playlist_tracks, fetch_additional_track_details
# from dotenv import load_dotenv
# import os
# import datetime
# import pandas as pd

# def main():

#     load_dotenv()
#     client_id = os.getenv("SPOTIFY_CLIENT_ID")
#     client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
#     access_token = get_access_token(client_id, client_secret)

#     playlist_id = '5jJKoLaJ3YboeBsAuba76K'  # Correct playlist ID
#     top_tracks = get_playlist_tracks(playlist_id, access_token)
#     detailed_tracks = fetch_additional_track_details(top_tracks, access_token)

#     # Convert to DataFrame before saving to CSV
#     detailed_tracks_df = pd.DataFrame(detailed_tracks)
#     print(detailed_tracks_df.columns)
#     print(detailed_tracks_df.head())  # Show the first few rows to see the data
#     current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#     filename = f'song_sequence_{current_time}.csv'
#     detailed_tracks_df[['name', 'artists', 'key', 'mode']].to_csv(filename, index=False)
#     print(f"Sequence generated and saved to {filename}.")

# if __name__ == "__main__":
#     main()

from utils import get_access_token, get_track_ids, get_tracks_features, fetch_additional_track_details
from dotenv import load_dotenv
import os
import datetime
import pandas as pd

def main():
    load_dotenv()
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    access_token = get_access_token(client_id, client_secret)

    playlist_id = '5jJKoLaJ3YboeBsAuba76K'  # Use your actual playlist ID here

    # Step 1: Fetch track IDs from the playlist
    track_ids = get_track_ids(playlist_id, access_token)
    print(f"Total track IDs fetched: {len(track_ids)}")

    # Step 2: Fetch features for these track IDs in batches
    tracks_features = get_tracks_features(track_ids, access_token)
    print(f"Features fetched for {len(tracks_features)} tracks")

    # Step 3: Fetch additional details like artist name and track name
    detailed_tracks = fetch_additional_track_details(tracks_features, access_token)
    print(f"Details fetched for {len(detailed_tracks)} tracks")

    # Convert detailed track data to DataFrame
    detailed_tracks_df = pd.DataFrame(detailed_tracks)

    if not detailed_tracks_df.empty:
        print(detailed_tracks_df.columns)
        print(detailed_tracks_df.head())  # Show the first few rows to see the data
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f'song_sequence_{current_time}.csv'
        detailed_tracks_df[['name', 'artists', 'key', 'mode']].to_csv(filename, index=False)
        print(f"Sequence generated and saved to {filename}.")
    else:
        print("No tracks were fetched or all tracks had missing essential data.")

if __name__ == "__main__":
    main()
