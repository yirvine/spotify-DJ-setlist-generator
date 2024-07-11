import pandas as pd
import requester
import config
import utils
import asyncio

async def process_playlist_data(playlist_id, access_token):
    # Fetch track IDs from the playlist
    track_ids = await requester.get_playlist_tracks(playlist_id, access_token)
    print(f"Fetched {len(track_ids)} tracks from playlist {playlist_id}")

    # Fetch audio features for the tracks
    audio_features = await requester.fetch_audio_features(track_ids, access_token)
    print(f"Fetched audio features for {len(audio_features)} tracks")

    # Fetch track details
    track_details = await requester.get_track_details(track_ids, access_token)
    print(f"Fetched details for {len(track_details)} tracks")

    # Collect all unique artist IDs
    artist_ids = list(set([track['artists'][0]['id'] for track in track_details]))  # Assuming first artist is primary

    # Fetch genres for all unique artist IDs
    artist_genres = await requester.get_track_genres(artist_ids, access_token)
    artist_genres_dict = {artist['id']: artist['genres'] for artist in artist_genres}

    # Create a DataFrame from the track details and audio features
    data = []
    for track, features in zip(track_details, audio_features):
        artist_id = track['artists'][0]['id']  # Assuming first artist is primary
        genres = artist_genres_dict.get(artist_id, [])

        track_data = {
            'Track ID': track['id'],
            'Artist ID': artist_id,
            'Track Name': track['name'],
            'Artist Name(s)': ", ".join([artist['name'] for artist in track['artists']]),
            'Release Date': track['album']['release_date'],
            'Duration': track['duration_ms'],
            'Popularity': track['popularity'],
            'Genres': ", ".join(genres),
            'Danceability': features['danceability'],
            'Energy': features['energy'],
            'Key': features['key'],
            'Loudness': features['loudness'],
            'Mode': features['mode'],
            'Acousticness': features['acousticness'],
            'Tempo': features['tempo']
        }
        data.append(track_data)

    df = pd.DataFrame(data)
    df = utils.adjust_popularity(df)
    # print(df.head())
    return df

if __name__ == "__main__":
    asyncio.run(process_playlist_data(config.playlist_id, config.access_token))  # Use config.playlist_id and access_token
