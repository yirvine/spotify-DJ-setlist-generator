# import pandas as pd
# from requester import fetch_audio_features, get_playlist_tracks, get_track_details, get_track_genres

# def process_playlist_data(playlist_id):
#     track_ids = get_playlist_tracks(playlist_id)
#     track_details = get_track_details(track_ids)
#     audio_features = fetch_audio_features(track_ids)

#     data = []
#     for details, features in zip(track_details, audio_features):
#         artist_id = details['artists'][0]['id']
#         genres = get_track_genres(artist_id)
#         data.append({
#             'Track ID': details['id'],
#             'Artist ID': artist_id,
#             'Track Name': details['name'],
#             'Artist Name': details['artists'][0]['name'],
#             'Release Date': details['album']['release_date'],
#             'Duration': details['duration_ms'],
#             'Popularity': details['popularity'],
#             'Genres': genres,
#             'Danceability': features['danceability'],
#             'Energy': features['energy'],
#             'Key': features['key'],
#             'Loudness': features['loudness'],
#             'Mode': features['mode'],
#             'Acousticness': features['acousticness'],
#             'Tempo': features['tempo'],
#         })

#     df = pd.DataFrame(data)
#     return df
